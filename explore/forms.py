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
from mgi.models import Template, TemplateVersion
from oai_pmh.explore.forms import KeywordForm as KeywordFormOAIPMH
class ExportForm(forms.Form):
    """
    Create the form for exporting data
    """
    my_exporters = forms.MultipleChoiceField(label='', choices=[], widget=forms.CheckboxSelectMultiple())
    my_exporters_disabled = ""

    EXPORT_OPTIONS = []
    def __init__(self, templateIds=[]):
        self.EXPORT_OPTIONS = []
        self.EXPORT_OPTIONS_DISABLED = []
        dictExporters = []
        #We retrieve exporters for those templates
        templates = Template.objects(pk__in=templateIds)
        for template in templates:
            dictExporters.append(set(template.exporters))

        mutualExporters = []
        diffExporters = []
        if len(dictExporters) > 0:
            mutualExporters = set.intersection(*dictExporters)

        if len(dictExporters) > 1:
            diffExporters = set.union(*dictExporters) - mutualExporters

        for exporter in mutualExporters:
            if exporter.name != 'XSLT':
                #We add them
                self.EXPORT_OPTIONS.append((exporter.url,exporter.name))

        self.my_exporters_disabled = ", ".join(x.name for x in diffExporters if x.name !='XSLT')

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
    my_xslts_disabled = ""
    EXPORT_OPTIONS = []
    def __init__(self, templateIds=[]):
        self.EXPORT_OPTIONS = []
        self.EXPORT_OPTIONS_DISABLED = []
        dictExporters = []
        #We retrieve all XSLTFiles available for those templates
        templates = Template.objects(pk__in=templateIds)
        for template in templates:
            dictExporters.append(set(template.XSLTFiles))

        xslts = []
        if len(dictExporters) > 0:
            xslts = set.intersection(*dictExporters)

        diffXslts = []
        if len(dictExporters) > 1:
            diffXslts = set.union(*dictExporters) - xslts

        for xslt in xslts:
            #We add them
            self.EXPORT_OPTIONS.append((xslt.id, xslt.name))

        self.my_xslts_disabled = ", ".join(x.name for x in diffXslts)

        super(UploadXSLTForm, self).__init__()
        self.fields['my_xslts'].choices = []
        self.fields['my_xslts'].choices = self.EXPORT_OPTIONS


class KeywordForm(forms.Form):
    """
    Create the form for the keyword search: input and checkboxes
    """
    my_schemas = forms.MultipleChoiceField(label='', choices=[], widget=forms.CheckboxSelectMultiple(attrs={"checked":""}))
    my_user_schemas = forms.MultipleChoiceField(label='', choices=[], widget=forms.CheckboxSelectMultiple(attrs={"checked":""}))
    search_entry = forms.CharField(widget=forms.TextInput(attrs={'class': 'research'}))
    my_schemas_nb = 0
    my_user_schemas_nb = 0
    SCHEMAS_OPTIONS = []
    SCHEMAS_USER_OPTIONS = []
    def __init__(self, userId=""):
        self.SCHEMAS_OPTIONS = []
        self.SCHEMAS_USER_OPTIONS = []

        #We retrieve all common template + user template
        currentSchemas = TemplateVersion.objects(isDeleted=False).distinct(field="current")
        schemas = Template.objects(pk__in=currentSchemas, user=None).distinct(field="title")

        userSchemas = Template.objects(user=str(userId)).distinct(field="title")

        for schema in schemas:
            #We add them
            self.SCHEMAS_OPTIONS.append((schema, schema))

        for schema in userSchemas:
            #We add them
            self.SCHEMAS_USER_OPTIONS.append((schema, schema))

        super(KeywordForm, self).__init__()
        #Init KeywordFormOAIPMH
        self.form_oai_pmh = KeywordFormOAIPMH()
        self.fields['my_schemas'].choices = []
        self.fields['my_schemas'].choices = self.SCHEMAS_OPTIONS
        self.fields['my_user_schemas'].choices = []
        self.fields['my_user_schemas'].choices = self.SCHEMAS_USER_OPTIONS

        self.my_schemas_nb = len(self.SCHEMAS_OPTIONS)
        self.my_user_schemas_nb = len(self.SCHEMAS_USER_OPTIONS)

        if self.my_schemas_nb + self.my_user_schemas_nb == 1:
            self.fields['my_schemas'].widget.attrs['disabled'] = True
            self.fields['my_user_schemas'].widget.attrs['disabled'] = True
