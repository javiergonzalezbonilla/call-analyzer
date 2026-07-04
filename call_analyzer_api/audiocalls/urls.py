from django.urls import path

from . import views

app_name = "audiocalls"
urlpatterns = [
    path("upload/", views.UploadAudioFileView.as_view(), name="upload_file"),
    path("list/", views.ListCallsView.as_view(), name="list_calls"),
    path("details/<str:call_id>/", views.CallDetailsView.as_view(), name="call_detail"),
]
