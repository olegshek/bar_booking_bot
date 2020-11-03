from aiogram import types
from aiogram.types import ContentType
from aiogram.utils.exceptions import TelegramAPIError
from django.utils import timezone

from apps.bot import dispatcher as dp, bot, keyboards, messages, telegram_calendar
from apps.bot.callback_filters import message_is_not_start, keyboard_back, date_selection, time_processing, accept_time, \
    data_is_digit, inline_back, feedback_choice
from apps.bot.keyboards import cancel_keyboard
from apps.bot.states import BotForm
from apps.bot.telegram_calendar import separate_callback_data, create_calendar
from apps.bot.tortoise_models import Button, SeatsManager, WorkingHours
from apps.customer.callback_filters import main_menu_filter
from apps.customer.states import RegisterForm, CustomerForm
from apps.customer.telegram_views import registration_form
from apps.customer.tortoise_models import Customer, BookRequest, Feedback


async def back(user_id, state, locale, message_id=None):
    state_name = await state.get_state()

    if state_name in [*map(lambda state_obj: state_obj.state, RegisterForm.states)]:
        customer = await Customer.get(id=user_id)
        customer.gender = None
        customer.age = None
        customer.full_name = None
        customer.related_people = None
        customer.phone_number = None
        await customer.save()
        await registration_form(user_id, locale)

    if state_name in [BotForm.book_date.state, CustomerForm.language_choice.state]:
        try:
            await bot.delete_message(user_id, message_id)
        except TelegramAPIError:
            pass

        await registration_form(user_id, locale)

    if state_name == BotForm.book_time.state:
        message = await messages.get_message('book_date', locale)
        keyboard = await telegram_calendar.create_calendar(locale)
        await BotForm.book_date.set()
        await bot.edit_message_text(message, user_id, message_id, reply_markup=keyboard)

    if state_name == BotForm.people_quantity.state:
        async with state.proxy() as data:
            date = timezone.datetime.strptime(data['date'], '%Y-%m-%d').date()

        message = await messages.get_message('book_time', locale)
        keyboard = await keyboards.time_choice(date, locale)
        await BotForm.book_time.set()
        await bot.edit_message_text(message, user_id, message_id, reply_markup=keyboard)


@dp.message_handler(keyboard_back, state='*')
async def button_back(message, state, locale):
    await back(message.from_user.id, state, locale)


@dp.callback_query_handler(inline_back, state='*')
async def back_inline(query, state, locale):
    await back(query.from_user.id, state, locale, query.message.message_id)


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, locale):
    user_id = message.from_user.id
    customer = await Customer.filter(id=user_id).first()
    if not customer:
        await Customer.create(id=user_id, username=message.from_user.username)

    await bot.send_message(user_id, await messages.get_message('greeting', locale),
                           reply_markup=keyboards.remove_keyboard)

    if not customer.language:
        await CustomerForm.language_choice.set()
        return await bot.send_message(user_id, await messages.get_message('language_choice', locale),
                                      reply_markup=await keyboards.language_choice(locale, False))
    await registration_form(user_id, locale)


@dp.message_handler(message_is_not_start, main_menu_filter, state=BotForm.main_menu)
async def main_menu(message, state, locale):
    user_id = message.from_user.id
    button = await Button.get(**{f'text_{locale}': message.text})

    if button.name == 'book':
        message = await messages.get_message('book_date', locale)
        keyboard = await telegram_calendar.create_calendar(locale)
        await BotForm.book_date.set()
        await bot.send_message(user_id, '✔️', reply_markup=keyboards.remove_keyboard)
        return await bot.send_message(user_id, message, reply_markup=keyboard)

    await CustomerForm.language_choice.set()
    return await bot.send_message(user_id, await messages.get_message('language_choice', locale),
                                  reply_markup=await keyboards.language_choice(locale, True))


@dp.callback_query_handler(date_selection, state=BotForm.book_date)
async def process_date_selection(query, state, locale):
    user_id = query.from_user.id
    message_id = query.message.message_id
    action, year, month, day = separate_callback_data(query.data)
    date = timezone.datetime(int(year), int(month), int(day)).date()

    now = timezone.now()
    end_time = (await WorkingHours.first()).end_time
    if (now.astimezone() + timezone.timedelta(hours=1)).time() >= end_time and now.date() == date:
        return await bot.edit_message_text(
            await messages.get_message('invalid_date', locale),
            user_id,
            message_id,
            reply_markup=await telegram_calendar.create_calendar(locale)
        )

    if date < timezone.now().date():
        message = await messages.get_message('book_date', locale)
        keyboard = await create_calendar(locale)
        try:
            return await bot.edit_message_text(message, user_id, message_id, reply_markup=keyboard)
        except TelegramAPIError:
            return

    for book_request in await BookRequest.filter(datetime__gte=timezone.now().date(), customer_id=user_id):
        if book_request.datetime.date() == date:
            local_datetime = book_request.datetime.astimezone()
            message = (await messages.get_message('already_booked', locale)) % {
                'book_id': book_request.book_id,
                'date': str(local_datetime.date()),
                'time': timezone.datetime.strftime(local_datetime, '%H:%M'),
                'people_quantity': str(book_request.people_quantity)
            }

            keyboard = await create_calendar(locale)
            try:
                return await bot.edit_message_text(message, user_id, message_id, reply_markup=keyboard)
            except TelegramAPIError:
                return

    async with state.proxy() as data:
        data['date'] = str(date)

    message = await messages.get_message('book_time', locale)
    keyboard = await keyboards.time_choice(date, locale)
    await BotForm.book_time.set()
    await bot.edit_message_text(message, user_id, message_id, reply_markup=keyboard)


@dp.callback_query_handler(time_processing, state=BotForm.book_time)
async def time_choice_processing(query, locale, state):
    user_id = query.from_user.id
    message_id = query.message.message_id
    option, time_type, time_data = query.data.split(';')
    async with state.proxy() as data:
        date = timezone.datetime.strptime(data['date'], '%Y-%m-%d').date()

    try:
        await bot.edit_message_reply_markup(
            user_id,
            message_id,
            reply_markup=await keyboards.time_choice(date, locale, option, time_type, time_data)
        )
    except TelegramAPIError:
        pass


@dp.callback_query_handler(accept_time, state=BotForm.book_time)
async def accept_order_time(query, state, locale):
    user_id = query.from_user.id
    message_id = query.message.message_id
    data = query.data
    time = data.split(';')[1]

    async with state.proxy() as data:
        data['time'] = time

    await BotForm.people_quantity.set()
    await bot.edit_message_text(
        await messages.get_message('people_quantity', locale),
        user_id,
        message_id,
        reply_markup=await keyboards.people_quantity(locale)
    )


@dp.callback_query_handler(data_is_digit, state=BotForm.people_quantity)
async def people_quantity(query, state, locale):
    user_id = query.from_user.id
    quantity = int(query.data)

    async with state.proxy() as data:
        date = data['date']
        time = data['time']

    free_seats = await (await SeatsManager.first()).get_free_seats(timezone.datetime.strptime(date, '%Y-%m-%d'))
    is_confirmed = quantity <= free_seats
    confirmed_at = timezone.now() if is_confirmed else None

    if not is_confirmed:
        message = (await messages.get_message('no_seats', locale)) % {'seats': str(free_seats)}
        keyboard = await keyboards.people_quantity(locale)
    else:
        datetime = timezone.datetime.strptime(date + time, '%Y-%m-%d%H:%M:%S')
        book_request = await BookRequest.create(
            customer_id=user_id,
            people_quantity=quantity,
            datetime=datetime,
            confirmed_at=confirmed_at
        )
        message = (await messages.get_message('successful_booking', locale)) % {
            'book_id': book_request.book_id,
            'date': str(datetime.date()),
            'time': timezone.datetime.strftime(datetime, '%H:%M'),
            'people_quantity': str(book_request.people_quantity)
        }
        keyboard = None

    try:
        await bot.edit_message_text(message, user_id, query.message.message_id, reply_markup=keyboard)
    except TelegramAPIError:
        pass

    if is_confirmed:
        await state.finish()
        await BotForm.main_menu.set()
        keyboard = await keyboards.main_menu(locale)
        await bot.send_message(user_id, await messages.get_message('main_menu', locale), reply_markup=keyboard)


@dp.callback_query_handler(feedback_choice, state='*')
async def choice_feedback(query, locale, state):
    action, request_id = query.data.split(';')
    user_id = query.from_user.id
    message_id = query.message.message_id
    if action == 'no':
        try:
            await bot.delete_message(user_id, message_id)
        except TelegramAPIError:
            pass
        return

    async with state.proxy() as data:
        data['request_id'] = request_id

    await BotForm.feedback_write.set()

    try:
        await bot.delete_message(user_id, message_id)
    except TelegramAPIError:
        pass

    await bot.send_message(user_id, await messages.get_message('feedback_write', locale),
                           reply_markup=await cancel_keyboard(locale))


@dp.message_handler(message_is_not_start, state=BotForm.feedback_write, content_types=[ContentType.TEXT])
async def feedback_save(message, locale, state):
    text = message.text
    user_id = message.from_user.id

    if text != getattr(await Button.get(name='cancel'), f'text_{locale}'):
        async with state.proxy() as data:
            request_id = data['request_id']

        book_request = await BookRequest.get(book_id=request_id)
        await Feedback.create(book_request=book_request, text=text)
        await bot.send_message(user_id, await messages.get_message('feedback_accepted', locale))

    await registration_form(user_id, locale)
