from fastapi.encoders import jsonable_encoder
import openai
from pydantic import UUID4
import ujson
from app.ai.client import get_summary_chain, text_splitter
from app.ai.prompt import (
    get_gpt_messages,
    get_zero_shot_prompt,
)
from app.ai import repository as ai_coaching_repository
from app.ai.utils import calc_cost, transform_func
from app.ai.config import ai_settings
from app.core.exceptions.base import BadRequestException
from app.utils.ecs_log import logger
from app.services import fcm_service
from langchain.callbacks import get_openai_callback
import tiktoken
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import NotFoundException


async def make_ai_coaching(user_input: str, user_id: UUID4, post_id: UUID4, model_name="gpt-3.5-turbo"):
    summary_chain = get_summary_chain(
        model_name=model_name,
        chain_type="map_reduce",
        verbose=True,
    )

    processed_text = transform_func({"text": user_input})
    logger.debug(processed_text)
    # count token length with tiktoken tokenizer

    encoding = tiktoken.encoding_for_model(model_name)
    token_length = len(encoding.encode(get_zero_shot_prompt(processed_text["transformed_text"])))
    logger.debug(f"prompt token counts: {token_length}")
    result = None

    try:
        if token_length > 1024 * 4:
            with get_openai_callback() as cb:
                docs = text_splitter.create_documents([processed_text["transformed_text"]])
                logger.debug(f"docs: {docs}")
                text = await summary_chain.arun(docs)

                logger.debug(repr(cb))
                result = {
                    "response": text,
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "cost": cb.total_cost,
                    "model_name": model_name,
                }
        else:
            result = await openai_chat_completion(
                user_input=processed_text["transformed_text"],
                model_name=model_name,
            )
    except Exception as e:
        logger.error(e)
        raise e

    if result is not None:
        try:
            result["post_id"] = post_id
            result["user_id"] = user_id
            await ai_coaching_repository.create_ai_coaching(result)
            parsed_response = ujson.loads(result["response"])
            if parsed_response["summary"] is not None:
                await ai_coaching_repository.update_post_summary_where_id(
                    post_id,
                    parsed_response["summary"][:200],
                )
            if parsed_response["answer"] is not None:
                await fcm_service.send_message_to_single_device_by_uid(
                    user_id=user_id,
                    title="AI 코칭이 도착했어요!",
                    body=parsed_response["answer"][:50],  # 50자까지만 보여주기
                    data={"post_id": str(post_id)},
                )
        except Exception as e:
            logger.error(e)


async def openai_chat_completion(user_input: str, model_name="gpt-3.5-turbo"):
    openai.api_key = ai_settings.OPENAI_API_KEY
    messages = get_gpt_messages(model_name=model_name, user_input=user_input)
    response = await openai.ChatCompletion.acreate(model=model_name, messages=messages, temperature=0.1)
    logger.debug(response)
    prompt_tokens = response["usage"]["prompt_tokens"]
    completion_tokens = response["usage"]["completion_tokens"]
    cost = calc_cost(prompt_tokens, completion_tokens, model_name)
    return {
        "response": response["choices"][0]["message"]["content"],
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cost": cost,
        "model_name": model_name,
    }


async def get_ai_coaching_where_post_id(post_id: int, user_id: UUID4 | None) -> dict | None:
    ai_coaching_obj = await ai_coaching_repository.get_ai_coaching_where_post_id(post_id, user_id)
    if ai_coaching_obj is None:
        return None
    encoded = jsonable_encoder(ai_coaching_obj)
    ai_response: dict | None = None
    try:
        ai_response_raw = encoded.pop("response")
        ai_response = ujson.loads(ai_response_raw)
    except KeyError:
        ai_response = None
    except ujson.JSONDecodeError:
        ai_response = {"answer": ai_response_raw}
    return {**encoded, **ai_response} if ai_response is not None else {**encoded}


async def get_ai_coaching_where_id(ai_coaching_id: int, user_id: UUID4) -> dict:
    try:
        ai_coaching_obj = await ai_coaching_repository.get_ai_coaching_where_id(ai_coaching_id, user_id)
        encoded = jsonable_encoder(ai_coaching_obj)
        ai_response = ujson.loads(encoded.pop("response"))
        return {**encoded, **ai_response}

    except NoResultFound as e:
        raise NotFoundException("AI Coaching not found") from e


async def create_or_update_ai_coaching_like(ai_coaching_id: int, user_id: UUID4, like: int):
    try:
        await ai_coaching_repository.create_or_update_like(ai_coaching_id, user_id, like)
        return await get_ai_coaching_where_id(ai_coaching_id, user_id)
    except IntegrityError as e:
        raise BadRequestException(str(e.orig)) from e


async def delete_ai_coaching_like(ai_coaching_id: int, user_id: UUID4):
    try:
        await ai_coaching_repository.delete_like_where_ai_coaching_id_and_user_id(ai_coaching_id, user_id)
        return await get_ai_coaching_where_id(ai_coaching_id, user_id)
    except NoResultFound as e:
        raise NotFoundException("Like not found") from e
