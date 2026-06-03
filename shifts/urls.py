from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('events/', views.events_api, name='events_api'),
    path('shifts/<int:shift_id>/staff/', views.shift_staff, name='shift_staff'),
    path('shifts/<int:shift_id>/staff/add/', views.shift_add_staff, name='shift_add_staff'),
    path('shifts/<int:shift_id>/staff/<int:staff_id>/remove/', views.shift_remove_staff, name='shift_remove_staff'),
]
