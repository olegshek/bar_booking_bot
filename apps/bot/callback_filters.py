from apps.bot.tortoise_models import Button


async def keyboard_back(message):
    return message.text == (await Button.get(name='back')).text


async def message_is_not_start(message):
    return message.text not in ['/start', '/stop', (await Button.get(name='back')).text]


async def calendar_selection_filter(query):
    return 'PREV' in query.data or 'NEXT' in query.data


async def date_selection(query):
    return 'DAY' in query.data
