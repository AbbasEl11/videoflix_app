from django.urls import path , include
from .views import VideoView

urlpatterns = [
    path('video/', VideoView.as_view(), name='video'),

] 
