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
    list_display = ('sender', 'room_name', 'message_type', 'is_read', 'created_at')
    list_filter = ('message_type', 'is_read', 'created_at')
    search_fields = ('message', 'sender__username', 'room_name')
    readonly_fields = ('created_at',)
