import calendar

from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from apps.bot import bot, dispatcher as dp, messages, keyboards, logger
from apps.bot.callback_filters import calendar_selection_filter, date_selection
from apps.bot.states import BotForm
from apps.customer.tortoise_models import BookRequest


def create_callback_data(action, year, month, day):
    return ";".join([action, str(year), str(month), str(day)])


def separate_callback_data(data):
    return data.split(";")


async def create_calendar(year=None, month=None):
    now = timezone.datetime.now()
    if not year:
        year = now.year
    if not month:
        month = now.month
    data_ignore = create_callback_data("IGNORE", year, month, 0)
    keyboard = InlineKeyboardMarkup()

    row = []
    row.append(
        InlineKeyboardButton("<", callback_data=create_callback_data("PREV-MONTH", year, month, timezone.now().day)))
    row.append(InlineKeyboardButton(calendar.month_name[month], callback_data=data_ignore))
    row.append(
        InlineKeyboardButton(">", callback_data=create_callback_data("NEXT-MONTH", year, month, timezone.now().day)))
    keyboard.row(*row)

    row = []
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вр"]:
        row.append(InlineKeyboardButton(str(day), callback_data=data_ignore))
    keyboard.row(*row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data=data_ignore))
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=create_callback_data("DAY", year, month, day)))
        keyboard.row(*row)

    return keyboard


@dp.callback_query_handler(calendar_selection_filter, state=BotForm.book_date)
async def process_calendar_selection(query):
    action, year, month, day = separate_callback_data(query.data)
    curr = timezone.datetime(int(year), int(month), 1)

    if 'MONTH' in action:
        prev_month = curr - timezone.timedelta(days=1)
        next_month = curr + timezone.timedelta(days=31)

        change = prev_month if 'PREV' in action and prev_month.date().month >= now().date().month else \
                 next_month if 'NEXT' in action else \
                 curr

    else:
        return

    try:
        await bot.edit_message_text(
            text=query.message.text,
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=await create_calendar(int(change.year), int(curr.month if 'YEAR' in action else change.month))
        )
    except:
        pass


@dp.callback_query_handler(date_selection, state=BotForm.book_date)
async def process_date_selection(query, state):
    user_id = query.from_user.id
    message_id = query.message.message_id
    action, year, month, day = separate_callback_data(query.data)
    date = timezone.datetime(int(year), int(month), int(day))

    if date.date() < now().date():
        message = await messages.get_message('book_date')
        keyboard = await create_calendar()
        try:
            return await bot.edit_message_text(message, user_id, message_id, reply_markup=keyboard)
        except:
            return

    async with state.proxy() as data:
        people_quantity = data['people_quantity']

    logger.info(date)
    book_request = await BookRequest.create(customer_id=user_id, people_quantity=people_quantity, date=date.date())
    message = (await messages.get_message('successful_booking')) % {'book_id': book_request.book_id}

    await state.finish()
    await BotForm.main_menu.set()
    await bot.edit_message_text(message, user_id, message_id)

    keyboard = await keyboards.main_menu()
    await bot.send_message(user_id, await messages.get_message('main_menu'), reply_markup=keyboard)