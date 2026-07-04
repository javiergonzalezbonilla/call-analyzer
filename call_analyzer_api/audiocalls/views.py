from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from call_analyzer_api.taskapp.celery import process_audio_file_task

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

        process_audio_file_task.delay(call.call_id)

        return Response(CallSerializer(call).data, status=status.HTTP_201_CREATED)


class ListCallsView(APIView):
    def get(self, request):
        calls = Call.objects.filter(user=request.user)
        serializer = CallSerializer(calls, many=True)
        return Response(serializer.data)


class CallDetailsView(APIView):
    def get(self, request, call_id):
        call = get_object_or_404(Call, call_id=call_id, user=request.user)
        serializer = CallSerializer(call)
        return Response(serializer.data)
