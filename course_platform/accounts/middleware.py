"""
Middleware to prevent browser from caching pages after logout.
Sets Cache-Control headers so the back button doesn't show stale content.
"""


class NoCacheMiddleware:
    """
    Adds Cache-Control: no-cache, no-store headers to all responses.
    This prevents the browser from showing cached authenticated pages
    after the user logs out and hits the back button.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
