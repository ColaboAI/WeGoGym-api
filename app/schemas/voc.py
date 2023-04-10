# voc response, request schema 정의(pydantic)

# app/schemas/voc.py
from pydantic import BaseModel, Field


class VOCBase(BaseModel):
    type: str = Field(..., title="신고 유형", description="신고 유형")
    plaintiff: str | None = Field(None, title="신고자", description="신고자")
    defendant: str | None = Field(None, title="피신고자", description="피신고자")
    content: str = Field(..., title="내용", description="내용")
    reason: str | None = Field(None, title="신고 사유", description="신고 사유")


class VOCRequest(VOCBase):
    def __str__(self) -> str:
        return f"""
        신고 유형: {self.type}\n신고자: {self.plaintiff}\n신고대상: {self.defendant}\n신고 사유: {self.reason}\n내용: {self.content}
        """
