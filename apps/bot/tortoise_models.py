from tortoise import models, fields

from apps.bot import app_name


class Button(models.Model):
    name = fields.CharField(max_length=50, unique=True)
    text = fields.CharField(max_length=50, unique=True)

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
    text = fields.TextField()

    class Meta:
        table = f'{app_name}_message'
