from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    """Home page view."""
    return render(request, 'trips/home.html')

def trips_list(request):
    """List all trips."""
    return render(request, 'trips/trips_list.html')

def new_trip(request):
    """Create a new trip."""
    return render(request, 'trips/new_trip.html')

def reports(request):
    """Generate and view reports."""
    return render(request, 'trips/reports.html')

