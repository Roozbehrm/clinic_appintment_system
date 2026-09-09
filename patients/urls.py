from django.urls import path
from patients.views import MyAppointmentsView 



app_name = 'patients'

urlpatterns = [
    path ('my-appointments/',
          MyAppointmentsView.as_view(),
          name = 'my_appointments') 
]