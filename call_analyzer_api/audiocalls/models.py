from datetime import datetime

from django.db import models
import uuid
from users.models import User

# Create your models here.


class CallStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class Call(models.Model):
    call_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="audiocalls")
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    transcript = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    priority = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=CallStatus.choices, default=CallStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField("Tags", related_name="audiocalls")

    @property
    def uploaded_file(self):
        return UploadedAudioFile.objects.filter(call=self).first()


class TranscriptSegment(models.Model):
    call = models.ForeignKey(
        Call, on_delete=models.CASCADE, related_name="transcript_segments"
    )
    summary = models.TextField(null=True, blank=True)
    start_time = models.FloatField()
    end_time = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tags(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TranscriptionRole(models.Model):
    transcript_segment = models.ForeignKey(
        "TranscriptSegment",
        on_delete=models.CASCADE,
        related_name="transcription_roles",
    )
    speaker = models.CharField(max_length=100)
    start_time = models.FloatField()
    end_time = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    text = models.TextField()


class UploadedAudioFile(models.Model):
    audio = models.FileField(upload_to="uploaded_audio_files/")
    size = models.IntegerField()
    type = models.CharField(max_length=100)
    call = models.ForeignKey(Call, on_delete=models.CASCADE, related_name="audiocalls")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    path = models.CharField(max_length=200)
    metadata = models.JSONField(default=dict, blank=True)
