import os
import django
import sys
import uuid
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myday.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from events.models import Event
from bookings.models import Booking
from utils.email_utils import (
    send_welcome_email,
    send_booking_confirmation,
    send_booking_approved,
    send_booking_rejected,
    send_event_reminder
)
from django.conf import settings

def test_all_emails():
    # Print email settings
    print(f"Email settings:")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'Not set'}")
    print()
    
    # Get a user
    try:
        user = User.objects.get(username='Aryanayusharushdevang')
    except User.DoesNotExist:
        print("User not found. Please create a user first.")
        return
    
    # Get an event
    try:
        event = Event.objects.first()
        if not event:
            print("No events found. Please create an event first.")
            return
    except:
        print("Error getting event.")
        return
    
    # Create a test booking
    booking = Booking(
        user=user,
        event=event,
        booking_id=uuid.uuid4(),
        booking_date=timezone.now().date(),
        guest_count=5,
        total_price=5000,
        final_price=4500,
        status='pending'
    )
    
    # Save the booking to the database
    try:
        booking.save()
        print(f"Test booking created with ID: {booking.booking_id}")
    except Exception as e:
        print(f"Error creating test booking: {e}")
    
    # Test welcome email
    print("\nTesting welcome email...")
    result = send_welcome_email(user)
    print(f"Welcome email sent: {result}")
    
    # Test booking confirmation email
    print("\nTesting booking confirmation email...")
    result = send_booking_confirmation(booking)
    print(f"Booking confirmation email sent: {result}")
    
    # Test booking approved email
    print("\nTesting booking approved email...")
    result = send_booking_approved(booking)
    print(f"Booking approved email sent: {result}")
    
    # Test booking rejected email
    print("\nTesting booking rejected email...")
    result = send_booking_rejected(booking)
    print(f"Booking rejected email sent: {result}")
    
    # Test event reminder email
    print("\nTesting event reminder email...")
    result = send_event_reminder(booking)
    print(f"Event reminder email sent: {result}")
    
    print("\nAll email tests completed!")

if __name__ == "__main__":
    test_all_emails()
