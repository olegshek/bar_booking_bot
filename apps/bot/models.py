from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.customer.models import BookRequest


class Button(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Name'))
    text = models.CharField(max_length=50, unique=True, verbose_name=_('Text'))

    class Meta:
        verbose_name = _('Button')
        verbose_name_plural = _('Buttons')

    def __str__(self):
        return self.name


class Keyboard(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Name'))
    buttons = models.ManyToManyField(Button, related_name='keyboards', through='KeyboardButtonsOrdering',
                                     verbose_name=_('Buttons'))

    class Meta:
        verbose_name = _('Keyboard')
        verbose_name_plural = _('Keyboards')


class KeyboardButtonsOrdering(models.Model):
    keyboard = models.ForeignKey(Keyboard, on_delete=models.CASCADE, related_name='buttons_ordering',
                                 verbose_name=_('Keyboard'))
    button = models.ForeignKey(Button, on_delete=models.CASCADE, related_name='ordering', verbose_name=_('Keyboard'))
    ordering = models.PositiveIntegerField(verbose_name='Ordering')

    class Meta:
        verbose_name = _('Keyboard buttons ordering')
        verbose_name_plural = _('Keyboard buttons orderings')


class Message(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name=_('Title'))
    text = models.TextField()

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    def __str__(self):
        return self.title


class SeatsManager(models.Model):
    stock_seats_number = models.PositiveIntegerField(default=50, verbose_name=_('Seats number'))
    additional_seats_number = models.PositiveIntegerField(default=0, verbose_name=_('Additional seats number'))

    class Meta:
        verbose_name = _('Seats manager')
        verbose_name_plural = _('Seats manager')

    def get_free_seats(self, date=timezone.now().date()):
        occupied_seats = BookRequest.objects.filter(created_at__date=date).aggregate(
            seats_sum=Coalesce(Sum('people_quantity'), 0)
        )['seats_sum']
        return self.stock_seats_number - occupied_seats + self.additional_seats_number


class WorkingHours(models.Model):
    start_time = models.TimeField(verbose_name=_('Start time'))
    end_time = models.TimeField(verbose_name=_('End time'))

    class Meta:
        verbose_name = _('Working hours')
        verbose_name_plural = _('Working hours')

    def __str__(self):
        return f'{self._meta.verbose_name}-{self.id}'


class Weekday(models.Model):
    name = models.CharField(max_length=2, verbose_name=_('Name'))

