from django.contrib import admin
from .models import Appointment

# TASK T3.2 (Mahyar)
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'time_slot', 'price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    
# ادمین نمی‌تونه تاریخ ایجاد و آپدیت رو دستی عوض کنه
    readonly_fields = ('created_at', 'updated_at')
# فیلد هایی که ادمین میتونه سرچشون کنه     
    search_fields = ('patient__id', 'time_slot__id')