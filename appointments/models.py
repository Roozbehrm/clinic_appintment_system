from django.db import models

# Create your models here.
class Review(models.Model):
 
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveSmallIntegerField(validators=[models.MinValueValidator(1), models.MaxValueValidator(5)], verbose_name='امتیاز')
    comment = models.TextField(null=True, blank=True, verbose_name='متن نظر')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'

    def __str__(self):
        return f"Review for Appointment {self.appointment.id} - Rating: {self.rating}"
    