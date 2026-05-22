from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('events/', views.events_api, name='events_api'),
    path('shifts/<int:shift_id>/staff/', views.shift_staff, name='shift_staff'),
]
