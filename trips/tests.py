from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
import csv
from decimal import Decimal
from datetime import date, time
from .models import Trip, Student, TripResponse

User = get_user_model()


class TripValidationTestCase(TestCase):
    """Test validation rules for creating trips."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='tripcreator',
            password='testpass123',
            is_staff=True,
        )

    def test_deadline_after_trip_date_is_rejected(self):
        trip = Trip(
            name='Invalid Date Trip',
            destination='School Grounds',
            trip_date=date(2026, 10, 15),
            departure_time=time(9, 0),
            return_time=time(16, 0),
            cost=Decimal('25.00'),
            permission_deadline=date(2026, 10, 16),
            packed_lunch_required=True,
            year_group='Year 7',
            created_by=self.user,
        )

        with self.assertRaises(ValidationError) as raised:
            trip.full_clean()

        self.assertIn('Permission deadline must be before the trip date.', raised.exception.messages)


class TripResponseValidationTestCase(TestCase):
    """Test validation rules for returned permission slips."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='responseuser',
            password='testpass123',
            is_staff=True,
        )
        self.trip = Trip.objects.create(
            name='Response Validation Trip',
            destination='Science Centre',
            trip_date=date(2026, 10, 15),
            departure_time=time(9, 0),
            return_time=time(16, 0),
            cost=Decimal('25.00'),
            permission_deadline=date(2026, 10, 1),
            packed_lunch_required=True,
            year_group='Year 7',
            created_by=self.user,
        )
        self.student = Student.objects.create(
            first_name='Test',
            last_name='Student',
            form_class='7A',
        )

    def test_returned_slip_without_consent_is_allowed(self):
        response = TripResponse(
            trip=self.trip,
            student=self.student,
            slip_returned=True,
            emergency_contact_number='07123456789',
            consent_given=False,
        )

        response.full_clean()

        self.assertFalse(response.consent_given)

    def test_consent_without_parent_signature_is_rejected(self):
        response = TripResponse(
            trip=self.trip,
            student=self.student,
            emergency_contact_number='07123456789',
            consent_given=True,
        )

        with self.assertRaises(ValidationError) as raised:
            response.full_clean()

        self.assertIn('parent_signature_name', raised.exception.message_dict)


class TripReportCsvExportTestCase(TestCase):
    """Test the trip report CSV export."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='csvuser',
            password='testpass123',
            is_staff=True,
        )
        self.trip = Trip.objects.create(
            name='CSV Export Trip',
            destination='City Museum',
            trip_date=date(2026, 10, 15),
            departure_time=time(9, 0),
            return_time=time(16, 0),
            cost=Decimal('25.00'),
            permission_deadline=date(2026, 10, 1),
            packed_lunch_required=True,
            year_group='Year 7',
            created_by=self.user,
        )

        for first_name, last_name in [('Alice', 'One'), ('Bob', 'Two'), ('Charlie', 'Three')]:
            student = Student.objects.create(
                first_name=first_name,
                last_name=last_name,
                form_class='7A',
            )
            TripResponse.objects.create(
                trip=self.trip,
                student=student,
                emergency_contact_number='07123456789',
            )

    def test_csv_export_contains_one_row_per_student(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('trips:export_trip_report_csv', args=[self.trip.pk]))

        self.assertEqual(response.status_code, 200)
        rows = list(csv.reader(response.content.decode('utf-8').splitlines()))
        self.assertEqual(len(rows) - 1, 3)


class TripIncomeCalculationTestCase(TestCase):
    """Test cases for Trip income calculation methods."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create a trip with a cost of £25.00
        self.trip = Trip.objects.create(
            name='School Museum Visit',
            destination='British Museum',
            trip_date=date(2026, 10, 15),
            departure_time=time(9, 0),
            return_time=time(16, 30),
            cost=Decimal('25.00'),
            permission_deadline=date(2026, 10, 1),
            packed_lunch_required=True,
            year_group='Year 7',
            created_by=self.user
        )
        
        # Create test students
        self.student1 = Student.objects.create(
            first_name='Alice',
            last_name='Johnson',
            form_class='7A'
        )
        
        self.student2 = Student.objects.create(
            first_name='Bob',
            last_name='Smith',
            form_class='7A'
        )
        
        self.student3 = Student.objects.create(
            first_name='Charlie',
            last_name='Brown',
            form_class='7B'
        )
        
        self.student4 = Student.objects.create(
            first_name='Diana',
            last_name='Prince',
            form_class='7B'
        )
    
    def test_total_expected_income_with_all_students_paid(self):
        """Test expected income when all students have paid."""
        # Create 4 responses with all payments received
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student1,
            slip_returned=True,
            payment_received=True,
            emergency_contact_number='07123456789',
            parent_signature_name='Parent One',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student2,
            slip_returned=True,
            payment_received=True,
            emergency_contact_number='07234567890',
            parent_signature_name='Parent Two',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student3,
            slip_returned=True,
            payment_received=True,
            emergency_contact_number='07345678901',
            parent_signature_name='Parent Three',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student4,
            slip_returned=True,
            payment_received=True,
            emergency_contact_number='07456789012',
            parent_signature_name='Parent Four',
            consent_given=True
        )
        
        # Expected: 4 students × £25 = £100
        expected_income = Decimal('100.00')
        self.assertEqual(self.trip.total_expected_income(), expected_income)
    
    def test_total_collected_income_with_all_students_paid(self):
        """Test collected income when all students have paid."""
        # Create 4 responses with all payments received
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student1,
            slip_returned=True,
            payment_received=True,
            emergency_contact_number='07123456789',
            parent_signature_name='Parent One',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student2,
            slip_returned=True,
            payment_received=True,
            emergency_contact_number='07234567890',
            parent_signature_name='Parent Two',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student3,
            slip_returned=True,
            payment_received=True,
            emergency_contact_number='07345678901',
            parent_signature_name='Parent Three',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student4,
            slip_returned=True,
            payment_received=True,
            emergency_contact_number='07456789012',
            parent_signature_name='Parent Four',
            consent_given=True
        )
        
        # Collected: 4 paid × £25 = £100
        collected_income = Decimal('100.00')
        self.assertEqual(self.trip.total_collected_income(), collected_income)
    
    def test_total_expected_income_with_mixed_payments(self):
        """Test expected income with a mix of paid and unpaid responses."""
        # Create 4 responses: 2 paid, 2 unpaid
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student1,
            slip_returned=True,
            payment_received=True,  # PAID
            emergency_contact_number='07123456789',
            parent_signature_name='Parent One',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student2,
            slip_returned=True,
            payment_received=False,  # UNPAID
            emergency_contact_number='07234567890',
            parent_signature_name='Parent Two',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student3,
            slip_returned=True,
            payment_received=True,  # PAID
            emergency_contact_number='07345678901',
            parent_signature_name='Parent Three',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student4,
            slip_returned=True,
            payment_received=False,  # UNPAID
            emergency_contact_number='07456789012',
            parent_signature_name='Parent Four',
            consent_given=True
        )
        
        # Expected: 4 students × £25 = £100 (regardless of payment status)
        expected_income = Decimal('100.00')
        self.assertEqual(self.trip.total_expected_income(), expected_income)
    
    def test_total_collected_income_with_mixed_payments(self):
        """Test collected income with a mix of paid and unpaid responses."""
        # Create 4 responses: 2 paid, 2 unpaid
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student1,
            slip_returned=True,
            payment_received=True,  # PAID
            emergency_contact_number='07123456789',
            parent_signature_name='Parent One',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student2,
            slip_returned=True,
            payment_received=False,  # UNPAID
            emergency_contact_number='07234567890',
            parent_signature_name='Parent Two',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student3,
            slip_returned=True,
            payment_received=True,  # PAID
            emergency_contact_number='07345678901',
            parent_signature_name='Parent Three',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student4,
            slip_returned=True,
            payment_received=False,  # UNPAID
            emergency_contact_number='07456789012',
            parent_signature_name='Parent Four',
            consent_given=True
        )
        
        # Collected: 2 paid × £25 = £50
        collected_income = Decimal('50.00')
        self.assertEqual(self.trip.total_collected_income(), collected_income)
    
    def test_total_collected_income_with_no_payments(self):
        """Test collected income when no students have paid."""
        # Create 4 responses with no payments
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student1,
            slip_returned=True,
            payment_received=False,
            emergency_contact_number='07123456789',
            parent_signature_name='Parent One',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student2,
            slip_returned=True,
            payment_received=False,
            emergency_contact_number='07234567890',
            parent_signature_name='Parent Two',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student3,
            slip_returned=True,
            payment_received=False,
            emergency_contact_number='07345678901',
            parent_signature_name='Parent Three',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=self.trip,
            student=self.student4,
            slip_returned=True,
            payment_received=False,
            emergency_contact_number='07456789012',
            parent_signature_name='Parent Four',
            consent_given=True
        )
        
        # Collected: 0 paid × £25 = £0
        collected_income = Decimal('0.00')
        self.assertEqual(self.trip.total_collected_income(), collected_income)
    
    def test_total_expected_income_with_no_students(self):
        """Test expected income when no students are linked to the trip."""
        # No responses created
        expected_income = Decimal('0.00')
        self.assertEqual(self.trip.total_expected_income(), expected_income)
    
    def test_total_collected_income_with_no_responses(self):
        """Test collected income when no responses exist."""
        # No responses created
        collected_income = Decimal('0.00')
        self.assertEqual(self.trip.total_collected_income(), collected_income)
    
    def test_total_expected_income_calculation_accuracy(self):
        """Test expected income calculation with decimal cost values."""
        # Create a trip with a decimal cost
        trip_decimal = Trip.objects.create(
            name='Zoo Visit',
            destination='London Zoo',
            trip_date=date(2026, 11, 20),
            departure_time=time(10, 0),
            return_time=time(15, 0),
            cost=Decimal('17.50'),  # £17.50
            permission_deadline=date(2026, 11, 10),
            packed_lunch_required=False,
            year_group='Year 8',
            created_by=self.user
        )
        
        # Create 3 responses
        for i, student in enumerate([self.student1, self.student2, self.student3], 1):
            TripResponse.objects.create(
                trip=trip_decimal,
                student=student,
                slip_returned=True,
                payment_received=(i % 2 == 1),  # Alternate paid/unpaid
                emergency_contact_number=f'0712345678{i}',
                parent_signature_name=f'Parent {i}',
                consent_given=True
            )
        
        # Expected: 3 students × £17.50 = £52.50
        expected_income = Decimal('52.50')
        self.assertEqual(trip_decimal.total_expected_income(), expected_income)
    
    def test_total_collected_income_calculation_accuracy(self):
        """Test collected income calculation with decimal cost values."""
        # Create a trip with a decimal cost
        trip_decimal = Trip.objects.create(
            name='Zoo Visit',
            destination='London Zoo',
            trip_date=date(2026, 11, 20),
            departure_time=time(10, 0),
            return_time=time(15, 0),
            cost=Decimal('17.50'),  # £17.50
            permission_deadline=date(2026, 11, 10),
            packed_lunch_required=False,
            year_group='Year 8',
            created_by=self.user
        )
        
        # Create 3 responses: 2 paid, 1 unpaid
        TripResponse.objects.create(
            trip=trip_decimal,
            student=self.student1,
            slip_returned=True,
            payment_received=True,  # PAID
            emergency_contact_number='07123456781',
            parent_signature_name='Parent 1',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=trip_decimal,
            student=self.student2,
            slip_returned=True,
            payment_received=True,  # PAID
            emergency_contact_number='07123456782',
            parent_signature_name='Parent 2',
            consent_given=True
        )
        TripResponse.objects.create(
            trip=trip_decimal,
            student=self.student3,
            slip_returned=True,
            payment_received=False,  # UNPAID
            emergency_contact_number='07123456783',
            parent_signature_name='Parent 3',
            consent_given=True
        )
        
        # Collected: 2 paid × £17.50 = £35.00
        collected_income = Decimal('35.00')
        self.assertEqual(trip_decimal.total_collected_income(), collected_income)
    
    def test_income_methods_after_payment_update(self):
        """Test that income calculations update correctly when payment status changes."""
        # Create 2 responses, both unpaid initially
        response1 = TripResponse.objects.create(
            trip=self.trip,
            student=self.student1,
            slip_returned=True,
            payment_received=False,
            emergency_contact_number='07123456789',
            parent_signature_name='Parent One',
            consent_given=True
        )
        response2 = TripResponse.objects.create(
            trip=self.trip,
            student=self.student2,
            slip_returned=True,
            payment_received=False,
            emergency_contact_number='07234567890',
            parent_signature_name='Parent Two',
            consent_given=True
        )
        
        # Initial state: expected £50, collected £0
        self.assertEqual(self.trip.total_expected_income(), Decimal('50.00'))
        self.assertEqual(self.trip.total_collected_income(), Decimal('0.00'))
        
        # Update one response to paid
        response1.payment_received = True
        response1.save()
        
        # After update: expected still £50, collected now £25
        self.assertEqual(self.trip.total_expected_income(), Decimal('50.00'))
        self.assertEqual(self.trip.total_collected_income(), Decimal('25.00'))
        
        # Update second response to paid
        response2.payment_received = True
        response2.save()
        
        # After second update: expected £50, collected £50
        self.assertEqual(self.trip.total_expected_income(), Decimal('50.00'))
        self.assertEqual(self.trip.total_collected_income(), Decimal('50.00'))

