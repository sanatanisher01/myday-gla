"""
Minimal URLs for Render deployment.
This file contains the bare minimum URL patterns needed to run the application on Render.
"""

from django.contrib import admin
from django.urls import path
from django.http import HttpResponse, FileResponse
from django.conf import settings
import os

def health_check(request):
    """
    Simple health check endpoint for Render.
    """
    return HttpResponse("OK", status=200)

def static_home(request):
    """
    Serve a static home page.
    """
    # Path to the static index.html file
    index_path = os.path.join(settings.STATIC_ROOT, 'index.html')
    
    # If the file exists, serve it
    if os.path.exists(index_path):
        return FileResponse(open(index_path, 'rb'))
    
    # Otherwise, return a simple response
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MyDay - Welcome</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
                color: #333;
            }
            h1 {
                color: #4a6bdf;
            }
        </style>
    </head>
    <body>
        <h1>Welcome to MyDay</h1>
        <p>Your one-stop platform for event management at GLA University.</p>
        <p>The application is currently being set up.</p>
    </body>
    </html>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', static_home, name='home'),
]
