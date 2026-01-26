from django.urls import path , include
from video_app.api.views import (
    VideoView,
     
)

urlpatterns = [
    path('video/', VideoView.as_view(), name='video-list'),

]

