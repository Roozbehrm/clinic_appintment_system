from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import AdminUserCreationForm, AdminUserChangeForm
from .models import User, OTP, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm

    ordering = ["-date_joined"]
    list_display = ["email", "phone_number", "is_verified", "is_staff", "is_active"]
    search_fields = ["email", "phone_number"]
    inlines = [ProfileInline]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("اطلاعات", {"fields": ("phone_number",)}),
        ("دسترسی‌ها", {"fields": ("is_active", "is_verified", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "phone_number", "password1", "password2")}),
    )

    def get_inline_instances(self, request, obj=None):
 
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ["user", "code", "purpose", "is_used", "expires_at"]
    list_filter = ["purpose", "is_used"]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "user", "gender"]
    search_fields = ["full_name", "user__email", "user__phone_number"]

    def get_inline_instances(self, request, obj=None):
        from doctors.admin import DoctorInline
        if obj is None:
            return []
        return [DoctorInline(self.model, self.admin_site)]
