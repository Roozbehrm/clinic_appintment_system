from datetime import time, timedelta

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from accounts.models import Profile, User

from .models import Specialty, Doctor, WorkingHour, TimeSlot
from .services import generate_time_slots


class DoctorModelsTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="09120000000",
            email="ali@example.com",
            password="testpassword123",
        )

        self.profile = Profile.objects.create(
            user=self.user,
            full_name="دکتر علی رضایی",
        )

        self.specialty = Specialty.objects.create(
            name="قلب و عروق",
            description="متخصص بیماری های قلب و عروق",
        )

        self.doctor = Doctor.objects.create(
            profile=self.profile,
            specialty=self.specialty,
            bio="پزشک متخصص قلب",
            consultation_fee=500000,
            is_active=True,
        )

    def test_specialty_creation(self):

        self.assertEqual(self.specialty.name, "قلب و عروق")
        self.assertEqual(
            Specialty.objects.count(),
            1,
        )

    def test_specialty_name_is_unique(self):

        with self.assertRaises(IntegrityError):
            Specialty.objects.create(
                name="قلب و عروق",
            )

    def test_doctor_profile_and_specialty_relationships(self):

        self.assertEqual(
            self.doctor.profile,
            self.profile,
        )

        self.assertEqual(
            self.doctor.specialty,
            self.specialty,
        )

        self.assertEqual(
            self.profile.doctor,
            self.doctor,
        )

        self.assertIn(
            self.doctor,
            self.specialty.doctors.all(),
        )

    def test_working_hour_relationship(self):

        working_hour = WorkingHour.objects.create(
            doctor=self.doctor,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(12, 0),
            slot_duration_minutes=30,
        )

        self.assertEqual(
            working_hour.doctor,
            self.doctor,
        )

        self.assertIn(
            working_hour,
            self.doctor.working_hours.all(),
        )

    def test_time_slot_relationship_and_is_free(self):

        working_hour = WorkingHour.objects.create(
            doctor=self.doctor,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(10, 0),
            slot_duration_minutes=30,
        )

        visit_date = timezone.localdate()

        slot = TimeSlot.objects.create(
            doctor=self.doctor,
            working_hours=working_hour,
            visit_date=visit_date,
            start_time=time(9, 0),
            end_time=time(9, 30),
            status="free",
        )

        self.assertEqual(
            slot.doctor,
            self.doctor,
        )

        self.assertEqual(
            slot.working_hours,
            working_hour,
        )

        self.assertTrue(slot.is_free)

        slot.status = "booked"
        slot.save()
        slot.refresh_from_db()

        self.assertFalse(slot.is_free)

    def test_time_slot_unique_constraint(self):

        visit_date = timezone.localdate()

        TimeSlot.objects.create(
            doctor=self.doctor,
            visit_date=visit_date,
            start_time=time(9, 0),
            end_time=time(9, 30),
            status="free",
        )

        with self.assertRaises(IntegrityError):
            TimeSlot.objects.create(
                doctor=self.doctor,
                visit_date=visit_date,
                start_time=time(9, 0),
                end_time=time(9, 30),
                status="free",
            )

    def test_doctor_average_rating_without_reviews(self):

        self.assertEqual(
            self.doctor.average_rating,
            0,
        )

    def test_doctor_review_count_without_reviews(self):

        self.assertEqual(
            self.doctor.review_count,
            0,
        )


class GenerateTimeSlotsTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="09121111111",
            email="doctor@example.com",
            password="testpass123",
        )

        self.profile = Profile.objects.create(
            user=self.user,
            full_name="دکتر تست",
        )

        self.specialty = Specialty.objects.create(
            name="تخصص تست",
        )

        self.doctor = Doctor.objects.create(
            profile=self.profile,
            specialty=self.specialty,
        )

    def test_generate_time_slots_creates_slots(self):
        today = timezone.localdate()

        from .models import PY_WEEKDAY_TO_OUR

        project_weekday = PY_WEEKDAY_TO_OUR[today.weekday()]

        WorkingHour.objects.create(
            doctor=self.doctor,
            day_of_week=project_weekday,
            start_time=time(9, 0),
            end_time=time(11, 0),
            slot_duration_minutes=30,
        )

        created_count = generate_time_slots(
            self.doctor,
            days_ahead=0,
        )

        self.assertEqual(
            created_count,
            4,
        )

        self.assertEqual(
            TimeSlot.objects.count(),
            4,
        )

    def test_generate_time_slots_for_14_days(self):
        today = timezone.localdate()

        from .models import PY_WEEKDAY_TO_OUR

        for day_offset in range(15):
            visit_date = today + timedelta(days=day_offset)

            project_weekday = PY_WEEKDAY_TO_OUR[visit_date.weekday()]

            WorkingHour.objects.create(
                doctor=self.doctor,
                day_of_week=project_weekday,
                start_time=time(9, 0),
                end_time=time(10, 0),
                slot_duration_minutes=30,
            )

        generate_time_slots(
            self.doctor,
            days_ahead=14,
        )

        dates = set(
            TimeSlot.objects.values_list(
                "visit_date",
                falt=True,
            )
        )

        expected_dates = {
            today + timedelta(days=day_offset) for day_offset in range(15)
        }

        self.assertEqual(dates, expected_dates)

    def test_generate_slots_have_correct_times(self):
        today = timezone.localdate()

        from .models import PY_WEEKDAY_TO_OUR

        project_weekday = PY_WEEKDAY_TO_OUR[today.weekday()]

        WorkingHour.objects.create(
            doctor=self.doctor,
            day_of_week=project_weekday,
            start_time=time(9, 0),
            end_time=time(10, 0),
            slot_duration_minutes=30,
        )

        generate_time_slots(
            self.doctor,
            days_ahead=0,
        )

        slots = TimeSlot.objects.filter(
            doctor=self.doctor,
            visit_date=today,
        ).order_by("start_time")

        self.assertEqual(slots.count(), 2)

        self.assertEqual(
            slots[0].start_time,
            time(9, 0),
        )
        self.assertEqual(
            slots[0].end_time,
            time(9, 30),
        )

        self.assertEqual(
            slots[1].start_time,
            time(9, 30),
        )
        self.assertEqual(
            slots[1].end_time,
            time(10, 0),
        )

    def test_generated_slots_are_free(self):
        today = timezone.localdate()

        from .models import PY_WEEKDAY_TO_OUR

        project_weekday = PY_WEEKDAY_TO_OUR[today.weekday()]

        WorkingHour.objects.create(
            doctor=self.doctor,
            day_of_week=project_weekday,
            start_time=time(9, 0),
            end_time=time(10, 0),
            slot_duration_minutes=30,
        )

        generate_time_slots(
            self.doctor,
            days_ahead=0,
        )

        slots = TimeSlot.objects.filter(
            doctor=self.doctor,
            visit_date=today,
        )

        self.assertEqual(slots.count(), 2)

        for slot in slots:
            self.assertEqual(
                slot.status,
                "free",
            )
            self.assertTrue(slot.is_free)

    def test_generate_time_slots_is_idempotent(self):
        today = timezone.localdate()

        from .models import PY_WEEKDAY_TO_OUR

        project_weekday = PY_WEEKDAY_TO_OUR[today.weekday()]

        WorkingHour.objects.create(
            doctor=self.doctor,
            day_of_week=project_weekday,
            start_time=time(9, 0),
            end_time=time(11, 0),
            slot_duration_minutes=30,
        )

        first_created_count = generate_time_slots(
            self.doctor,
            days_ahead=0,
        )
        first_total_count = TimeSlot.objects.filter(
            doctor=self.doctor,
        ).count()
        second_created_count = generate_time_slots(
            self.doctor,
            days_ahead=0,
        )
        second_total_count = TimeSlot.objects.filter(
            doctor=self.doctor,
        ).count()

        self.assertEqual(
            first_created_count,
            4,
        )
        self.assertEqual(
            first_total_count,
            4,
        )
        self.assertEqual(
            second_created_count,
            0,
        )
        self.assertEqual(
            second_total_count,
            4,
        )
