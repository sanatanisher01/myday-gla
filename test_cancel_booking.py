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
from utils.email_utils import send_booking_cancelled

def test_cancel_booking():
    # Get the latest booking
    try:
        booking = Booking.objects.filter(status='pending').first()
        if not booking:
            print("No pending bookings found. Creating a new booking...")
            # Get a user
            user = User.objects.get(username='Aryanayusharushdevang')
            # Get an event
            event = Event.objects.first()
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
            booking.save()
            print(f"Test booking created with ID: {booking.booking_id}")
    except Exception as e:
        print(f"Error getting or creating booking: {e}")
        return
    
    # Cancel the booking
    booking.status = 'cancelled'
    booking.save()
    print(f"Booking cancelled with ID: {booking.booking_id}")
    
    # Send booking cancelled email
    print("\nSending booking cancelled email...")
    result = send_booking_cancelled(booking)
    print(f"Booking cancelled email sent: {result}")
    
    print("\nTest booking cancellation completed successfully!")
    return booking

if __name__ == "__main__":
    test_cancel_booking()
