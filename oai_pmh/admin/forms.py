################################################################################
#
# File Name: forms.py
# Application: Informatics Core
# Description:
#
# Author: Pierre Francois RIGODIAT
#         pierre-francois.rigodiat@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from django import forms
from django.core.validators import MinValueValidator
from mgi.models import OaiXslt, OaiMetadataFormat, OaiSet, Template, TemplateVersion, OaiMySet


class UploadOaiPmhXSLTForm(forms.Form):
    """
    Form to upload a new XSLT for OAI-PMH purpose
    """
    oai_name = forms.CharField(label='Enter XSLT name', max_length=100, required=True)
    oai_pmh_xslt_file = forms.FileField(label='Select a file',required=True)


class FormDataModelChoiceField(forms.ModelChoiceField):
    #Used to return the name of the xslt file
    def label_from_instance(self, obj):
        return obj.name


class AssociateXSLT(forms.Form):
    """
    Associate XSLTs to a metadata formats (per template)
    """

    def clean(self):
        #Check if an XSLT file is provided when the Metadata Format is activated
        cleaned_data = super(AssociateXSLT, self).clean()
        name = cleaned_data.get("oai_name")
        activated = cleaned_data.get("activated")
        xslt_file = cleaned_data.get("oai_pmh_xslt_file")
        #If not, raise validation error
        if activated and not xslt_file:
            raise forms.ValidationError("Please provide an XSLT File for the '%s' Metadata Format." % name)

    template_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    oai_my_mf_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    oai_name = forms.CharField(label='Enter XSLT name', max_length=100, required=True, widget=forms.TextInput(attrs={'readonly':'readonly', 'style': 'background-color:transparent;border:none'}))
    oai_pmh_xslt_file = FormDataModelChoiceField(queryset=OaiXslt.objects().all(), required=False, widget=forms.Select(attrs={'style':'width:500px'}))
    activated = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'cmn-toggle cmn-toggle-round'}), required=False)


class MyRegistryForm(forms.Form):
    """
        A my registry form
    """
    name = forms.CharField(label='Name', required=True)
    repo_identifier = forms.CharField(label='Repository Identifier', required=True)
    enable_harvesting = forms.BooleanField(label='Enable Harvesting ?', widget=forms.CheckboxInput(attrs={'class':'cmn-toggle cmn-toggle-round', 'visibility': 'hidden'}), required=False, initial=False)
    id = forms.CharField(widget=forms.HiddenInput(), required=False)


class RegistryForm(forms.Form):
    """
        A registry form
    """
    name = forms.CharField(widget=forms.HiddenInput(), required=False)
    url = forms.URLField(label='URL', required=True)
    harvestrate = forms.IntegerField(label='Harvestrate (seconds)', required=False, validators=[MinValueValidator(0)])
    harvest = forms.BooleanField(label='Harvest ?', widget=forms.CheckboxInput(attrs={'class':'cmn-toggle cmn-toggle-round', 'visibility': 'hidden'}), required=False, initial=True)
    id = forms.CharField(widget=forms.HiddenInput(), required=False)


class UpdateRegistryForm(forms.Form):
    """
        A registry update form
    """
    id = forms.CharField(widget=forms.HiddenInput(), required=False)
    harvestrate = forms.IntegerField(label='Harvestrate (seconds)', required=False)
    edit_harvest = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'cmn-toggle cmn-toggle-round'}), required=False)


class MyMetadataFormatForm(forms.Form):
    """
        A MyMetadataFormatForm form
    """
    metadataPrefix = forms.CharField(label='Metadata Prefix', required=True, widget=forms.TextInput(attrs={'placeholder': 'example: oai_dc'}))
    schema = forms.CharField(label='Schema URL', required=True)
    # metadataNamespace = forms.CharField(label='Namespace URL', required=True)
    # xmlSchema = forms.FileField(label='Select a file')


class FormDataModelChoiceFieldTemplateMF(forms.ModelChoiceField):
    #Used to return the title of the template
    def label_from_instance(self, obj):
        return obj.title


class MyTemplateMetadataFormatForm(forms.Form):
    """
        A MyTemplateMetadataFormatForm form
    """
    metadataPrefix = forms.CharField(label='Metadata Prefix', required=True, widget=forms.TextInput(attrs={'placeholder': 'example: oai_dc'}))
    template = FormDataModelChoiceFieldTemplateMF(label='Template', queryset=[])

    def __init__(self, *args, **kwargs):
        templatesVersionID = Template.objects.distinct(field="templateVersion")
        templatesID = TemplateVersion.objects(pk__in=templatesVersionID, isDeleted=False).distinct(field="current")
        templates = Template.objects(pk__in=templatesID).all()
        super(MyTemplateMetadataFormatForm, self).__init__(*args, **kwargs)
        # self.fields['template'].queryset
        self.fields['template'].queryset = templates


class FormDataModelChoiceFieldTemplate(forms.ModelChoiceField):
    #Used to return the name of the xslt file
    def label_from_instance(self, obj):
        return obj.title


class MySetForm(forms.Form):
    """
        A MyMetadataFormatForm form
    """
    setSpec = forms.CharField(label='Set spec', required=True)
    setName = forms.CharField(label='Set name', required=True)
    description = forms.CharField(label='Description', required=True, widget=forms.Textarea(attrs = {'cols': '60', 'rows': '5', 'style': 'height:14em;width:30em;'}))
    templates = FormDataModelChoiceFieldTemplate(label='Templates', queryset=[], widget=forms.SelectMultiple(), empty_label=None, required=False)

    def __init__(self, *args, **kwargs):
        super(MySetForm, self).__init__(*args, **kwargs)
        # self.fields['templates'].queryset = []
        self.fields['templates'].queryset = Template.objects.filter()


    # def clean(self):
    #     #Check if an XSLT file is provided when the Metadata Format is activated
    #     cleaned_data = super(MySetForm, self).clean()
    #     templates = cleaned_data.get("templates")
    #     #If not, raise validation error
    #     if templates is None:
    #         raise forms.ValidationError("Please pick templates")


class UpdateMyMetadataFormatForm(forms.Form):
    """
        A UpdateMyMetadataFormatForm update form
    """
    id = forms.CharField(widget=forms.HiddenInput(), required=False)
    metadataPrefix = forms.CharField(label='Metadata Prefix', required=True)
    # schema = forms.CharField(label='Schema', required=True)
    # metadataNamespace = forms.CharField(label='Namespace', required=True)


class UpdateMySetForm(forms.Form):
    """
        A UpdateMySetForm update form
    """
    id = forms.CharField(widget=forms.HiddenInput(), required=False)
    setSpec = forms.CharField(label='Set spec', required=True)
    setName = forms.CharField(label='Set name', required=True)
    description = forms.CharField(label='Description', required=True, widget=forms.Textarea(attrs = {'cols': '60', 'rows': '5', 'style': 'height:14em;width:30em;'}))
    templates = FormDataModelChoiceFieldTemplate(label='Templates', queryset=[], widget=forms.SelectMultiple(), empty_label=None, required=False)

    def __init__(self, *args, **kwargs):
        if 'id' in kwargs:
            set_id = kwargs.pop('id')
            information = OaiMySet.objects.get(pk=set_id)
            data = {'id': set_id, 'setSpec': information.setSpec, 'setName': information.setName, 'description': information.description}
            kwargs['initial'] = data
            super(UpdateMySetForm, self).__init__(*args, **kwargs)
            self.fields['templates'].initial = [template.id for template in information.templates]
            # self.fields['templates'].queryset = []
            self.fields['templates'].queryset = Template.objects.filter()


class FormDataModelChoiceFieldMF(forms.ModelChoiceField):
    #Used to return the prefix of the metadata format
    def label_from_instance(self, obj):
        return obj.metadataPrefix


class FormDataModelChoiceFieldSet(forms.ModelChoiceField):
    #Used to return the name of the set
    def label_from_instance(self, obj):
        return obj.setName


class SettingHarvestForm(forms.Form):
    """
        A SettingHarvestForm form
    """
    id = forms.CharField(widget=forms.HiddenInput(), required=False)
    metadataFormats = FormDataModelChoiceFieldMF(label='Metadata Formats', queryset=[], widget=forms.CheckboxSelectMultiple(attrs={'class':'cmn-toggle cmn-toggle-round'}), empty_label=None, required=False)
    sets = FormDataModelChoiceFieldSet(label='Sets', queryset=[], required=False, widget=forms.CheckboxSelectMultiple(attrs={'class':'cmn-toggle cmn-toggle-round'}), empty_label=None)

    def __init__(self, *args, **kwargs):
        if 'id' in kwargs:
            registryId = kwargs.pop('id')

        metadataFormats = OaiMetadataFormat.objects(registry=str(registryId)).all()
        sets = OaiSet.objects(registry=str(registryId)).all()

        super(SettingHarvestForm, self).__init__(*args, **kwargs)
        self.fields['id'].initial = registryId
        self.fields['metadataFormats'].initial = [mf.id for mf in metadataFormats if mf.harvest]
        # self.fields['metadataFormats'].queryset = []
        self.fields['metadataFormats'].queryset = metadataFormats
        self.fields['sets'].initial = [set.id for set in sets if set.harvest]
        # self.fields['sets'].queryset = []
        self.fields['sets'].queryset = sets
