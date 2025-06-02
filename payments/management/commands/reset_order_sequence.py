from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Max

from payments.models import Order

class Command(BaseCommand):
    help = 'Resets the primary key sequence for the Order table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            table_name = Order._meta.db_table
            sequence_name = f"{table_name}_id_seq"
            
            # Get current max ID
            max_id = Order.objects.all().aggregate(Max('id'))['id__max'] or 0

            
            # Get current sequence value
            cursor.execute(f"SELECT last_value FROM {sequence_name};")
            current_seq = cursor.fetchone()[0]
            
            # Always reset sequence to max ID + 1 to fix any inconsistencies
            cursor.execute(f"ALTER SEQUENCE {sequence_name} RESTART WITH {max_id + 1};")
            self.stdout.write(self.style.SUCCESS(
                f"Reset sequence {sequence_name} from {current_seq} to {max_id + 1}"
            ))
