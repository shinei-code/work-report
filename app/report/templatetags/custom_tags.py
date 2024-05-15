from django import template
from datetime import date, timedelta
import calendar
import json
from datetime import date, datetime, time
from decimal import Decimal
from django.utils.safestring import mark_safe

register = template.Library()

# date, datetime, time, decimalの変換関数
def json_serial(obj):
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError ("Type %s not serializable" % type(obj))

@register.simple_tag
def queryset_to_json(queryset, *fields):
    ary = list(queryset.values(*fields))
    json_ary = json.dumps(ary, ensure_ascii=False, default=json_serial)
    return mark_safe(json_ary)

# その月（引数）のカレンダー生成
# ex. ['2024/4/1', '2024/4/2', ... '2024/4/30']
@register.filter
def make_calendar(year_month):
    # if type(year_month) != str:
    #     year_month = str(year_month)

    year = int(year_month[:4])
    month = int(year_month[4:])
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    month = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]
    return month

@register.filter
def get_report(reports, day):
    for report in reports:
        if report.work_dt == day:
            return report

@register.filter
def holiday(day):
    holiday = None
    if day.weekday() == 5:
        holiday = 'saturday'
    elif day.weekday() == 6:
        holiday = 'sunday'
    return holiday

@register.filter
def prev_month(year_month):
    # if type(year_month) != str:
    #     year_month = str(year_month)

    year = int(year_month[:4])
    month = int(year_month[4:])

    # 前月
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    return f"{prev_year}{str(prev_month).zfill(2)}"

@register.filter
def next_month(year_month):
    # if type(year_month) != str:
    #     year_month = str(year_month)

    year = int(year_month[:4])
    month = int(year_month[4:])

    # 翌月
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1

    return f"{next_year}{str(next_month).zfill(2)}"

@register.filter
def class_button(theme):
    return f'btn btn-sm btn-outline-{theme} rounded-pill text-nowrap'

@register.filter
def format_time(time_text):
    return time_text.strftime('%H:%M') if time_text else ""