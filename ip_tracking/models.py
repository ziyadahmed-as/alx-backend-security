# ip_tracking/models.py
from django.db import models
from django.utils import timezone


class SuspiciousIP(models.Model):
    REASON_CHOICES = [
        ('high_volume', 'High request volume'),
        ('sensitive_path', 'Accessed sensitive paths'),
        ('multiple_reasons', 'Multiple suspicious activities'),
    ]
    
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.ip_address} ({self.get_reason_display()})"
    
    class Meta:
        verbose_name = 'Suspicious IP'
        verbose_name_plural = 'Suspicious IPs'
        ordering = ['-created_at']

# Add this to your existing RequestLog model if not present

class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(default=timezone.now)
    path = models.CharField(max_length=255)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        location = f"{self.city}, {self.country}" if self.city and self.country else "Unknown"
        return f"{self.ip_address} ({location}) - {self.timestamp} - {self.path}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Request Log'
        verbose_name_plural = 'Request Logs'

class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ip_address

    class Meta:
        verbose_name = 'Blocked IP'
        verbose_name_plural = 'Blocked IPs'