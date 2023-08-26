from pydantic import BaseModel
from typing import Optional


class AppVersion(BaseModel):
    version_number: str
    update_link_iOS: str
    update_link_android: str


latest_version = AppVersion(
    version_number="1.0.4",
    update_link_iOS="https://apps.apple.com/kr/app/wegogym/id6447636341",
    update_link_android="https://play.google.com/store/search?q=%EC%9C%84%EA%B3%A0%EC%A7%90&c=apps&hl=ko-KR",
)
