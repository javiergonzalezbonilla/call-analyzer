from django.urls import path

from . import views

app_name = "audiocalls"
urlpatterns = [
    path("upload/", views.UploadAudioFileView.as_view(), name="upload_file"),
]
