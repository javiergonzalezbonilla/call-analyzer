from rest_framework import serializers

from .models import Call, UploadedAudioFile


class UploadedAudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedAudioFile
        fields = ["id", "audio", "size", "type", "path", "metadata", "created_at"]
        read_only_fields = fields


class CallSerializer(serializers.ModelSerializer):
    uploaded_audio_files = UploadedAudioFileSerializer(
        source="audiocalls", many=True, read_only=True
    )

    class Meta:
        model = Call
        fields = [
            "call_id",
            "status",
            "uploaded_audio_files",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class AudioUploadSerializer(serializers.Serializer):
    audio = serializers.FileField()
