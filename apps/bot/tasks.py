from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
from django.utils import timezone
from telebot import types, TeleBot

from apps.bot.models import WorkingHours, SeatsManager, KeyboardButtonsOrdering, Message
from apps.customer.models import BookRequest


bot = TeleBot(settings.TELEGRAM_TOKEN)


def feedback_choice(locale, request_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    for keyboard_button in KeyboardButtonsOrdering.objects.filter(keyboard__name='feedback').order_by('ordering'):
        button = keyboard_button.button
        keyboard.add(types.InlineKeyboardButton(
            getattr(button, f'text_{locale}'),
            callback_data=f'{button.name};{request_id}')
        )

    return keyboard


@periodic_task(run_every=crontab(minute='*'), name='renew_additional_seats', ignore_result=True)
def renew_additional_seats():
    if WorkingHours.objects.first().end_time < timezone.now().astimezone().time():
        SeatsManager.objects.update(additional_seats_number=0)


@periodic_task(run_every=crontab(hour=7, minute=0), name='send_feedback', ignore_result=True)
def send_feedback():
    today = timezone.now().date()
    book_requests = BookRequest.objects.filter(
        datetime__date__gte=today - timezone.timedelta(days=1),
        datetime__lte=today,
        confirmed_at__isnull=False
    )

    for request in book_requests:
        user = request.customer
        locale = user.language

        text = getattr(Message.objects.get(title='feedback_choice'), f'text_{locale}')
        bot.send_message(user.id, text, reply_markup=feedback_choice(locale, request.book_id))
