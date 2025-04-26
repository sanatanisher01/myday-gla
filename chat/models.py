from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    sender_id = models.IntegerField()
    receiver_id = models.IntegerField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    @property
    def sender(self):
        return User.objects.get(id=self.sender_id)

    @property
    def receiver(self):
        return User.objects.get(id=self.receiver_id)

    def __str__(self):
        try:
            sender_username = User.objects.get(id=self.sender_id).username
            receiver_username = User.objects.get(id=self.receiver_id).username
            return f"{sender_username} to {receiver_username}: {self.message[:50]}"
        except User.DoesNotExist:
            return f"Message {self.id}: {self.message[:50]}"
