from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('', views.home, name='home'),
    path('trips/', views.trips_list, name='trips_list'),
    path('trips/new/', views.new_trip, name='new_trip'),
    path('reports/', views.reports, name='reports'),
]
