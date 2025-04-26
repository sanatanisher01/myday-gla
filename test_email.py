import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myday.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    subject = 'Test Email from MyDay'
    message = 'This is a test email from MyDay application.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [settings.EMAIL_HOST_USER]  # Send to yourself for testing
    
    print(f"Attempting to send email from {from_email} to {recipient_list}")
    print(f"Email settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, TLS={settings.EMAIL_USE_TLS}")
    
    try:
        result = send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        print(f"Email sent successfully! Result: {result}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

if __name__ == "__main__":
    test_email()
