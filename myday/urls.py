"""
URL configuration for myday project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from events import views
from .health_check import health_check

# Simple view for maintenance page
def maintenance_view(request):
    return render(request, 'maintenance.html')

# Static home page for initial deployment
def static_home_view(request):
    from django.http import FileResponse
    import os
    from django.conf import settings

    # Path to the static index.html file
    index_path = os.path.join(settings.STATIC_ROOT, 'index.html')

    # If the file exists, serve it
    if os.path.exists(index_path):
        return FileResponse(open(index_path, 'rb'))

    # Otherwise, fall back to the regular home view
    return views.home(request)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('events/', include('events.urls')),
    path('bookings/', include('bookings.urls')),
    path('chat/', include('chat.urls')),
    path('maintenance/', maintenance_view, name='maintenance'),  # Direct maintenance page
    path('health/', health_check, name='health_check'),  # Health check endpoint for Render
    path('', static_home_view, name='home'),  # Static home page for initial deployment
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
