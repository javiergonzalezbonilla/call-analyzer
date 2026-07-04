from .base import *  # noqa
from .base import env

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True


STT_PROVIDER = env("STT_PROVIDER", default="mock")
DEEPGRAM_API_KEY = env("DEEPGRAM_API_KEY", default="")
ADMIN_EMAIL = env("ADMIN_EMAIL")
ADMIN_PASSWORD = env("ADMIN_PASSWORD")