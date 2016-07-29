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
from password_policies.forms.validators import BaseCountValidator
from django.utils.translation import ungettext
import os
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)

class UpperCaseLetterCountValidator(BaseCountValidator):
    """
Counts the occurrences of letters and raises a
:class:`~django.core.exceptions.ValidationError` if the count
is less than :func:`~UpperCaseLetterCountValidator.get_min_count`.
"""
    categories = ['Lu']
    """
The unicode data letter categories:
====  ===========
Code  Description
====  ===========
LC    Letter, Cased
Ll    Letter, Lowercase
Lu    Letter, Uppercase
Lt    Letter, Titlecase
Lo    Letter, Other
Nl    Number, Letter
====  ===========
"""
    #: The validator's error code.
    code = u"invalid_letter_count"

    def get_error_message(self):
        """
Returns this validator's error message.
"""
        msg = ungettext("The new password must contain %d or more uppercase letter.",
                        "The new password must contain %d or more uppercase letters.",
                        self.get_min_count()) % self.get_min_count()
        return msg

    def get_min_count(self):
        """
:returns: :py:attr:`password_policies.conf.Settings.PASSWORD_MIN_LETTERS`
"""
        return settings.PASSWORD_MIN_UPPERCASE_LETTERS


class LowerCaseLetterCountValidator(BaseCountValidator):
    """
Counts the occurrences of letters and raises a
:class:`~django.core.exceptions.ValidationError` if the count
is less than :func:`~LowerCaseLetterCountValidator.get_min_count`.
"""
    categories = ['Ll']
    """
The unicode data letter categories:
====  ===========
Code  Description
====  ===========
LC    Letter, Cased
Ll    Letter, Lowercase
Lu    Letter, Uppercase
Lt    Letter, Titlecase
Lo    Letter, Other
Nl    Number, Letter
====  ===========
"""
    #: The validator's error code.
    code = u"invalid_letter_count"

    def get_error_message(self):
        """
Returns this validator's error message.
"""
        msg = ungettext("The new password must contain %d or more lower letter.",
                        "The new password must contain %d or more lower letters.",
                        self.get_min_count()) % self.get_min_count()
        return msg

    def get_min_count(self):
        """
:returns: :py:attr:`password_policies.conf.Settings.PASSWORD_MIN_LETTERS`
"""
        return settings.PASSWORD_MIN_LOWERCASE_LETTERS

