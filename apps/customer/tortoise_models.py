import random

from django.utils import timezone
from tortoise import models, fields
from tortoise.fields import SET_NULL, CASCADE

from apps.customer import app_name


def _generate_book_id():
    return random.randint(1000, 10000000)


class Gender(models.Model):
    name = fields.CharField(max_length=9)
    name_ru = fields.CharField(max_length=10)

    class Meta:
        table = f'{app_name}_gender'


class Customer(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, blank=True, null=True)
    full_name = fields.CharField(max_length=200, null=True, blank=True)
    phone_number = fields.CharField(max_length=20, null=True)
    age = fields.IntField(null=True)
    gender = fields.ForeignKeyField('customer.Gender', related_name='customers', on_delete=SET_NULL, null=True)
    related_people = fields.TextField(null=True)
    is_blocked = fields.BooleanField(default=False)

    class Meta:
        table = f'{app_name}_customer'


class BlockedUser(models.Model):
    phone_number = fields.CharField(max_length=15)

    class Meta:
        table = f'{app_name}_blockeduser'


class BookRequest(models.Model):
    book_id = fields.IntField(default=_generate_book_id)
    customer = fields.ForeignKeyField('customer.Customer', on_delete=CASCADE, related_name='book_requests')
    date = fields.DateField(null=True)
    people_quantity = fields.IntField(null=True)
    created_at = fields.DatetimeField(default=timezone.now)

    class Meta:
        table = f'{app_name}_bookrequest'