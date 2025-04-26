from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', null=True)
    room_name = models.CharField(max_length=100, null=True)
    message = models.TextField()
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    file_url = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username if self.sender else 'Unknown'}: {self.message[:50]}"
