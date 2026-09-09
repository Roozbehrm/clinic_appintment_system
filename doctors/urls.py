from django.urls import path

from .views import SearchDoctorsView

urlspatterns = [
    path("search/", SearchDoctorsView.as_view(), name="search"),
]
