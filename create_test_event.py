import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myday.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from events.models import Event, SubEvent, Category
from django.utils.text import slugify

def create_test_event():
    # Get a user
    try:
        user = User.objects.get(username='Aryanayusharushdevang')
    except User.DoesNotExist:
        print("User not found. Please create a user first.")
        return

    # Create test event
    event_name = 'Test Event for Email Testing'
    event_slug = slugify(event_name)

    # Check if event already exists
    if Event.objects.filter(slug=event_slug).exists():
        event = Event.objects.get(slug=event_slug)
        print(f"Event '{event_name}' already exists with ID: {event.id}")
    else:
        event = Event.objects.create(
            name=event_name,
            slug=event_slug,
            description='This is a test event for email testing.',
            cover_photo='event_covers/default.jpg',  # Default image
            created_by=user
        )
        print(f"Event '{event_name}' created with ID: {event.id}")

    # Create sub-event
    sub_event, created = SubEvent.objects.get_or_create(
        event=event,
        name='Test Sub-Event',
        defaults={
            'description': 'This is a test sub-event for email testing.',
            'price': 500
        }
    )

    if created:
        print(f"Sub-event 'Test Sub-Event' created for event '{event_name}'")
    else:
        print(f"Sub-event 'Test Sub-Event' already exists for event '{event_name}'")

    # Create category
    category, created = Category.objects.get_or_create(
        sub_event=sub_event,
        name='Test Category',
        defaults={
            'description': 'This is a test category for email testing.',
            'price': 200
        }
    )

    if created:
        print(f"Category 'Test Category' created for sub-event 'Test Sub-Event'")
    else:
        print(f"Category 'Test Category' already exists for sub-event 'Test Sub-Event'")

    print("\nTest event setup completed!")
    return event

if __name__ == "__main__":
    create_test_event()
