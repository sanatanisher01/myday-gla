from django.shortcuts import render, redirect
from django.db.utils import OperationalError, ProgrammingError, InterfaceError
from django.conf import settings
from django.urls import reverse
import sys
import os
import time

class DatabaseErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.db_check_attempts = 0
        self.max_db_check_attempts = 3
        self.last_check_time = 0
        self.check_interval = 60  # seconds between checks
        self.db_available = False
        self.app_startup_time = time.time()
        self.app_ready = False
        self.max_startup_time = 15  # seconds (reduced from 60 to 15 seconds)

        # Print database configuration on startup
        print("Database configuration at middleware initialization:", file=sys.stderr)
        print(f"Database engine: {settings.DATABASES['default']['ENGINE']}", file=sys.stderr)
        print(f"Database name: {settings.DATABASES['default']['NAME']}", file=sys.stderr)

    def __call__(self, request):
        # Skip database check for static files, health check, maintenance page, loading page, and other non-critical paths
        if (request.path.startswith('/static/') or
            request.path == '/maintenance/' or
            request.path == '/loading/' or
            request.path.startswith('/health') or
            request.path == '/favicon.ico' or
            request.path == '/fallback.html' or
            request.path == '/robots.txt' or
            request.path == '/sitemap.xml' or
            request.method == 'HEAD' or
            request.method == 'OPTIONS'):
            return self.get_response(request)

        # For the home page during startup, serve a static fallback page
        if request.path == '/' and not self.app_ready:
            from django.http import FileResponse
            import os
            fallback_path = os.path.join(settings.STATIC_ROOT, 'fallback.html')
            if os.path.exists(fallback_path):
                return FileResponse(open(fallback_path, 'rb'))
            else:
                # If fallback.html doesn't exist in STATIC_ROOT, try the static directory
                fallback_path = os.path.join(settings.BASE_DIR, 'static', 'fallback.html')
                if os.path.exists(fallback_path):
                    return FileResponse(open(fallback_path, 'rb'))

        # Check if the app is still in startup phase
        current_time = time.time()
        if not self.app_ready and current_time - self.app_startup_time < self.max_startup_time:
            # Check if database is ready - use a more efficient approach
            try:
                # Import connection only once
                from django.db import connection

                # Use a faster query and close cursor properly
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()

                # If we get here, the database is working, mark app as ready
                self.app_ready = True
                print(f"App ready after {current_time - self.app_startup_time:.2f} seconds", file=sys.stderr)
            except Exception as e:
                # Database not ready, redirect to loading page
                print(f"Database not ready: {e}", file=sys.stderr)
                return redirect('loading')

        # If we've exceeded the maximum startup time, mark the app as ready
        if current_time - self.app_startup_time >= self.max_startup_time:
            self.app_ready = True

        # If we're using SQLite, we can proceed without checking connection
        if 'sqlite3' in settings.DATABASES['default']['ENGINE']:
            try:
                response = self.get_response(request)
                return response
            except Exception as e:
                print(f"Error with SQLite database: {e}", file=sys.stderr)
                return render(request, 'maintenance.html', {
                    'error_message': str(e),
                    'during_request': True,
                    'using_sqlite': True
                })

        # For PostgreSQL, check connection periodically
        if 'postgresql' in settings.DATABASES['default']['ENGINE']:
            # Only check database connection periodically to avoid overloading the database
            current_time = time.time()
            if current_time - self.last_check_time > self.check_interval or self.db_check_attempts < self.max_db_check_attempts:
                self.last_check_time = current_time
                self.db_check_attempts += 1

                try:
                    # Try to access the database
                    from django.db import connection
                    cursor = connection.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    cursor.close()

                    # If we get here, the database is working
                    self.db_available = True
                    print(f"PostgreSQL connection successful on attempt {self.db_check_attempts}", file=sys.stderr)

                except (OperationalError, ProgrammingError, InterfaceError) as e:
                    # Log the error
                    print(f"PostgreSQL error on attempt {self.db_check_attempts}: {e}", file=sys.stderr)
                    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'not set')}", file=sys.stderr)

                    self.db_available = False

                    # Return the maintenance page
                    return render(request, 'maintenance.html', {
                        'error_message': str(e),
                        'attempt': self.db_check_attempts,
                        'max_attempts': self.max_db_check_attempts,
                        'using_postgresql': True
                    })

                except Exception as e:
                    # Log other errors
                    print(f"Other error in middleware on attempt {self.db_check_attempts}: {e}", file=sys.stderr)
                    self.db_available = False

            # If database is available or we've exceeded check attempts, proceed with the request
            if self.db_available or self.db_check_attempts >= self.max_db_check_attempts:
                try:
                    response = self.get_response(request)
                    return response
                except (OperationalError, ProgrammingError, InterfaceError) as e:
                    # Handle database errors that occur during request processing
                    print(f"Database error during request processing: {e}", file=sys.stderr)
                    return render(request, 'maintenance.html', {
                        'error_message': str(e),
                        'during_request': True,
                        'using_postgresql': True
                    })
                except Exception as e:
                    # Log other errors but let them pass through
                    print(f"Other error during request processing: {e}", file=sys.stderr)
                    raise

        # Default case - just process the request
        return self.get_response(request)
