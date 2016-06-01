################################################################################
#
# File Name: forms.py
# Application: curate
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

from django import forms
from mgi.models import FormData


class NewForm(forms.Form):
    """
    Form to start curating from an empty form
    """
    document_name = forms.CharField(label='', max_length=100, required=True)


class FormDataModelChoiceField(forms.ModelChoiceField):
    """
    Choice Field to select an existing form
    """
    def label_from_instance(self, obj):
        return obj.name


class OpenForm(forms.Form):
    """
    Form to open an existing form
    """
    forms = FormDataModelChoiceField(label='', queryset=FormData.objects().none())

    def __init__(self, *args, **kwargs):
        if 'forms' in kwargs:
            qs = kwargs.pop('forms')
        else:
            qs = FormData.objects().none()   
        super(OpenForm, self).__init__(*args, **kwargs)
        self.fields['forms'].queryset = qs


class UploadForm(forms.Form):
    """
    Form to start curating from a file
    """
    file = forms.FileField(label='')


class SaveDataForm(forms.Form):
    """
    Form to save a form
    """
    def is_valid(self):
        return super(SaveDataForm, self).is_valid() and self.data['title'].strip() != ""

    title = forms.CharField(label='Save As', min_length=1, max_length=100, required=True)


class CancelChangesForm(forms.Form):
    CANCEL_CHOICES = [('revert', 'Revert to my previously Saved Form'),
                      ('return', 'Return to Add Resources')]

    cancel = forms.ChoiceField(label='', choices=CANCEL_CHOICES, widget=forms.RadioSelect())
