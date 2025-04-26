from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'short_message', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('message', 'sender__username', 'receiver__username')
    readonly_fields = ('timestamp',)

    def short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message

    short_message.short_description = 'Message'
