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


STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_STORAGE_BUCKET_NAME = 'static'

AWS_ACCESS_KEY_ID = 'abcd'
AWS_SECRET_ACCESS_KEY = 'abcd2345'
AWS_S3_ENDPOINT_URL = 'http://localhost:9000'