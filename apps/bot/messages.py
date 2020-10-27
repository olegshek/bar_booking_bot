from apps.bot.tortoise_models import Message


async def get_message(title, locale):
    return getattr(await Message.get(title=title), f'text_{locale}')
