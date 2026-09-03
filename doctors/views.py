from django.views.generic import DetailView
from django.db.models import Avg
from django.utils import timezone
from .models import Doctor, TimeSlot
from appointments.models import Review 

# TASK T3.1 (Mahyar)
class DoctorDetailView(DetailView):
    model = Doctor
    template_name = 'doctors/doctor_detail.html'
    context_object_name = 'doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.get_object()
        
        #دریافت تایم اسلات های خالی
        context['available_slots'] = TimeSlot.objects.filter(
            doctor=doctor, 
            status='available', 
            visit_date__gte=timezone.now().date()
        ).order_by('visit_date', 'start_time')
        
        #دریافت لیست نظرات 
        reviews = Review.objects.filter(appointment__time_slot__doctor=doctor).order_by('-created_at')
        context['reviews'] = reviews
        
        #محاسبه میانگین امتیاز
        avg_rating = reviews.aggregate(average=Avg('rating'))['average']
        context['avg_rating'] = round(avg_rating, 1) if avg_rating else "بدون امتیاز"

        return context