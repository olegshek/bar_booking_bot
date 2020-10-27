from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from apps.bot import dispatcher as dp, bot, keyboards, messages, logger
from apps.bot.callback_filters import message_is_not_start
from apps.bot.states import BotForm
from apps.bot.tortoise_models import Button
from apps.customer import callback_filters
from apps.customer.states import RegisterForm, CustomerForm
from apps.customer.tortoise_models import Customer, BlockedUser, Gender


async def registration_form(user_id, locale):
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

    await (getattr(RegisterForm, message_title) if message_title != 'main_menu' else BotForm.main_menu).set()
    await bot.send_message(
        customer.id,
        await messages.get_message(message_title, locale),
        reply_markup=await keyboard(locale)
    )


@dp.message_handler(callback_filters.language_choice, state=CustomerForm.language_choice)
async def language_choice_processing(message, locale, state):
    user_id = message.from_user.id
    text = message.text
    en_button = await Button.get(name='en')
    ru_button = await Button.get(name='ru')
    language = en_button.name if text == en_button.text_en else ru_button.name
    await Customer.filter(id=user_id).update(language=language)
    await registration_form(user_id, language)


@dp.message_handler(
    message_is_not_start,
    state=RegisterForm.all_states,
    content_types=[ContentType.TEXT, ContentType.CONTACT]
)
async def register_customer(message, state: FSMContext, locale):
    text = message.text
    user_id = message.from_user.id
    customer = await Customer.get(id=user_id)
    state = await state.get_state()

    if state == RegisterForm.age.state:
        if not text.isdigit():
            message = await messages.get_message('age', locale)
            keyboard = await keyboards.back_keyboard(locale)
            return await bot.send_message(user_id, message, keyboard=keyboard)

        age = int(text)
        customer.age = int(text)
        if age < 21:
            customer.is_blocked = True

    if state == RegisterForm.phone_number.state:
        contact = message.contact

        logger.info(message)
        if not contact or (contact and contact.user_id != user_id):
            message = await messages.get_message('phone_number', locale)
            keyboard = await keyboards.phone_number(locale)
            return await bot.send_message(user_id, message, reply_markup=keyboard)

        phone_number = contact.phone_number
        customer.phone_number = phone_number

        if phone_number in await BlockedUser.all().values_list('phone_number', flat=True):
            customer.is_blocked = True

    if state == RegisterForm.gender.state:
        genders = await Gender.all().values_list(f'text_{locale}', flat=True)

        if text not in genders:
            message = await messages.get_message('gender', locale)
            keyboard = await keyboards.gender(locale)
            return await bot.send_message(user_id, message, reply_markup=keyboard)

        customer.gender = await Gender.get(**{f'text_{locale}': text})

    if state == RegisterForm.full_name.state:
        customer.full_name = text

    if state == RegisterForm.related_people.state:
        customer.related_people = text

    await customer.save()

    if customer.is_blocked:
        await bot.send_message(
            user_id,
            await messages.get_message('is_blocked', locale),
            reply_markup=keyboards.remove_keyboard
        )
        return

    await registration_form(user_id, locale)
