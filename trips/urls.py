from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('', views.home, name='home'),
    path('trips/', views.TripListView.as_view(), name='trips_list'),
    path('trips/<int:pk>/', views.TripDetailView.as_view(), name='trip_detail'),
    path('trips/new/', views.TripCreateView.as_view(), name='new_trip'),
    path('trips/<int:trip_id>/student/<int:student_id>/record/', views.record_slip, name='record_slip'),
    path('reports/', views.reports, name='reports'),
]
