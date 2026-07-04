from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Call, UploadedAudioFile
from .serializers import AudioUploadSerializer, CallSerializer


class UploadAudioFileView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = AudioUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        audio = serializer.validated_data["audio"]

        call = Call.objects.create(user=request.user)
        UploadedAudioFile.objects.create(
            call=call,
            audio=audio,
            size=audio.size,
            type=audio.content_type or "",
            path=audio.name,
        )

        return Response(CallSerializer(call).data, status=status.HTTP_201_CREATED)
