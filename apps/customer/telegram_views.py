from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from apps.bot import dispatcher as dp, bot, keyboards, messages, logger
from apps.bot.callback_filters import message_is_not_start
from apps.bot.states import BotForm
from apps.customer.states import CustomerForm
from apps.customer.tortoise_models import Customer, BlockedUser, Gender


async def registration_form(user_id):
    customer = await Customer.get(id=user_id)
    message_title = 'full_name' if not customer.full_name else \
                    'age' if not customer.age else \
                    'phone_number' if not customer.phone_number else \
                    'gender' if not customer.gender else \
                    'related_people' if not customer.related_people else \
                    'main_menu'

    keyboard = keyboards.phone_number if message_title == 'phone_number' else \
               keyboards.gender if message_title == 'gender' else \
               keyboards.main_menu if message_title == 'main_menu' else \
               keyboards.back_keyboard

    await (getattr(CustomerForm, message_title) if message_title != 'main_menu' else BotForm.main_menu).set()
    await bot.send_message(customer.id, await messages.get_message(message_title), reply_markup=await keyboard())


@dp.message_handler(
    message_is_not_start,
    state=CustomerForm.all_states,
    content_types=[ContentType.TEXT, ContentType.CONTACT]
)
async def register_customer(message, state: FSMContext):
    text = message.text
    user_id = message.from_user.id
    customer = await Customer.get(id=user_id)
    state = await state.get_state()

    if state == CustomerForm.age.state:
        if not text.isdigit():
            message = await messages.get_message('age')
            keyboard = await keyboards.back_keyboard()
            return await bot.send_message(user_id, message, keyboard=keyboard)

        age = int(text)
        customer.age = int(text)
        if age < 21:
            customer.is_blocked = True

    if state == CustomerForm.phone_number.state:
        contact = message.contact

        logger.info(message)
        if not contact or (contact and contact.user_id != user_id):
            message = await messages.get_message('phone_number')
            keyboard = await keyboards.phone_number()
            return await bot.send_message(user_id, message, reply_markup=keyboard)

        phone_number = contact.phone_number
        customer.phone_number = phone_number

        if phone_number in await BlockedUser.all().values_list('phone_number', flat=True):
            customer.is_blocked = True

    if state == CustomerForm.gender.state:
        genders = await Gender.all().values_list('name_ru', flat=True)

        if text not in genders:
            message = await messages.get_message('gender')
            keyboard = await keyboards.gender()
            return await bot.send_message(user_id, message, reply_markup=keyboard)

        customer.gender = await Gender.get(name_ru=text)

    if state == CustomerForm.full_name.state:
        customer.full_name = text

    if state == CustomerForm.related_people.state:
        customer.related_people = text

    await customer.save()

    if customer.is_blocked:
        await bot.send_message(user_id, await messages.get_message('is_blocked'), reply_markup=keyboards.remove_keyboard)
        return

    await registration_form(user_id)
