# 🏥 سیستم نوبت‌دهی آنلاین پزشکان

پروژه‌ی بوت‌کمپ Quera — مدیریت و رزرو آنلاین نوبت‌های ویزیت پزشکان با معماری MVT جنگو.

## ✨ فیچرهای اصلی

### 🔐 سیستم احراز هویت پیشرفته
- **ثبت نام بدون رمز**: کاربران می‌توانند بدون تعیین رمز ثبت‌نام کنند؛ سیستم خودکار یک رمز محفوظ برای آنها ایجاد می‌کند
- **تایید دو مرحله‌ای (OTP)**:
  - ✉️ ارسال کد تایید از طریق **ایمیل**
  - 📱 ارسال کد تایید از طریق **پیامک (SMS)**
- **لاگین با گوگل**: یکپارچگی با Google OAuth برای ورود سریع و امن
- **مدیریت پروفایل**: سفارشی‌سازی اطلاعات کاربری و عکس پروفایل

### 👨‍⚕️ داشبورد دکتر
داشبورد جامع برای دکترها شامل:
- 📊 **نمایش درآمد**: مجموع درآمد و تفکیک تراکنش‌ها
- ⭐ **مدیریت نظرات و امتیازات**: مشاهده و پاسخ به نظرات بیماران
- 🕐 **تعیین ساعات کاری**: تعریف روزهای کاری و ساعات دسترسی
- 📅 **مدیریت نوبت‌ها**: مشاهده نوبت‌های رزرو شده و لغو‌شده
- 👥 **نمایش اطلاعات بیماران**: جزئیات بیمار برای هر نوبت

### 🗓️ مدیریت ذکی TimeSlots
- **ایجاد خودکار نوبت‌های خالی**: بر اساس ساعات کاری تعریف‌شده
- **حذف خودکار TimeSlots منقضی**: 
  - ✅ هر ساعت از طریق **Celery Task** اجرا می‌شود
  - 🧹 نوبت‌های گذشته به‌صورت خودکار از دیتابیس حذف می‌شوند
  - 📌 فقط نوبت‌های خالی (رزرو نشده) حذف می‌شوند

### 💳 سیستم پرداخت و کیف پول
- **کیف پول الکترونیک**: شارژ و کسر موجودی برای بیماران
- **تاریخچه تراکنش‌ها**: مشاهده دقیق تمام تراکنش‌ها
- **رزرو امن نوبت**: کسر هزینه با تراکنش درون‌سیستمی

### 📋 سیستم نقاشی و نوبت‌ها
- **رزرو نوبت آنلاین**: انتخاب دکتر، تخصص و زمان مناسب
- **لغو نوبت**: لغو نوبت‌های رزرو شده (تا ۲۴ ساعت قبل)
- **نظرات و امتیازات**: ثبت نظر بیماران پس از ویزیت

## 🏗️ ساختار اپ‌ها

| اپ | مسئولیت | کلیدی ترین مدل‌ها |
|---|---|---|
| **`accounts`** | احراز هویت، ثبت‌نام، OTP و پروفایل کاربر | `User` (سفارشی)، `OTPToken` |
| **`doctors`** | مدیریت دکترها و ساعات کاری | `Doctor`، `Specialty`، `WorkingHour`، `TimeSlot` |
| **`patients`** | مدیریت بیماران و اطلاعات شخصی | `Patient` |
| **`payments`** | کیف پول و تراکنش‌ها | `Wallet`، `Transaction` |
| **`appointments`** | نوبت‌ها و منطق رزرو/لغو | `Appointment` |
| **`reviews`** | نقاشی و امتیازات دکترها | `Review` |
| **`sms`** | ارسال SMS و OTP | Backend مختلف برای SMS |

نمودار ERD در `documents/ERD.png` قرار دارد.

## 🛠️ تکنولوژی و فریم‌ورک‌ها

### بک‌اند
- **Django 4.2+**: فریم‌ورک وب پایتون
- **Django REST Framework**: برای API (اگر مورد نیاز)
- **django-allauth**: احراز هویت و OAuth (گوگل)
- **Celery + Redis**: تسک‌های ناهمزمان و حذف خودکار TimeSlots
- **PostgreSQL / SQLite**: پایگاه داده

### فرانت‌اند
- **HTML5 / CSS3**: الگوها و استایل‌ها
- **Bootstrap / Tailwind CSS**: طراحی responsive
- **JavaScript**: تعامل کاربری

### دیپلویمنت
- **Docker & Docker Compose**: کنتینرایزاسیون
- **Gunicorn**: سرور WSGI
- **Nginx**: reverse proxy

## 📋 نیازمندی‌های سیستم

- **Python 3.9+**
- **pip** و **venv**
- **PostgreSQL 12+** (اختیاری - SQLite برای توسعه کافیست)
- **Redis** (برای Celery)
- **Docker** (پیشنهادی)

## ⚙️ تنظیمات: توسعه (dev) در برابر پروداکشن (production)

`config/settings/` یک پکیج است، نه یک فایل:
```
config/settings/
├── base.py         # مشترک بین هر دو محیط
├── dev.py          # DEBUG=True، SQLite، ایمیل/پیامک کنسول
└── production.py   # DEBUG=False، Postgres اجباری، HTTPS/HSTS، ایمیل و پیامک واقعی
```
سوییچ بین این دو فقط با متغیر محیطی `DJANGO_SETTINGS_MODULE` انجام می‌شود
(در `.env`):
```bash
DJANGO_SETTINGS_MODULE=config.settings.dev          # پیش‌فرض توسعه
DJANGO_SETTINGS_MODULE=config.settings.production    # پروداکشن
```
`docker-compose.yml` همیشه `production` را صریح ست می‌کند (نیازی به تغییر
دستی نیست). اگر بدون Docker و بدون تنظیم این متغیر اجرا کنید، پیش‌فرض `dev`
فعال می‌شود.

⚠️ `config.settings.production` عمداً برای `SECRET_KEY`، `ALLOWED_HOSTS` و
اطلاعات دیتابیس مقدار پیش‌فرض ندارد — اگر در `.env` ست نشوند، اجرا با خطا
متوقف می‌شود (به‌جای بالاآمدن ناامن با مقادیر توسعه).

### متغیرهای محیطی اساسی

```bash
# احراز هویت گوگل (برای OAuth)
GOOGLE_OAUTH_CLIENT_ID=your_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret

# تنظیمات ایمیل (برای OTP و اطلاع‌رسانی)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# تنظیمات SMS (برای OTP)
SMS_API_KEY=your_sms_provider_api_key
SMS_FROM_NUMBER=your_sender_number

# Celery و Redis (برای تسک‌های ناهمزمان)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# دیتابیس PostgreSQL (پروداکشن)
DB_NAME=clinic_db
DB_USER=clinic_user
DB_PASSWORD=strong_password
DB_HOST=localhost
DB_PORT=5432
```

## 🔄 تسک‌های خودکار (Celery)

### حذف خودکار TimeSlots منقضی
```python
# هر ساعت اجرا می‌شود
tasks.delete_expired_timeslots()
```
این تسک:
- ✅ تمام `TimeSlot`های که زمان آنها گذشته است را پیدا می‌کند
- ✅ فقط نوبت‌های **خالی** (رزرو نشده) حذف می‌شود
- ✅ نوبت‌های رزرو شده محفوظ می‌ماند
- ✅ هر ساعت خودکار اجرا می‌شود

### راه‌اندازی Celery
```bash
# شروع Celery Worker
celery -A clinic_appointment_system worker -l info

# شروع Celery Beat (برای تسک‌های دوره‌ای)
celery -A clinic_appointment_system beat -l info
```

## 🚀 راه‌اندازی با Docker (روش پیشنهادی)

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

## 👨‍⚕️ داشبورد دکتر - راهنمای استفاده

### دسترسی
- **URL**: `http://localhost:8000/doctor/dashboard/`
- **نیاز دارد**: ورود به عنوان دکتر

### بخش‌های اصلی

#### 📊 درآمد و مالی
- **مجموع درآمد**: کل پول دریافتی از تمام نوبت‌های پزشکی
- **آخرین تراکنش‌ها**: فهرست ۱۰ آخرین پرداخت
- **تفکیک درآمد**: بر اساس تاریخ/نوع ویزیت

#### ⭐ نقاشی و امتیازات
- **میانگین امتیاز**: نمایش رتبه‌ی کلی دکتر (۱ تا ۵ ستاره)
- **تعداد نقاشی**: کل نقاشی‌های دریافتی
- **دیدگاه‌های اخیر**: نمایش ۵ آخرین نظر با جزئیات

#### 🕐 ساعات کاری
- **افزودن ساعات**: تعیین روزهای کاری و ساعات شروع/پایان
- **ویرایش ساعات**: تغییر ساعات قبلی
- **نوبت‌های خودکار**: سیستم خودکار TimeSlot‌های خالی را برای شما ایجاد می‌کند

#### 📅 مدیریت نوبت‌ها
- **نوبت‌های پیش‌رو**: لیست نوبت‌های آینده
- **نوبت‌های گذشته**: تاریخچه ویزیت‌های انجام‌شده
- **لغو نوبت**: امکان لغو در صورت ضرورت

#### 👥 اطلاعات بیماران
- **نام و شماره تلفن**: تماس با بیمار
- **سابقه ویزیت‌ها**: مشاهده نوبت‌های قبلی هر بیمار

## 📱 سیستم OTP و احراز هویت

### روش ثبت‌نام و ورود
1. **کاربر شماره تلفن/ایمیل را وارد می‌کند**
2. **سیستم کد OTP را ارسال می‌کند**:
   - 📧 **Email OTP**: برای ایمیل
   - 📱 **SMS OTP**: برای شماره تلفن
3. **کاربر کد را تایید می‌کند**
4. **سیستم خودکار یک رمز محفوظ ایجاد می‌کند** (بدون اینکه کاربر نیاز داشته باشد)
5. **اکاونت ایجاد و فعال می‌شود**

### تنظیم OTP
- **مدت زمان اعتبار OTP**: 10 دقیقه
- **طول کد**: 6 رقم
- **تعداد تلاش مجاز**: ۵ تلاش

### لاگین گوگل (OAuth)
```
1. کاربر روی "ورود با گوگل" کلیک می‌کند
2. Google OAuth dialog باز می‌شود
3. کاربر اکاونت گوگل خود را انتخاب می‌کند
4. حساب کاربری خودکار ایجاد/تایید می‌شود
5. کاربر وارد سیستم می‌شود
```

## 🖥️ راه‌اندازی بدون Docker (توسعه لوکال)

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

## 📁 ساختار پروژه

```
clinic_appointment_system/
├── accounts/                 # مدیریت اکاونت و احراز هویت
│   ├── models.py            # User سفارشی
│   ├── views.py             # ورود، ثبت‌نام، OTP
│   └── services.py          # کارهای OTP و کاربر
├── doctors/                  # مدیریت دکترها و ساعات کاری
│   ├── models.py            # Doctor, WorkingHour, TimeSlot
│   ├── views.py             # داشبورد و مدیریت ساعات
│   └── services.py          # تولید TimeSlot خودکار
├── appointments/            # رزرو و مدیریت نوبت‌ها
│   ├── models.py            # Appointment
│   └── views.py             # رزرو و لغو
├── patients/                # مدیریت بیماران
│   └── models.py            # Patient
├── payments/                # مدیریت پرداخت و کیف‌پول
│   ├── models.py            # Wallet, Transaction
│   └── views.py             # شارژ کیف‌پول
├── reviews/                 # نقاشی و امتیاز‌دهی
│   └── models.py            # Review
├── config/                  # تنظیمات Django
│   ├── settings/
│   │   ├── base.py         # تنظیمات مشترک
│   │   ├── dev.py          # تنظیمات توسعه
│   │   └── production.py    # تنظیمات پروداکشن
│   └── celery.py           # تنظیمات Celery
├── templates/              # الگوهای HTML
├── statics/                # فایل‌های CSS/JS
├── docker-compose.yml      # تنظیم Docker
├── Dockerfile              # ایمج Docker
├── requirements.txt        # نیازمندی‌های Python
└── manage.py               # خط فرمان Django
```

## 🧪 تست و QA

### اجرای تست‌ها
```bash
# تمام تست‌ها
pytest

# تست یک اپ مشخص
pytest patients/tests/

# تست با coverage
pytest --cov=.
```

### ابزارهای مورد استفاده
- **pytest**: فریم‌ورک تست
- **pytest-django**: پلاگین Django برای pytest


## 📚 مستندات اضافی

- **ERD Diagram**: `documents/ERD.png` - نمودار رابطه‌ی مدل‌ها
- **دستور کلی**: بررسی کنید `manage.py help`
- **مستندات Django**: https://docs.djangoproject.com/

## 🤝 مشارکت و بهبود

اگر ایراد یا پیشنهادی دارید:
1. Issue جدید باز کنید
2. یک pull request ارسال کنید
3. تغییرات را به‌تفصیل توضیح دهید

## 📄 لایسنس

این پروژه تحت لایسنس [MIT](LICENSE) است.

---