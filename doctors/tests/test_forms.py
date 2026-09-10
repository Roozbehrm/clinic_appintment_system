import pytest

from doctors.forms import WorkingHourForm


@pytest.mark.django_db
class TestWorkingHourForm:
    def test_valid_non_overlapping_hour_passes(self, doctor_user, working_hour):
        # working_hour موجود: شنبه ۰۸:۰۰-۱۲:۰۰ ؛ این یکی شنبه ۱۳:۰۰-۱۵:۰۰ است، همپوشانی ندارد
        form = WorkingHourForm(data={
            "day_of_week": 0,
            "start_time": "13:00",
            "end_time": "15:00",
            "slot_duration_minutes": 30,
        }, doctor=doctor_user)
        assert form.is_valid(), form.errors

    def test_start_after_end_is_invalid(self, doctor_user):
        form = WorkingHourForm(data={
            "day_of_week": 0,
            "start_time": "15:00",
            "end_time": "13:00",
            "slot_duration_minutes": 30,
        }, doctor=doctor_user)
        assert not form.is_valid()

    def test_overlapping_hour_same_day_is_invalid(self, doctor_user, working_hour):
        # working_hour موجود: شنبه ۰۸:۰۰-۱۲:۰۰ ؛ این یکی ۱۰:۰۰-۱۴:۰۰ با آن تداخل دارد
        form = WorkingHourForm(data={
            "day_of_week": 0,
            "start_time": "10:00",
            "end_time": "14:00",
            "slot_duration_minutes": 30,
        }, doctor=doctor_user)
        assert not form.is_valid()
        assert "همپوشانی" in str(form.errors)

    def test_same_hours_on_different_day_is_valid(self, doctor_user, working_hour):
        # working_hour موجود: شنبه(0) ۰۸:۰۰-۱۲:۰۰ ؛ این یکی یکشنبه(1) با همان ساعت‌هاست
        form = WorkingHourForm(data={
            "day_of_week": 1,
            "start_time": "08:00",
            "end_time": "12:00",
            "slot_duration_minutes": 30,
        }, doctor=doctor_user)
        assert form.is_valid(), form.errors

    def test_adjacent_hours_touching_boundary_is_valid(self, doctor_user, working_hour):
        # working_hour موجود تا ۱۲:۰۰ است؛ این یکی درست از ۱۲:۰۰ شروع می‌شود (همپوشانی واقعی ندارد)
        form = WorkingHourForm(data={
            "day_of_week": 0,
            "start_time": "12:00",
            "end_time": "14:00",
            "slot_duration_minutes": 30,
        }, doctor=doctor_user)
        assert form.is_valid(), form.errors

    def test_without_doctor_kwarg_skips_overlap_check(self):
        # اگر doctor پاس داده نشود (مثلاً استفاده‌ی مستقل از فرم)، فقط اعتبارسنجی
        # start<end انجام می‌شود و کد نباید خطا بدهد.
        form = WorkingHourForm(data={
            "day_of_week": 0,
            "start_time": "08:00",
            "end_time": "12:00",
            "slot_duration_minutes": 30,
        })
        assert form.is_valid(), form.errors
