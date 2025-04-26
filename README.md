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

### Deployment on Railway

This project is configured for deployment on Railway. The deployment is automated using the `railway.json` configuration file.

#### Prerequisites

1. A Railway account
2. A Cloudinary account for media storage
3. (Optional) An email service account for sending emails

#### Deployment Steps

1. Fork or clone this repository to your GitHub account
2. Create a new project on Railway
3. Connect your GitHub repository to Railway
4. Add a PostgreSQL database to your project
5. Configure the environment variables in the Railway dashboard:
   - `DJANGO_SECRET_KEY`: A secure random key for Django
   - `DJANGO_DEBUG`: Set to False for production
   - `RAILWAY_ENVIRONMENT`: Set to production
   - `CLOUDINARY_CLOUD_NAME`: Your Cloudinary cloud name
   - `CLOUDINARY_API_KEY`: Your Cloudinary API key
   - `CLOUDINARY_API_SECRET`: Your Cloudinary API secret
   - `EMAIL_HOST_USER`: Your email address for sending emails
   - `EMAIL_HOST_PASSWORD`: Your email password or app password

#### Manual Deployment

If you prefer to set up the deployment manually:

1. Create a new service on Railway
2. Connect your GitHub repository
3. Railway will automatically detect the `Procfile` and deploy your application
4. Add the environment variables listed above
5. Create a PostgreSQL database and link it to your service

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
- PostgreSQL: Database (in production)
- SQLite: Database (in development)
- SMTP: Email sending
- Gunicorn: WSGI HTTP Server
- WhiteNoise: Static file serving
- Railway: Cloud hosting platform

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Django documentation
- Bootstrap documentation
- Cloudinary documentation
- All contributors to the project
