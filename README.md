# سیستم نوبت‌دهی آنلاین پزشکان

پروژه‌ی بوت‌کمپ Quera برای مدیریت و رزرو آنلاین نوبت‌های ویزیت پزشکان، با معماری MVT جنگو.

نمودار ERD در فایل `ERD.png` موجود است.

## امکانات

- ثبت‌نام و ورود با شماره تلفن یا ایمیل
- ورود سریع با کد یکبار مصرف (پیش‌فرض، بدون رمز عبور) یا با رمز عبور، برای بیمار و پزشک
- ورود با حساب گوگل برای بیماران
- صفحه‌ی ورود جداگانه برای پزشکان
- پروفایل کاربری با آواتار قابل‌تنظیم و تاریخ تولد شمسی برای بیماران
- ساخت حساب پزشک از پنل ادمین، شامل تخصص، شماره نظام پزشکی و هزینه‌ی ویزیت
- تعریف ساعات کاری پزشک و تولید خودکار نوبت‌های خالی
- جستجوی پزشک بر اساس نام یا تخصص
- رزرو و لغو نوبت با کسر و بازگشت خودکار از کیف‌پول
- ثبت نظر و امتیاز بیمار برای پزشک
- نمایش تاریخ‌ها به شمسی در تمام صفحات
- ارسال پیامک با بک‌اند قابل‌تعویض (کنسول، Kavenegar، ملی‌پیامک)
- ارسال ایمیل برای تاییدیه‌ی رزرو، بازیابی رمز عبور و تغییر ایمیل
- پردازش ناهمگام با Celery برای ارسال پیام‌ها و پاک‌سازی دوره‌ای نوبت‌های منقضی
- دستور مدیریتی برای ساخت داده‌ی نمونه با Faker
- تست‌های خودکار با pytest

## پشته‌ی فنی

Django 5.2، PostgreSQL، Redis، Celery، django-allauth، Gunicorn، nginx، WhiteNoise، jdatetime، Bootstrap 5

## ساختار اپ‌ها

| اپ | مسئولیت |
|---|---|
| accounts | کاربر، احراز هویت، پروفایل |
| doctors | پزشک، تخصص، ساعات کاری، نوبت‌های خالی |
| patients | بیمار، نوبت‌های من |
| payments | کیف‌پول و تراکنش‌ها |
| appointments | رزرو و لغو نوبت |
| reviews | نظر و امتیاز |
| common | ابزارهای مشترک بین اپ‌ها |

## تنظیمات

تنظیمات پروژه در `clinic_appointment_system/settings/` به سه بخش تقسیم شده:

- `base.py`: تنظیمات مشترک
- `dev.py`: محیط توسعه، SQLite، ایمیل و پیامک در کنسول
- `test.py`: مخصوص اجرای تست‌ها
- `production.py`: محیط نهایی، PostgreSQL، HTTPS، ایمیل و پیامک واقعی

انتخاب محیط با متغیر `DJANGO_SETTINGS_MODULE` در فایل `.env` انجام می‌شود:

```
DJANGO_SETTINGS_MODULE=clinic_appointment_system.settings.dev
DJANGO_SETTINGS_MODULE=clinic_appointment_system.settings.production
```

در `docker-compose.yml` این مقدار همیشه روی production تنظیم شده است. در
صورت اجرای بدون Docker و نبود این متغیر، محیط dev فعال می‌شود.

توجه: در تنظیمات production، مقادیر `SECRET_KEY`، `ALLOWED_HOSTS` و اطلاعات
دیتابیس مقدار پیش‌فرض ندارند و باید در `.env` تعیین شوند.

## راه‌اندازی با Docker

```bash
cp .env.example .env
docker compose up --build
```

این دستور سرویس‌های db، redis، web، nginx، celery_worker و celery_beat را
اجرا می‌کند. برای ساخت کاربر ادمین:

```bash
docker compose exec web python manage.py createsuperuser
```

آدرس پروژه پس از اجرا: `http://localhost`

توجه: تنظیمات nginx فعلاً بدون گواهی SSL است. اگر `SECURE_SSL_REDIRECT`
روی True باشد و SSL واقعی پیکربندی نشده باشد، سایت بالا نمی‌آید. تا آماده
شدن SSL، این مقدار را False بگذارید.

## راه‌اندازی بدون Docker

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

برای اجرای کارهای ناهمگام (اختیاری در محیط توسعه):

```bash
celery -A clinic_appointment_system worker -l info
celery -A clinic_appointment_system beat -l info
```

## متغیرهای محیطی

توضیح کامل متغیرها در فایل `.env.example` آمده است. مهم‌ترین‌ها:

| متغیر | کاربرد |
|---|---|
| DJANGO_SETTINGS_MODULE | انتخاب محیط dev یا production |
| SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS | تنظیمات امنیتی production |
| USE_SQLITE, DB_* | تنظیمات دیتابیس |
| EMAIL_* | ارسال ایمیل واقعی |
| GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET | ورود با گوگل |
| SMS_BACKEND, SMS_API_KEY, SMS_SENDER_LINE | تنظیمات پیامک |
| REDIS_URL | و کش celery  برای  Redis آدرس  |

### ورود با گوگل

۱. در Google Cloud Console یک OAuth Client ID از نوع Web application بسازید.
۲. آدرس بازگشت را برابر بگذارید با:
`https://<دامنه‌ی شما>/social-auth/google/login/callback/`
۳. مقادیر GOOGLE_CLIENT_ID و GOOGLE_CLIENT_SECRET را در `.env` قرار دهید.

### پیامک

بک‌اند پیامک با متغیر SMS_BACKEND قابل تغییر است:

| بک‌اند | کاربرد |
|---|---|
| sms.backends.console.ConsoleBackend | توسعه، چاپ در کنسول |
| sms.backends.locmem.LocmemBackend | تست خودکار |
| sms.backends.kavenegar.KavenegarBackend | پروداکشن |
| sms.backends.mellipayamak.MelliPayamakBackend | جایگزین پروداکشن |

برای افزودن پنل جدید، یک فایل مشابه در `sms/backends/` با متد send_message
ایجاد کنید.

## داده‌ی نمونه

```bash
python manage.py seed_demo_data
python manage.py seed_demo_data --specialties 8 --doctors 12 --patients 30 --appointments 40 --password Test1234
```

## ساخت حساب پزشک

حساب پزشک فقط از پنل ادمین ساخته می‌شود:

۱. وارد `/admin/` شوید و از بخش Doctors گزینه‌ی Add Doctor را انتخاب کنید.
۲. شماره تلفن، ایمیل، نام، تخصص، شماره نظام پزشکی و هزینه‌ی ویزیت را وارد
کنید. رمز عبور اختیاری است و در صورت خالی‌بودن به‌صورت خودکار ساخته می‌شود.
۳. اطلاعات ورود برای پزشک از طریق پیامک و ایمیل ارسال می‌شود.
۴. پزشک از آدرس `/doctors/login/` یا با کد یکبار مصرف از
`/doctors/login/otp/` وارد می‌شود.

## تست‌ها

```bash
pytest
pytest doctors/
pytest -v -k login
```

تنظیمات تست مستقل از محیط توسعه است و از پایگاه‌داده‌ی SQLite در حافظه
استفاده می‌کند؛ ایمیل و پیامک در این محیط ارسال واقعی ندارند.

## لایسنس

 .را ببینید MIT فایل لایسنس 
