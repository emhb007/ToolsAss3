from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field
from .models import Trip, TripResponse


class TripForm(forms.ModelForm):
    """ModelForm for creating and editing trips."""
    
    class Meta:
        model = Trip
        fields = [
            'name',
            'destination',
            'trip_date',
            'departure_time',
            'return_time',
            'cost',
            'permission_deadline',
            'packed_lunch_required',
            'year_group',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter trip name'
            }),
            'destination': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter destination'
            }),
            'trip_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'departure_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'return_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'cost': forms.DecimalInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'permission_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'packed_lunch_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'year_group': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Year 7, Year 8'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set up crispy forms helper with Bootstrap 5
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.use_custom_control = True
        
        # Define the form layout with Bootstrap 5
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6'),
                Column('destination', css_class='col-md-6'),
            ),
            Row(
                Column('trip_date', css_class='col-md-4'),
                Column('permission_deadline', css_class='col-md-4'),
                Column('year_group', css_class='col-md-4'),
            ),
            Row(
                Column('departure_time', css_class='col-md-4'),
                Column('return_time', css_class='col-md-4'),
                Column('cost', css_class='col-md-4'),
            ),
            Row(
                Column(
                    Field('packed_lunch_required', css_class='form-check-input', 
                          wrapper_class='form-check col-md-6'),
                    css_class='col-md-6'
                ),
            ),
            HTML('<hr class="my-4">'),
            Submit('submit', 'Create Trip', css_class='btn btn-primary btn-lg me-2'),
            HTML('<a href="{% url "trips:trips_list" %}" class="btn btn-secondary btn-lg">Cancel</a>'),
        )
    
    def clean_cost(self):
        """Validate that cost is greater than 0."""
        cost = self.cleaned_data.get('cost')
        if cost is not None and cost <= 0:
            raise ValidationError('Cost must be greater than 0.')
        return cost
    
    def clean(self):
        """Validate that departure_time is earlier than return_time."""
        cleaned_data = super().clean()
        departure_time = cleaned_data.get('departure_time')
        return_time = cleaned_data.get('return_time')
        
        if departure_time and return_time and departure_time >= return_time:
            raise ValidationError(
                'Departure time must be earlier than return time.'
            )
        
        return cleaned_data


class TripResponseForm(forms.ModelForm):
    """ModelForm for recording student trip responses/registration."""
    
    class Meta:
        model = TripResponse
        fields = [
            'slip_returned',
            'date_returned',
            'payment_received',
            'emergency_contact_number',
            'medical_needs',
            'parent_signature_name',
            'consent_given',
        ]
        widgets = {
            'slip_returned': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'date_returned': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'payment_received': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'emergency_contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '07123456789 or +44 7123 456789'
            }),
            'medical_needs': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter any medical needs or allergies'
            }),
            'parent_signature_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parent/Guardian name'
            }),
            'consent_given': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set up crispy forms helper with Bootstrap 5
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.use_custom_control = True
        
        # Define the form layout with Bootstrap 5
        self.helper.layout = Layout(
            HTML('<h5 class="mb-4">Permission Slip</h5>'),
            Row(
                Column('slip_returned', css_class='col-md-6'),
                Column('date_returned', css_class='col-md-6'),
            ),
            HTML('<hr class="my-4">'),
            HTML('<h5 class="mb-4">Payment & Consent</h5>'),
            Row(
                Column('payment_received', css_class='col-md-6'),
                Column('consent_given', css_class='col-md-6'),
            ),
            HTML('<hr class="my-4">'),
            HTML('<h5 class="mb-4">Contact & Medical Information</h5>'),
            'emergency_contact_number',
            'medical_needs',
            'parent_signature_name',
            HTML('<hr class="my-4">'),
            Submit('submit', 'Save Response', css_class='btn btn-primary btn-lg me-2'),
            HTML('<a href="javascript:history.back()" class="btn btn-secondary btn-lg">Cancel</a>'),
        )
    
    def clean(self):
        """Auto-set date_returned to today if slip_returned is checked and date_returned is blank."""
        cleaned_data = super().clean()
        slip_returned = cleaned_data.get('slip_returned')
        date_returned = cleaned_data.get('date_returned')
        
        # Auto-set date_returned to today if slip is marked as returned and date is blank
        if slip_returned and not date_returned:
            cleaned_data['date_returned'] = timezone.now().date()
        
        return cleaned_data

