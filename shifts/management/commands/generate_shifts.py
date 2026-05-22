from datetime import date, timedelta
import random

from django.core.management.base import BaseCommand
from shifts.models import Staff, Shift


class Command(BaseCommand):
    help = 'Generate random shifts for 6 months with 2 days off per week per staff member'

    def handle(self, *args, **options):
        today = date.today()
        end = today + timedelta(days=183)

        # Start from the Monday of the current week
        week_start = today - timedelta(days=today.weekday())

        staff = list(Staff.objects.all())
        shift_types = [Shift.MORNING, Shift.AFTERNOON, Shift.NIGHT]

        # Clear any existing shifts from today onwards
        deleted, _ = Shift.objects.filter(date__gte=today).delete()
        if deleted:
            self.stdout.write(f'Cleared {deleted} existing shift records.')

        shift_cache = {}

        def get_or_create_shift(d, stype):
            key = (d, stype)
            if key not in shift_cache:
                shift_cache[key], _ = Shift.objects.get_or_create(date=d, shift_type=stype)
            return shift_cache[key]

        for member in staff:
            current_monday = week_start
            while current_monday <= end:
                week_days = [current_monday + timedelta(days=i) for i in range(7)]
                in_range = [d for d in week_days if today <= d <= end]

                days_off = set(random.sample(in_range, min(2, len(in_range))))

                for day in in_range:
                    if day not in days_off:
                        shift_type = random.choice(shift_types)
                        get_or_create_shift(day, shift_type).staff.add(member)

                current_monday += timedelta(weeks=1)

        total = Shift.objects.filter(date__gte=today).count()
        self.stdout.write(self.style.SUCCESS(
            f'Done. Generated shifts from {today} to {end} ({total} shift slots across {len(staff)} staff).'
        ))
