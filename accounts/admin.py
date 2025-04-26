from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_manager')

    def is_manager(self, obj):
        return obj.profile.is_manager

    is_manager.boolean = True
    is_manager.short_description = 'Manager'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)