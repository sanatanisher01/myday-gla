from django.shortcuts import render
from django.db.utils import OperationalError, ProgrammingError, InterfaceError
from django.conf import settings
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

        # Print database configuration on startup
        print("Database configuration at middleware initialization:", file=sys.stderr)
        print(f"Database engine: {settings.DATABASES['default']['ENGINE']}", file=sys.stderr)
        print(f"Database name: {settings.DATABASES['default']['NAME']}", file=sys.stderr)

    def __call__(self, request):
        # Skip database check for static files and maintenance page
        if request.path.startswith('/static/') or request.path == '/maintenance/':
            return self.get_response(request)

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
