from django.utils import timezone

from apps.bot.tortoise_models import WorkingHours


async def today_end_datetime(date):
    working_hours = await WorkingHours.first()

    end_datetime = timezone.datetime.combine(
        date,
        working_hours.end_time
    )

    if end_datetime.time() < working_hours.start_time:
        end_datetime += timezone.timedelta(days=1)

    return end_datetime


async def order_datetime(date):
    now = timezone.now().astimezone()
    working_hours = await WorkingHours.first()
    end_datetime = await today_end_datetime(date)

    book_time_datetime = (now + timezone.timedelta(minutes=60)).replace(tzinfo=None)

    res_datetime = book_time_datetime

    if date == now.date() and book_time_datetime >= end_datetime:
        res_datetime = end_datetime

    if date != now.date():
        res_datetime = timezone.datetime.combine(
            date,
            working_hours.start_time
        )

    return res_datetime
