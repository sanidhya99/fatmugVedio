from django.urls import path
from . import views

urlpatterns = [
    path('', views.video_list, name='video_list'),
    path('upload/', views.upload_video, name='upload_video'),
    # path('upload/error/', views.upload_error, name='upload_error'),  # Add this line
    path('search/', views.search_video, name='search_video'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
]
