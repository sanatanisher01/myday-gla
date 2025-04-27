from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import logging
import traceback

# Set up logging
logger = logging.getLogger(__name__)

def send_welcome_email(user, request=None):
    """
    Send a welcome email to newly registered users
    """
    subject = 'Welcome to MyDay!'

    # Create context with site_url if request is provided
    context = {'user': user}
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        site_url = f"{protocol}://{host}"
        context['site_url'] = site_url

    html_message = render_to_string('emails/welcome_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = user.email

    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False

def send_booking_confirmation(booking, request=None):
    """
    Send a booking confirmation email
    """
    subject = f'Booking Confirmation - {booking.event.name}'

    # Create context with site_url if request is provided
    context = {'booking': booking}
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        site_url = f"{protocol}://{host}"
        context['site_url'] = site_url

    html_message = render_to_string('emails/booking_confirmation.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
    to_email = booking.user.email

    # Log email details for debugging
    logger.info(f"Attempting to send booking confirmation email to {to_email}")
    logger.info(f"Email settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, USER={settings.EMAIL_HOST_USER}")

    try:
        # Check if email credentials are configured
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            logger.error("Email credentials are not configured. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD settings.")
            return False

        # Send the email
        result = send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False,
        )

        if result:
            logger.info(f"Successfully sent booking confirmation email to {to_email}")
            return True
        else:
            logger.error(f"Failed to send booking confirmation email to {to_email} (send_mail returned {result})")
            return False

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error sending booking confirmation email: {e}")
        logger.error(f"Error details: {error_details}")
        return False

def send_booking_approved(booking, request=None):
    """
    Send a booking approved email
    """
    subject = f'Booking Approved - {booking.event.name}'

    # Create context with site_url if request is provided
    context = {'booking': booking}
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        site_url = f"{protocol}://{host}"
        context['site_url'] = site_url

    html_message = render_to_string('emails/booking_approved.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = booking.user.email

    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending booking approved email: {e}")
        return False

def send_booking_rejected(booking, request=None):
    """
    Send a booking rejected email
    """
    subject = f'Booking Not Approved - {booking.event.name}'

    # Create context with site_url if request is provided
    context = {'booking': booking}
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        site_url = f"{protocol}://{host}"
        context['site_url'] = site_url

    html_message = render_to_string('emails/booking_rejected.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = booking.user.email

    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending booking rejected email: {e}")
        return False

def send_event_reminder(booking, request=None):
    """
    Send a reminder email for upcoming events
    """
    subject = f'Reminder: Your Event {booking.event.name} is Coming Up!'

    # Create context with site_url if request is provided
    context = {'booking': booking}
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        site_url = f"{protocol}://{host}"
        context['site_url'] = site_url

    html_message = render_to_string('emails/event_reminder.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = booking.user.email

    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending event reminder email: {e}")
        return False

def send_booking_cancelled(booking, request=None):
    """
    Send a booking cancelled email
    """
    subject = f'Booking Cancelled - {booking.event.name}'

    # Create context with site_url if request is provided
    context = {'booking': booking}
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        site_url = f"{protocol}://{host}"
        context['site_url'] = site_url

    html_message = render_to_string('emails/booking_cancelled.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
    to_email = booking.user.email

    # Log email details for debugging
    logger.info(f"Attempting to send booking cancelled email to {to_email}")

    try:
        # Check if email credentials are configured
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            logger.error("Email credentials are not configured. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD settings.")
            return False

        # Send the email
        result = send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False,
        )

        if result:
            logger.info(f"Successfully sent booking cancelled email to {to_email}")
            return True
        else:
            logger.error(f"Failed to send booking cancelled email to {to_email} (send_mail returned {result})")
            return False

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error sending booking cancelled email: {e}")
        logger.error(f"Error details: {error_details}")
        return False

def test_email_configuration(to_email=None):
    """
    Test the email configuration by sending a test email
    """
    if not to_email:
        # Use the default email if none provided
        to_email = settings.EMAIL_HOST_USER

    subject = 'MyDay Email Test'
    message = 'This is a test email from MyDay to verify the email configuration is working correctly.'
    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER

    logger.info(f"Testing email configuration with the following settings:")
    logger.info(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    logger.info(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    logger.info(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    logger.info(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    logger.info(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    logger.info(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    logger.info(f"Sending test email to: {to_email}")

    try:
        # Check if email credentials are configured
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            logger.error("Email credentials are not configured. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD settings.")
            return False

        # Send the email
        result = send_mail(
            subject,
            message,
            from_email,
            [to_email],
            fail_silently=False,
        )

        if result:
            logger.info(f"Successfully sent test email to {to_email}")
            return True
        else:
            logger.error(f"Failed to send test email to {to_email} (send_mail returned {result})")
            return False

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error sending test email: {e}")
        logger.error(f"Error details: {error_details}")
        return False
