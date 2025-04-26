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
from utils.email_utils import send_booking_confirmation, send_booking_approved

def create_test_booking():
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
        return
    
    # Send booking confirmation email
    print("\nSending booking confirmation email...")
    result = send_booking_confirmation(booking)
    print(f"Booking confirmation email sent: {result}")
    
    # Approve the booking
    booking.status = 'approved'
    booking.save()
    print(f"Booking approved with ID: {booking.booking_id}")
    
    # Send booking approved email
    print("\nSending booking approved email...")
    result = send_booking_approved(booking)
    print(f"Booking approved email sent: {result}")
    
    print("\nTest booking created and approved successfully!")
    return booking

if __name__ == "__main__":
    create_test_booking()
