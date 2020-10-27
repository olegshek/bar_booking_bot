from aiogram.dispatcher.filters.state import StatesGroup, State


class RegisterForm(StatesGroup):
    age = State()
    phone_number = State()
    full_name = State()
    gender = State()
    related_people = State()


class CustomerForm(StatesGroup):
    language_choice = State()