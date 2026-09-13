#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    # اگر DJANGO_SETTINGS_MODULE در .env یا متغیرهای محیطی ست شده باشد
    # (مثلاً config.settings.production)، همان استفاده می‌شود؛ در غیر این
    # صورت پیش‌فرض توسعه (dev) فعال می‌شود.
    try:
        from decouple import config
        settings_module = config("DJANGO_SETTINGS_MODULE", default="clinic_appointment_system.settings.dev")
    except ImportError:
        settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "clinic_appointment_system.settings.dev")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

