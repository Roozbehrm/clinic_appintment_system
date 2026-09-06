from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["profile", "birth_date"]
    search_fields = ["profile__full_name"]
