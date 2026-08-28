from django.shortcuts import render, get_object_or_404, redirect
import csv
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST
from weasyprint import HTML
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from .models import Trip, TripResponse, Student
from .forms import TripForm, TripResponseForm

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


class TripReportView(LoginRequiredMixin, DetailView):
    """Display a summary report for one trip."""

    model = Trip
    template_name = 'trips/trip_report.html'
    context_object_name = 'trip'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trip = self.object
        responses = TripResponse.objects.filter(trip=trip).select_related('student')
        total_students = responses.count()
        returned_count = responses.filter(slip_returned=True).count()
        outstanding_responses = responses.filter(slip_returned=False)
        outstanding_count = outstanding_responses.count()

        context.update({
            'total_students': total_students,
            'returned_count': returned_count,
            'returned_percentage': (returned_count / total_students * 100) if total_students else 0,
            'outstanding_count': outstanding_count,
            'outstanding_percentage': (outstanding_count / total_students * 100) if total_students else 0,
            'outstanding_students': outstanding_responses,
            'payments_received_count': responses.filter(payment_received=True).count(),
            'total_collected_income': trip.total_collected_income(),
            'total_expected_income': trip.total_expected_income(),
            'total_outstanding_income': trip.total_expected_income() - trip.total_collected_income(),
            'medical_needs_responses': responses.exclude(medical_needs='').exclude(medical_needs__isnull=True),
        })
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


def record_slip(request, trip_id, student_id):
    """Record a student's trip response/permission slip."""
    # Get the trip and student, or return 404 if not found
    trip = get_object_or_404(Trip, pk=trip_id)
    student = get_object_or_404(Student, pk=student_id)
    
    # Get or create the TripResponse
    trip_response, created = TripResponse.objects.get_or_create(
        trip=trip,
        student=student
    )
    
    if request.method == 'POST':
        form = TripResponseForm(request.POST, instance=trip_response)
        if form.is_valid():
            # Save the form
            trip_response = form.save()
            
            # Check if the response is overdue
            if trip_response.is_overdue:
                messages.warning(
                    request,
                    f'⚠️ Warning: Permission slip for {student.first_name} {student.last_name} '
                    f'is overdue (deadline was {trip.permission_deadline.strftime("%d %b %Y")}).'
                )
            else:
                messages.success(
                    request,
                    f'✓ Successfully recorded response for {student.first_name} {student.last_name}.'
                )
            
            # Redirect back to trip detail page
            return redirect('trips:trip_detail', pk=trip_id)
    else:
        form = TripResponseForm(instance=trip_response)
    
    context = {
        'form': form,
        'trip': trip,
        'student': student,
        'trip_response': trip_response,
        'is_new': created,
    }
    
    return render(request, 'trips/record_slip.html', context)


@login_required
@user_passes_test(lambda user: user.is_staff)
@require_POST
def toggle_slip_returned(request, response_id):
    """Toggle a trip response's returned status for staff table updates."""
    response = get_object_or_404(TripResponse, pk=response_id)
    response.slip_returned = not response.slip_returned
    response.date_returned = timezone.now().date() if response.slip_returned else None
    response.save(update_fields=['slip_returned', 'date_returned'])

    return JsonResponse({
        'slip_returned': response.slip_returned,
        'date_returned': response.date_returned.isoformat() if response.date_returned else None,
        'overdue': response.is_overdue and not response.slip_returned,
    })


def permission_slip(request, trip_id):
    """Render a printable permission slip letter for a trip."""
    trip = get_object_or_404(Trip, pk=trip_id)
    
    context = {
        'trip': trip,
    }
    
    return render(request, 'trips/permission_slip.html', context)


def generate_slip_pdf(request, trip_id, student_id=None):
    """Generate a PDF permission slip for a trip, optionally pre-filled with a student."""
    trip = get_object_or_404(Trip, pk=trip_id)
    student = None
    
    if student_id:
        student = get_object_or_404(Student, pk=student_id)
    
    context = {
        'trip': trip,
        'prefill_student': student,
    }
    
    # Render the HTML template to a string
    html_string = render_to_string('trips/permission_slip.html', context)
    
    # Convert HTML to PDF using WeasyPrint
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf_bytes = html.write_pdf()
    
    # Create HTTP response with PDF
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    
    # Set filename for download
    if student:
        filename = f'permission_slip_{student.first_name}_{student.last_name}_{trip.name}.pdf'
    else:
        filename = f'permission_slip_{trip.name}.pdf'
    
    # Sanitize filename
    filename = filename.replace(' ', '_').replace('/', '_')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def generate_all_slips_pdf(request, trip_id):
    """Generate one PDF containing a permission slip for every linked student."""
    trip = get_object_or_404(Trip, pk=trip_id)
    pdf_writer = PdfWriter()

    for student in trip.students.all():
        context = {
            'trip': trip,
            'prefill_student': student,
        }
        html_string = render_to_string('trips/permission_slip.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        student_pdf = PdfReader(BytesIO(html.write_pdf()))

        for page in student_pdf.pages:
            pdf_writer.add_page(page)

    pdf_buffer = BytesIO()
    pdf_writer.write(pdf_buffer)

    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    filename = trip.name.replace(' ', '_').replace('/', '_')
    response['Content-Disposition'] = f'attachment; filename="permission_slips_{filename}.pdf"'
    return response


def reports(request):
    """Generate and view reports."""
    return render(request, 'trips/reports.html')


@login_required
def export_trip_report_csv(request, trip_id):
    """Export all student responses for a trip as a CSV download."""
    trip = get_object_or_404(Trip, pk=trip_id)
    responses = TripResponse.objects.filter(trip=trip).select_related('student')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="trip_report_{trip.pk}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        'Name',
        'Form Class',
        'Slip Returned',
        'Date Returned',
        'Payment Received',
        'Emergency Contact',
        'Medical Needs',
    ])

    for trip_response in responses:
        writer.writerow([
            f'{trip_response.student.first_name} {trip_response.student.last_name}',
            trip_response.student.form_class,
            'Yes' if trip_response.slip_returned else 'No',
            trip_response.date_returned.isoformat() if trip_response.date_returned else '',
            'Yes' if trip_response.payment_received else 'No',
            trip_response.emergency_contact_number,
            trip_response.medical_needs,
        ])

    return response

