from django.db import models


class Staff(models.Model):
    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'
    EMPLOYMENT_CHOICES = [
        (FULL_TIME, 'Full Time'),
        (PART_TIME, 'Part Time'),
    ]
    DAY = 'day'
    NIGHT = 'night'
    PREFERENCE_CHOICES = [
        (DAY, 'Day'),
        (NIGHT, 'Night'),
    ]

    name = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES, default=FULL_TIME)
    shift_preference = models.CharField(max_length=10, choices=PREFERENCE_CHOICES, default=DAY)

    def __str__(self):
        return self.name


class Shift(models.Model):
    MORNING = 'morning'
    AFTERNOON = 'afternoon'
    NIGHT = 'night'
    SHIFT_TYPES = [
        (MORNING, 'Morning'),
        (AFTERNOON, 'Afternoon'),
        (NIGHT, 'Night'),
    ]

    date = models.DateField()
    shift_type = models.CharField(max_length=20, choices=SHIFT_TYPES)
    staff = models.ManyToManyField(Staff, blank=True, related_name='shifts')

    class Meta:
        unique_together = ('date', 'shift_type')

    def __str__(self):
        return f"{self.date} {self.get_shift_type_display()}"
