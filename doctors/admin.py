from django.contrib import admin

from .models import Specialty, Doctor, WorkingHour, TimeSlot


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "profile",
        "specialty",
        "consultation_fee",
        "is_active",
        "average_rating",
        "review_count",
    )

    list_filter = (
        "specialty",
        "is_active",
    )

    search_fields = (
        "profile__full_name",
        "specialty__name",
    )

    list_select_related = (
        "profile",
        "specialty",
    )


@admin.register(WorkingHour)
class WorkingHourAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "doctor",
        "day_of_week",
        "start_time",
        "end_time",
        "slot_duration_minutes",
    )

    list_filter = ("day_of_week",)

    search_fields = ("doctor__profile__full_name",)

    list_select_related = ("doctor",)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "doctor",
        "visit_date",
        "start_time",
        "end_time",
        "status",
    )

    list_filter = (
        "status",
        "visit_date",
    )

    search_fields = ("doctor__profile__full_name",)

    list_select_related = (
        "doctor",
        "working_hours",
    )
