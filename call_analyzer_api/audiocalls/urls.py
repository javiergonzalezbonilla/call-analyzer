from django.urls import path

from . import views

app_name = "audiocalls"
urlpatterns = [
    path("", views.ListCallsView.as_view(), name="list_calls"),
    path("upload/", views.UploadAudioFileView.as_view(), name="upload_file"),
    path("<str:call_id>/", views.CallDetailsView.as_view(), name="call_detail"),
]
