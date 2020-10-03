from aiogram import types
from aiogram.types import ContentType
from django.utils import timezone

from apps.bot import dispatcher as dp, bot, keyboards, messages, telegram_calendar
from apps.bot.callback_filters import message_is_not_start, keyboard_back
from apps.bot.states import BotForm
from apps.bot.tortoise_models import Button
from apps.customer.callback_filters import main_menu_filter
from apps.customer.states import CustomerForm
from apps.customer.telegram_views import registration_form
from apps.customer.tortoise_models import Customer, BookRequest


@dp.message_handler(keyboard_back, state='*')
async def back(message, state):
    user_id = message.from_user.id
    state = await state.get_state()

    if state in [*map(lambda state_obj: state_obj.state, CustomerForm.states), BotForm.people_quantity.state]:
        customer = await Customer.get(id=user_id)
        customer.gender = None
        customer.age = None
        customer.full_name = None
        customer.related_people = None
        customer.phone_number = None
        await customer.save()
        await registration_form(user_id)

    if state == BotForm.book_date.state:
        message = await messages.get_message('people_quantity')
        keyboard = await keyboards.back_keyboard()
        await BotForm.people_quantity.set()
        await bot.send_message(user_id, message, reply_markup=keyboard)


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message):
    user_id = message.from_user.id
    customer = await Customer.filter(id=user_id).first()
    if not customer:
        customer = await Customer.create(id=user_id, username=message.from_user.username)

    message_title = 'greeting'
    if customer.is_blocked:
        message_title = 'is_blocked'

    await bot.send_message(user_id, await messages.get_message(message_title), reply_markup=keyboards.remove_keyboard)
    await registration_form(user_id)


@dp.message_handler(message_is_not_start, main_menu_filter, state=BotForm.main_menu)
async def main_menu(message, state):
    user_id = message.from_user.id
    button = await Button.get(text=message.text)

    if button.name == 'book':
        book_request = await BookRequest.filter(date__gte=timezone.now().date(), customer_id=user_id).first()
        if book_request:
            message = (await messages.get_message('already_booked')) % {'book_id': book_request.book_id}
            await bot.send_message(user_id, message, reply_markup=keyboards.remove_keyboard)

            message = await messages.get_message('main_menu')
            keyboard = await keyboards.main_menu()
            return await bot.send_message(user_id, message, reply_markup=keyboard)

        message = await messages.get_message('people_quantity')
        keyboard = await keyboards.back_keyboard()
        await BotForm.people_quantity.set()
        await bot.send_message(user_id, message, reply_markup=keyboard)


@dp.message_handler(message_is_not_start, state=BotForm.people_quantity, content_types=[ContentType.TEXT])
async def people_quantity(message, state):
    user_id = message.from_user.id
    quantity = message.text

    if not quantity.isdigit():
        message = await messages.get_message('people_quantity')
        keyboard = keyboards.remove_keyboard
        return await bot.send_message(user_id, message, reply_markup=keyboard)

    async with state.proxy() as data:
        data['people_quantity'] = int(quantity)

    message = await messages.get_message('book_date')
    keyboard = await telegram_calendar.create_calendar()
    await BotForm.book_date.set()
    await bot.send_message(user_id, message, reply_markup=keyboard)
