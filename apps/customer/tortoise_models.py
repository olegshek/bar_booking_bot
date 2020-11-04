import random
from enum import Enum

from django.utils import timezone
from tortoise import models, fields
from tortoise.fields import SET_NULL, CASCADE

from apps.customer import app_name


async def _generate_book_id():
    new_id = random.randint(1000, 10000000)
    if new_id in await BookRequest.all().values_list('id', flat=True):
        return await _generate_book_id()
    else:
        return new_id


class Gender(models.Model):
    name = fields.CharField(max_length=9)
    text_ru = fields.CharField(max_length=10)
    text_en = fields.CharField(max_length=10)

    class Meta:
        table = f'{app_name}_gender'


class Customer(models.Model):
    class Languages(str, Enum):
        RU = 'ru'
        UZ = 'uz'

    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, blank=True, null=True)
    full_name = fields.CharField(max_length=200, null=True, blank=True)
    phone_number = fields.CharField(max_length=20, null=True)
    age = fields.IntField(null=True)
    gender = fields.ForeignKeyField('customer.Gender', related_name='customers', on_delete=SET_NULL, null=True)
    related_people = fields.TextField(null=True)
    is_blocked = fields.BooleanField(default=False)

    language = fields.CharField(max_length=2, choices=Languages, null=True)

    class Meta:
        table = f'{app_name}_customer'


class BlockedUser(models.Model):
    phone_number = fields.CharField(max_length=15)

    class Meta:
        table = f'{app_name}_blockeduser'


class BookRequest(models.Model):
    book_id = fields.IntField()
    customer = fields.ForeignKeyField('customer.Customer', on_delete=CASCADE, related_name='book_requests')
    datetime = fields.DatetimeField(null=True)
    people_quantity = fields.IntField(null=True)

    confirmed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(default=timezone.now)

    class Meta:
        table = f'{app_name}_bookrequest'


class Feedback(models.Model):
    book_request = fields.OneToOneField('customer.BookRequest', on_delete=CASCADE, related_name='feedback', pk=True)
    text = fields.CharField(max_length=4096)
    created_at = fields.DatetimeField(default=timezone.now)

    class Meta:
        table = f'{app_name}_feedback'