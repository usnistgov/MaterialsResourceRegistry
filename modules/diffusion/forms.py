from django import forms

class ExcelUploaderForm(forms.Form):
    file = forms.FileField(label='Select Excel File')
