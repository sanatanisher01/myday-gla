from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.conf import settings
from django.shortcuts import render
import sys
import os
import time

@never_cache
@require_GET
def health_check(request):
    """
    Health check endpoint for Render and other monitoring services.
    Checks database connection and returns status.
    """
    # If this is a HEAD request (like Render uses), return a simple 200 response
    if request.method == 'HEAD':
        response = HttpResponse(status=200)
        # Add CORS headers
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        return response

    # Record the start time of the health check
    start_time = time.time()

    status = {
        "status": "healthy",
        "database": "unknown",
        "database_engine": settings.DATABASES['default']['ENGINE'],
        "allowed_hosts": settings.ALLOWED_HOSTS,
        "debug": settings.DEBUG,
        "render": os.environ.get('RENDER', 'false')
    }

    # Check if this is a request from the loading page
    is_loading_check = request.GET.get('from_loading', 'false') == 'true'

    # Check database connection - simplified for loading page checks
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            status["database"] = "connected"
            status["database_result"] = str(result)

            # For loading page checks, we only need to know if the database is connected
            if is_loading_check:
                # Skip the rest of the checks to make the response faster
                pass
            else:
                # Only do the more intensive checks for monitoring tools, not the loading page
                # Check what tables exist
                if 'sqlite3' in connection.settings_dict['ENGINE']:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                elif 'postgresql' in connection.settings_dict['ENGINE']:
                    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")

                tables = [row[0] for row in cursor.fetchall()]
                status["tables"] = tables
                status["table_count"] = len(tables)

                # Check for core Django tables
                core_tables = ['django_migrations', 'auth_user', 'django_content_type']
                missing_tables = [table for table in core_tables if table not in tables]
                if missing_tables:
                    status["missing_core_tables"] = missing_tables
                    status["status"] = "warning"
    except Exception as e:
        status["status"] = "unhealthy"
        status["database"] = str(e)
        print(f"Health check database error: {e}", file=sys.stderr)

    # Calculate response time
    end_time = time.time()
    response_time = end_time - start_time
    status["response_time_ms"] = round(response_time * 1000, 2)

    # Return status with appropriate HTTP status code
    status_code = 200 if status["status"] in ["healthy", "warning"] else 503
    return JsonResponse(status, status=status_code)
