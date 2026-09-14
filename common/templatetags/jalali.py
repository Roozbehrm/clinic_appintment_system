import jdatetime

from django import template


register = template.Library()


@register.filter
def to_jalali(value):
    if not value:
        return ""

    if hasattr(value, "date"):
        value = value.date()

    jalali_date = jdatetime.date.fromgregorian(
        date=value
    )

    return jalali_date.strftime("%Y/%m/%d")