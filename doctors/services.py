from datetime import datetime, timedelta

from django.db.models import Q
from django.utils import timezone

from .models import TimeSlot, PY_WEEKDAY_TO_OUR


def delete_expired_free_slots(doctor=None):
    now = timezone.localtime()
    slots = TimeSlot.objects.filter(status="free")
    if doctor is not None:
        slots = slots.filter(doctor=doctor)
    expired_slots = slots.filter(
        Q(visit_date__lt=now.date())
        | Q(visit_date=now.date(), end_time__lte=now.time().replace(tzinfo=None))
    )
    deleted_count, _ = expired_slots.delete()
    return deleted_count


def generate_time_slots(doctor, days_ahead=14):
  
    today = datetime.now().date()
    created_count = 0
    working_hours = doctor.working_hours.all()

    for i in range(days_ahead):
        day = today + timedelta(days=i)
        our_weekday = PY_WEEKDAY_TO_OUR[day.weekday()]
        day_working_hours = [wh for wh in working_hours if wh.day_of_week == our_weekday]

        for wh in day_working_hours:
            cursor = datetime.combine(day, wh.start_time)
            end = datetime.combine(day, wh.end_time)
            step = timedelta(minutes=wh.slot_duration_minutes)

            while cursor + step <= end:
                slot_end = cursor + step
                _, is_new = TimeSlot.objects.get_or_create(
                    doctor=doctor,
                    visit_date=day,
                    start_time=cursor.time(),
                    defaults={
                        "working_hours": wh,
                        "end_time": slot_end.time(),
                        "status": "free",
                    },
                )
                if is_new:
                    created_count += 1
                cursor = slot_end

    return created_count
