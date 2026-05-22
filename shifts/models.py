from django.db import models


class Staff(models.Model):
    name = models.CharField(max_length=100)

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
