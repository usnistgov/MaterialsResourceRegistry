################################################################################
#
# File Name: views.py
# Application: Informatics Core
# Description:
#
# Author: Pierre Francois RIGODIAT
#         pierre-francois.rigodiat@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from rest_framework import status
from django.http.response import HttpResponseBadRequest
from oai_pmh.admin.forms import UpdateRegistryForm, MyMetadataFormatForm, RegistryForm, MyRegistryForm, UpdateMyMetadataFormatForm, MySetForm, UpdateMySetForm, \
MyTemplateMetadataFormatForm, SettingHarvestForm
import json
import os
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
OAI_HOST_URI = settings.OAI_HOST_URI
OAI_USER = settings.OAI_USER
OAI_PASS = settings.OAI_PASS
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
# Responses
from django.http import HttpResponse
# Requests
import requests
from django.template import RequestContext, loader
from mgi.models import OaiRegistry, OaiSettings, OaiMyMetadataFormat, OaiXslt, OaiTemplMfXslt, Template, OaiMySet
from django.contrib.admin.views.decorators import staff_member_required
from mgi.models import Message, OaiMetadataFormat, OaiSet, OaiRecord
from oai_pmh.forms import Url
from oai_pmh.admin.forms import UploadOaiPmhXSLTForm
from django.utils.dateformat import DateFormat
import lxml.etree as etree
from lxml.etree import XMLSyntaxError
from mongoengine import NotUniqueError, OperationError
from django.forms import formset_factory
from oai_pmh.admin.forms import AssociateXSLT
from django.core.urlresolvers import reverse
from oai_pmh.api.messages import APIMessage


################################################################################
#
# Function Name: oai_pmh(request)
# Inputs:        request -
# Outputs:       OAI-PMH Page
# Exceptions:    None
# Description:   Page that allows to manage OAI-PMH
#
################################################################################
@staff_member_required
def oai_pmh(request):
    template = loader.get_template('oai_pmh/admin/oai_pmh.html')

    registry_form = RegistryForm();
    registries = OaiRegistry.objects.all()
    context = RequestContext(request, {
        'registry_form': registry_form,
        'registries': registries,
    })

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: check_registry(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH Check if the Registry is available
#
################################################################################
@login_required(login_url='/login')
def check_registry(request):
    try:
        #Get the oai registry URL
        form = Url(request.POST)
        if form.is_valid():
            #Call the identify function from the API.
            uri= OAI_HOST_URI + reverse("api_objectIdentify")
            req = requests.post(uri, {"url":request.POST.get("url")}, auth=(OAI_USER, OAI_PASS))
            #If the return status is HTTP_200_OK, the OAI Registry is available
            isAvailable = req.status_code == status.HTTP_200_OK
        else:
            isAvailable = False
    except:
        isAvailable = False
    return HttpResponse(json.dumps({'isAvailable' : isAvailable }), content_type='application/javascript')


################################################################################
#
# Function Name: add_registry(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH Client add registry page
#
################################################################################
@login_required(login_url='/login')
def add_registry(request):
    if request.method == 'POST':
        form = RegistryForm(request.POST)
        #Check the Form
        if form.is_valid():
            try:
                #We add the registry
                uri = OAI_HOST_URI + reverse("api_add_registry")
                try:
                    url = request.POST.get('url')
                except ValueError:
                    return HttpResponseBadRequest('Please provide a URL.')

                #We retrieve information from the form
                if 'harvestrate' in request.POST:
                    harvestrate = request.POST.get('harvestrate')
                else:
                    harvestrate = ""
                if 'harvest' in request.POST:
                    harvest = True
                else:
                    harvest = False

                #Call to the API to add the registry
                try:
                    req = requests.post(uri, {"url":url,
                                              "harvestrate":harvestrate,
                                              "harvest":harvest},
                                        auth=(OAI_USER, OAI_PASS))
                    #If the status is OK, sucess message
                    if req.status_code == status.HTTP_201_CREATED:
                        messages.add_message(request, messages.SUCCESS, 'Data provider added with success.')
                        return HttpResponse('CREATED')
                    #Else, we return a bad request response with the message provided by the API
                    else:
                        data = json.loads(req.text)
                        return HttpResponseBadRequest(data[APIMessage.label])
                except Exception as e:
                    return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
            except Exception as e:
                return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
        else:
            return HttpResponseBadRequest('Bad entries. Please enter a valid URL and a positive integer')

################################################################################
#
# Function Name: update_registry(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH update one registry
#
# ################################################################################
@login_required(login_url='/login')
def update_registry(request):
    if request.method == 'POST':
        #UPDATE the registry
        try:
            uri = OAI_HOST_URI + reverse("api_update_registry")
            #Get the ID
            if 'id' in request.POST:
                id = request.POST.get('id')
            else:
                return HttpResponseBadRequest('Please provide an ID in order to edit the data provider.')
            #Get all form information
            if 'harvestrate' in request.POST:
                harvestrate = request.POST.get('harvestrate')
            else:
                harvestrate = ''
            if 'edit_harvest' in request.POST:
                harvest = True
            else:
                harvest = False
            #Call the API to update the registry
            try:
                req = requests.put(uri,
                                   {"id":id,
                                    "harvestrate":harvestrate,
                                    "harvest": harvest},
                                   auth=(OAI_USER, OAI_PASS))
                #If the status is OK, sucess message
                if req.status_code == status.HTTP_200_OK:
                    messages.add_message(request, messages.INFO, 'Data Provider successfully edited.')
                    return HttpResponse(json.dumps({}), content_type='application/javascript')
                #Else, we return a bad request response with the message provided by the API
                else:
                    data = json.loads(req.text)
                    return HttpResponseBadRequest(data[APIMessage.label])
            except Exception as e:
                return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
        except Exception as e:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
    elif request.method == 'GET':
        #Build the template to render for the registry edition
        template = loader.get_template('oai_pmh/admin/form_registry_edit.html')
        registry_id = request.GET['registry_id']
        try:
            registry = OaiRegistry.objects.get(pk=registry_id)
            data = {'id': registry.id, 'harvestrate': registry.harvestrate,
                    'edit_harvest': registry.harvest}
            registry_form= UpdateRegistryForm(data)
        except:
            registry_form = UpdateRegistryForm()

        context = RequestContext(request, {
            'registry_form': registry_form,
        })

        return HttpResponse(json.dumps({'template': template.render(context)}), content_type='application/javascript')

################################################################################
#
# Function Name: delete_registry(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH Delete Registry
#
################################################################################
@login_required(login_url='/login')
def delete_registry(request):
    uri = OAI_HOST_URI + reverse("api_delete_registry")
    try:
        id = request.POST.get('RegistryId')
    except ValueError:
        return HttpResponseBadRequest('Please provide an ID in order to delete the data provider.')
    try:
        req = requests.post(uri, {"RegistryId":id}, auth=(OAI_USER, OAI_PASS))

        #If the status is OK, sucess message
        if req.status_code == status.HTTP_200_OK:
            messages.add_message(request, messages.INFO, 'Data provider deleted with success.')
            return HttpResponse(json.dumps({}), content_type='application/javascript')
        #Else, we return a bad request response with the message provided by the API
        else:
            data = json.loads(req.text)
            return HttpResponseBadRequest(data[APIMessage.label])
    except Exception as e:
        return HttpResponseBadRequest('An error occurred. Please contact your administrator.')


################################################################################
#
# Function Name: deactivate_registry(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH Deactivate Registry
#
################################################################################
@login_required(login_url='/login')
def deactivate_registry(request):
    uri = OAI_HOST_URI + reverse("api_deactivate_registry")
    try:
        id = request.POST.get('RegistryId')
    except ValueError:
        return HttpResponseBadRequest('Please provide an ID in order to deactivate the data provider.')
    try:
        req = requests.post(uri, {"RegistryId":id}, auth=(OAI_USER, OAI_PASS))

        #If the status is OK, sucess message
        if req.status_code == status.HTTP_200_OK:
            messages.add_message(request, messages.INFO, 'Data provider deactivated with success.')
            return HttpResponse(json.dumps({}), content_type='application/javascript')
        #Else, we return a bad request response with the message provided by the API
        else:
            data = json.loads(req.text)
            return HttpResponseBadRequest(data[APIMessage.label])
    except Exception as e:
        return HttpResponseBadRequest('An error occurred. Please contact your administrator.')


################################################################################
#
# Function Name: reactivate_registry(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH Deactivate Registry
#
################################################################################
@login_required(login_url='/login')
def reactivate_registry(request):
    uri = OAI_HOST_URI + reverse("api_reactivate_registry")
    try:
        id = request.POST.get('RegistryId')
    except ValueError:
        return HttpResponseBadRequest('Please provide an ID in order to reactivate the data provider.')
    try:
        req = requests.post(uri, {"RegistryId":id}, auth=(OAI_USER, OAI_PASS))

        #If the status is OK, sucess message
        if req.status_code == status.HTTP_200_OK:
            messages.add_message(request, messages.INFO, 'Data provider reactivate with success.')
            return HttpResponse(json.dumps({}), content_type='application/javascript')
        #Else, we return a bad request response with the message provided by the API
        else:
            data = json.loads(req.text)
            return HttpResponseBadRequest(data[APIMessage.label])
    except Exception as e:
        return HttpResponseBadRequest('An error occurred. Please contact your administrator.')


################################################################################
#
# Function Name: deactivate_registry(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH Deactivate Registry
#
################################################################################
@login_required(login_url='/login')
def deactivate_registry(request):
    uri = OAI_HOST_URI + reverse("api_deactivate_registry")
    try:
        id = request.POST.get('RegistryId')
    except ValueError:
        return HttpResponseBadRequest('Please provide an ID in order to deactivate the data provider.')
    try:
        req = requests.post(uri, {"RegistryId":id}, auth=(OAI_USER, OAI_PASS))

        #If the status is OK, sucess message
        if req.status_code == status.HTTP_200_OK:
            messages.add_message(request, messages.INFO, 'Data provider deactivated with success.')
            return HttpResponse(json.dumps({}), content_type='application/javascript')
        #Else, we return a bad request response with the message provided by the API
        else:
            data = json.loads(req.text)
            return HttpResponseBadRequest(data['message'])
    except Exception as e:
        return HttpResponseBadRequest('An error occurred. Please contact your administrator.')


################################################################################
#
# Function Name: reactivate_registry(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH Deactivate Registry
#
################################################################################
@login_required(login_url='/login')
def reactivate_registry(request):
    uri = OAI_HOST_URI + reverse("api_reactivate_registry")
    try:
        id = request.POST.get('RegistryId')
    except ValueError:
        return HttpResponseBadRequest('Please provide an ID in order to reactivate the data provider.')
    try:
        req = requests.post(uri, {"RegistryId":id}, auth=(OAI_USER, OAI_PASS))

        #If the status is OK, sucess message
        if req.status_code == status.HTTP_200_OK:
            messages.add_message(request, messages.INFO, 'Data provider reactivate with success.')
            return HttpResponse(json.dumps({}), content_type='application/javascript')
        #Else, we return a bad request response with the message provided by the API
        else:
            data = json.loads(req.text)
            return HttpResponseBadRequest(data['message'])
    except Exception as e:
        return HttpResponseBadRequest('An error occurred. Please contact your administrator.')


################################################################################
#
# Function Name: oai_pmh_detail_registry(request)
# Inputs:        request -
# Outputs:       OAI-PMH Page
# Exceptions:    None
# Description:   Page that allows to get information about a OAI Registry
#
################################################################################
@staff_member_required
def oai_pmh_detail_registry(request):
    result_id = request.GET['id']
    template = loader.get_template('oai_pmh/admin/oai_pmh_detail_registry.html')
    context = RequestContext(request, {
        'registry': OaiRegistry.objects.get(pk=result_id),
        'metadataformats': OaiMetadataFormat.objects(registry=result_id),
        'sets': OaiSet.objects(registry=result_id),
        'nbRecords': OaiRecord.objects(registry=result_id).count(),
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: harvest(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH -  Harvest Data from a OAI Registry
#
# ################################################################################
@login_required(login_url='/login')
def harvest(request):
    if request.method == 'POST':
        try:
            #Get the ID
            registry_id = request.POST['registry_id']
            uri = OAI_HOST_URI + reverse("api_harvest")

            #Call the API to update all records for this registry
            try:
                r = requests.post(uri,
                                   {"registry_id": registry_id},
                                   auth=(OAI_USER, OAI_PASS))
                return HttpResponse(json.dumps({}), content_type='application/javascript')
            except Exception as e:
                return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
        except Exception as e:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')


################################################################################
#
# Function Name: check_harvest_data(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH Return the state of the registries (isHarvesting), if we are harvesting data from them
#                and the last update date
#
# ################################################################################
@login_required(login_url='/login')
def check_harvest_data(request):
    if request.method == 'POST':
        try:
            harvestDataInfo = []
            #Get all registries
            registries = OaiRegistry.objects.only('id', 'isHarvesting', 'lastUpdate').all()
            #Build array with registry id and isHarvesting value
            for registry in registries:
                result_json = {}
                result_json['registry_id'] = str(registry.id)
                result_json['isHarvesting'] = registry.isHarvesting
                #If we have a last update date, format the date
                if registry.lastUpdate:
                    df =  DateFormat(registry.lastUpdate)
                    lastUpdate = df.format('F j, Y, g:i a')
                else:
                    lastUpdate = ''
                result_json['lastUpdate'] = lastUpdate
                harvestDataInfo.append(result_json)

            return HttpResponse(json.dumps(harvestDataInfo), content_type='application/javascript')
        except Exception as e:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')


################################################################################
#
# Function Name: oai_pmh_my_infos(request)
# Inputs:        request -
# Outputs:       OAI-PMH Page
# Exceptions:    None
# Description:   Page that allows to manage my server's information (OAI-PMH)
#
################################################################################
@staff_member_required
def oai_pmh_my_infos(request):
    #Template name
    template = loader.get_template('oai_pmh/admin/oai_pmh_my_infos.html')
    #Get settings information in database
    information = OaiSettings.objects.get()
    if information:
        name = information.repositoryName
        repoIdentifier = information.repositoryIdentifier
        enableHarvesting = information.enableHarvesting
    else:
        name = settings.OAI_NAME
        repoIdentifier = settings.OAI_REPO_IDENTIFIER
        enableHarvesting = False
    #Fill the information
    data_provider = {
            'name': name,
            'baseURL': settings.OAI_HOST_URI + "/oai_pmh/server/",
            'protocole_version': settings.OAI_PROTOCOLE_VERSION,
            'admins': (email for name, email in settings.OAI_ADMINS),
            # 'earliest_date': self.getEarliestDate(),   # placeholder
            'deleted': settings.OAI_DELETED_RECORD,
            'granularity': settings.OAI_GRANULARITY,
            'identifier_scheme': settings.OAI_SCHEME,
            'repository_identifier': repoIdentifier,
            'identifier_delimiter': settings.OAI_DELIMITER,
            'sample_identifier': settings.OAI_SAMPLE_IDENTIFIER,
            'enable_harvesting': enableHarvesting,
        }
    #Form to manage MF
    metadataformat_form = MyMetadataFormatForm()
    #Form to manage template MF
    template_metadataformat_form = MyTemplateMetadataFormatForm()
    #Form to manage set
    set_form = MySetForm()
    #Get my server's Set
    sets = OaiMySet.objects.all()
    #Get my server's MF
    metadataFormats = OaiMyMetadataFormat.objects(isDefault=False, isTemplate=False or None).all()
    #Get my server's default MF
    defaultMetadataFormats = OaiMyMetadataFormat.objects(isDefault=True).all()
    #Get my server's template MF
    templateMetadataFormats = OaiMyMetadataFormat.objects(isTemplate=True).all()
    context = RequestContext(request, {
        'data_provider': data_provider,
        'metadataformat_form': metadataformat_form,
        'template_metadataformat_form' : template_metadataformat_form,
        'metadataFormats': metadataFormats,
        'set_form': set_form,
        'sets': sets,
        'defaultMetadataFormats': defaultMetadataFormats,
        'templateMetadataFormats': templateMetadataFormats
    })

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: update_my_registry(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH update my registry
#
# ################################################################################
@login_required(login_url='/login')
def update_my_registry(request):
    if request.method == 'POST':
        #UPDATE the registry
        try:
            uri = OAI_HOST_URI + reverse("api_update_my_registry")
            #Get all form information
            if 'name' in request.POST:
                name = request.POST.get('name')
            else:
                name = ''
            if 'enable_harvesting' in request.POST:
                enable_harvesting = True
            else:
                enable_harvesting = False
            #Call the API to update the registry
            try:
                req = requests.put(uri,
                                   {"repositoryName": name,
                                    # "repositoryIdentifier": repo_identifier,
                                    "enableHarvesting": enable_harvesting},
                                   auth=(OAI_USER, OAI_PASS))
                #If the status is OK, sucess message
                if req.status_code == status.HTTP_200_OK:
                    messages.add_message(request, messages.INFO, 'Data provider edited with success.')
                    return HttpResponse(json.dumps({}), content_type='application/javascript')
                #Else, we return a bad request response with the message provided by the API
                else:
                    data = json.loads(req.text)
                    return HttpResponseBadRequest(data[APIMessage.label])
            except Exception as e:
                return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
        except Exception as e:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
    elif request.method == 'GET':
        #Build the template to render for the registry edition
        template = loader.get_template('oai_pmh/admin/form_my_registry_edit.html')
        try:
            information = OaiSettings.objects.get()
            data = {'name': information.repositoryName, 'repo_identifier': information.repositoryIdentifier,
                    'enable_harvesting': information.enableHarvesting}
            registry_form= MyRegistryForm(data)
        except:
            registry_form = MyRegistryForm()

        context = RequestContext(request, {
            'registry_form': registry_form,
        })

        return HttpResponse(json.dumps({'template': template.render(context)}), content_type='application/javascript')


################################################################################
#
# Function Name: add_my_metadataFormat(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Add a new Metadata Format for the server
#
################################################################################
@login_required(login_url='/login')
def add_my_metadataFormat(request):
    if request.method == 'POST':
        form = MyMetadataFormatForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                #We add the metadata Format
                uri = OAI_HOST_URI + reverse("api_add_my_metadataFormat")
                #We retrieve information from the form
                if 'metadataPrefix' in request.POST:
                    metadataprefix = request.POST.get('metadataPrefix')

                if 'schema' in request.POST:
                    schema = request.POST.get('schema')

                #Call to the API to add the registry
                try:
                    req = requests.post(uri, {"metadataPrefix": metadataprefix,
                                              "schema": schema},#,
                                              #"metadataNamespace": namespace,
                                              #"xmlSchema": xml_data},
                                        auth=(OAI_USER, OAI_PASS))

                    #If the status is OK, sucess message
                    if req.status_code == status.HTTP_201_CREATED:
                        messages.add_message(request, messages.SUCCESS, 'Metadata Format added with success.')
                        return HttpResponse('CREATED')
                    #Else, we return a bad request response with the message provided by the API
                    else:
                        data = json.loads(req.text)
                        return HttpResponseBadRequest(data[APIMessage.label])
                except Exception as e:
                    return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
            except Exception as e:
                return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
        else:
            return HttpResponseBadRequest('Bad entries. Check your entry')


################################################################################
#
# Function Name: add_my_template_metadataFormat(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Add a new template Metadata Format for the server
#
################################################################################
@login_required(login_url='/login')
def add_my_template_metadataFormat(request):
    if request.method == 'POST':
        form = MyTemplateMetadataFormatForm(request.POST)
        if form.is_valid():
            try:
                #We add the tempalte metadata Format
                uri = OAI_HOST_URI + reverse("api_add_my_template_metadataFormat")
                #We retrieve information from the form
                if 'metadataPrefix' in request.POST:
                    metadataprefix = request.POST.get('metadataPrefix')
                else:
                    return HttpResponseBadRequest('Please enter a metadata prefix.')

                if 'template' in request.POST:
                    template = request.POST.get('template')
                else:
                    return HttpResponseBadRequest('Please choose a template.')

                #Call to the API to add the template metadata prefix
                try:
                    req = requests.post(uri, {"metadataPrefix": metadataprefix,
                                              "template": template},
                                        auth=(OAI_USER, OAI_PASS))
                    #If the status is OK, sucess message
                    if req.status_code == status.HTTP_201_CREATED:
                        messages.add_message(request, messages.SUCCESS, 'Metadata Format added with success.')
                        return HttpResponse('CREATED')
                    #Else, we return a bad request response with the message provided by the API
                    else:
                        data = json.loads(req.text)
                        return HttpResponseBadRequest(data[APIMessage.label])
                except Exception as e:
                    return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
            except Exception as e:
                return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
        else:
            return HttpResponseBadRequest('Bad entries. Check your entry')


################################################################################
#
# Function Name: delete_my_metadataFormat(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH Delete MyMetadata format
#
################################################################################
@login_required(login_url='/login')
def delete_my_metadataFormat(request):
    uri = OAI_HOST_URI + reverse("api_delete_my_metadataFormat")
    try:
        id = request.POST.get('MetadataFormatId')
    except ValueError:
        return HttpResponseBadRequest('Please provide an ID in order to delete the metadata format.')
    try:
        req = requests.post(uri, {"MetadataFormatId":id}, auth=(OAI_USER, OAI_PASS))

        #If the status is OK, sucess message
        if req.status_code == status.HTTP_200_OK:
            messages.add_message(request, messages.INFO, 'Metadata Format deleted with success.')
            return HttpResponse(json.dumps({}), content_type='application/javascript')
        #Else, we return a bad request response with the message provided by the API
        else:
            data = json.loads(req.text)
            return HttpResponseBadRequest(data[APIMessage.label])
    except Exception as e:
        return HttpResponseBadRequest('An error occurred. Please contact your administrator.')


################################################################################
#
# Function Name: update_my_metadataFormat(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH update my metadata format
#
# ################################################################################
@login_required(login_url='/login')
def update_my_metadataFormat(request):
    if request.method == 'POST':
        #UPDATE the registry
        try:
            uri = OAI_HOST_URI + reverse("api_update_my_metadataFormat")
            #Get all form information
            if 'id' in request.POST:
                id = request.POST.get('id')

            if 'metadataPrefix' in request.POST:
                metadataprefix = request.POST.get('metadataPrefix')

            #Call the API to update my metadataFormat
            try:
                req = requests.put(uri, { "id": id,
                                          "metadataPrefix": metadataprefix#,
                                          # "schema": schema,
                                          # "metadataNamespace": namespace
                                          },
                                        auth=(OAI_USER, OAI_PASS))

                #If the status is OK, sucess message
                if req.status_code == status.HTTP_200_OK:
                    messages.add_message(request, messages.INFO, 'Metadata Format edited with success.')
                    return HttpResponse(json.dumps({}), content_type='application/javascript')
                #Else, we return a bad request response with the message provided by the API
                else:
                    data = json.loads(req.text)
                    return HttpResponseBadRequest(data[APIMessage.label])
            except Exception as e:
                return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
        except Exception as e:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
    elif request.method == 'GET':
        #Build the template to render for the metadata format edition
        template = loader.get_template('oai_pmh/admin/form_my_metadata_format_edit.html')
        metadata_format_id = request.GET['metadata_format_id']
        try:
            information = OaiMyMetadataFormat.objects.get(pk=metadata_format_id)
            data = {'id': metadata_format_id, 'metadataPrefix': information.metadataPrefix, 'schema': information.schema,
                    'metadataNamespace': information.metadataNamespace}
            metadataformat_form = UpdateMyMetadataFormatForm(data)
        except:
            metadataformat_form = UpdateMyMetadataFormatForm()

        context = RequestContext(request, {
            'metadataformat_form': metadataformat_form,
        })

        return HttpResponse(json.dumps({'template': template.render(context)}), content_type='application/javascript')

################################################################################
#
# Function Name: add_my_set(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Add a new set for the server
#
################################################################################
@login_required(login_url='/login')
def add_my_set(request):
    if request.method == 'POST':
        try:
            #We add the set
            uri = OAI_HOST_URI + reverse("api_add_my_set")
            #We retrieve information from the form
            if 'setSpec' in request.POST:
                setSpec = request.POST.get('setSpec')

            if 'setName' in request.POST:
                setName = request.POST.get('setName')

            if 'description' in request.POST:
                description = request.POST.get('description')

            if 'templates' in request.POST:
                templates = request.POST.getlist('templates')
            else:
                templates = []

            #Call to the API to add the set
            try:
                req = requests.post(uri, {"setSpec": setSpec,
                                          "setName": setName,
                                          "description": description,
                                          'templates': templates},
                                    auth=(OAI_USER, OAI_PASS))
                #If the status is OK, sucess message
                if req.status_code == status.HTTP_201_CREATED:
                    messages.add_message(request, messages.SUCCESS, 'Set added with success.')
                    return HttpResponse('CREATED')
                #Else, we return a bad request response with the message provided by the API
                else:
                    data = json.loads(req.text)
                    return HttpResponseBadRequest(data[APIMessage.label])
            except Exception as e:
                return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
        except Exception as e:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')


################################################################################
#
# Function Name: delete_my_set(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH Delete MySet
#
################################################################################
@login_required(login_url='/login')
def delete_my_set(request):
    uri = OAI_HOST_URI + reverse("api_delete_my_set")
    try:
        id = request.POST.get('set_id')
    except ValueError:
        return HttpResponseBadRequest('Please provide an ID in order to delete the set.')
    try:
        req = requests.post(uri, {"set_id":id}, auth=(OAI_USER, OAI_PASS))

        #If the status is OK, sucess message
        if req.status_code == status.HTTP_200_OK:
            messages.add_message(request, messages.INFO, 'Set deleted with success.')
            return HttpResponse(json.dumps({}), content_type='application/javascript')
        #Else, we return a bad request response with the message provided by the API
        else:
            data = json.loads(req.text)
            return HttpResponseBadRequest(data[APIMessage.label])
    except Exception as e:
        return HttpResponseBadRequest('An error occurred. Please contact your administrator.')


################################################################################
#
# Function Name: update_my_set(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH update my set
#
# ################################################################################
@login_required(login_url='/login')
def update_my_set(request):
    if request.method == 'POST':
        #UPDATE the set
        try:
            uri = OAI_HOST_URI + reverse("api_update_my_set")
            #Get all form information
            if 'id' in request.POST:
                id = request.POST.get('id')
            if 'setSpec' in request.POST:
                setSpec = request.POST.get('setSpec')
            if 'setName' in request.POST:
                setName = request.POST.get('setName')
            if 'description' in request.POST:
                description = request.POST.get('description')
            if 'templates' in request.POST:
                templates = request.POST.getlist('templates')
            else:
                templates = []

            #Call the API to update my set
            try:
                req = requests.put(uri, { "id": id,
                                          "setSpec": setSpec,
                                          "setName": setName,
                                          "description": description,
                                          "templates": templates},
                                        auth=(OAI_USER, OAI_PASS))

                #If the status is OK, sucess message
                if req.status_code == status.HTTP_200_OK:
                    messages.add_message(request, messages.INFO, 'Set edited with success.')
                    return HttpResponse(json.dumps({}), content_type='application/javascript')
                #Else, we return a bad request response with the message provided by the API
                else:
                    data = json.loads(req.text)
                    return HttpResponseBadRequest(data[APIMessage.label])
            except Exception as e:
                return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
        except Exception as e:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
    elif request.method == 'GET':
        #Build the template to render for the set edition
        template = loader.get_template('oai_pmh/admin/form_my_set_edit.html')
        set_id = request.GET['set_id']
        try:
            set_form = UpdateMySetForm(id = set_id)
        except:
            set_form = UpdateMySetForm()

        context = RequestContext(request, {
            'set_form': set_form,
        })
        return HttpResponse(json.dumps({'template': template.render(context)}), content_type='application/javascript')


################################################################################
#
# Function Name: update_registry_harvest(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH update harvest configuration
#                Harvest records for the metadata formats and sets provided
#
# ################################################################################
@login_required(login_url='/login')
def update_registry_harvest(request):
    if request.method == 'POST':
        try:
            uri = OAI_HOST_URI + reverse("api_update_registry_harvest")
            #Get all form information
            if 'id' in request.POST:
                id = request.POST.get('id')
            if 'metadataFormats' in request.POST:
                metadataFormats = request.POST.getlist('metadataFormats')
            else:
                metadataFormats = []
            if 'sets' in request.POST:
                sets = request.POST.getlist('sets')
            else:
                sets = []
            #Call the API to update the harvest configuration
            try:
                req = requests.put(uri, { "id": id,
                                          "metadataFormats": metadataFormats,
                                          "sets": sets},
                                        auth=(OAI_USER, OAI_PASS))
                #If the status is OK, sucess message
                if req.status_code == status.HTTP_200_OK:
                    messages.add_message(request, messages.INFO, 'Data provider edited with success.')
                    return HttpResponse(json.dumps({}), content_type='application/javascript')
                #Else, we return a bad request response with the message provided by the API
                else:
                    data = json.loads(req.text)
                    return HttpResponseBadRequest(data[APIMessage.label])
            except Exception as e:
                return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
        except Exception as e:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
    elif request.method == 'GET':
        #Build the template to render for the harvest configuration
        template = loader.get_template('oai_pmh/admin/form_harvest.html')
        registry_id = request.GET['registry_id']
        try:
            #Configure if we have to harvest all metadataFormats and all sets
            harvest_form = SettingHarvestForm(id=registry_id)
        except:
            harvest_form = SettingHarvestForm()

        context = RequestContext(request, {
            'harvest_form': harvest_form,
        })
        return HttpResponse(json.dumps({'template': template.render(context)}), content_type='application/javascript')


################################################################################
#
# Function Name: update_registry_info(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH update Data Provider information
#
# ################################################################################
@login_required(login_url='/login')
def update_registry_info(request):
    if request.method == 'POST':
        try:
            #Get the ID
            registry_id = request.POST['registry_id']
            uri = OAI_HOST_URI + reverse("api_update_registry_info")
            #Call the API to update information
            try:
                requests.put(uri,
                                   {"registry_id": registry_id},
                                   auth=(OAI_USER, OAI_PASS))
                return HttpResponse(json.dumps({}), content_type='application/javascript')
            except Exception as e:
                return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
        except Exception as e:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')


################################################################################
#
# Function Name: check_harvest_data(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH Return the state of the registries (isUpdating), if we
#                updating Data Provider information
#
# ################################################################################
@login_required(login_url='/login')
def check_update_info(request):
    if request.method == 'POST':
        try:
            updateInfo = []
            #Get all registries
            registries = OaiRegistry.objects.only('id', 'isUpdating', 'name').all()
            #Build array with registry id and isHarvesting value
            for registry in registries:
                result_json = {}
                result_json['registry_id'] = str(registry.id)
                result_json['isHarvesting'] = registry.isUpdating
                result_json['name'] = registry.name
                updateInfo.append(result_json)

            return HttpResponse(json.dumps(updateInfo), content_type='application/javascript')
        except Exception as e:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')


################################################################################
#
# Function Name: oai_pmh_conf_xslt(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   OAI-PMH Return the state of the registries (isHarvesting)
#
# ################################################################################
@login_required(login_url='/login')
def oai_pmh_conf_xslt(request):
    if request.method == 'POST':
        uri = OAI_HOST_URI + reverse("api_oai_pmh_conf_xslt")
        try:
            errors = []
            AssociateFormSet = formset_factory(AssociateXSLT, extra=3)
            article_formset = AssociateFormSet(request.POST)
            if article_formset.is_valid():
                for f in article_formset:
                    cd = f.cleaned_data
                    myMetadataFormat_id = cd.get('oai_my_mf_id')
                    template_id = cd.get('template_id')
                    activated = cd.get('activated')
                    xslt = cd.get('oai_pmh_xslt_file')
                    xslt_id = None
                    if xslt:
                        xslt_id = xslt.id
                    req = requests.post(uri, {"template_id": template_id,
                                              "my_metadata_format_id": myMetadataFormat_id,
                                              "xslt_id": xslt_id,
                                              "activated": activated}, auth=(OAI_USER, OAI_PASS))
                    #If sth wrong happened, we keep the error
                    if req.status_code != status.HTTP_200_OK:
                        data = json.loads(req.text)
                        errors.append(data[APIMessage.label])

                #Good treatment
                if len(errors) == 0:
                    messages.add_message(request, messages.INFO, 'XSLT edited with success.')
                    return HttpResponse(json.dumps({}), content_type='application/javascript')
                #Else, we return a bad request response with the message provided by the API
                else:
                    return HttpResponseBadRequest(errors)
            else:
                return HttpResponseBadRequest([x['__all__'] for x in article_formset.errors if '__all__' in x],
                                              content_type='application/javascript')
        except Exception:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
    else:
        template = loader.get_template('oai_pmh/admin/oai_pmh_conf_xslt.html')
        template_id = request.GET.get('id', None)
        if template_id is not None:
            templateName = Template.objects.only('title').get(pk=template_id).title
            allXsltFiles = OaiXslt.objects.all()
            myMetadataFormats = OaiMyMetadataFormat.objects(isTemplate=False or None).all()

            infos= dict()
            for myMetadataFormat in myMetadataFormats:
                try:
                    obj = OaiTemplMfXslt.objects(template=template_id, myMetadataFormat=myMetadataFormat).get()
                    infos[myMetadataFormat] = {'oai_pmh_xslt_file': obj.xslt.id if obj.xslt else None,
                                               'activated': obj.activated}
                except:
                    infos[myMetadataFormat] = {'oai_pmh_xslt_file': None, 'activated': False}

            AssociateFormSet = formset_factory(AssociateXSLT, extra=0)
            init = [{'template_id': template_id, 'oai_my_mf_id': x.id, 'oai_name': x.metadataPrefix,
                     'oai_pmh_xslt_file': infos[x]['oai_pmh_xslt_file'], 'activated': infos[x]['activated']}
                    for x in myMetadataFormats]
            formset = AssociateFormSet(initial=init)

            context = RequestContext(request,{
                'metadataFormats': myMetadataFormats,
                'xsltFiles': allXsltFiles,
                'formSet': formset,
                'templateName': templateName
            })

            return HttpResponse(template.render(context))


################################################################################
#
# Function Name: manage_oai_pmh_xslt(request)
# Inputs:        request -
# Outputs:       Manage OAI-PMH XSLT Page
# Exceptions:    None
# Description:   Page that allows to upload new OAI-PMH XSLT and manage the existing ones
#
################################################################################
@staff_member_required
def manage_oai_pmh_xslt(request, id=None):
    if request.method == 'POST':
        try:
            uri = OAI_HOST_URI + reverse("api_upload_oai_pmh_xslt")
            upload_form = UploadOaiPmhXSLTForm(request.POST, request.FILES)
            name = upload_form['oai_name'].value()
            name = name.strip(' \t\n\r')
            xml_file = upload_form['oai_pmh_xslt_file'].value()
            # put the cursor at the beginning of the file
            xml_file.seek(0)
            # read the content of the file
            xml_data = xml_file.read()
            # check XML data or not?
            try:
                etree.fromstring(xml_data)
            except XMLSyntaxError:
                return HttpResponseBadRequest('Uploaded File is not well formed XML.')
            #No exceptions, we can add it in DB
            req = requests.post(uri, {"name": name, 'filename': xml_file.name, 'content': xml_data},
                                        auth=(OAI_USER, OAI_PASS))
            #If the status is OK, sucess message
            if req.status_code == status.HTTP_201_CREATED:
                messages.add_message(request, messages.INFO, 'XSLT added with success.')
                return HttpResponse(json.dumps({}), content_type='application/javascript')
            #Else, we return a bad request response with the message provided by the API
            else:
                data = json.loads(req.text)
                return HttpResponseBadRequest(data[APIMessage.label])
        except Exception:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
    else:
        return HttpResponseBadRequest('This method should not be called on GET.')

################################################################################
#
# Function Name: delete_oai_pmh_xslt(request)
# Inputs:        request -
# Outputs:       Delete OAI-PMH XSLT document
# Exceptions:    None
# Description:   Page that allows to delete an OAI-PMH XSLT
#
################################################################################
@staff_member_required
def delete_oai_pmh_xslt(request):
    if request.method == 'POST':
        uri = OAI_HOST_URI + reverse("api_delete_oai_pmh_xslt")
        try:
            xslt_id = request.POST['xslt_id']
            req = requests.post(uri, {"xslt_id": xslt_id}, auth=(OAI_USER, OAI_PASS))
            #If the status is OK, sucess message
            if req.status_code == status.HTTP_200_OK:
                messages.add_message(request, messages.INFO, 'XSLT deleted with success.')
                return HttpResponse(json.dumps({}), content_type='application/javascript')
            #Else, we return a bad request response with the message provided by the API
            else:
                data = json.loads(req.text)
                return HttpResponseBadRequest(data[APIMessage.label])
        except Exception:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')


################################################################################
#
# Function Name: edit_oai_pmh_xslt(request)
# Inputs:        request -
# Outputs:       Edit XSLT
# Exceptions:    None
# Description:   Page that allows to edit an existing XSLT
#
################################################################################
@staff_member_required
def edit_oai_pmh_xslt(request, id=None):
    if request.method == 'POST':
        uri = OAI_HOST_URI + reverse("api_edit_oai_pmh_xslt")
        try:
            xslt_id = request.POST['object_id']
            new_name = request.POST['new_name']
            new_name = new_name.strip(' \t\n\r')
            req = requests.put(uri, {"xslt_id": xslt_id, "name": new_name}, auth=(OAI_USER, OAI_PASS))
            if req.status_code == status.HTTP_200_OK:
                messages.add_message(request, messages.INFO, 'XSLT edited with success.')
                return HttpResponse(json.dumps({}), content_type='application/javascript')
            #Else, we return a bad request response with the message provided by the API
            else:
                data = json.loads(req.text)
                return HttpResponseBadRequest(data[APIMessage.label])
        except Exception:
            return HttpResponseBadRequest('An error occurred. Please contact your administrator.')
