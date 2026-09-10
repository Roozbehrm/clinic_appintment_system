from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["appointment", "get_doctor", "get_patient", "rating", "created_at"]
    list_filter = ["rating", "appointment__time_slot__doctor"]
    search_fields = [
        "appointment__time_slot__doctor__profile__full_name",
        "appointment__patient__profile__full_name",
    ]

    @admin.display(description="پزشک", ordering="appointment__time_slot__doctor")
    def get_doctor(self, obj):
        return obj.appointment.time_slot.doctor

    @admin.display(description="بیمار", ordering="appointment__patient")
    def get_patient(self, obj):
        return obj.appointment.patient

