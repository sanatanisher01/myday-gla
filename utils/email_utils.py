from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_welcome_email(user):
    """
    Send a welcome email to newly registered users
    """
    subject = 'Welcome to MyDay!'
    html_message = render_to_string('emails/welcome_email.html', {'user': user})
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

def send_booking_confirmation(booking):
    """
    Send a booking confirmation email
    """
    subject = f'Booking Confirmation - {booking.event.name}'
    html_message = render_to_string('emails/booking_confirmation.html', {'booking': booking})
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

def send_booking_approved(booking):
    """
    Send a booking approved email
    """
    subject = f'Booking Approved - {booking.event.name}'
    html_message = render_to_string('emails/booking_approved.html', {'booking': booking})
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

def send_booking_rejected(booking):
    """
    Send a booking rejected email
    """
    subject = f'Booking Not Approved - {booking.event.name}'
    html_message = render_to_string('emails/booking_rejected.html', {'booking': booking})
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

def send_event_reminder(booking):
    """
    Send a reminder email for upcoming events
    """
    subject = f'Reminder: Your Event {booking.event.name} is Coming Up!'
    html_message = render_to_string('emails/event_reminder.html', {'booking': booking})
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

def send_booking_cancelled(booking):
    """
    Send a booking cancelled email
    """
    subject = f'Booking Cancelled - {booking.event.name}'
    html_message = render_to_string('emails/booking_cancelled.html', {'booking': booking})
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
