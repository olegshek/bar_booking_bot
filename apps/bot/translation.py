from modeltranslation import translator

from apps.bot.models import Button, Message, Weekday
from core.translation import TranslationOptionsMixin


@translator.register(Button)
class ButtonOptions(TranslationOptionsMixin):
    fields = ('text', )


@translator.register(Message)
class MessageOptions(TranslationOptionsMixin):
    fields = ('text', )


@translator.register(Weekday)
class WeekdayOption(TranslationOptionsMixin):
    fields = ('name', )
