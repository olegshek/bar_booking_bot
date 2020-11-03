from django.utils import timezone

from apps.bot.tortoise_models import WorkingHours


async def order_datetime(date):
    now = timezone.now().astimezone()
    working_time = (await WorkingHours.first()).start_time
    book_time = (now + timezone.timedelta(minutes=60)).time()

    if date == now.date() and book_time >= working_time:
        res_time = book_time
    else:
        res_time = working_time
    return timezone.datetime.strptime(str(date) + str(res_time).split('.')[0], '%Y-%m-%d%H:%M:%S').astimezone()