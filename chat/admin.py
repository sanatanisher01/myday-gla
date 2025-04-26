from django.contrib import admin
from .models import ChatRoom, ChatMessage

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'get_users')
    search_fields = ('name', 'users__username')
    filter_horizontal = ('users',)
    readonly_fields = ('created_at', 'updated_at')

    def get_users(self, obj):
        return ", ".join([user.username for user in obj.users.all()])

    get_users.short_description = 'Users'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'short_message', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('message', 'sender__username', 'receiver__username')
    readonly_fields = ('timestamp',)

    def short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message

    short_message.short_description = 'Message'
