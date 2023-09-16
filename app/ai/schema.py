from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, ConfigDict, Field


class AiCoachingFromLLM(BaseModel):
    summary: str
    answer: str
    motivation: str


class AiCoachingRead(BaseModel):
    id: int
    post_id: int
    response: str

    model_config = ConfigDict(
        from_attributes=True,
    )


ai_coaching_parser = PydanticOutputParser(pydantic_object=AiCoachingFromLLM)  # type: ignore
