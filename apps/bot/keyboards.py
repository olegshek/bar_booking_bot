from aiogram import types
from django.utils import timezone

from apps.bot.tortoise_models import Button, KeyboardButtonsOrdering, WorkingHours
from apps.customer.tortoise_models import Gender

checkout_emoji = {
    'PICKUP': '🏃‍♂️',
    'DELIVERY': '🚘'
}


def generate_time_button(date, book_time):
    next_book_time = (timezone.datetime.combine(date, book_time) + timezone.timedelta(hours=1)).time()
    button = types.InlineKeyboardButton(
        f"{book_time.strftime('%H:%M')} - {next_book_time.strftime('%H:%M')}",
        callback_data=f'time;{book_time}'
    )
    return next_book_time, button


async def get_back_button_obj():
    return await Button.get(name='back')


async def language_choice(locale='ru', change=False):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    buttons = []
    for keyboard_button in await KeyboardButtonsOrdering.filter(keyboard__name='language_choice').order_by(
            'ordering'):
        button = await keyboard_button.button
        button_name = button.name
        buttons.append(types.InlineKeyboardButton(
            button.text_ru if button_name == 'ru' else button.text_uz if button_name == 'uz' else button.text_en
        ))

    if change:
        back_button_obj = await get_back_button_obj()
        buttons.append(types.KeyboardButton(getattr(back_button_obj, f'text_{locale}')))

    keyboard.add(*buttons)
    return keyboard


async def main_menu(locale):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    for keyboard_button in await KeyboardButtonsOrdering.filter(keyboard__name='main_menu').order_by('ordering'):
        button = await keyboard_button.button
        keyboard.add(types.KeyboardButton(getattr(button, f'text_{locale}')))

    return keyboard


async def phone_number(locale):
    back_button_obj = await get_back_button_obj()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    for keyboard_button in await KeyboardButtonsOrdering.filter(keyboard__name='phone_number').order_by('ordering'):
        button = await keyboard_button.button
        keyboard.add(types.KeyboardButton(
            getattr(button, f'text_{locale}'),
            request_contact=True if button.name == 'phone_number' else None
        ))
    keyboard.add(types.KeyboardButton(getattr(back_button_obj, f'text_{locale}')))
    return keyboard


async def gender(locale):
    back_button_obj = await get_back_button_obj()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    for gender_name in await Gender.all().values_list(f'text_{locale}', flat=True):
        keyboard.add(types.KeyboardButton(gender_name))

    keyboard.add(getattr(back_button_obj, f'text_{locale}'))
    return keyboard


async def people_quantity(locale):
    back_button_obj = await get_back_button_obj()
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=4)

    buttons = []
    for i in range(1, 5):
        buttons.append(types.InlineKeyboardButton(str(i), callback_data=str(i)))
    keyboard.row(*buttons)

    keyboard.add(
        types.InlineKeyboardButton(getattr(back_button_obj, f'text_{locale}'), callback_data=back_button_obj.name))
    return keyboard


async def time_choice(date, locale):
    now = timezone.now().astimezone()
    now_time = now.time().replace(tzinfo=None)

    keyboard = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_button_obj = await get_back_button_obj()

    working_hours = await WorkingHours.first()
    start_time = working_hours.start_time
    end_time = working_hours.end_time
    end_datetime = timezone.datetime.combine(date, end_time)

    last_book_time = (end_datetime - timezone.timedelta(hours=1)).time()

    buttons = []

    if date != now.date():
        if start_time > end_time and end_time.hour > 0:
            book_time = now_time.replace(hour=0, minute=0, second=0, microsecond=0)

            while book_time <= last_book_time:
                next_book_time, button = generate_time_button(date, book_time)
                buttons.append(button)
                book_time = next_book_time

            book_time = start_time.replace(minute=0, second=0)

            while book_time.hour > 0:
                next_book_time, button = generate_time_button(date, book_time)
                buttons.append(button)
                book_time = next_book_time

        else:
            book_time = start_time.replace(minute=0, second=0)

            zero_exists = False
            while book_time <= last_book_time:
                if book_time.hour == 0 and zero_exists:
                    break

                next_book_time, button = generate_time_button(date, book_time)
                buttons.append(button)
                book_time = next_book_time

                if book_time.hour == 0:
                    zero_exists = True

    else:
        if start_time > end_time and end_time.hour > 0:
            if now_time < start_time or now_time <= last_book_time:
                book_time = (
                        timezone.datetime.combine(date, now_time) +
                        timezone.timedelta(hours=1)
                ).replace(minute=0, second=0, microsecond=0).time()

                while book_time <= last_book_time:
                    next_book_time, button = generate_time_button(date, book_time)
                    buttons.append(button)
                    book_time = next_book_time

                book_time = start_time.replace(minute=0, second=0)

                while book_time.hour > 0:
                    next_book_time, button = generate_time_button(date, book_time)
                    buttons.append(button)
                    book_time = next_book_time

            else:
                book_time = (
                        timezone.datetime.combine(date, now_time) +
                        timezone.timedelta(hours=1)
                ).replace(minute=0, second=0, microsecond=0).time()

                while book_time <= last_book_time:
                    next_book_time, button = generate_time_button(date, book_time)
                    buttons.append(button)
                    book_time = next_book_time

        else:
            book_time = now_time.replace(minute=0, second=0, microsecond=0) if now_time > start_time else start_time
            zero_exists = False
            while book_time <= last_book_time:
                if book_time.hour == 0 and zero_exists:
                    break

                next_book_time, button = generate_time_button(date, book_time)
                buttons.append(button)
                book_time = next_book_time

                if book_time.hour == 0:
                    zero_exists = True

    keyboard.add(*buttons)

    keyboard.add(types.InlineKeyboardButton(
        getattr(back_button_obj, f'text_{locale}'),
        callback_data=back_button_obj.name)
    )
    return keyboard


async def accept_keyboard(locale):
    keyboard = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_button_obj = await get_back_button_obj()
    accept_button = await Button.get(name='accept')

    keyboard.add(types.InlineKeyboardButton(getattr(accept_button, f'text_{locale}'), callback_data=accept_button.name))
    keyboard.add(types.InlineKeyboardButton(
        getattr(back_button_obj, f'text_{locale}'),
        callback_data=back_button_obj.name)
    )

    return keyboard


async def back_keyboard(locale):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = await get_back_button_obj()
    keyboard.add(types.KeyboardButton(getattr(button, f'text_{locale}')))
    return keyboard


async def cancel_keyboard(locale):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = await Button.get(name='cancel')
    keyboard.add(types.KeyboardButton(getattr(button, f'text_{locale}')))
    return keyboard


remove_keyboard = types.ReplyKeyboardRemove()
