from django.http import JsonResponse
from django.db import connection
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

@never_cache
@require_GET
def health_check(request):
    """
    Health check endpoint for Render and other monitoring services.
    Checks database connection and returns status.
    """
    status = {"status": "healthy", "database": "unknown"}
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        status["database"] = "connected"
    except Exception as e:
        status["status"] = "unhealthy"
        status["database"] = str(e)
    
    # Return status with appropriate HTTP status code
    status_code = 200 if status["status"] == "healthy" else 503
    return JsonResponse(status, status=status_code)
