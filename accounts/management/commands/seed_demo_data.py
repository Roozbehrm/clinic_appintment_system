import random
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from accounts.models import User, Profile
from doctors.models import Specialty, Doctor, WorkingHour
from doctors.services import generate_time_slots
from patients.models import Patient
from payments.models import Wallet
from appointments.services import book_appointment
from reviews.models import Review

SPECIALTY_POOL = [
    "قلب و عروق", "پوست و مو", "گوش و حلق و بینی", "ارتوپدی", "چشم‌پزشکی",
    "زنان و زایمان", "اطفال", "روانپزشکی", "داخلی", "مغز و اعصاب",
    "ارولوژی", "دندانپزشکی",
]


class Command(BaseCommand):
    help = "با استفاده از Faker، داده‌ی نمونه (پزشک، بیمار، نوبت، نظر و ...) برای تست تولید می‌کند."

    def add_arguments(self, parser):
        parser.add_argument("--specialties", type=int, default=6, help="تعداد تخصص‌ها")
        parser.add_argument("--doctors", type=int, default=12, help="تعداد پزشکان")
        parser.add_argument("--patients", type=int, default=20, help="تعداد بیماران")
        parser.add_argument("--appointments", type=int, default=25, help="تعداد نوبت‌های رزروشده")
        parser.add_argument("--password", type=str, default="Password123",
                             help="رمز عبور یکسان برای همه‌ی کاربران نمونه")

    def handle(self, *args, **options):
        self.faker = Faker("fa_IR")
        self.password = options["password"]
        self._used_phones = set(User.objects.values_list("phone_number", flat=True))
        self._used_mccs = set(Doctor.objects.values_list("mcc", flat=True))

        with transaction.atomic():
            specialties = self._create_specialties(options["specialties"])
            doctors = self._create_doctors(options["doctors"], specialties)
            patients = self._create_patients(options["patients"])
            self._create_appointments_and_reviews(options["appointments"], doctors, patients)

        self.stdout.write(self.style.SUCCESS(
            f"انجام شد: {len(specialties)} تخصص، {len(doctors)} پزشک، "
            f"{len(patients)} بیمار، رمز عبور همه: {self.password}"
        ))

    def _unique_phone(self):
        while True:
            phone = f"09{random.randint(100000000, 999999999)}"
            if phone not in self._used_phones:
                self._used_phones.add(phone)
                return phone

    def _unique_mcc(self):
        while True:
            mcc = str(random.randint(10000, 99999))
            if mcc not in self._used_mccs:
                self._used_mccs.add(mcc)
                return mcc

    def _create_specialties(self, count):
        names = SPECIALTY_POOL[:count] if count <= len(SPECIALTY_POOL) else SPECIALTY_POOL
        specialties = []
        for name in names:
            specialty, _ = Specialty.objects.get_or_create(
                name=name, defaults={"description": self.faker.sentence()})
            specialties.append(specialty)
        return specialties

    def _create_doctors(self, count, specialties):
        doctors = []
        for _ in range(count):
            phone = self._unique_phone()
            user = User.objects.create(phone_number=phone, email=self.faker.unique.email(), is_verified=True)
            user.set_password(self.password)
            user.save()

            profile = Profile.objects.create(
                user=user,
                full_name=self.faker.name(),
                gender=random.choice(["male", "female"]),
                national_code=str(random.randint(1000000000, 9999999999)),
                address=self.faker.address(),
            )

            doctor = Doctor.objects.create(
                profile=profile,
                specialty=random.choice(specialties),
                mcc=self._unique_mcc(),
                bio=self.faker.paragraph(nb_sentences=3),
                consultation_fee=random.choice(range(150000, 800000, 50000)),
                is_active=True,
            )


            chosen_days = random.sample(range(0, 7), k=random.randint(2, 4))
            for day in chosen_days:
                start_hour = random.choice([8, 9, 14, 16])
                WorkingHour.objects.create(
                    doctor=doctor,
                    day_of_week=day,
                    start_time=f"{start_hour:02d}:00",
                    end_time=f"{start_hour + 4:02d}:00",
                    slot_duration_minutes=random.choice([15, 20, 30]),
                )

            generate_time_slots(doctor, days_ahead=14)
            doctors.append(doctor)
        return doctors

    def _create_patients(self, count):
        patients = []
        for _ in range(count):
            phone = self._unique_phone()
            user = User.objects.create(phone_number=phone, email=self.faker.unique.email(), is_verified=True)
            user.set_password(self.password)
            user.save()

            profile = Profile.objects.create(
                user=user,
                full_name=self.faker.name(),
                gender=random.choice(["male", "female"]),
                national_code=str(random.randint(1000000000, 9999999999)),
                address=self.faker.address(),
            )

            patient = Patient.objects.create(
                profile=profile,
                birth_date=date(1980, 1, 1) + timedelta(days=random.randint(0, 15000)),
            )
            Wallet.objects.create(patient=patient, balance=random.choice(range(300000, 5000000, 100000)))
            patients.append(patient)
        return patients

    def _create_appointments_and_reviews(self, count, doctors, patients):
        created = 0
        reviewed = 0
        attempts = 0
        max_attempts = count * 5

        while created < count and attempts < max_attempts:
            attempts += 1
            doctor = random.choice(doctors)
            free_slot = doctor.time_slots.filter(status="free").order_by("?").first()
            if not free_slot:
                continue
            patient = random.choice(patients)

            try:
                appointment = book_appointment(patient, free_slot.id)
            except ValidationError:
                continue

            created += 1

            if random.random() < 0.7:
                appointment.status = "completed"
                appointment.save()
                if random.random() < 0.7:
                    Review.objects.get_or_create(
                        appointment=appointment,
                        defaults={
                            "rating": random.randint(3, 5),
                            "comment": self.faker.sentence(),
                        },
                    )
                    reviewed += 1

        self.stdout.write(f"{created} نوبت ساخته شد، {reviewed} مورد با نظر ثبت‌شده.")
