from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from apps.bot import bot, messages, keyboards
from apps.customer.tortoise_models import Customer, BlockedUser


class AccessControl(BaseMiddleware):
    async def on_process_message(self, message, *args, **kwargs):
        user_id = message.from_user.id
        customer = await Customer.filter(id=user_id).first()

        if customer:
            if customer.is_blocked or \
                    customer.phone_number in await BlockedUser.all().values_list('phone_number', flat=True):
                message = await messages.get_message('is_blocked')
                await bot.send_message(user_id, message, reply_markup=keyboards.remove_keyboard)
                raise CancelHandler()
