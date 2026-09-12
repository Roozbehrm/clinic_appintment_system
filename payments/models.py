from django.db import models
from patients.models import Patient


class Wallet(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField("موجودی", max_digits=12, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "کیف پول"
        verbose_name_plural = "کیف‌های پول"

    def __str__(self):
        return f"کیف پول {self.patient}"


class Transaction(models.Model):
    TYPE_CHOICES = [("deposit", "واریز"), ("payment", "پرداخت"), ("refund", "بازگشت وجه")]
    STATUS_CHOICES = [("pending", "در انتظار"), ("success", "موفق"), ("failed", "ناموفق")]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions", verbose_name="کیف پول")
    appointment = models.ForeignKey("appointments.Appointment", on_delete=models.SET_NULL,
null=True, blank=True, related_name="transactions", verbose_name="نوبت")
    amount = models.DecimalField( max_digits=12, decimal_places=0, verbose_name="مبلغ")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="نوع")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="success", verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount} - {self.wallet.patient}"
