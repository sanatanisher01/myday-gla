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
        # Skip for static files, admin, and API requests
        if (request.path.startswith('/static/') or 
            request.path.startswith('/admin/') or 
            request.path.startswith('/health/') or
            request.path == '/favicon.ico'):
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
        """
        try:
            logger.info("Starting application warmup")
            
            # Simulate warmup tasks
            time.sleep(2)
            
            # Mark warmup as complete
            logger.info("Application warmup complete")
            self.is_waking_up = False
        except Exception as e:
            logger.error(f"Error during application warmup: {e}")
            self.is_waking_up = False
