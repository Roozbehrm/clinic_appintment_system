from django.shortcuts import render
from django.views import View
from .admin import Doctor, Specialty


class HomeView(View):
    def get(self, request):
        top_doctors = Doctor.objects.filter(is_active=True).select_related(
            "profile", "specialty").order_by("-id")[:6]
        specialties = Specialty.objects.all()[:8]
        return render(request, "doctors/home.html", {
            "top_doctors": top_doctors, "specialties": specialties,
        })
