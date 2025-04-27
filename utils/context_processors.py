from django.conf import settings

def site_url(request):
    """
    Add site_url to the context for use in templates, especially emails
    """
    # Get the protocol (http or https)
    protocol = 'https' if request.is_secure() else 'http'
    
    # Get the host (domain)
    host = request.get_host()
    
    # Construct the full site URL
    site_url = f"{protocol}://{host}"
    
    return {'site_url': site_url}
