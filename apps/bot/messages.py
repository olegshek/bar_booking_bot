from datetime import datetime

from django.utils import timezone

from apps.bot.tortoise_models import Message


async def get_message(title, locale):
    return getattr(await Message.get(title=title), f'text_{locale}')


async def book_message(title, locale, book_request, local_datetime):
    next_datetime = local_datetime + timezone.timedelta(hours=1)
    return (await get_message(title, locale)) % {
        'book_id': book_request.book_id,
        'date': str(local_datetime.date()),
        'time': f"{datetime.strftime(local_datetime, '%H:%M')} - {datetime.strftime(next_datetime, '%H:%M')}",
        'people_quantity': str(book_request.people_quantity)
    }
