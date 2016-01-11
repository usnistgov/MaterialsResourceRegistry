from django import forms
from django.forms.widgets import HiddenInput


class NamePIDForm(forms.Form):
    """
    Form to substitute unsupported NamePID
    """
    name = forms.CharField(label='', required=False)
    pid = forms.CharField(label='PID', required=False)
    tag = forms.CharField(widget=HiddenInput(), required=True)
    

class DateForm(forms.Form):
    """
    Form to substitute unsupported Date
    """
    date = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'yyyy-mm-dd'}), required=False)
    role = forms.CharField(label='Role', required=False)
    tag = forms.CharField(widget=HiddenInput(), required=True)