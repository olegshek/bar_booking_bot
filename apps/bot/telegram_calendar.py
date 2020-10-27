import calendar

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.utils import timezone

from apps.bot import utils
from apps.bot.keyboards import get_back_button_obj
from apps.bot.tortoise_models import Weekday, WorkingHours


def create_callback_data(action, year, month, day):
    return ";".join([action, str(year), str(month), str(day)])


def separate_callback_data(data):
    return data.split(";")


async def create_calendar(locale, year=None, month=None):
    now = timezone.datetime.now()
    if not year:
        year = now.year
    if not month:
        month = now.month
    data_ignore = create_callback_data("IGNORE", year, month, 0)
    keyboard = InlineKeyboardMarkup()

    row = []
    row.append(InlineKeyboardButton(calendar.month_name[month], callback_data=data_ignore))

    row = []
    for day in await Weekday.all().values_list(f'name_{locale}', flat=True):
        row.append(InlineKeyboardButton(str(day), callback_data=data_ignore))
    keyboard.row(*row)

    date = now.date()
    if now + timezone.timedelta(hours=1) >= await utils.order_datetime(date):
        date += timezone.timedelta(days=1)

    if timezone.now().time() > (await WorkingHours.first()).start_time:
        date += timezone.timedelta(days=1)

    dates = []
    for i in range(7):
        dates.append(date)
        date += timezone.timedelta(days=1)

    weeks = []
    for date in dates:
        for cal_week in calendar.Calendar().monthdatescalendar(year, date.month):
            if date in cal_week and cal_week not in weeks:
                weeks.append(cal_week)

    today = now.date()
    for week in weeks:
        row = []
        for date in week:
            if today > date or date > today + timezone.timedelta(days=6):
                row.append(InlineKeyboardButton(" ", callback_data=data_ignore))
            else:
                row.append(InlineKeyboardButton(str(date.day),
                                                callback_data=create_callback_data("DAY", year, month, date.day)))
        keyboard.row(*row)

    back_button_obj = await get_back_button_obj()
    keyboard.add(
        InlineKeyboardButton(getattr(back_button_obj, f'text_{locale}'), callback_data=back_button_obj.name)
    )

    return keyboard
