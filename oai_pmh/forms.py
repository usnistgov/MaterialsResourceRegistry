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
from mgi.models import OaiRegistry

VERBS = (('0', 'Pick one'),
         ('1', 'Identify'),
         ('2', 'Get Record'),
         ('3', 'List Records'),
         ('4', 'List Sets'),
         ('5', 'List Identifiers'),
         ('6', 'List Metadata Formats'))

class Url(forms.Form):
    """
        A record form
    """
    url = forms.URLField(label='url', required=True)

class RequestForm(forms.Form):
    """
        A request form
    """
    dataProvider= forms.ChoiceField(label='Data Provider', choices=[], required=False, widget=forms.Select(attrs={'style':'width:500px'}))
    verb = forms.ChoiceField(label='Verb', choices=VERBS, required=False, widget=forms.Select(attrs={'style':'width:500px'}))
    set = forms.ChoiceField(label='Set', choices=[], required=False, widget=forms.Select(attrs={'style':'width:500px', 'disabled':'true', 'class':'form-control'}))
    identifiers = forms.CharField(label='Identifier', required=False)
    metadataprefix = forms.ChoiceField(label='Matadata Prefix', choices=[], required=False, widget=forms.Select(attrs={'style':'width:500px', 'disabled':'true'}))
    From = forms.CharField(label='From', required=False, widget=forms.DateInput(attrs={'data-date-format':'yyyy-mm-ddThh:ii:00Z'}))
    until = forms.CharField(label='Until', required=False, widget=forms.DateInput(attrs={'data-date-format':'yyyy-mm-ddThh:ii:00Z'}))
    resumptionToken = forms.CharField(label='Resumption Token', required=False)

    def __init__ (self):
        super(RequestForm, self).__init__()
        self.dataproviders = []
        self.dataproviders.append(('0', 'Pick one'))
        self.fields['metadataprefix'].choices = self.dataproviders
        self.fields['set'].choices = self.dataproviders
        for o in OaiRegistry.objects(isDeactivated=False).all():
            self.dataproviders.append((str(o.id)+'|'+o.url, str(o.name.encode('utf8'))))
        self.fields['dataProvider'].choices = self.dataproviders
