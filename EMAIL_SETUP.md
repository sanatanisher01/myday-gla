# Email Setup for MyDay

This document provides instructions on how to set up and use the email functionality in the MyDay application.

## Email Configuration

The email functionality is configured in the `settings.py` file. The following settings are used:

```python
# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
```

## Environment Variables

The email settings are loaded from environment variables. You can set these variables in the `.env` file in the root directory of the project:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Gmail App Password

If you're using Gmail as your email provider, you need to create an app password for your application. Here's how:

1. Go to your Google Account settings: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", click on "2-Step Verification"
4. Scroll down to the bottom and click on "App passwords"
5. Select "Mail" as the app and "Other" as the device
6. Enter a name for your app (e.g., "MyDay")
7. Click on "Generate"
8. Copy the generated password and use it as your `EMAIL_HOST_PASSWORD`

## Email Templates

The email templates are located in the `templates/emails` directory. The following templates are available:

- `base_email.html`: Base template for all emails
- `welcome_email.html`: Welcome email sent when a user registers
- `booking_confirmation.html`: Confirmation email sent when a user creates a booking
- `booking_approved.html`: Email sent when a booking is approved
- `booking_rejected.html`: Email sent when a booking is rejected
- `booking_cancelled.html`: Email sent when a user cancels a booking
- `event_reminder.html`: Reminder email sent before an event

## Email Utility Functions

The email utility functions are located in the `utils/email_utils.py` file. The following functions are available:

- `send_welcome_email(user)`: Send a welcome email to a new user
- `send_booking_confirmation(booking)`: Send a booking confirmation email
- `send_booking_approved(booking)`: Send a booking approved email
- `send_booking_rejected(booking)`: Send a booking rejected email
- `send_booking_cancelled(booking)`: Send a booking cancelled email
- `send_event_reminder(booking)`: Send an event reminder email

## Sending Event Reminders

The application includes a management command to send event reminders for upcoming events. You can run this command manually or set up a cron job to run it automatically.

To send reminders for events happening tomorrow:

```
python manage.py send_event_reminders --days=1
```

To send reminders for events happening today:

```
python manage.py send_event_reminders --days=0
```

## Setting Up a Cron Job

To set up a cron job to send event reminders automatically, you can use the following command:

```
0 8 * * * cd /path/to/myday && python manage.py send_event_reminders --days=1
```

This will run the command every day at 8:00 AM and send reminders for events happening the next day.

## Troubleshooting

If you're having issues with the email functionality, you can try the following:

1. Check the email settings in the `.env` file
2. Make sure the email templates exist in the `templates/emails` directory
3. Check if the email utility functions are imported correctly
4. Try sending a test email using the `test_email.py` script

If you're still having issues, please contact the development team for assistance.
