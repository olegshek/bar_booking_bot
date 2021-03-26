from django.utils import timezone

from apps.bot.tortoise_models import WorkingHours


async def order_time(date):
    now = timezone.now().astimezone()
    working_hours = await WorkingHours.first()
    book_time_datetime = (now + timezone.timedelta(hours=1)).replace(tzinfo=None)
    book_time = book_time_datetime.time().replace(minute=0, second=0)
    start_time = working_hours.start_time
    end_time = working_hours.end_time

    start_datetime = timezone.datetime.combine(date, start_time)
    end_datetime = timezone.datetime.combine(date, end_time)

    if date != now.date():
        if end_time < start_time and (end_datetime - timezone.timedelta(hours=1)).date() != date:
            return (end_datetime - timezone.timedelta(hours=1)).time().replace(minute=0, second=0)

        if start_time.minute:
            start_time = (start_datetime + timezone.timedelta(hours=1)).time()
            return start_time.replace(minute=0, second=0)

    if end_time < start_time and (end_datetime - timezone.timedelta(hours=1)).date() == date:
        return (end_datetime - timezone.timedelta(hours=1)).time().replace(minute=0, second=0)

    if (end_datetime - timezone.timedelta(minutes=40)).time() < book_time < start_time:
        book_time = start_time
    else:
        if book_time < start_time:
            book_time = start_time

        if book_time > end_time:
            book_time = None

    if book_time and book_time.minute:
        book_time = (timezone.datetime.combine(date, book_time) + timezone.timedelta(hours=1)).time()
        book_time = book_time.replace(minute=0, second=0, microsecond=0)

    return book_time
