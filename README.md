# سیستم نوبت‌دهی آنلاین پزشکان

پروژه‌ی بوت‌کمپ Quera — مدیریت و رزرو آنلاین نوبت‌های ویزیت پزشکان با معماری MVT جنگو.

## ساختار اپ‌ها

| اپ | مسئولیت |
|---|---|
| `accounts` | User سفارشی (ورود با شماره تلفن)، OTP، Profile |
| `doctors` | Specialty، Doctor، WorkingHour، TimeSlot و تولید خودکار نوبت خالی |
| `patients` | Patient، ویو نوبت‌های من، context processor موجودی کیف پول |
| `payments` | Wallet، Transaction، شارژ و کسر کیف‌پول |
| `appointments` | Appointment و منطق رزرو/لغو نوبت (تراکنشی و امن) |
| `reviews` | Review و امتیازدهی به پزشک پس از ویزیت |

نمودار ERD در `documents/ERD.png` قرار دارد.

## تنظیمات: توسعه (dev) در برابر پروداکشن (production)

`config/settings/` یک پکیج است، نه یک فایل:
```
config/settings/
├── base.py         # مشترک بین هر دو محیط
├── dev.py          # DEBUG=True، SQLite، ایمیل/پیامک کنسول
└── production.py   # DEBUG=False، Postgres اجباری، HTTPS/HSTS، ایمیل و پیامک واقعی
```
سوییچ بین این دو فقط با متغیر محیطی `DJANGO_SETTINGS_MODULE` انجام می‌شود
(در `.env`):
```
DJANGO_SETTINGS_MODULE=config.settings.dev          # پیش‌فرض توسعه
DJANGO_SETTINGS_MODULE=config.settings.production    # پروداکشن
```
`docker-compose.yml` همیشه `production` را صریح ست می‌کند (نیازی به تغییر
دستی نیست). اگر بدون Docker و بدون تنظیم این متغیر اجرا کنید، پیش‌فرض `dev`
فعال می‌شود.

⚠️ `config.settings.production` عمداً برای `SECRET_KEY`، `ALLOWED_HOSTS` و
اطلاعات دیتابیس مقدار پیش‌فرض ندارد — اگر در `.env` ست نشوند، اجرا با خطا
متوقف می‌شود (به‌جای بالاآمدن ناامن با مقادیر توسعه).

## راه‌اندازی با Docker (روش پیشنهادی)

```bash
cp .env.example .env
# مقادیر .env را (به‌خصوص SECRET_KEY) ویرایش کنید
docker compose up --build
```

سپس یک بار کاربر ادمین بسازید:
```bash
docker compose exec web python manage.py createsuperuser
```

پروژه روی `http://localhost:8000` بالا می‌آید.

## راه‌اندازی بدون Docker (توسعه لوکال)

> ⚠️ چون فیلد `email` روی مدل `User` از حالت اختیاری به «اجباری و یکتا»
> تغییر کرده، اگر از قبل دیتابیس (`db.sqlite3`) با رکوردهای بدون ایمیل
> دارید، مایگریشن ممکن است خطا بدهد. ساده‌ترین راه در محیط توسعه: فایل
> `db.sqlite3` را حذف کنید و از صفر `makemigrations`/`migrate` بزنید.

1. ساخت محیط مجازی و نصب پکیج‌ها:
   ```bash
   python -m venv venv
   source venv/bin/activate   # ویندوز: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. فایل `.env` را از روی `.env.example` بسازید:
   ```bash
   cp .env.example .env
   ```
   به‌صورت پیش‌فرض `USE_SQLITE=True` است، یعنی نیازی به نصب/تنظیم Postgres نیست و
   دیتابیس به‌صورت فایل `db.sqlite3` ساخته می‌شود — برای توسعه و تست سریع کافیست.
   اگر می‌خواهید از Postgres واقعی استفاده کنید، `USE_SQLITE=False` بگذارید و
   `DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT` را مطابق دیتابیسی که خودتان
   روی سیستم ساخته‌اید (و رمز عبورش را می‌دانید) پر کنید.
3. مایگریشن و اجرا:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```
