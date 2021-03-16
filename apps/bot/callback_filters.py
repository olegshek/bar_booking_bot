from apps.bot.tortoise_models import Button
from apps.customer.tortoise_models import Customer, BookRequest


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


async def yes_or_no_validation(query, action_name):
    data = query.data
    if len(data.split(';')) != 3:
        return False

    action, option, request_id = data.split(';')
    book_request_ids = await BookRequest.all().values_list('id', flat=True)
    return action == action_name and option in ['yes', 'no'] and int(request_id) in book_request_ids


async def feedback_choice(query):
    return await yes_or_no_validation(query, 'feedback')


async def book_notification(query):
    return await yes_or_no_validation(query, 'notification')
