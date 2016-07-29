################################################################################
#
# File Name: admin.py
# Application: admin_mdcs
# Purpose:   
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import models as auth_models
from password_policies.models import PasswordHistory
from django.utils import timezone

admin.site.register(Permission)


class UserAdmin(auth_admin.UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'password_age')

    def password_age(self, obj):
        newest = PasswordHistory.objects.filter(user=obj).last()
        if newest:
            last_change = newest.created
        else:
            # TODO: Do not rely on this property!
            last_change = obj.date_joined

        delta = timezone.now() - last_change
        return "%s" % (delta.days)
    password_age.short_description = 'Password Age (Days)'

# Re-register UserAdmin
admin.site.unregister(auth_models.User)
admin.site.register(auth_models.User, UserAdmin)
