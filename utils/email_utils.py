from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

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
        print(f"Error sending booking confirmation email: {e}")
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
        print(f"Error sending booking cancelled email: {e}")
        return False
