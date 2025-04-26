from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('create/<int:user_id>/', views.create_chat, name='create_chat'),
    path('upload/', views.upload_file, name='upload_file'),
    path('<int:user_id>/', views.chat_room, name='chat_room'),
]
