#!/usr/bin/env python
"""
Script to set up the manager user with the correct credentials.
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myday.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def setup_manager():
    """Set up the manager user with the correct credentials."""
    print("Setting up manager user...")
    
    # Check if user exists
    if User.objects.filter(username='Aryanayusharushdevang').exists():
        user = User.objects.get(username='Aryanayusharushdevang')
        print(f"User {user.username} already exists. Updating password...")
        user.set_password('Aditya@010')
        user.save()
    else:
        # Create user
        print("Creating new manager user...")
        user = User.objects.create_user(
            username='Aryanayusharushdevang',
            email='aryansanatani01@gmail.com',
            password='Aditya@010'
        )
        user.first_name = 'Aryan'
        user.last_name = 'Manager'
        user.save()
    
    # Ensure user has manager privileges
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.is_manager = True
    profile.save()
    
    print(f"Manager user {user.username} is set up with the correct credentials.")
    print("Username: Aryanayusharushdevang")
    print("Password: Aditya@010")

if __name__ == '__main__':
    setup_manager()