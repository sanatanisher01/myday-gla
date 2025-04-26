from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Creates a manager user'

    def handle(self, *args, **kwargs):
        try:
            # Check if user already exists
            if User.objects.filter(username='aryanayusharushdevang').exists():
                user = User.objects.get(username='aryanayusharushdevang')
                self.stdout.write(self.style.WARNING(f'User {user.username} already exists'))
            else:
                # Create user
                user = User.objects.create_user(
                    username='aryanayusharushdevang',
                    email='aryansanatani01@gmail.com',
                    password='Aryanada@010'
                )
                user.first_name = 'Aryan'
                user.last_name = 'Manager'
                user.save()
                self.stdout.write(self.style.SUCCESS(f'User {user.username} created successfully'))
            
            # Get or create profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_manager = True
            profile.save()
            
            self.stdout.write(self.style.SUCCESS(f'User {user.username} is now a manager'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
