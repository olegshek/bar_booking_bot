from modeltranslation import translator

from apps.customer.models import Gender
from core.translation import TranslationOptionsMixin


@translator.register(Gender)
class ButtonOptions(TranslationOptionsMixin):
    fields = ('text', )

