
# ip_tracking/admin.py
from django.contrib import admin
from ip_tracking.models import RequestLog, BlockedIP

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'timestamp', 'path')
    list_filter = ('timestamp',)
    search_fields = ('ip_address', 'path')

@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'created_at')
    search_fields = ('ip_address',)