from aiogram import types

from apps.bot.tortoise_models import Button, KeyboardButtonsOrdering
from apps.customer import GENDERS
from apps.customer.tortoise_models import Gender

checkout_emoji = {
    'PICKUP': '🏃‍♂️',
    'DELIVERY': '🚘'
}


async def get_back_button_obj():
    return await Button.get(name='back')


async def main_menu():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    for keyboard_button in await KeyboardButtonsOrdering.filter(keyboard__name='main_menu').order_by('ordering'):
        button = await keyboard_button.button
        keyboard.add(types.KeyboardButton(button.text))

    return keyboard


async def phone_number():
    back_button_obj = await get_back_button_obj()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    for keyboard_button in await KeyboardButtonsOrdering.filter(keyboard__name='phone_number').order_by('ordering'):
        button = await keyboard_button.button
        keyboard.add(types.KeyboardButton(
            button.text,
            request_contact=True if button.name == 'phone_number' else None
        ))
    keyboard.add(types.KeyboardButton(back_button_obj.text))
    return keyboard


async def gender():
    back_button_obj = await get_back_button_obj()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    for gender_name in await Gender.all().values_list('name_ru', flat=True):
        keyboard.add(types.KeyboardButton(gender_name))

    keyboard.add(back_button_obj.text)
    return keyboard


async def back_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = await get_back_button_obj()
    keyboard.add(types.KeyboardButton(button.text))
    return keyboard


remove_keyboard = types.ReplyKeyboardRemove()
