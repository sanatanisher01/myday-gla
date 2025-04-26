# Deploying MyDay on Railway

This guide provides step-by-step instructions for deploying the MyDay application on Railway.

## Prerequisites

1. A Railway account (sign up at https://railway.app/)
2. A GitHub account with the MyDay repository
3. A Cloudinary account for media storage (optional but recommended)

## Deployment Steps

### 1. Fork or Clone the Repository

If you haven't already, fork or clone the MyDay repository to your GitHub account.

### 2. Create a New Project on Railway

1. Log in to your Railway account
2. Click on "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account if you haven't already
5. Select the MyDay repository

### 3. Add a PostgreSQL Database

1. In your project dashboard, click on "New"
2. Select "Database"
3. Choose "PostgreSQL"
4. Railway will automatically create a PostgreSQL database and set the DATABASE_URL environment variable

### 4. Configure Environment Variables

1. In your project dashboard, go to the "Variables" tab
2. Add the following environment variables:

```
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=false
RAILWAY_ENVIRONMENT=production

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

Replace the placeholder values with your actual credentials.

### 5. Deploy the Application

1. Railway will automatically deploy your application when you push changes to your GitHub repository
2. You can also manually trigger a deployment from the Railway dashboard by clicking on "Deploy"

### 6. Access Your Application

1. Once the deployment is complete, Railway will provide you with a URL to access your application
2. You can also set up a custom domain in the "Settings" tab

## Troubleshooting

### Database Migration Issues

If you encounter database migration issues, you can run migrations manually:

1. In your project dashboard, go to the "Shell" tab
2. Run the following commands:
   ```
   python manage.py migrate --noinput
   python manage.py initialize_db
   ```

### Static Files Issues

If static files are not loading correctly:

1. In your project dashboard, go to the "Shell" tab
2. Run the following command:
   ```
   python manage.py collectstatic --noinput
   ```

### Application Errors

If your application is returning errors:

1. In your project dashboard, go to the "Logs" tab
2. Check the logs for error messages
3. Fix the issues in your code and push the changes to GitHub

## Maintenance

### Updating the Application

1. Make changes to your code locally
2. Push the changes to GitHub
3. Railway will automatically deploy the new version

### Monitoring

1. In your project dashboard, go to the "Metrics" tab
2. Monitor CPU, memory, and disk usage
3. Set up alerts if needed

## Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
