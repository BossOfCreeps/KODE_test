import os
from pydantic import BaseModel


class Scheme404(BaseModel):
    detail: str


MESSAGES_LIMIT = 5
AUTH_TOKEN_LENGTH = 20
MEDIA_FILENAME_LENGTH = 20

BASE_MEDIA_URL = "/media/"
BASE_MEDIA_PATH = os.path.join(os.curdir, "media")

if not os.path.exists(BASE_MEDIA_PATH):
    os.mkdir(BASE_MEDIA_PATH)
