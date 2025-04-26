# MyDay - Event Booking Platform

MyDay is a comprehensive event booking platform that allows users to browse, book, and manage various events. The platform also provides event managers with tools to create and manage their events, handle bookings, and communicate with customers.

## Features

- User registration and authentication
- Event browsing and searching
- Event booking with customization options
- Booking management for users and event managers
- Event gallery with image uploads
- Reviews and ratings for events
- Discount code system
- Email notifications for various actions
- Chat functionality between users and event managers
- Dashboard for event managers with analytics

## Installation

### Local Development

1. Clone the repository:
```
git clone https://github.com/yourusername/myday.git
cd myday
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:
```
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Cloudinary settings (for image uploads)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

5. Run the migrations:
```
python manage.py migrate
```

6. Create a superuser:
```
python manage.py createsuperuser
```

7. Run the development server:
```
python manage.py runserver
```

8. Visit `http://127.0.0.1:8000/` in your browser.

### Deployment

To deploy this application to a production environment, you'll need to:

1. Set up a web server (e.g., Nginx, Apache)
2. Configure a WSGI server (e.g., Gunicorn, uWSGI)
3. Set up a production database (e.g., PostgreSQL, MySQL)
4. Configure environment variables for production settings
5. Set up static file serving
6. Configure SSL/TLS for secure connections

Detailed deployment instructions will depend on your hosting provider and preferences.

## Email Functionality

The application includes email functionality for various actions:

- Welcome email when a user registers
- Booking confirmation email when a user creates a booking
- Booking approved email when a booking is approved
- Booking rejected email when a booking is rejected
- Booking cancelled email when a user cancels a booking
- Event reminder email before an event

For more information on how to set up and use the email functionality, see [EMAIL_SETUP.md](EMAIL_SETUP.md).

## Management Commands

The application includes management commands for various tasks:

- `send_event_reminders`: Send reminder emails for upcoming events
```
python manage.py send_event_reminders --days=1
```

## User Roles

### Regular Users
- Browse and search events
- Create and manage bookings
- Chat with event managers
- Write reviews for events

### Event Managers
- Create and manage events
- Handle bookings (approve, reject)
- Chat with customers
- Create and manage discount codes
- View analytics for their events

### Admin
- Manage all users, events, and bookings
- Access the Django admin interface

## Technologies Used

- Django: Web framework
- Bootstrap: Frontend framework
- Cloudinary: Image storage
- SQLite: Database
- SMTP: Email sending
- WhiteNoise: Static file serving

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Django documentation
- Bootstrap documentation
- Cloudinary documentation
- All contributors to the project
