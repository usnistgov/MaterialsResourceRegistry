from django import forms


class BLOBHosterForm(forms.Form):
    file = forms.FileField(label='')


class URLForm(forms.Form):
    url = forms.URLField(label='')