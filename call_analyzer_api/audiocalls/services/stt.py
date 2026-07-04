import abc
import json
from django.conf import settings
from deepgram import DeepgramClient

AUDIO_URL = "https://static.deepgram.com/examples/Bueller-Life-moves-pretty-fast.wav"


class SSTService(abc.ABC):
    @abc.abstractmethod
    def transcript(self, audio_url: str):
        pass


class DeepgramSSTService(SSTService):
    def __init__(self):
        self.deepgram = DeepgramClient(api_key=settings.DEEPGRAM_API_KEY)

    def transcript(self, audio_url: str):
        try:
            response = self.deepgram.listen.v1.media.transcribe_url(
                url=audio_url,
                model="nova-3",
                language="en",
                summarize="v2",
                topics=True,
                intents=True,
                sentiment=True,
                smart_format=True,
                diarize=True,
                paragraphs=True,
            )
            return response
        except Exception as e:
            print(f"Exception: {e}")


class MockSSTService(SSTService):
    def transcript(self, audio_url: str):
        try:
            with open("./mock_data/mock_transcription.json", "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Exception: {e}")


class SttServiceFactory:

    def get_service(self, provider: str):
        povider = settings.STT_PROVIDER
        if povider == "deepgram":
            return DeepgramSSTService()
        elif povider == "mock":
            return MockSSTService()
        else:
            raise ValueError(f"Invalid provider: {provider}")
