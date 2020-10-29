from datetime import datetime
from typing import Any, Optional

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from tortoise import models, fields
from tortoise.functions import Sum

from apps.bot import app_name
from apps.customer.tortoise_models import BookRequest


class TimeField(fields.DatetimeField):
    skip_to_python_if_native = True
    SQL_TYPE = "TIME"

    def to_python_value(self, value: Any) -> Optional[datetime.time]:
        if value is None or isinstance(value, datetime.time):
            return value
        return parse_datetime(value).time()


class Button(models.Model):
    name = fields.CharField(max_length=50, unique=True)
    text_ru = fields.CharField(max_length=50, unique=True)
    text_en = fields.CharField(max_length=50, unique=True)

    class Meta:
        table = f'{app_name}_button'

    def __str__(self):
        return self.name


class Keyboard(models.Model):
    name = fields.CharField(max_length=50, unique=True)
    buttons = fields.ManyToManyField('bot.Button', related_name='keyboards', through='bot_keyboardbuttonsordering',
                                     forward_key='button_id', backward_key='keyboard_id')

    class Meta:
        table = f'{app_name}_keyboard'


class KeyboardButtonsOrdering(models.Model):
    keyboard = fields.ForeignKeyField('bot.Keyboard', on_delete=fields.CASCADE, related_name='buttons_ordering')
    button = fields.ForeignKeyField('bot.Button', on_delete=fields.CASCADE, related_name='ordering')
    ordering = fields.SmallIntField()

    class Meta:
        table = f'{app_name}_keyboardbuttonsordering'


class Message(models.Model):
    title = fields.CharField(max_length=100, unique=True)
    text_ru = fields.TextField()
    text_en = fields.TextField()

    class Meta:
        table = f'{app_name}_message'


class SeatsManager(models.Model):
    stock_seats_number = fields.IntField(default=50)
    additional_seats_number = fields.IntField(default=0)

    class Meta:
        table = f'{app_name}_seatsmanager'

    async def get_free_seats(self, date=timezone.now().date()):
        occupied_seats = await BookRequest.filter(
            created_at__gte=date,
            created_at__lte=date + timezone.timedelta(days=1),
            confirmed_at__isnull=False
        ).order_by('people_quantity').annotate(seats_sum=Sum('people_quantity')).first()

        return (self.stock_seats_number or 0) - \
               (occupied_seats.seats_sum if occupied_seats else 0) + \
               self.additional_seats_number


class WorkingHours(models.Model):
    start_time = TimeField()
    end_time = TimeField()

    class Meta:
        table = f'{app_name}_workinghours'


class Weekday(models.Model):
    name_en = fields.CharField(max_length=2)
    name_ru = fields.CharField(max_length=2)

    class Meta:
        table = f'{app_name}_weekday'
        ordering = ('id', )

