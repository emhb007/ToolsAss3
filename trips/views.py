from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Trip, TripResponse
from .forms import TripForm

# Create your views here.

def home(request):
    """Home page view."""
    return render(request, 'trips/home.html')


class TripListView(LoginRequiredMixin, ListView):
    """List view for all trips."""
    
    model = Trip
    template_name = 'trips/trips_list.html'
    context_object_name = 'trips'
    paginate_by = 10
    
    def get_queryset(self):
        """Return queryset ordered by trip date."""
        return Trip.objects.all().order_by('-trip_date')


class TripDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a single trip with statistics."""
    
    model = Trip
    template_name = 'trips/trip_detail.html'
    context_object_name = 'trip'
    slug_field = 'pk'
    slug_url_kwarg = 'pk'
    
    def get_queryset(self):
        """Return queryset with annotated counts."""
        return Trip.objects.annotate(
            total_students=Count('responses', distinct=True),
            slips_returned_count=Count(
                'responses',
                filter=Q(responses__slip_returned=True),
                distinct=True
            ),
            payments_received_count=Count(
                'responses',
                filter=Q(responses__payment_received=True),
                distinct=True
            ),
            consent_given_count=Count(
                'responses',
                filter=Q(responses__consent_given=True),
                distinct=True
            ),
        )
    
    def get_context_data(self, **kwargs):
        """Add trip statistics to the context."""
        context = super().get_context_data(**kwargs)
        trip = self.object
        
        # Add annotated counts to context
        context['total_students'] = trip.total_students
        context['slips_returned_count'] = trip.slips_returned_count
        context['payments_received_count'] = trip.payments_received_count
        context['consent_given_count'] = trip.consent_given_count
        
        # Calculate percentages
        if trip.total_students > 0:
            context['slips_returned_percentage'] = int(
                (trip.slips_returned_count / trip.total_students) * 100
            )
            context['payments_received_percentage'] = int(
                (trip.payments_received_count / trip.total_students) * 100
            )
            context['consent_given_percentage'] = int(
                (trip.consent_given_count / trip.total_students) * 100
            )
        else:
            context['slips_returned_percentage'] = 0
            context['payments_received_percentage'] = 0
            context['consent_given_percentage'] = 0
        
        # Get all trip responses for this trip
        context['responses'] = TripResponse.objects.filter(trip=trip).select_related('student')
        
        return context


class TripCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create view for new trips, restricted to staff users."""
    
    model = Trip
    form_class = TripForm
    template_name = 'trips/trip_form.html'
    
    def test_func(self):
        """Check if user is staff."""
        return self.request.user.is_staff
    
    def form_valid(self, form):
        """Set created_by to the current user."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to trip detail page on success."""
        return reverse_lazy('trips:trip_detail', kwargs={'pk': self.object.pk})


def new_trip(request):
    """Create a new trip."""
    return render(request, 'trips/new_trip.html')


def reports(request):
    """Generate and view reports."""
    return render(request, 'trips/reports.html')

