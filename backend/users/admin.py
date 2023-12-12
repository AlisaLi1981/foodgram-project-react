from django.contrib import admin

from .models import Subscriptions, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'username',)
    list_filter = ('email', 'username',)


class SubscriptionsAdmin(admin.ModelAdmin):
    search_fields = ('user', 'author',)
    list_filter = ('user', 'author',)


admin.site.register(User, UserAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
