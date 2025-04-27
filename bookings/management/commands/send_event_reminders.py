from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from bookings.models import Booking
from utils.email_utils import send_event_reminder

class Command(BaseCommand):
    help = 'Send reminder emails for upcoming events'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Send reminders for events happening in this many days'
        )

    def handle(self, *args, **options):
        days = options['days']

        # Calculate the target date
        target_date = timezone.now().date() + timedelta(days=days)

        # Get all approved bookings for the target date
        bookings = Booking.objects.filter(
            status='approved',
            booking_date=target_date
        )

        self.stdout.write(f"Found {bookings.count()} approved bookings for {target_date}")

        # Send reminder emails
        success_count = 0
        for booking in bookings:
            try:
                # Create a mock request with the site URL from settings
                class MockRequest:
                    def __init__(self):
                        self.is_secure = lambda: True
                        self.get_host = lambda: settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'

                mock_request = MockRequest()
                result = send_event_reminder(booking, mock_request)
                if result:
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"Successfully sent reminder for booking {booking.booking_id} to {booking.user.email}"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"Failed to send reminder for booking {booking.booking_id} to {booking.user.email}"
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Error sending reminder for booking {booking.booking_id}: {str(e)}"
                ))

        self.stdout.write(self.style.SUCCESS(
            f"Successfully sent {success_count} out of {bookings.count()} reminders"
        ))
