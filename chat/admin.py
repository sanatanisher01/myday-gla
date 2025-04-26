from django.contrib import admin
from django.contrib.auth.models import User
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('get_sender', 'get_receiver', 'short_message', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('message',)
    readonly_fields = ('timestamp', 'sender_id', 'receiver_id')

    def get_sender(self, obj):
        try:
            return User.objects.get(id=obj.sender_id).username
        except User.DoesNotExist:
            return f"User {obj.sender_id}"

    def get_receiver(self, obj):
        try:
            return User.objects.get(id=obj.receiver_id).username
        except User.DoesNotExist:
            return f"User {obj.receiver_id}"

    def short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message

    get_sender.short_description = 'Sender'
    get_receiver.short_description = 'Receiver'
    short_message.short_description = 'Message'
