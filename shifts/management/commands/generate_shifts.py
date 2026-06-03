from datetime import date, timedelta
import random

from django.core.management.base import BaseCommand
from shifts.models import Staff, Shift


class Command(BaseCommand):
    help = 'Generate 6 months of shifts based on each staff member\'s employment type and shift preference'

    def handle(self, *args, **options):
        today = date.today()
        end = today + timedelta(days=183)
        week_start = today - timedelta(days=today.weekday())

        all_staff = list(Staff.objects.all())
        if not all_staff:
            self.stdout.write(self.style.ERROR('No staff in database.'))
            return

        Shift.objects.filter(date__gte=today).delete()
        self.stdout.write('Cleared existing shifts from today onwards.')

        shift_cache = {}

        def get_shift(d, stype):
            key = (d, stype)
            if key not in shift_cache:
                shift_cache[key], _ = Shift.objects.get_or_create(date=d, shift_type=stype)
            return shift_cache[key]

        for member in all_staff:
            current_monday = week_start
            week_idx = 0

            while current_monday <= end:
                week_days = [current_monday + timedelta(days=i) for i in range(7)]
                in_range = [d for d in week_days if today <= d <= end]

                if in_range:
                    if member.employment_type == Staff.FULL_TIME:
                        # 37.5 h/week = 5 × 7.5 h → 5 shifts, 2 days off
                        days_off = set(random.sample(in_range, min(2, len(in_range))))
                        for day in in_range:
                            if day not in days_off:
                                if member.shift_preference == Staff.NIGHT:
                                    stype = Shift.NIGHT
                                else:
                                    stype = random.choice([Shift.MORNING, Shift.AFTERNOON])
                                get_shift(day, stype).staff.add(member)
                    else:
                        # Part time 20 h/week ≈ 2.67 × 7.5 h
                        # 3-3-2 week cycle → exact 20 h/week average
                        n = 2 if week_idx % 3 == 2 else 3
                        work_days = random.sample(in_range, min(n, len(in_range)))
                        for day in work_days:
                            if member.shift_preference == Staff.NIGHT:
                                stype = Shift.NIGHT
                            else:
                                stype = random.choice([Shift.MORNING, Shift.AFTERNOON])
                            get_shift(day, stype).staff.add(member)

                current_monday += timedelta(weeks=1)
                week_idx += 1

        total = Shift.objects.filter(date__gte=today).count()
        self.stdout.write(self.style.SUCCESS(
            f'Done. {total} shift slots generated from {today} to {end} across {len(all_staff)} staff.'
        ))
