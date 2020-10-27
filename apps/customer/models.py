from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Gender(models.Model):
    name = models.CharField(max_length=6, verbose_name=_('Name'))
    text = models.CharField(max_length=10, null=True, verbose_name=_('Text'))

    def __str__(self):
        return self.text


class Customer(models.Model):
    id = models.IntegerField(primary_key=True, editable=False, unique=True)
    username = models.CharField(max_length=20, blank=True, null=True)
    full_name = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Full name'))
    phone_number = models.CharField(max_length=20, null=True, verbose_name=_('Phone number'))
    age = models.IntegerField(null=True, verbose_name=_('Age'))
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, related_name='customers',
                               verbose_name=_('Gender'))
    related_people = models.TextField(null=True, verbose_name=_('Related people'))
    is_blocked = models.BooleanField(default=False, verbose_name=_('Is blocked'))

    language = models.CharField(max_length=2, choices=settings.LANGUAGES, null=True, verbose_name=_('Language'))

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    def __str__(self):
        return self.full_name if self.full_name else str(self.id)


class BlockedUser(models.Model):
    phone_number = models.CharField(max_length=15, unique=True, verbose_name=_('Phone number'))

    class Meta:
        verbose_name = _('Blocked user')
        verbose_name_plural = _('Blocked users')

    def __str__(self):
        return self.phone_number


class BookRequest(models.Model):
    book_id = models.IntegerField(null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='book_requests', verbose_name=_('Customer'))
    datetime = models.DateTimeField(null=True, verbose_name=_('Datetime'))
    people_quantity = models.IntegerField(null=True, verbose_name=_('People quantity'))

    confirmed_at = models.DateTimeField(null=True, verbose_name=_('Confirmed at'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('Created at'))

    class Meta:
        ordering = ('-confirmed_at', )
        verbose_name = _('Book request')
        verbose_name_plural = _('Book requests')

    def __str__(self):
        return str(self.book_id)

    @property
    def is_active(self):
        return self.datetime.date() >= timezone.now().date()



