from datetime import datetime, timedelta

from django.utils import timezone

from .models import TimeSlot, PY_WEEKDAY_TO_OUR


def generate_time_slots(doctor, days_ahead=14):

    created_count = 0

    today = timezone.localdate()

    for day_offset in range(days_ahead + 1):
        visit_date = today + timedelta(days=day_offset)

        our_weekday = PY_WEEKDAY_TO_OUR[visit_date.weekday()]

        working_hours = doctor.working_hours.filter(day_of_week=our_weekday)

        for working_hour in working_hours:

            current_datetime = datetime.combine(
                visit_date,
                working_hour.start_time,
            )

            end_datetime = datetime.combine(
                visit_date,
                working_hour.end_time,
            )

            duration = timedelta(minutes=working_hour.slot_duration_minutes)

            while current_datetime + duration <= end_datetime:

                start_time = current_datetime.time()
                end_time = (current_datetime + duration).time()

                _, created = TimeSlot.objects.get_or_create(
                    doctor=doctor,
                    visit_date=visit_date,
                    start_time=start_time,
                    defaults={
                        "end_time": end_time,
                        "working_hours": working_hour,
                        "status": TimeSlot.STATUS_FREE,
                    },
                )

                if created:
                    created_count += 1

                current_datetime += duration

    return created_count
