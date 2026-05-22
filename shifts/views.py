from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Shift, Staff

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


def index(request):
    staff = Staff.objects.order_by('name')
    return render(request, 'index.html', {'staff': staff})


def events_api(request):
    shift_type = request.GET.get('shift_type')
    shifts = Shift.objects.prefetch_related('staff').all()
    if shift_type:
        shifts = shifts.filter(shift_type=shift_type)

    events = [
        {
            'id': shift.id,
            'title': str(shift.staff.count()),
            'start': shift.date.isoformat(),
            'color': SHIFT_COLORS.get(shift.shift_type, '#7B4F3A'),
            'order': SHIFT_ORDER.get(shift.shift_type, 9),
            'extendedProps': {'shift_type': shift.shift_type},
        }
        for shift in shifts
    ]
    return JsonResponse(events, safe=False)


def shift_staff(request, shift_id):
    shift = get_object_or_404(Shift.objects.prefetch_related('staff'), id=shift_id)
    return render(request, 'partials/staff_list.html', {'shift': shift})
