import pytest
from doctors.services import generate_time_slots
from doctors.models import TimeSlot , WorkingHour
from datetime import datetime , time 
from doctors.models import PY_WEEKDAY_TO_OUR



@pytest.mark.django_db
class TestGenerateTimeSlots:
    def test_create_time_slots(self, doctor_user):

        today = datetime.now().date()
        our_weekday = PY_WEEKDAY_TO_OUR[today.weekday()]

        working_hour = WorkingHour.objects.create(
            doctor = doctor_user,
            day_of_week = our_weekday, 
            start_time = time(8,0),
            end_time = time(12,0),
            slot_duration_minutes = 30,
        )

        created_count = generate_time_slots(doctor_user, days_ahead=1)

        assert created_count == 8 
        assert TimeSlot.objects.filter(
                    doctor=doctor_user,
                ).count() == 8


    def test_creats_slots_with_correct_times(self , doctor_user):

        today = datetime.now().date()
        our_weekday = PY_WEEKDAY_TO_OUR[today.weekday()]

        working_hour = WorkingHour.objects.create(
            doctor = doctor_user,
            day_of_week = our_weekday, 
            start_time = time(8,0),
            end_time = time(12,0),
            slot_duration_minutes = 30,
        )

        generate_time_slots(doctor_user, days_ahead=1)

        slots = TimeSlot.objects.filter(
            doctor = doctor_user,
        ).order_by('start_time')

        assert slots.count() == 8

        assert slots[0].start_time == time(8,0)
        assert slots[0].end_time == time(8,30)

        assert slots[1].start_time == time(8,30)
        assert slots[1].end_time == time(9,0)

        assert slots[2].start_time == time(9,00)
        assert slots[2].end_time == time(9,30)

        assert slots[3].start_time == time(9,30)
        assert slots[3].end_time == time(10,00)



    def test_does_not_create_dublicate_slots(self,doctor_user):

        today = datetime.now().date()
        our_weekday = PY_WEEKDAY_TO_OUR[today.weekday()]

        working_hour = WorkingHour.objects.create(
            doctor = doctor_user,
            day_of_week = our_weekday, 
            start_time = time(8,0),
            end_time = time(12,0),
            slot_duration_minutes = 30,
        )

        first_count = generate_time_slots(doctor_user, days_ahead=1)

        second_count = generate_time_slots(doctor_user, days_ahead=1)

        assert first_count == 8
        assert second_count == 0

        slots = TimeSlot.objects.filter(
            doctor = doctor_user,
        )

        assert slots.count() == 8 


    def test_does_not_create_incomplete_last_slot(self,doctor_user):

        today = datetime.now().date()
        our_weekday = PY_WEEKDAY_TO_OUR[today.weekday()]

        working_hour = WorkingHour.objects.create(
            doctor = doctor_user,
            day_of_week = our_weekday, 
            start_time = time(8,0),
            end_time = time(11,15),
            slot_duration_minutes = 30,
        )

        created_count = generate_time_slots(doctor_user, days_ahead=1)

        slots = TimeSlot.objects.filter(
                    doctor = doctor_user,
                ).order_by('start_time')
        
        assert created_count == 6
        assert slots.last().end_time == time(11,0)
        assert slots.count() == 6



