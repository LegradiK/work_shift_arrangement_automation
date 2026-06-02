from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Shift, Staff
from datetime import date, timedelta

def hex_to_rgba(hex_color, alpha=0.35):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({r},{g},{b},{alpha})'

SHIFT_COLORS = {
    'morning':   '#C8922A',
    'afternoon': '#7B4F3A',
    'night':     '#3E2314',
}
SHIFT_ORDER = {
    'morning':   1,
    'afternoon': 2,
    'night':     3,
}
SHIFT_THRESHOLDS = {
    'morning':   4,
    'afternoon': 4,
    'night':     3,
}
SHIFT_TYPES = ['morning', 'afternoon', 'night']

def index(request):
    staff = Staff.objects.order_by('name')
    return render(request, 'index.html', {'staff': staff})

def events_api(request):
    shift_type = request.GET.get('shift_type')

    try:
        start = date.fromisoformat(request.GET.get('start', '').split('T')[0])
        end = date.fromisoformat(request.GET.get('end', '').split('T')[0])
    except (ValueError, AttributeError):
        today = date.today()
        start = today.replace(day=1)
        end = (today.replace(day=1) + timedelta(days=32)).replace(day=1)

    types_to_create = [shift_type] if shift_type else SHIFT_TYPES

    today = date.today()
    create_start = max(start, today)
    current = create_start
    while current < end:
        for stype in types_to_create:
            Shift.objects.get_or_create(date=current, shift_type=stype)
        current += timedelta(days=1)

    shifts = Shift.objects.prefetch_related('staff').filter(date__gte=start, date__lt=end)
    if shift_type:
        shifts = shifts.filter(shift_type=shift_type)

    events = [
        {
            'id': shift.id,
            'title': str(shift.staff.count()),
            'start': shift.date.isoformat(),
            'backgroundColor': hex_to_rgba(SHIFT_COLORS.get(shift.shift_type, '#7B4F3A')),
            'borderColor': SHIFT_COLORS.get(shift.shift_type, '#7B4F3A'),
            'textColor': '#3a3a3a',
            'order': SHIFT_ORDER.get(shift.shift_type, 9),
            'extendedProps': {
                'shift_type': shift.shift_type,
                'understaffed': shift.staff.count() < SHIFT_THRESHOLDS.get(shift.shift_type, 1),
            },
        }
        for shift in shifts
    ]
    return JsonResponse(events, safe=False)

def shift_staff(request, shift_id):
    shift = get_object_or_404(Shift.objects.prefetch_related('staff'), id=shift_id)
    return render(request, 'partials/staff_list.html', {'shift': shift})