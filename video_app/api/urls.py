from django.urls import path , include
from video_app.api.views import (
    VideoListView,VideoPlayListView,VideoHlsSegmentView
     
)

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video-list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', VideoPlayListView.as_view(), name='video-playlist'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', VideoHlsSegmentView.as_view(), name='video-segment'),
]

