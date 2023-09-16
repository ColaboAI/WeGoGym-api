import re
from langchain.chains import TransformChain
from langchain.callbacks.openai_info import (
    MODEL_COST_PER_1K_TOKENS,
    standardize_model_name,
    get_openai_token_cost_for_model,
)


def transform_func(inputs: dict) -> dict:
    text = inputs["text"]

    # replace multiple new lines and multiple spaces with a single one
    text = re.sub(r"(\r\n|\r|\n){2,}", r"\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return {"transformed_text": text}


async def async_transform_func(inputs: dict) -> dict:
    return transform_func(inputs)


def calc_cost(prompt_tokens: int, completion_tokens: int, model_name: str) -> float:
    model_name = standardize_model_name(model_name)
    if model_name not in MODEL_COST_PER_1K_TOKENS:
        raise ValueError(f"Model {model_name} not found in cost dictionary.")
    input_cost = get_openai_token_cost_for_model(model_name, prompt_tokens)
    output_cost = get_openai_token_cost_for_model(model_name, completion_tokens, is_completion=True)
    return input_cost + output_cost


transform_chain = TransformChain(
    input_variables=["text"],
    output_variables=["transformed_text"],
    transform=transform_func,
    atransform=None,
    verbose=True,
)
