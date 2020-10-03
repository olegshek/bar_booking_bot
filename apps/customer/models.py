from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Gender(models.Model):
    name = models.CharField(max_length=6, verbose_name=_('Name'))
    name_ru = models.CharField(max_length=10, verbose_name=_('Name ru'))

    def __str__(self):
        return self.name_ru


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

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    def __str__(self):
        return self.full_name


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
    date = models.DateField(null=True, verbose_name=_('Date'))
    people_quantity = models.IntegerField(null=True, verbose_name=_('People quantity'))
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return str(self.book_id)

    @property
    def is_active(self):
        return self.date >= timezone.now().date()



