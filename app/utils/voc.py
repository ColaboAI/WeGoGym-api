import json

import requests

from app.core.config import settings


def create_voc(message: dict[str, str]):
    res = requests.post(settings.DISCORD_WEBHOOK_URL, data=message)
    return res
