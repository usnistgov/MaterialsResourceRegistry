################################################################################
#
# File Name: forms.py
# Application: explore
# Purpose:
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
#         Pierre Francois RIGODIAT
#		  pierre-francois.rigodiat@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from django import forms
from mgi.models import Template

class ExportForm(forms.Form):
    """
    Create the form for exporting data
    """
    my_exporters = forms.MultipleChoiceField(label='', choices=[], widget=forms.CheckboxSelectMultiple())
    EXPORT_OPTIONS = []
    def __init__(self, templateId=""):
        self.EXPORT_OPTIONS = []
        #We retrieve exporters for this template
        exporters = Template.objects.get(pk=templateId).exporters
        for exporter in exporters:
            if exporter.name != 'XSLT':
                #We add them
                self.EXPORT_OPTIONS.append((exporter.url,exporter.name))

        super(ExportForm, self).__init__()
        self.fields['my_exporters'].choices = []
        self.fields['my_exporters'].choices = self.EXPORT_OPTIONS

class FormDataModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "XSLT: "+ obj.name

class UploadXSLTForm(forms.Form):
    """
    Create the form for exporting data with an XSLT
    """
    my_xslts = forms.MultipleChoiceField(label='', choices=[], widget=forms.CheckboxSelectMultiple())
    EXPORT_OPTIONS = []
    def __init__(self, templateId=""):
        self.EXPORT_OPTIONS = []
        #We retrieve all XSLTFiles available for this template
        xslts = Template.objects.get(pk=templateId).XSLTFiles
        for xslt in xslts:
            #We add them
            self.EXPORT_OPTIONS.append((xslt.id, xslt.name))

        super(UploadXSLTForm, self).__init__()
        self.fields['my_xslts'].choices = []
        self.fields['my_xslts'].choices = self.EXPORT_OPTIONS

class KeywordForm(forms.Form):
    """
    Create the form for the keyword search: input and checkboxes
    """
    my_schemas = forms.MultipleChoiceField(label='', choices=[], widget=forms.CheckboxSelectMultiple(attrs={"checked":""}))
    search_entry = forms.CharField(widget=forms.TextInput(attrs={'class': 'research'}))
    SCHEMAS_OPTIONS = []
    def __init__(self, templateId=""):
        self.SCHEMAS_OPTIONS = []
        # Retrieve all schemas
        schemas = Template.objects.all().distinct(field="title")
        for schema in schemas:
            # Add them to available options
            self.SCHEMAS_OPTIONS.append((schema, schema))

        super(KeywordForm, self).__init__()
        self.fields['my_schemas'].choices = []
        self.fields['my_schemas'].choices = self.SCHEMAS_OPTIONS
        
