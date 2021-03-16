from telebot import types

from apps.bot.models import KeyboardButtonsOrdering


def feedback_choice(locale, request_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    for keyboard_button in KeyboardButtonsOrdering.objects.filter(keyboard__name='yes_or_no').order_by('ordering'):
        button = keyboard_button.button
        keyboard.add(types.InlineKeyboardButton(
            getattr(button, f'text_{locale}'),
            callback_data=f'feedback;{button.name};{request_id}')
        )

    return keyboard


def book_notification(book_request_id, locale):
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    buttons = []
    for keyboard_button in KeyboardButtonsOrdering.objects.filter(keyboard__name='yes_or_no').order_by('ordering'):
        button = keyboard_button.button
        buttons.append(types.InlineKeyboardButton(
            getattr(button, f'text_{locale}'),
            callback_data=f'notification;{button.name};{book_request_id}'
        ))

    keyboard.add(*buttons)
    return keyboard
