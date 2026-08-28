from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone

# Create your models here.

class Trip(models.Model):
    """Model representing a school trip."""
    
    name = models.CharField(max_length=200, help_text="Trip name")
    destination = models.CharField(max_length=200, help_text="Trip destination")
    trip_date = models.DateField(help_text="Date of the trip")
    departure_time = models.TimeField(help_text="Time of departure")
    return_time = models.TimeField(help_text="Time of return")
    cost = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        help_text="Cost per student in GBP"
    )
    permission_deadline = models.DateField(help_text="Deadline for permission forms")
    packed_lunch_required = models.BooleanField(
        default=True, 
        help_text="Whether students need to bring a packed lunch"
    )
    year_group = models.CharField(
        max_length=50, 
        help_text="Year group (e.g., Year 7, Year 8)"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trips_created',
        help_text="User who created this trip"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-trip_date']
        verbose_name = 'Trip'
        verbose_name_plural = 'Trips'
        permissions = [
            ('can_manage_trips', 'Can create and edit trips'),
        ]
    
    def __str__(self):
        """Return string representation of the trip."""
        return f"{self.name} - {self.destination} ({self.trip_date})"
    
    def clean(self):
        """Validate that permission_deadline is before trip_date."""
        if self.permission_deadline >= self.trip_date:
            raise ValidationError(
                'Permission deadline must be before the trip date.'
            )
    
    def total_expected_income(self):
        """Calculate total expected income (cost * total number of linked students)."""
        total_students = self.students.count()
        return self.cost * total_students
    
    def total_collected_income(self):
        """Calculate total collected income (cost * count of paid responses)."""
        paid_responses = self.responses.filter(payment_received=True).count()
        return self.cost * paid_responses


class Student(models.Model):
    """Model representing a student."""
    
    first_name = models.CharField(max_length=100, help_text="Student's first name")
    last_name = models.CharField(max_length=100, help_text="Student's last name")
    form_class = models.CharField(max_length=10, help_text="Form class (e.g., 7A, 8B)")
    trips = models.ManyToManyField(Trip, through='TripResponse', related_name='students')
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
    
    def __str__(self):
        """Return string representation of the student."""
        return f"{self.first_name} {self.last_name} ({self.form_class})"


class TripResponse(models.Model):
    """Store a student's trip response and sensitive permission-slip data.

    Emergency contact numbers, medical needs, and parent signature names are
    sensitive personal data and must be handled according to the school's
    data protection policy.
    """
    
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='responses')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='trip_responses')
    slip_returned = models.BooleanField(
        default=False,
        help_text="Whether the permission slip was returned"
    )
    date_returned = models.DateField(
        null=True, 
        blank=True,
        help_text="Date the permission slip was returned"
    )
    payment_received = models.BooleanField(
        default=False,
        help_text="Whether payment has been received"
    )
    emergency_contact_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^(\+44|0)[0-9\s\-\(\)]{9,}$',
                message='Please enter a valid UK phone number (e.g., 07123456789 or +44 7123 456789)',
                code='invalid_uk_phone'
            )
        ],
        help_text="Emergency contact phone number (UK format)"
    )
    medical_needs = models.TextField(
        blank=True,
        help_text="Any medical needs or allergies"
    )
    parent_signature_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Parent/Guardian name for signature (digital record)"
    )
    consent_given = models.BooleanField(
        default=False,
        help_text="Whether parental consent has been given"
    )
    
    class Meta:
        unique_together = ('trip', 'student')
        verbose_name = 'Trip Response'
        verbose_name_plural = 'Trip Responses'
        ordering = ['trip', 'student']
    
    def clean(self):
        """Validate that if slip_returned is True, consent_given and parent_signature_name are set."""
        errors = {}
        
        if self.slip_returned:
            if not self.consent_given:
                errors['consent_given'] = 'Consent must be given when permission slip is returned.'
            if not self.parent_signature_name:
                errors['parent_signature_name'] = 'Parent/Guardian signature name is required when permission slip is returned.'
        
        if errors:
            raise ValidationError(errors)
    
    def __str__(self):
        """Return string representation of the trip response."""
        return f"{self.student} - {self.trip.name}"
    
    @property
    def is_overdue(self):
        """Check if permission slip is overdue (past deadline and not returned)."""
        return not self.slip_returned and timezone.now().date() > self.trip.permission_deadline

