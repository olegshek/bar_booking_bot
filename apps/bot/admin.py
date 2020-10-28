from django.contrib import admin
from django.contrib.auth.models import User, Group

from apps.bot.models import Button, Message, WorkingHours, SeatsManager, Weekday

admin.site.unregister(User)
admin.site.unregister(Group)


class ButtonAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('__str__', 'text')
    readonly_fields = ('name', )


class MessageAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('__str__', 'text')
    readonly_fields = ('title', )


class WorkingHoursAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SeatsManagerAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class WeekdayAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Button, ButtonAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(WorkingHours, WorkingHoursAdmin)
admin.site.register(SeatsManager, SeatsManagerAdmin)
admin.site.register(Weekday, WeekdayAdmin)

