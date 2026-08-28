from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field
from .models import Trip


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
