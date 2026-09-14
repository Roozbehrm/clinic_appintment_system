import pytest

from doctors.models import PY_WEEKDAY_TO_OUR, TimeSlot
from doctors.services import generate_time_slots


@pytest.mark.django_db
class TestGenerateTimeSlots:
    def test_creates_slots_matching_working_hour_duration(self, doctor_user, working_hour):

        created = generate_time_slots(doctor_user, days_ahead=14)

        assert created > 0

        total_slots = TimeSlot.objects.filter(doctor=doctor_user).count()
        assert total_slots == created
        assert total_slots % 8 == 0

    def test_slots_only_created_on_matching_weekday(self, doctor_user, working_hour):

        generate_time_slots(doctor_user, days_ahead=14)

        for slot in TimeSlot.objects.filter(doctor=doctor_user):
            our_weekday = PY_WEEKDAY_TO_OUR[slot.visit_date.weekday()]
            assert our_weekday == working_hour.day_of_week

    def test_is_idempotent_on_second_call(self, doctor_user, working_hour):
        first_run = generate_time_slots(doctor_user, days_ahead=14)
        second_run = generate_time_slots(doctor_user, days_ahead=14)

        assert first_run > 0
        assert second_run == 0  
        assert TimeSlot.objects.filter(doctor=doctor_user).count() == first_run

    def test_no_working_hours_creates_no_slots(self, doctor_user):
        created = generate_time_slots(doctor_user, days_ahead=14)
        assert created == 0
        assert TimeSlot.objects.filter(doctor=doctor_user).count() == 0

    def test_slot_times_stay_within_working_hour_bounds(self, doctor_user, working_hour):
        generate_time_slots(doctor_user, days_ahead=14)

        for slot in TimeSlot.objects.filter(doctor=doctor_user):
            assert slot.start_time >= working_hour.start_time
            assert slot.end_time <= working_hour.end_time