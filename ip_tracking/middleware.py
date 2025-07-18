# ip_tracking/middleware.py
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.core.cache import cache
from ip_tracking.models import RequestLog, BlockedIP
from ipgeolocation import IpGeolocationAPI
# ip_tracking/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit

def rate_limit_exceeded(request, exception):
    return JsonResponse(
        {'error': 'Rate limit exceeded. Please try again later.'},
        status=429
    )

@require_GET
@ratelimit(key='ip', rate=RATELIMIT_RATE['anon'], block=True)
def public_api_view(request):
    return JsonResponse({'message': 'This is a public API endpoint'})

@login_required
@ratelimit(key='user', rate=RATELIMIT_RATE['user'], block=True)
def private_api_view(request):
    return JsonResponse({'message': 'This is a private API endpoint'})

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_view(request):
    # Your existing login logic here
    return JsonResponse({'message': 'Login successful'})

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.geolocation_api = IpGeolocationAPI(api_key='your_api_key')  # Replace with actual API key

    def __call__(self, request):
        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        # Check if IP is blocked
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP address has been blocked.")

        # Get geolocation data (cached for 24 hours)
        cache_key = f'ip_geo_{ip}'
        geo_data = cache.get(cache_key)

        if not geo_data:
            try:
                geo_data = self.geolocation_api.get_geolocation(ip_address=ip)
                cache.set(cache_key, geo_data, timeout=86400)  # 24 hours cache
            except Exception as e:
                geo_data = {'country': None, 'city': None}

        # Create log entry
        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
            timestamp=timezone.now(),
            country=geo_data.get('country'),
            city=geo_data.get('city')
        )

        response = self.get_response(request)
        return response