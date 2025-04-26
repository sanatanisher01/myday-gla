from django.shortcuts import render
from django.db.utils import OperationalError, ProgrammingError
import sys

class DatabaseErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Try to access the database
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            
            # If we get here, the database is working
            response = self.get_response(request)
            return response
            
        except (OperationalError, ProgrammingError) as e:
            # Log the error
            print(f"Database error: {e}", file=sys.stderr)
            
            # Return the maintenance page
            return render(request, 'maintenance.html')
        except Exception as e:
            # Log other errors but let them pass through
            print(f"Other error in middleware: {e}", file=sys.stderr)
            response = self.get_response(request)
            return response
