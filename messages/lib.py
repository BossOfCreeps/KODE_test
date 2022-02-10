import base64
import os
from random import choice
from string import ascii_letters, digits

import requests

from constants import BASE_MEDIA_PATH, MEDIA_FILENAME_LENGTH, BASE_MEDIA_URL


def unique_filename() -> str:
    temp_filename = ''.join(choice(ascii_letters + digits) for _ in range(MEDIA_FILENAME_LENGTH))
    if temp_filename in os.listdir(BASE_MEDIA_PATH):
        return unique_filename()
    else:
        return temp_filename


def save_file_from_url(url: str) -> str:
    filename = f"{unique_filename()}.{url.split('.')[-1]}"
    with open(os.path.join(BASE_MEDIA_PATH, filename), 'wb') as file:
        file.write(requests.get(url, allow_redirects=True).content)
    return f"{BASE_MEDIA_URL}{filename}"


def save_file_from_base64(name: str, value: str) -> str:
    filename = f"{unique_filename()}.{name.split('.')[-1]}"
    with open(os.path.join(BASE_MEDIA_PATH, filename), 'wb') as file:
        file.write(base64.b64decode(value))
    return f"{BASE_MEDIA_URL}{filename}"
