import smtplib
import ssl
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myday.settings')
django.setup()

from django.conf import settings

def test_smtp_connection():
    print(f"Testing SMTP connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    print(f"Using TLS: {settings.EMAIL_USE_TLS}")
    print(f"Username: {settings.EMAIL_HOST_USER}")
    
    try:
        # Create a secure SSL context
        context = ssl.create_default_context()
        
        # Try to connect to the SMTP server
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.ehlo()  # Can be omitted
            if settings.EMAIL_USE_TLS:
                server.starttls(context=context)
                server.ehlo()  # Can be omitted
            
            # Try to login
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            print("SMTP connection successful!")
            
            # Try to send a test email
            sender_email = settings.EMAIL_HOST_USER
            receiver_email = settings.EMAIL_HOST_USER  # Send to yourself for testing
            message = f"""\
Subject: Test Email from MyDay SMTP Test

This is a test email from MyDay SMTP test script.
If you're seeing this, the SMTP connection is working correctly!
"""
            
            server.sendmail(sender_email, receiver_email, message)
            print(f"Test email sent to {receiver_email}")
            
            return True
    except Exception as e:
        print(f"Error connecting to SMTP server: {e}")
        return False

if __name__ == "__main__":
    test_smtp_connection()
