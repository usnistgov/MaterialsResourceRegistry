from django import forms
from django.forms.widgets import HiddenInput


class NamePIDForm(forms.Form):
    """
    Form to substitute unsupported NamePID
    """
    name = forms.CharField(label='', required=False)
    pid = forms.CharField(label='PID', required=False)
    tag = forms.CharField(widget=HiddenInput(), required=True)
