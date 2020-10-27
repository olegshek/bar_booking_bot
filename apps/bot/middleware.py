import gettext
from typing import Tuple, Any, Dict

from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from django.conf import settings

from apps.bot import bot, messages, keyboards
from apps.customer.tortoise_models import Customer, BlockedUser


class AccessControl(BaseMiddleware):
    async def on_process_message(self, message, *args, **kwargs):
        user_id = message.from_user.id
        customer = await Customer.filter(id=user_id).first()

        if customer:
            if customer.is_blocked or \
                    customer.phone_number in await BlockedUser.all().values_list('phone_number', flat=True):
                message = await messages.get_message('is_blocked', customer.language)
                await bot.send_message(user_id, message, reply_markup=keyboards.remove_keyboard)
                raise CancelHandler()


class Localization(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> str:
        *_, data = args
        user = args[0].from_user
        if not user:
            raise CancelHandler()

        customer = await Customer.filter(id=user.id).first()
        language = data['locale'] = customer.language if customer and customer.language else 'ru'
        return language

    def find_locales(self) -> Dict[str, gettext.GNUTranslations]:
        translation_list = {}
        paths = self.path
        for path in paths:
            self.path = path
            try:
                translation_list.update(super(Localization, self).find_locales())
            except FileNotFoundError:
                continue

        return translation_list


i18n = Localization(settings.I18N_DOMAIN, settings.LOCALE_PATHS)