# ip_tracking/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP

@shared_task(bind=True)
def detect_suspicious_ips(self):
    one_hour_ago = timezone.now() - timedelta(hours=1)
    sensitive_paths = ['/admin', '/login', '/wp-admin']  # Add more as needed
    
    # Detect high volume IPs (>100 requests/hour)
    high_volume_ips = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(request_count=models.Count('id'))
        .filter(request_count__gt=100)
    )
    
    # Detect IPs accessing sensitive paths
    sensitive_access_ips = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago, path__in=sensitive_paths)
        .values('ip_address')
        .distinct()
    )
    
    # Process high volume IPs
    for entry in high_volume_ips:
        ip = entry['ip_address']
        SuspiciousIP.objects.update_or_create(
            ip_address=ip,
            defaults={'reason': 'high_volume'}
        )
        # Mark all requests from this IP as suspicious
        RequestLog.objects.filter(ip_address=ip).update(
            is_suspicious=True,
            suspicious_reason='high_volume'
        )
    
    # Process sensitive path access
    for entry in sensitive_access_ips:
        ip = entry['ip_address']
        exists = SuspiciousIP.objects.filter(ip_address=ip).exists()
        
        if exists:
            # Update existing record if it was only high volume before
            SuspiciousIP.objects.filter(
                ip_address=ip,
                reason='high_volume'
            ).update(reason='multiple_reasons')
        else:
            SuspiciousIP.objects.create(
                ip_address=ip,
                reason='sensitive_path'
            )
        
        # Mark sensitive path accesses as suspicious
        RequestLog.objects.filter(
            ip_address=ip,
            path__in=sensitive_paths
        ).update(
            is_suspicious=True,
            suspicious_reason='sensitive_path'
        )
    
    return f"Detected {len(high_volume_ips)} high volume IPs and {len(sensitive_access_ips)} sensitive access IPs"