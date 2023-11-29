from django.contrib import admin

from users.models import Subscriptions, User


admin.site.register(User)
admin.site.register(Subscriptions)
