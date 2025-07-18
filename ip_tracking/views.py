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