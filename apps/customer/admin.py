from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.customer.models import Customer, BlockedUser, BookRequest


def block_user(modeladmin, request, queryset):
    queryset.update(is_blocked=True)


def unblock_user(modeladmin, request, queryset):
    queryset.update(is_blocked=False)


block_user.short_description = 'Block selected users'
unblock_user.short_description = 'Unblock selected users'


class CustomerAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return None

    def has_delete_permission(self, request, obj=None):
        return None

    list_display = ('full_name', 'phone_number', 'gender', 'related_people', 'is_blocked')
    readonly_fields = ('id', 'full_name', 'phone_number', 'gender', 'related_people')
    actions = (block_user, unblock_user)


class ActiveBookRequests(SimpleListFilter):
    title = _('By status')
    parameter_name = ''

    def lookups(self, request, model_admin):
        filters = (
            ('Active', _('Active')),
        )
        return list(f for f in filters)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__gte=timezone.now().date())
        return queryset


class BookRequestAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super(BookRequestAdmin, self).get_queryset(request).filter(confirmed_at__isnull=False)

    list_display = ('book_id', 'customer', 'is_active', 'datetime', 'people_quantity', 'created_at')
    readonly_fields = ('book_id', 'customer', 'is_active', 'datetime', 'people_quantity', 'created_at')
    search_fields = ('book_id', )
    list_filter = (ActiveBookRequests, 'created_at', 'customer', 'datetime')

    def is_active(self, obj):
        return '✅' if obj.is_active else '❌'

    is_active.short_description = _('Active')
    is_active.allow_tags = True


admin.site.register(Customer, CustomerAdmin)
admin.site.register(BlockedUser)
admin.site.register(BookRequest, BookRequestAdmin)