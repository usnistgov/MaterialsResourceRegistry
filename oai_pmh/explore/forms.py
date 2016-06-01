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
from mgi.models import OaiRegistry, OaiMetadataFormat, Template
from itertools import groupby
from django.utils.html import format_html
import json

class KeywordForm(forms.Form):
    """
    Create the form for the keyword search: input and checkboxes
    """
    my_registries = forms.MultipleChoiceField(label='', choices=[], widget=forms.CheckboxSelectMultiple(attrs={"checked":""}))
    search_entry = forms.CharField(widget=forms.TextInput(attrs={'class': 'research'}))

    REGISTRIES_OPTIONS = []
    def __init__(self, userId=""):
        self.SCHEMAS_OPTIONS = []
        self.REGISTRIES_OPTIONS = []

        #We retrieve all registries (data providers)
        registries = OaiRegistry.objects(isDeactivated=False).order_by('name')

        for registry in registries:
            #We add them
            self.REGISTRIES_OPTIONS.append((registry.id, registry.name))
        super(KeywordForm, self).__init__()
        self.fields['my_registries'].choices = []
        self.fields['my_registries'].choices = self.REGISTRIES_OPTIONS
        self.my_registries_nb = len(self.REGISTRIES_OPTIONS)


class MetadataFormatsForm(forms.Form):
    """
    Create the form for the keyword search: input and checkboxes
    """
    my_schemas = forms.MultipleChoiceField(label='', choices=[], widget=forms.CheckboxSelectMultiple(attrs={"checked":""}))
    my_schemas_nb = 0
    SCHEMAS_OPTIONS = []

    def __init__(self, listRegistriesId=[]):
        self.SCHEMAS_OPTIONS = []
        #Retrieve registries name
        registriesName = {}
        for registryId in listRegistriesId:
            obj = OaiRegistry.objects(pk=registryId).get()
            registriesName[str(registryId)] = obj.name

        #We retrieve all common schemas
        schemas = OaiMetadataFormat.objects(registry__in=listRegistriesId).order_by('metadataPrefix')
        groups = []

        for k, g in groupby(schemas, lambda x: x.hash):
            groups.append(list(g))      # Store group iterator as a list

        #For each group
        for group in groups:
            #Get metadata prefix
            name = group[0].metadataPrefix
            #Get template name
            template = group[0].template
            listValues = []
            for elt in group:
                listValues.append((str(elt.id)))
            #Provide information about the number of registries using this MF
            if len(listValues) == 1: name = format_html(name + "<br> (in 1 Registry)")
            else: name = format_html(name + "<br> (in %s Registries)" % len(listValues))
            #If it's linked to a template
            if template != None:
                name += format_html(" <text class='local'> + Local </text>")
                template = Template.objects.only('id', 'title').get(pk=template.id)
                t = json.dumps({'oai-pmh': listValues, 'local': template.title})
            else:
                t = json.dumps({'oai-pmh': listValues})

            self.SCHEMAS_OPTIONS.append((( t , name)))

        super(MetadataFormatsForm, self).__init__()
        self.fields['my_schemas'].choices = []
        self.fields['my_schemas'].choices = self.SCHEMAS_OPTIONS

        self.my_schemas_nb = len(self.SCHEMAS_OPTIONS)
