
# ip_tracking/management/commands/block_ip.py
from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP
import argparse

class Command(BaseCommand):
    help = 'Add or remove IP addresses from the block list'

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='IP address to block/unblock')
        parser.add_argument(
            '--unblock',
            action='store_true',
            help='Unblock the IP address instead of blocking it'
        )

    def handle(self, *args, **options):
        ip = options['ip_address']
        unblock = options['unblock']

        if unblock:
            try:
                blocked_ip = BlockedIP.objects.get(ip_address=ip)
                blocked_ip.delete()
                self.stdout.write(self.style.SUCCESS(f'Successfully unblocked IP: {ip}'))
            except BlockedIP.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'IP {ip} was not blocked'))
        else:
            _, created = BlockedIP.objects.get_or_create(ip_address=ip)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully blocked IP: {ip}'))
            else:
                self.stdout.write(self.style.WARNING(f'IP {ip} was already blocked'))