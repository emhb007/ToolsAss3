from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('', views.home, name='home'),
    path('trips/', views.TripListView.as_view(), name='trips_list'),
    path('trips/<int:pk>/', views.TripDetailView.as_view(), name='trip_detail'),
    path('trips/new/', views.TripCreateView.as_view(), name='new_trip'),
    path('trips/<int:trip_id>/student/<int:student_id>/record/', views.record_slip, name='record_slip'),
    path('trips/<int:trip_id>/permission-slip/', views.permission_slip, name='permission_slip'),
    path('trips/<int:trip_id>/permission-slip/download/', views.generate_slip_pdf, name='download_slip_pdf'),
    path('trips/<int:trip_id>/permission-slips/download/', views.generate_all_slips_pdf, name='download_all_slips_pdf'),
    path('trips/<int:trip_id>/student/<int:student_id>/permission-slip/download/', views.generate_slip_pdf, name='download_slip_pdf_student'),
    path('reports/', views.reports, name='reports'),
]
