from typing import Annotated
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel

str_default_none = Annotated[str | None, None]


class AiCoachingFromLLM(BaseModel):
    summary: str
    answer: str
    motivation: str


class AiCoachingResponse(BaseModel):
    id: int
    post_id: int
    summary: str_default_none = None
    answer: str_default_none = None
    motivation: str_default_none = None

    like_cnt: int | None = 0
    is_liked: int | None = -1


ai_coaching_parser = PydanticOutputParser(pydantic_object=AiCoachingFromLLM)  # type: ignore
