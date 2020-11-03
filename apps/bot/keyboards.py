import math

from aiogram import types
from django.utils import timezone

from apps.bot import utils
from apps.bot.tortoise_models import Button, KeyboardButtonsOrdering, WorkingHours
from apps.customer.tortoise_models import Gender

checkout_emoji = {
    'PICKUP': '🏃‍♂️',
    'DELIVERY': '🚘'
}


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


async def time_choice(date, locale, option=None, time_type=None, time_data=None):
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    accept_button = await Button.get(name='accept')
    back_button_obj = await get_back_button_obj()

    order_datetime = await utils.order_datetime(date)
    order_time = order_datetime.time()

    if all([option, time_type, time_data]):
        datetime_data = timezone.datetime.strptime(str(date) + str(time_data), "%Y-%m-%d%H:%M:%S")
        new_timedelta = timezone.timedelta(hours=1) if time_type == 'hour' else timezone.timedelta(minutes=30)
        new_order_time = ((datetime_data + new_timedelta) if option == 'plus' else (datetime_data - new_timedelta))

        end_time = (await WorkingHours.first()).end_time
        if new_order_time >= order_datetime and \
                new_order_time.time() <= (
                timezone.datetime.strptime(str(end_time), '%H:%M:%S') - timezone.timedelta(hours=1)
        ).time():
            order_time = new_order_time.time()

    time_types = {
        0: 'hour',
        1: 'minute'
    }
    time_data_options = {
        0: order_time.hour,
        1: math.ceil(order_time.minute / 5) * 5
    }

    if time_data_options[1] > 59:
        time_data_options[0] += 1
        time_data_options[1] = 0

    order_time = timezone.datetime.strptime(f'{time_data_options[0]}:{time_data_options[1]}', '%H:%M').time()
    plus_buttons = []
    minus_buttons = []
    time_buttons = []

    for i in range(2):
        plus_buttons.append(
            types.InlineKeyboardButton('+', callback_data=f'plus;{time_types[i]};{order_time}')
        )
        minus_buttons.append(
            types.InlineKeyboardButton('-', callback_data=f'minus;{time_types[i]};{order_time}')
        )
        time_buttons.append(types.InlineKeyboardButton(str(time_data_options[i]), callback_data='ignore'))

    keyboard.add(*plus_buttons)
    keyboard.add(*time_buttons)
    keyboard.add(*minus_buttons)

    keyboard.add(types.InlineKeyboardButton(
        getattr(accept_button, f'text_{locale}'),
        callback_data=f'{accept_button.name};{order_time}'
    ))
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
