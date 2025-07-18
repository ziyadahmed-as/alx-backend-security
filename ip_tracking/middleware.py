from django.utils.timezone import now
from .models import RequestLog

class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        path = request.path
        RequestLog.objects.create(ip_address=ip, timestamp=now(), path=path)
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Get IP address from request headers"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
