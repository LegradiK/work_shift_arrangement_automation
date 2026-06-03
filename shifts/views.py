from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Shift, Staff
from datetime import date, timedelta

def hex_to_rgba(hex_color, alpha=0.55):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({r},{g},{b},{alpha})'

SHIFT_COLORS = {
    'morning':   '#C8922A',
    'afternoon': '#A0621C',
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
SHIFT_MAX = {
    'morning':   6,
    'afternoon': 6,
    'night':     5,
}
SHIFT_TYPES = ['morning', 'afternoon', 'night']
SHIFT_HOURS = {
    'morning':   7.5,
    'afternoon': 7.5,
    'night':     7.5,
}

def index(request):
    staff = Staff.objects.order_by('name')
    return render(request, 'index.html', {'staff': staff})

def events_api(request):
    shift_type = request.GET.get('shift_type')
    staff_id = request.GET.get('staff_id')

    try:
        start = date.fromisoformat(request.GET.get('start', '').split('T')[0])
        end = date.fromisoformat(request.GET.get('end', '').split('T')[0])
    except (ValueError, AttributeError):
        today = date.today()
        start = today.replace(day=1)
        end = (today.replace(day=1) + timedelta(days=32)).replace(day=1)

    types_to_create = [shift_type] if shift_type else SHIFT_TYPES
    today = date.today()
    current = max(start, today)
    while current < end:
        for stype in types_to_create:
            Shift.objects.get_or_create(date=current, shift_type=stype)
        current += timedelta(days=1)

    shifts = Shift.objects.prefetch_related('staff').filter(date__gte=start, date__lt=end)
    if shift_type:
        shifts = shifts.filter(shift_type=shift_type)
    if staff_id:
        shifts = shifts.filter(staff__id=staff_id)

    events = []

    if staff_id:
        weekly_hours = {}
        monthly_hours = {}

        # Determine the primary month being viewed (skip leading days from prev month)
        primary_month = (start + timedelta(days=6)).month
        primary_year = (start + timedelta(days=6)).year

        for shift in shifts:
            hours = SHIFT_HOURS.get(shift.shift_type, 8)

            days_until_saturday = (5 - shift.date.weekday()) % 7
            saturday = shift.date + timedelta(days=days_until_saturday)
            weekly_hours[saturday] = weekly_hours.get(saturday, 0) + hours

            next_month = (shift.date.replace(day=1) + timedelta(days=32)).replace(day=1)
            last_day = next_month - timedelta(days=1)
            monthly_hours[last_day] = monthly_hours.get(last_day, 0) + hours

            events.append({
                'id': shift.id,
                'title': shift.get_shift_type_display(),
                'start': shift.date.isoformat(),
                'backgroundColor': hex_to_rgba(SHIFT_COLORS.get(shift.shift_type, '#A0621C')),
                'borderColor': SHIFT_COLORS.get(shift.shift_type, '#A0621C'),
                'textColor': '#3a3a3a',
                'order': SHIFT_ORDER.get(shift.shift_type, 9),
                'extendedProps': {
                    'shift_type': shift.shift_type,
                    'understaffed': False,
                    'summary': False,
                },
            })

        for saturday, hours in weekly_hours.items():
            events.append({
                'id': f'week-{saturday.isoformat()}',
                'title': f'{hours}h',
                'start': saturday.isoformat(),
                'backgroundColor': 'transparent',
                'borderColor': 'transparent',
                'textColor': '#C8922A',
                'order': 10,
                'extendedProps': {
                    'shift_type': None,
                    'understaffed': False,
                    'summary': 'weekly',
                    'hours': hours,
                },
            })

        for last_day, hours in monthly_hours.items():
            if last_day.month == primary_month and last_day.year == primary_year:
                events.append({
                    'id': f'month-{last_day.isoformat()}',
                    'title': f'{hours}h',
                    'start': last_day.isoformat(),
                    'backgroundColor': 'transparent',
                    'borderColor': 'transparent',
                    'textColor': '#4A2C17',
                    'order': 11,
                    'extendedProps': {
                        'shift_type': None,
                        'understaffed': False,
                        'summary': 'monthly',
                        'hours': hours,
                    },
                })

    else:
        events = [
            {
                'id': shift.id,
                'title': str(shift.staff.count()),
                'start': shift.date.isoformat(),
                'backgroundColor': hex_to_rgba(SHIFT_COLORS.get(shift.shift_type, '#A0621C')),
                'borderColor': SHIFT_COLORS.get(shift.shift_type, '#A0621C'),
                'textColor': '#3a3a3a',
                'order': SHIFT_ORDER.get(shift.shift_type, 9),
                'extendedProps': {
                    'shift_type': shift.shift_type,
                    'understaffed': shift.staff.count() < SHIFT_THRESHOLDS.get(shift.shift_type, 1),
                    'overstaffed': shift.staff.count() > SHIFT_MAX.get(shift.shift_type, 99),
                    'summary': False,
                },
            }
            for shift in shifts
        ]

    return JsonResponse(events, safe=False)

def shift_staff(request, shift_id):
    shift = get_object_or_404(Shift.objects.prefetch_related('staff'), id=shift_id)
    ctx = {'shift': shift, 'is_admin': request.user.is_authenticated}
    if request.user.is_authenticated:
        ctx['all_staff'] = Staff.objects.order_by('name')
    return render(request, 'partials/staff_list.html', ctx)

def shift_add_staff(request, shift_id):
    if not request.user.is_authenticated:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()
    shift = get_object_or_404(Shift.objects.prefetch_related('staff'), id=shift_id)
    staff_id = request.POST.get('staff_id')
    if staff_id:
        shift.staff.add(staff_id)
    return render(request, 'partials/staff_list.html', {
        'shift': shift, 'is_admin': True, 'all_staff': Staff.objects.order_by('name'),
    })

def shift_remove_staff(request, shift_id, staff_id):
    if not request.user.is_authenticated:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()
    shift = get_object_or_404(Shift.objects.prefetch_related('staff'), id=shift_id)
    shift.staff.remove(staff_id)
    return render(request, 'partials/staff_list.html', {
        'shift': shift, 'is_admin': True, 'all_staff': Staff.objects.order_by('name'),
    })