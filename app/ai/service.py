import openai
from pydantic import UUID4
import ujson
from app.ai.client import get_summary_chain, text_splitter
from app.ai.prompt import get_zero_shot_prompt
from app.ai.repository import create_ai_coaching
from app.ai.utils import calc_cost, transform_func
from app.utils.ecs_log import logger
from app.services import fcm_service
from app.ai.config import ai_settings
from langchain.callbacks import get_openai_callback

import tiktoken


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
    docs = text_splitter.create_documents([processed_text["transformed_text"]])
    logger.debug(f"docs: {docs}")

    try:
        if token_length > 2048:
            with get_openai_callback() as cb:
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
            )
    except Exception as e:
        logger.error(e)
        raise e

    if result is not None:
        try:
            result["post_id"] = post_id
            result["user_id"] = user_id
            await create_ai_coaching(result)
            parsed_response = ujson.loads(result["response"])
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
    messages = [
        {"role": "user", "content": get_zero_shot_prompt(user_input)},
    ]
    response = await openai.ChatCompletion.acreate(model=model_name, messages=messages, temperature=0, max_tokens=2048)
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
