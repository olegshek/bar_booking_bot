from apps.bot.tortoise_models import Button
from apps.customer.tortoise_models import Customer


async def keyboard_back(message):
    return message.text in [getattr(await Button.get(name='back'), f'text_{locale}') for locale in ['en', 'ru']]


async def inline_back(query):
    return query.data == 'back'


async def message_is_not_start(message):
    user = await Customer.filter(id=message.from_user.id).first()
    if not user or not user.language:
        locale = 'ru'
    else:
        locale = user.language
    return message.text not in ['/start', '/stop', getattr(await Button.get(name='back'), f'text_{locale}')]


async def data_is_digit(query):
    return query.data.isdigit()


async def calendar_selection_filter(query):
    return 'PREV' in query.data or 'NEXT' in query.data


async def date_selection(query):
    return 'DAY' in query.data


async def time_processing(query):
    return 'plus' in query.data or 'minus' in query.data


async def accept_time(query):
    return 'accept' in query.data or 'certain_time' in query.data
