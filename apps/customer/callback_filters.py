from apps.bot.tortoise_models import Button
from core.filters import message_filter


async def main_menu_filter(message):
    return await message_filter(message, 'main_menu')


async def language_choice(message):
    en_text = (await Button.get(name='en')).text_en
    ru_text = (await Button.get(name='ru')).text_ru
    return message.text in [en_text, ru_text]