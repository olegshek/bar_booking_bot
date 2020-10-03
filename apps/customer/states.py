from aiogram.dispatcher.filters.state import StatesGroup, State


class CustomerForm(StatesGroup):
    age = State()
    phone_number = State()
    full_name = State()
    gender = State()
    related_people = State()