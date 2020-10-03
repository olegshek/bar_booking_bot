from apps.bot.tortoise_models import Message


async def get_message(title):
    return (await Message.get(title=title)).text
