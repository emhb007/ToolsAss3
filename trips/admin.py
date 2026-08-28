from django.contrib import admin
from .models import Trip, Student, TripResponse

# Register your models here.

class TripResponseInline(admin.TabularInline):
    """Inline admin for TripResponse."""
    model = TripResponse
    extra = 1
    fields = ('student', 'slip_returned', 'date_returned', 'payment_received', 'consent_given')
    readonly_fields = ('student',)


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    """Admin interface for Trip model."""
    
    list_display = ('name', 'destination', 'trip_date', 'year_group', 'cost', 'created_by')
    list_filter = ('trip_date', 'year_group', 'created_at')
    search_fields = ('name', 'destination', 'year_group')
    readonly_fields = ('created_by', 'created_at')
    inlines = [TripResponseInline]
    
    fieldsets = (
        ('Trip Information', {
            'fields': ('name', 'destination', 'trip_date', 'year_group')
        }),
        ('Timing', {
            'fields': ('departure_time', 'return_time', 'permission_deadline')
        }),
        ('Details', {
            'fields': ('cost', 'packed_lunch_required')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set created_by to the current user when creating a new trip."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model."""
    
    list_display = ('first_name', 'last_name', 'form_class')
    list_filter = ('form_class',)
    search_fields = ('first_name', 'last_name', 'form_class')
    ordering = ('last_name', 'first_name')


@admin.register(TripResponse)
class TripResponseAdmin(admin.ModelAdmin):
    """Admin interface for TripResponse model."""
    
    list_display = ('student', 'trip', 'slip_returned', 'payment_received', 'consent_given')
    list_filter = ('trip', 'slip_returned', 'payment_received', 'consent_given', 'date_returned')
    search_fields = ('student__first_name', 'student__last_name', 'trip__name')
    readonly_fields = ('trip', 'student')
    
    fieldsets = (
        ('Trip & Student', {
            'fields': ('trip', 'student')
        }),
        ('Permission Slip', {
            'fields': ('slip_returned', 'date_returned')
        }),
        ('Payment', {
            'fields': ('payment_received',)
        }),
        ('Parental Consent', {
            'fields': ('consent_given', 'parent_signature_name')
        }),
        ('Student Details', {
            'fields': ('emergency_contact_number', 'medical_needs')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Call full_clean() to validate the instance before saving."""
        obj.full_clean()
        super().save_model(request, obj, form, change)

