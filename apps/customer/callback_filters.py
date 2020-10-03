from apps.bot.tortoise_models import KeyboardButtonsOrdering, Button


async def main_menu_filter(message):
    buttons = Button.filter(id__in=await KeyboardButtonsOrdering.all().values_list('button_id', flat=True))
    return message.text in await buttons.values_list('text', flat=True)