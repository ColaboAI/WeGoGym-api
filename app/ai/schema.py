from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, ConfigDict, Field, FieldValidationInfo, validator


class AiCoachingFromLLM(BaseModel):
    summary: str
    answer: str
    motivation: str


class AiCoachingResponse(BaseModel):
    id: int
    post_id: int
    summary: str | None
    answer: str | None
    motivation: str | None

    like_cnt: int | None = 0
    is_liked: int | None = -1


ai_coaching_parser = PydanticOutputParser(pydantic_object=AiCoachingFromLLM)  # type: ignore
