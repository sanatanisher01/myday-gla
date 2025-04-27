from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Updates the manager user password'

    def handle(self, *args, **kwargs):
        try:
            # Check if user exists
            if User.objects.filter(username='Aryanayusharushdevang').exists():
                user = User.objects.get(username='Aryanayusharushdevang')
                user.set_password('Aditya@010')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Password updated for user {user.username}'))
                
                # Ensure user has manager privileges
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.is_manager = True
                profile.save()
                self.stdout.write(self.style.SUCCESS(f'User {user.username} is now a manager'))
            else:
                self.stdout.write(self.style.WARNING(f'User Aryanayusharushdevang does not exist. Run create_manager command first.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
