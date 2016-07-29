################################################################################
#
# File Name: views.py
# Application: dashboard
# Description:
#
# Author: Pierre Francois RIGODIAT
#        pierre-francois.rigodiat@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from password_policies.forms import PasswordPoliciesForm
from password_policies.forms.fields import PasswordPoliciesField
from user_dashboard.validators import LowerCaseLetterCountValidator, UpperCaseLetterCountValidator
from django.utils.translation import ugettext_lazy as _
from django import forms
import os
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)

class CustomPasswordPoliciesForm(PasswordPoliciesForm):
    """
A form that lets a user set his/her password without entering the
old password.
"""
    new_password1 = PasswordPoliciesField(label=_("New password"),
        validators=[LowerCaseLetterCountValidator,
                    UpperCaseLetterCountValidator],)



class PasswordPoliciesLowerUpperField(PasswordPoliciesField):
    """
A form field that validates a password using :ref:`api-validators`.
"""
    def __init__(self, *args, **kwargs):
        if "widget" not in kwargs:
            kwargs["widget"] = forms.PasswordInput(render_value=False)
        kwargs["min_length"] = settings.PASSWORD_MIN_LENGTH
        self.default_validators.append(UpperCaseLetterCountValidator())
        self.default_validators.append(LowerCaseLetterCountValidator())
        super(PasswordPoliciesLowerUpperField, self).__init__(*args, **kwargs)