from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("add/<int:appointment_id>/", views.AddReviewView.as_view(), name="add_review"),
    path("edit/<int:review_id>/", views.EditReviewView.as_view(), name="edit_review"),
]