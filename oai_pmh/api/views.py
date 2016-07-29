################################################################################
#
# File Name: views.py
# Application: Informatics Core
# Description:
#
# Author: Pierre Francois RIGODIAT
#         pierre-francois.rigodiat@nist.gov
#
#         Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

# REST Framework
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
# OAI-PMH
from sickle import Sickle
from sickle.models import Set, MetadataFormat, Record, Identify
# Serializers
from oai_pmh.api.serializers import RegistrySerializer, ListRecordsSerializer, RegistryURLSerializer, RecordSerializer,\
    IdentifySerializer, UpdateRegistrySerializer,\
    UpdateMyRegistrySerializer, MyMetadataFormatSerializer, DeleteMyMetadataFormatSerializer,\
    UpdateMyMetadataFormatSerializer, GetRecordSerializer, UpdateMySetSerializer, DeleteMySetSerializer,\
    MySetSerializer, MyTemplateMetadataFormatSerializer, DeleteXSLTSerializer, OaiConfXSLTSerializer, \
    OaiXSLTSerializer, RegistryIdSerializer, UpdateRegistryHarvestSerializer, AddRegistrySerializer,\
    ListIdentifierSerializer, HarvestSerializer, UpdateRegistryInfo, EditXSLTSerializer
# Models
from mgi.models import OaiRegistry
import os
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
OAI_HOST_URI = settings.OAI_HOST_URI
import requests
from lxml import etree
from oai_pmh.api.exceptions import OAIAPIException, OAIAPILabelledException, OAIAPISerializeLabelledException
from oai_pmh.api.messages import APIMessage
from admin_mdcs.models import api_permission_required, api_staff_member_required
import oai_pmh.rights as RIGHTS
from oai_pmh.api.models import objectIdentifyByURL, listObjectSetsByURL, listObjectMetadataFormatsByURL,\
    add_registry as add_registry_model, update_registry as update_registry_model,\
    delete_registry as delete_registry_model, deactivate_registry as deactivate_registry_model,\
    reactivate_registry as reactivate_registry_model, update_my_registry as update_my_registry_model,\
    add_my_metadataFormat as add_my_metadataFormat_model,\
    add_my_template_metadataFormat as add_my_template_metadataFormat_model, \
    delete_my_metadataFormat as delete_my_metadataFormat_model,\
    update_my_metadataFormat as update_my_metadataFormat_model, add_my_set as add_my_set_model,\
    delete_my_set as delete_my_set_model, update_my_set as update_my_set_model,\
    update_registry_harvest as update_registry_harvest_model,\
    update_registry_info as update_registry_info_model, oai_pmh_conf_xslt as oai_pmh_conf_xslt_model,\
    upload_oai_pmh_xslt as upload_oai_pmh_xslt_model, delete_oai_pmh_xslt as delete_oai_pmh_xslt_model,\
    edit_oai_pmh_xslt as edit_oai_pmh_xslt_model, getListRecords as getListRecords_model,\
    harvest as harvest_model

################################################################################
#
# Function Name: add_registry(request)
# Inputs:        request -
# Outputs:       201 Registry created.
# Exceptions:    400 Error connecting to database.
#                400 [List of missing required fields].
#                400 An error occured when trying to save document.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                409 Registry already exists
#                500 Internal error
# Description:   OAI-PMH Add Registry
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def add_registry(request):
    """
    POST http://localhost/oai_pmh/api/add/registry
    POST data query='{"url":"value","harvestrate":"number", "harvest":"True or False"}'
    """
    try:
        #Serialization of the input data
        serializer = AddRegistrySerializer(data=request.DATA)
        #If all fields are okay
        if serializer.is_valid():
            #Check the URL
            url = request.DATA['url']
            harvestrate = request.DATA['harvestrate']
            harvest = request.DATA['harvest'] == 'True'
            return add_registry_model(url, harvestrate, harvest)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: select_all_registries(request)
# Inputs:        request -
# Outputs:       200 Found registries.
# Exceptions:    400 Error connecting to database.
#                401 Unauthorized.
# Description:   OAI-PMH Select All Registries
#
################################################################################
@api_view(['GET'])
@api_permission_required(RIGHTS.oai_pmh_content_type, RIGHTS.oai_pmh_access)
def select_all_registries(request):
    """
    GET http://localhost/oai_pmh/api/select/all/registries
    """
    try:
        try:
            registry = OaiRegistry.objects.all()
        except Exception:
            raise OAIAPILabelledException(message='Error connecting to database.', status=status.HTTP_400_BAD_REQUEST)

        serializer = RegistrySerializer(registry)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: select_registry(request)
# Inputs:        request -
# Outputs:       200 Found registry.
# Exceptions:    400 Error connecting to database.
#                400 No record found matching the identifier: [identifier]
#                400 Serializer failed validation.
#                401 Unauthorized.
#                500 An error occurred when attempting to identify resource.
# Description:   OAI-PMH Select Registry
#
################################################################################
@api_view(['GET'])
@api_permission_required(RIGHTS.oai_pmh_content_type, RIGHTS.oai_pmh_access)
def select_registry(request):
    """
    GET http://localhost/oai_pmh/api/select/registry
    name: string
    """
    try:
        if 'name' in request.GET:
            name = request.GET['name']
        else:
            content = {'name':['This field is required.']}
            raise OAIAPIException(message=content, status=status.HTTP_400_BAD_REQUEST)
        try:
            registry = OaiRegistry.objects.get(name=name)
        except Exception as e:
            raise OAIAPILabelledException(message='No registry found with the given parameters.',
                                          status=status.HTTP_404_NOT_FOUND)

        serializer = RegistrySerializer(registry)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: update_registry(request)
# Inputs:        request -
# Outputs:       200 Registry updated.
# Exceptions:    400 Error connecting to database.
#                400 Unable to update record.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                404 No registry found with the given identity.
# Description:   OAI-PMH Update Registry
#
################################################################################
@api_view(['PUT'])
@api_staff_member_required()
def update_registry(request):
    """
    PUT http://localhost/oai_pmh/api/update/registry
    PUT data query='{"id":"value", "harvestrate":"value", "harvest":"True or False"}'
    id: string
    """
    try:
        #Serialization of the input data
        serializer = UpdateRegistrySerializer(data=request.DATA)
        #If it's valid
        if serializer.is_valid():
            #We retrieve all information
            id = request.DATA['id']
            harvestrate = request.DATA['harvestrate']
            harvest = request.DATA['harvest'] == 'True'
            return update_registry_model(id, harvestrate, harvest)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: update_my_registry(request)
# Inputs:        request -
# Outputs:       201 Registry updated.
# Exceptions:    400 Error connecting to database.
#                400 [Identifier] not found in request.
#                400 Unable to update record.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                404 No registry found with the given identity.
# Description:   OAI-PMH Update Registry
#
################################################################################
@api_view(['PUT'])
@api_staff_member_required()
def update_my_registry(request):
    """
    PUT http://localhost/oai_pmh/api/update/my-registry
    PUT data query='{"repositoryName":"value", "enableHarvesting":"True or False"}'
    """
    try:
        #Serialization of the input data
        serializer = UpdateMyRegistrySerializer(data=request.DATA)
        #If it's valid
        if serializer.is_valid():
            repositoryName = request.DATA['repositoryName']
            enableHarvesting = request.DATA['enableHarvesting'] == 'True'
            return update_my_registry_model(repositoryName, enableHarvesting)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: delete_registry(request)
# Inputs:        request -
# Outputs:       200 Record deleted.
# Exceptions:    400 Error connecting to database.
#                400 [Name] not found in request.
#                400 Unspecified.
#                401 Unauthorized.
#                404 No record found with the given identity.
# Description:   OAI-PMH Delete Registry
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def delete_registry(request):
    """
    POST http://localhost/oai_pmh/api/delete/registry
    POST data query='{"RegistryId":"value"}'
    """
    try:
        #Serialization of the input data
        serializer = RegistryIdSerializer(data=request.DATA)
        #If it's valid
        if serializer.is_valid():
            #Get the ID
            id = request.DATA['RegistryId']
            return delete_registry_model(id)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: deactivate_registry(request)
# Inputs:        request -
# Outputs:       200 Record deactivated.
# Exceptions:    400 Error connecting to database.
#                400 [RegistryId] not found in request.
#                401 Unauthorized.
#                404 No record found with the given identity.
# Description:   OAI-PMH Deactivate Registry
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def deactivate_registry(request):
    """
    POST http://localhost/oai_pmh/api/deactivate/registry
    POST data query='{"RegistryId":"value"}'
    """
    try:
        #Serialization of the input data
        serializer = RegistryIdSerializer(data=request.DATA)
        #If it's valid
        if serializer.is_valid():
            #Get the ID
            id = request.DATA['RegistryId']
            return deactivate_registry_model(id)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: reactivate_registry(request)
# Inputs:        request -
# Outputs:       200 Record deactivated.
# Exceptions:    400 Error connecting to database.
#                400 [RegistryId] not found in request.
#                401 Unauthorized.
#                404 No record found with the given identity.
# Description:   OAI-PMH Delete Registry
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def reactivate_registry(request):
    """
    POST http://localhost/oai_pmh/api/reactivate/registry
    POST data query='{"RegistryId":"value"}'
    """
    try:
        #Serialization of the input data
        serializer = RegistryIdSerializer(data=request.DATA)
        #If it's valid
        if serializer.is_valid():
            #Get the ID
            id = request.DATA['RegistryId']
            return reactivate_registry_model(id)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: getRecord(request)
# Inputs:        request -
# Outputs:       200 Response successful.
# Exceptions:    400 Error in Metadata Prefix value.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                500 An error occurred when attempting to retrieve record.
# Description:   OAI-PMH Get Record
#
################################################################################
@api_view(['POST'])
@api_permission_required(RIGHTS.oai_pmh_content_type, RIGHTS.oai_pmh_access)
def getRecord(request):
    """
    POST http://localhost/oai_pmh/api/rest/getrecord
    POST data query='{"url":"value", "identifier":"value", "metadataprefix":"value"}'
    """
    try:
        serializer = GetRecordSerializer(data=request.DATA)
        if serializer.is_valid():
            url = request.DATA['url']
            identifier = request.DATA['identifier']
            metadataprefix = request.DATA['metadataprefix']
            sickle = Sickle(url)
            grResponse = sickle.GetRecord(metadataPrefix=metadataprefix, identifier=identifier)
            record = Record(grResponse.xml)
            rtn=[]
            rtn.append({"identifier": record.header.identifier,
                      "datestamp": record.header.datestamp,
                      "deleted": record.deleted,
                      "sets": record.header.setSpecs,
                      "metadataPrefix": metadataprefix,
                      "metadata": etree.tostring(record.xml.find('.//' + '{http://www.openarchives.org/OAI/2.0/}' +
                                                                 'metadata/')) if not record.deleted else None,
                      "raw": record.raw})

            serializer = RecordSerializer(rtn)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled('An error occurred when attempting to retrieve record. %s'%e)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: objectIdentify(request)
# Inputs:        request -
# Outputs:       200 Response successful.
# Exceptions:    400 Error getting URL.
#                401 Unauthorized.
#                500 An error occurred when attempting to identify resource.
# Description:   OAI-PMH Identify
#
################################################################################
@api_view(['POST'])
@api_permission_required(RIGHTS.oai_pmh_content_type, RIGHTS.oai_pmh_access)
def objectIdentify(request):
    """
    POST http://localhost/oai_pmh/api/objectidentify
    POST data query='{"url":"value"}'
    """
    try:
        serializer = IdentifySerializer(data=request.DATA)
        if serializer.is_valid():
            url = request.DATA['url']
            req = objectIdentifyByURL(url)
            return Response(req.data, status=req.status_code)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception:
        content = APIMessage.getMessageLabelled('An error occurred when attempting to identify resource')
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: listObjectMetadataFormats(request)
# Inputs:        request -
# Outputs:       200 Response successful.
# Exceptions:    204 No metadata formats
#                400 Error in URL value.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                500 An error occurred when attempting to identify resource.
# Description:   OAI-PMH List Object Metadata Formats
#
################################################################################
@api_view(['POST'])
@api_permission_required(RIGHTS.oai_pmh_content_type, RIGHTS.oai_pmh_access)
def listObjectMetadataFormats(request):
    """
    POST http://localhost/oai_pmh/api/listobjectmetadataformats
    POST data query='{"url":"value"}'
    """
    try:
        serializer = IdentifySerializer(data=request.DATA)
        if serializer.is_valid():
            url = request.DATA['url']
            req = listObjectMetadataFormatsByURL(url)
            if req.status_code != status.HTTP_200_OK:
                raise OAIAPILabelledException(message=req.data[APIMessage.label], status=req.status_code)

            return Response(req.data, status=status.HTTP_200_OK)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled('An error occurred when attempting to identify resource')
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: listObjectSets(request)
# Inputs:        request -
# Outputs:       200 Response successful.
#                204 No Sets
# Exceptions:    400 Error(s) in required values value.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                500 An error occurred when attempting to identify resource.
# Description:   OAI-PMH List object Sets
#
################################################################################
@api_view(['POST'])
@api_permission_required(RIGHTS.oai_pmh_content_type, RIGHTS.oai_pmh_access)
def listObjectSets(request):
    """
    POST http://localhost/oai_pmh/api/listObjectSets
    POST data query='{"url":"value"}'
    """
    try:
        serializer = IdentifySerializer(data=request.DATA)
        if serializer.is_valid():
            url = request.DATA['url']
            req = listObjectSetsByURL(url)
            if req.status_code != status.HTTP_200_OK:
                raise OAIAPILabelledException(message=req.data[APIMessage.label], status=req.status_code)

            return Response(req.data, status=status.HTTP_200_OK)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled('An error occurred when attempting to identify resource')
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: listIdentifiers(request)
# Inputs:        request -
# Outputs:       200 Response successful.
# Exceptions:    400 Error(s) in required values value.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                500 An error occurred when attempting to identify resource.
# Description:   OAI-PMH List Identifiers
#
################################################################################
@api_view(['POST'])
@api_permission_required(RIGHTS.oai_pmh_content_type, RIGHTS.oai_pmh_access)
def listIdentifiers(request):
    """
    POST http://localhost/oai_pmh/api/listidentifiers
    POST data query='{"url":"value", "metadataprefix":"value"}' optional {"set":"value"}
    """
    try:
        serializer = RegistryURLSerializer(data=request.DATA)
        if serializer.is_valid():
            url = request.DATA['url']
            metadataprefix = request.DATA['metadataprefix']
            setH = request.DATA.get('set', None)
            sickle = Sickle(url)
            rsp = sickle.ListIdentifiers(metadataPrefix=metadataprefix, set=setH)
            rtn = []
            try:
                while True:
                    rtn.append( dict(rsp.next()) )
            except StopIteration:
                pass

            serializer = ListIdentifierSerializer(rtn)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled('An error occurred when attempting to identify resource: %s'%e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: getData(request)
# Inputs:        request -
# Outputs:       OAI_PMH response.
#                400 Error(s) in required values value.
#                401 Unauthorized.
#                404 Server not found.
#                500 Malformed URL.
#                500 An error occurred when attempting to identify resource.
# Description:   OAI_PMH response.
#
################################################################################
@api_view(['POST'])
@api_permission_required(RIGHTS.oai_pmh_content_type, RIGHTS.oai_pmh_access)
def getData(request):
    """
    POST http://localhost/oai_pmh/api/getdata/
    POST data query='{"url":"value"}'
    """
    try:
        serializer = IdentifySerializer(data=request.DATA)
        if serializer.is_valid():
            url = request.POST['url']
            if str(url).__contains__('?'):
                registryURl = str(url).split('?')[0]
                #Check if the OAI Registry is available
                sickle = Sickle(registryURl)
                sickle.Identify()
                http_response = requests.get(url)
                if http_response.status_code == status.HTTP_200_OK:
                    return Response(http_response.text, status=status.HTTP_200_OK)
                else:
                    raise OAIAPIException(message='An error occurred.', status=http_response.status_code)
            else:
                raise OAIAPIException(message='An error occurred, url malformed.', status=status.HTTP_400_BAD_REQUEST)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except requests.HTTPError, err:
        content = APIMessage.getMessageLabelled(err.message)
        return Response(content, status=err.response.status_code)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = 'An error occurred when attempting to identify resource: %s'%e.message
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: harvest(request)
# Inputs:        request -
# Outputs:       200 Response successful.
# Exceptions:    400 Error(s) in required values value.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                500 An error occurred when attempting to identify resource.
# Description:   OAI-PMH List Records
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def harvest(request):
    """
    POST http://localhost/oai_pmh/api/harvest
    POST data query='{"registry_id":"value"}'
    """
    #List of errors
    allErrors = []
    try:
        serializer = HarvestSerializer(data=request.DATA)
        if serializer.is_valid():
            registry_id = request.DATA['registry_id']
            return harvest_model(registry_id)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled('An error occurred during the harvest process: %s'%e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: update_registry_harvest(request)
# Inputs:        request -
# Outputs:       200 Registry updated.
# Exceptions:    400 Error connecting to database.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                500 An error occurred when attempting to identify resource.
# Description:   OAI-PMH Update Registry Harvest configuration.
#                Harvest records for the metadata formats and sets provided
#
################################################################################
@api_view(['PUT'])
@api_staff_member_required()
def update_registry_harvest(request):
    """
    PUT http://localhost/oai_pmh/api/update/registry-harvest
    PUT data query='{"id":"value", "metadataFormats":["id1", "id2"..], "sets":["id1", "id2"..]}'
    id: string
    """
    try:
        #Serialization of the input data
        serializer = UpdateRegistryHarvestSerializer(data=request.DATA)
        #If it's valid
        if serializer.is_valid():
            id = request.DATA['id']
            sets = request.DATA.get('sets')
            metadataFormats = request.DATA.get('metadataFormats')
            return update_registry_harvest_model(id, sets, metadataFormats)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors,
                                          status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled('Unable to update the harvest configuration for the registry.')
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: update_registry_info(request)
# Inputs:        request -
# Outputs:       200 Registry updated.
# Exceptions:    400 Error connecting to database.
#                400 [Identifier] not found in request.
#                400 Unable to update record.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                404 No registry found with the given identity.
# Description:   OAI-PMH update Data Provider information
#
################################################################################
@api_view(['PUT'])
@api_staff_member_required()
def update_registry_info(request):
    """
    PUT http://localhost/oai_pmh/api/update/registry-info
    PUT data query='{"registry_id":"value"}'
    id: string
    """
    try:
        #Serialization of the input data
        serializer = UpdateRegistryInfo(data=request.DATA)
        if serializer.is_valid():
            registry_id = request.DATA['registry_id']
            return update_registry_info_model(registry_id)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors,
                                          status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled('Unable to update the registry information.')
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: listRecords(request)
# Inputs:        request -
# Outputs:       200 Response successful.
# Exceptions:    400 Error(s) in required values value.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                500 An error occurred when attempting to identify resource.
# Description:   OAI-PMH List Records
#
################################################################################
@api_view(['POST'])
@api_permission_required(RIGHTS.oai_pmh_content_type, RIGHTS.oai_pmh_access)
def listObjectAllRecords(request):
    """
    POST http://localhost/oai_pmh/api/listobjectrecords
    POST data query='{"url":"value", "metadataprefix":"value"}'
    optional: '{"set":"value", "fromDate":"date", "untilDate":"date"}'
    """
    try:
        serializer = ListRecordsSerializer(data=request.DATA)
        if serializer.is_valid():
            url = request.DATA['url']
            metadataPrefix = request.DATA.get('metadataprefix', None)
            set_h = request.DATA.get('set', None)
            fromDate = request.DATA.get('fromDate', None)
            untilDate = request.DATA.get('untilDate', None)
            resumptionToken = request.DATA.get('resumptionToken', None)
            http_response, token = getListRecords_model(url=url, metadataPrefix=metadataPrefix,
                                                  resumptionToken=resumptionToken, set_h=set_h,
                                                  fromDate=fromDate, untilDate=untilDate)
            if http_response.status_code == status.HTTP_200_OK:
                rtn = http_response.data
            #Else, we return a bad request response with the message provided by the API
            else:
                content = http_response.data[APIMessage.label]
                raise OAIAPILabelledException(message=content, status=http_response.status_code)
            serializer = RecordSerializer(rtn)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled('An error occurred when attempting to identify resource: %s'%e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: add_my_metadataFormat(request)
# Inputs:        request -
# Outputs:       201 Registry updated.
# Exceptions:    400 Error connecting to database.
#                400 [Identifier] not found in request.
#                400 Unable to update record.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                404 No registry found with the given identity.
#                409 Metadata format already exists
# Description:   OAI-PMH Add a new my_metadataFormat
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def add_my_metadataFormat(request):
    """
    POST http://localhost/oai_pmh/api/add/my-metadataformat
    POST data query='{"metadataPrefix":"value", "schema":"schemaURL"}'
    """
    try:
        serializer = MyMetadataFormatSerializer(data=request.DATA)
        if serializer.is_valid():
            metadataprefix = request.DATA['metadataPrefix']
            schema = request.DATA['schema']
            return add_my_metadataFormat_model(metadataprefix, schema)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception, e:
        content = APIMessage.getMessageLabelled('Unable to add the new metadata format. \n%s'%e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: add_my_template_metadataFormat(request)
# Inputs:        request -
# Outputs:       201 Registry updated.
# Exceptions:    400 Error connecting to database.
#                400 [Identifier] not found in request.
#                400 Unable to update record.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                404 No template found with the given identity.
# Description:   OAI-PMH Add a new template_my_metadataFormat
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def add_my_template_metadataFormat(request):
    """
    POST http://localhost/oai_pmh/api/add/my-template-metadataformat
    POST data query='{"metadataPrefix":"value", "template":"templateID"}'
    """
    try:
    #Serialization of the input data
        serializer = MyTemplateMetadataFormatSerializer(data=request.DATA)
        #If it's valid
        if serializer.is_valid():
            metadataprefix = request.DATA['metadataPrefix']
            template = request.DATA['template']
            return add_my_template_metadataFormat_model(metadataprefix, template)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception, e:
        content = APIMessage.getMessageLabelled('Unable to add the new metadata format. \n%s'%e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: delete_my_metadataFormat(request)
# Inputs:        request -
# Outputs:       204 Record deleted.
# Exceptions:    400 Error connecting to database.
#                400 [Name] not found in request.
#                400 Unspecified.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                404 No record found with the given identity.
# Description:   OAI-PMH Delete my_metadataFormat
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def delete_my_metadataFormat(request):
    """
    POST http://localhost/oai_pmh/api/delete/my-metadataFormat
    POST data query='{"MetadataFormatId":"value"}'
    """
    try:
        serializer = DeleteMyMetadataFormatSerializer(data=request.DATA)
        if serializer.is_valid():
            id = request.DATA['MetadataFormatId']
            return delete_my_metadataFormat_model(id)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: update_my_metadataFormat(request)
# Inputs:        request -
# Outputs:       201 Registry updated.
# Exceptions:    400 Error connecting to database.
#                400 [Identifier] not found in request.
#                400 Unable to update record.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                404 No registry found with the given identity.
# Description:   OAI-PMH Update my_metadataFormat
#
################################################################################
@api_view(['PUT'])
@api_staff_member_required()
def update_my_metadataFormat(request):
    """
    PUT http://localhost/oai_pmh/api/update/my-metadataFormat
    PUT data query='{"id":"value", "metadataPrefix":"value"}'
    """
    try:
        serializer = UpdateMyMetadataFormatSerializer(data=request.DATA)
        if serializer.is_valid():
            #We retrieve all information
            id = request.DATA['id']
            metadataprefix = request.DATA['metadataPrefix']
            return update_my_metadataFormat_model(id, metadataprefix)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: add_my_set(request)
# Inputs:        request -
# Outputs:       201 Set updated.
# Exceptions:    400 Error connecting to database..
#                400 Unable to update record.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                409 The set already exists
# Description:   OAI-PMH Add new set
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def add_my_set(request):
    """
    PUT http://localhost/oai_pmh/api/add/my-set
    PUT data query='{"setSpec":"value", "setName":"value", templates:["id1", "id2"..]}'
    optional: {'description':'value'}"
    """
    try:
        #Serialization of the input data
        serializer = MySetSerializer(data=request.DATA)
        #If it's valid
        if serializer.is_valid():
            setSpec = request.DATA['setSpec']
            setName = request.DATA['setName']
            description = request.DATA.get('description', None)
            templates = request.DATA.getlist('templates')
            return add_my_set_model(setSpec, setName, templates, description)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: delete_my_set(request)
# Inputs:        request -
# Outputs:       204 Record deleted.
# Exceptions:    400 Error connecting to database.
#                400 [Name] not found in request.
#                400 Unspecified.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                404 No record found with the given identity.
# Description:   OAI-PMH Delete my_set
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def delete_my_set(request):
    """
    POST http://localhost/oai_pmh/api/delete/my-set
    POST data query='{"set_id":"value"}'
    """
    try:
        serializer = DeleteMySetSerializer(data=request.DATA)
        if serializer.is_valid():
            id = request.DATA['set_id']
            return delete_my_set_model(id)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: update_my_set(request)
# Inputs:        request -
# Outputs:       200 Set updated.
# Exceptions:    400 Error connecting to database.
#                400 [Identifier] not found in request.
#                400 Unable to update record.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                404 No set found with the given identity.
# Description:   OAI-PMH Update my_metadataFormat
#
################################################################################
@api_view(['PUT'])
@api_staff_member_required()
def update_my_set(request):
    """
    PUT http://localhost/oai_pmh/api/update/my-set
    PUT data query='{"id":"value", "setSpec":"value","setName":"value"}'
    optional: '{"description":"value", "templates":["id1", "id2"..]}'
    """
    try:
        #Serialization of the input data
        serializer = UpdateMySetSerializer(data=request.DATA)
        #If it's valid
        if serializer.is_valid():
            #We retrieve all information
            id = request.DATA['id']
            setSpec = request.DATA['setSpec']
            setName = request.DATA['setName']
            description = request.DATA.get('description', None)
            templates = request.DATA.get('templates', None)
            return update_my_set_model(id, setSpec, setName, templates, description)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: upload_oai_pmh_xslt(request)
# Inputs:        request -
# Outputs:       201 XSLT created.
# Exceptions:    400 Error connecting to database.
#                400 [name] not found in request.
#                400 [filename] not found in request.
#                400 [content] not found in request.
#                400 Unspecified.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                409 XSLT conf already exists
#                500 An error occurred.
# Description:   OAI-PMH Upload an XSLT for OAI-PMH
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def upload_oai_pmh_xslt(request):
    """
    POST http://localhost/oai_pmh/api/upload/xslt
    POST data query='{"name": ""value, "filename": "value", "content": "value"}
    """
    try:
        serializer = OaiXSLTSerializer(data=request.DATA)
        if serializer.is_valid():
            name = request.DATA['name']
            filename = request.DATA['filename']
            xmlStr = request.DATA['content']
            return upload_oai_pmh_xslt_model(name, filename, xmlStr)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: delete_oai_pmh_xslt(request)
# Inputs:        request -
# Outputs:       200 XSLT deleted.
# Exceptions:    400 Error connecting to database.
#                400 [xslt_id] not found in request.
#                400 Unspecified.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                404 No record found with the given identity.
#                500 An error occurred.
# Description:   OAI-PMH Delete OAI-PMH XSLT
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def delete_oai_pmh_xslt(request):
    """
    POST http://localhost/oai_pmh/api/delete/xslt
    POST data query='{"xslt_id":"value"}'
    """
    try:
        serializer = DeleteXSLTSerializer(data=request.DATA)
        if serializer.is_valid():
            id = request.DATA['xslt_id']
            return delete_oai_pmh_xslt_model(id)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: edit_oai_pmh_xslt(request)
# Inputs:        request -
# Outputs:       200 XSLT edited.
# Exceptions:    400 Error connecting to database.
#                400 [xslt_id] not found in request.
#                400 [Name] not found in request.
#                400 Unspecified.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                404 No record found with the given identity.
#                409 XSLT name already exists.
#                500 An error occurred.
# Description:   OAI-PMH Edit OAI-PMH XSLT
#
################################################################################
@api_view(['PUT'])
@api_staff_member_required()
def edit_oai_pmh_xslt(request):
    """
    POST http://localhost/oai_pmh/api/edit/xslt
    POST data query='{"xslt_id":"value", "name": "value"}'
    """
    try:
        serializer = EditXSLTSerializer(data=request.DATA)
        if serializer.is_valid():
            #Get the ID
            id = request.DATA['xslt_id']
            new_name = request.DATA['name']
            return edit_oai_pmh_xslt_model(id, new_name)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: oai_pmh_conf_xslt(request)
# Inputs:        request -
# Outputs:       200 OAI-PMH configured.
# Exceptions:    400 Error connecting to database.
#                400 [template_id] not found in request.
#                400 [my_metadata_format_id] not found in request.
#                400 [activated] not found in request.
#                400 Unspecified.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                500 An error occurred.
# Description:   OAI-PMH Edit OAI-PMH XSLT configuration.
#                Associate the Metadata Format with the template and provide an XSLT for the transformation toward
#                the metadata format schema.
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def oai_pmh_conf_xslt(request):
    """
    POST http://localhost/oai_pmh/api/oai-pmh-conf/xslt
    POST data query='{"template_id": "value", "my_metadata_format_id": "value", "xslt_id": "value",
    "activated": "value"}'
    """
    try:
        serializer = OaiConfXSLTSerializer(data=request.DATA)
        if serializer.is_valid():
            template_id = request.DATA['template_id']
            my_metadata_format_id = request.DATA['my_metadata_format_id']
            xslt_id = None
            if 'xslt_id' in request.DATA:
                xslt_id = request.DATA['xslt_id']
            activated = request.DATA['activated'] == "True"
            return oai_pmh_conf_xslt_model(template_id, my_metadata_format_id, xslt_id, activated)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
