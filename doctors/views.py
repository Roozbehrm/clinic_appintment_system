from django.views.generic import DetailView
from django.utils import timezone
from .models import Doctor, TimeSlot
from django.shortcuts import render
from django.views import View
from .admin import Doctor, Specialty


# TASK T3.1 (Mahyar)
class DoctorDetailView(DetailView):
    model = Doctor
    template_name = 'doctors/detail.html'
    context_object_name = 'doctor'

#دریافت تایم اسلات های خالی
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.get_object()
        
        context['available_slots'] = TimeSlot.objects.filter(
            doctor=doctor, 
            status='available', 
            visit_date__gte=timezone.now().date()
        ).order_by('visit_date', 'start_time')
        
        # ایمپورت برای جلوگیری از Circular Import  
        from reviews.models import Review
        from django.db.models import Avg
        
        #دریافت لیست نظرات 
        reviews = Review.objects.filter(appointment__time_slot__doctor=doctor).order_by('-created_at')
        context['reviews'] = reviews
        
        #محاسبه میانگین امتیاز
        if reviews.exists():
            avg_rating = reviews.aggregate(average=Avg('rating'))['average']
            context['avg_rating'] = round(avg_rating, 1) if avg_rating else "بدون امتیاز"
        else:
            context['avg_rating'] = "بدون امتیاز"

        return context

      
class HomeView(View):
    def get(self, request):
        top_doctors = Doctor.objects.filter(is_active=True).select_related(
            "profile", "specialty").order_by("-id")[:6]
        specialties = Specialty.objects.all()[:8]
        return render(request, "doctors/home.html", {
            "top_doctors": top_doctors, "specialties": specialties,
        })
