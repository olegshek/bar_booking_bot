from apps.bot.tortoise_models import KeyboardButtonsOrdering
from apps.customer.tortoise_models import Customer


async def callback_filter(query, keyboard_name):
    buttons = map(
        str,
        await KeyboardButtonsOrdering.filter(keyboard__name=keyboard_name).values_list('button__name', flat=True)
    )
    return query.data in buttons


async def message_filter(message, keyboard_name):
    user = await Customer.filter(id=message.from_user.id).first()
    if not user or user.language:
        return False

    locale = user.language
    buttons = map(
        str,
        await KeyboardButtonsOrdering.filter(keyboard__name=keyboard_name).values_list(f'button__text_{locale}', flat=True)
    )
    return message.text in buttons
