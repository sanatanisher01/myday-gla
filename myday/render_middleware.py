import time
import threading
import logging
from django.http import HttpResponse
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

class RenderWakeupMiddleware:
    """
    Middleware to handle Render's free tier sleep mode.

    This middleware detects if the application is waking up from sleep mode
    and shows a loading page to the user while the application initializes.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.last_request_time = time.time()
        self.is_waking_up = False
        self.wakeup_lock = threading.Lock()
        logger.info("RenderWakeupMiddleware initialized")

    def __call__(self, request):
        # Skip for static files, admin, health checks, and special requests
        if (request.path.startswith('/static/') or
            request.path.startswith('/admin/') or
            request.path.startswith('/health') or
            request.path == '/favicon.ico' or
            request.method == 'HEAD' or
            request.method == 'OPTIONS'):
            return self.get_response(request)

        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        # If it's been more than 10 minutes since the last request,
        # we might be waking up from sleep mode
        if time_since_last_request > 600:  # 10 minutes
            logger.info(f"Potential wakeup detected. Time since last request: {time_since_last_request:.2f}s")

            with self.wakeup_lock:
                if not self.is_waking_up:
                    self.is_waking_up = True
                    # Start a background thread to warm up the application
                    threading.Thread(target=self._warmup_application).start()

            # Show a loading page for the first request after sleep
            if self.is_waking_up and request.method == 'GET' and 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                html_content = render_to_string('wakeup.html')
                return HttpResponse(html_content)

        # Update the last request time
        self.last_request_time = current_time

        # Process the request normally
        return self.get_response(request)

    def _warmup_application(self):
        """
        Perform warmup tasks to speed up application initialization.
        This function preloads essential components to reduce startup time.
        """
        try:
            logger.info("Starting application warmup")

            # Import necessary modules here to preload them
            from django.db import connection
            from django.contrib.auth.models import User
            from events.models import Event
            from bookings.models import Booking

            # Perform a simple database query to warm up the connection
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                logger.info("Database connection warmed up")
            except Exception as db_error:
                logger.error(f"Database warmup error: {db_error}")

            # Preload essential model data
            try:
                # Count users to warm up auth models
                user_count = User.objects.count()
                # Count events to warm up event models
                event_count = Event.objects.count()
                # Count bookings to warm up booking models
                booking_count = Booking.objects.count()

                logger.info(f"Model cache warmed up: {user_count} users, {event_count} events, {booking_count} bookings")
            except Exception as model_error:
                logger.error(f"Model warmup error: {model_error}")

            # Mark warmup as complete after a maximum of 30 seconds
            # This ensures we don't keep users waiting too long
            time.sleep(0.5)  # Small delay to ensure other processes can start

            logger.info("Application warmup complete")
            self.is_waking_up = False
        except Exception as e:
            logger.error(f"Error during application warmup: {e}")
            self.is_waking_up = False
