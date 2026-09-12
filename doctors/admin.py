from django.contrib import admin, messages
from .models import Specialty, Doctor, WorkingHour, TimeSlot
from .forms import DoctorCreationForm


class DoctorInline(admin.StackedInline):

    model = Doctor
    can_delete = False
    extra = 0
    max_num = 1

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ["profile", "mcc", "specialty", "consultation_fee", "is_active"]
    list_filter = ["specialty", "is_active"]
    search_fields = ["profile__full_name", "mcc"]

    def get_form(self, request, obj=None, **kwargs):

        if obj is None:
            kwargs["form"] = DoctorCreationForm
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            phone = obj.profile.user.phone_number
            email = obj.profile.user.email
            password = getattr(form, "generated_password", None)

            text = (
                f"پزشک «{obj.profile.full_name}» ساخته شد. اطلاعات ورود از طریق پیامک "
                f"(شماره {phone}) و ایمیل ({email}) در پس‌زمینه برای خودِ پزشک ارسال می‌شود."
            )
            if password:
                text += f" رمز عبور اولیه (فقط برای پشتیبانی، اگر پیامک/ایمیل نرسید): {password}"
            self.message_user(request, text, level=messages.SUCCESS)

            request._skip_next_admin_message = True

    def message_user(self, request, message, level=messages.INFO, extra_tags="",
                      fail_silently=False):
        if getattr(request, "_skip_next_admin_message", False):
            request._skip_next_admin_message = False
            return
        super().message_user(request, message, level, extra_tags, fail_silently)


@admin.register(WorkingHour)
class WorkingHourAdmin(admin.ModelAdmin):
    list_display = ["doctor", "day_of_week", "start_time", "end_time", "slot_duration_minutes"]
    list_filter = ["day_of_week"]


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ["doctor", "visit_date", "start_time", "end_time", "status"]
    list_filter = ["status", "visit_date"]
    search_fields = ["doctor__profile__full_name"]
