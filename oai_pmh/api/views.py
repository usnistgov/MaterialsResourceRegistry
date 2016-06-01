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
from sickle.oaiexceptions import NoSetHierarchy, NoMetadataFormat
# Serializers
from oai_pmh.api.serializers import IdentifyObjectSerializer, MetadataFormatSerializer, SetSerializer,\
    RegistrySerializer, ListRecordsSerializer, RegistryURLSerializer, RecordSerializer, \
    IdentifySerializer, UpdateRegistrySerializer, \
    UpdateMyRegistrySerializer, MyMetadataFormatSerializer, DeleteMyMetadataFormatSerializer,\
    UpdateMyMetadataFormatSerializer, GetRecordSerializer, UpdateMySetSerializer, DeleteMySetSerializer,\
    MySetSerializer, MyTemplateMetadataFormatSerializer, DeleteXSLTSerializer, OaiConfXSLTSerializer, \
    OaiXSLTSerializer, RegistryIdSerializer, UpdateRegistryHarvestSerializer, AddRegistrySerializer,\
    ListIdentifierSerializer, HarvestSerializer, UpdateRegistryInfo
# Models
from mgi.models import OaiRegistry, OaiSet, OaiMetadataFormat, OaiIdentify, OaiSettings, Template, OaiRecord,\
OaiMyMetadataFormat, OaiMySet, OaiMetadataformatSet, OaiXslt, OaiTemplMfXslt
import os
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
OAI_HOST_URI = settings.OAI_HOST_URI
from mongoengine import NotUniqueError
import xmltodict
import requests
from utils.XSDhash import XSDhash
from lxml import etree
from lxml.etree import XMLSyntaxError
import datetime
from oai_pmh import datestamp
from django.core.urlresolvers import reverse
import mongoengine.errors as MONGO_ERRORS
from oai_pmh.api.exceptions import OAIAPIException, OAIAPILabelledException, OAIAPISerializeLabelledException
from oai_pmh.api.messages import APIMessage
from admin_mdcs.models import api_permission_required, api_staff_member_required
import oai_pmh.rights as RIGHTS
from django.http.request import QueryDict


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
            #We check first if this repository already exists in database. If yes, we return a response 409
            if OaiRegistry.objects(url__exact=url).count() > 0:
                raise OAIAPILabelledException(message='Unable to create the data provider. '
                                                      'The data provider already exists.',
                                              status=status.HTTP_409_CONFLICT)
            harvestrate = request.DATA['harvestrate']
            harvest = request.DATA['harvest'] == 'True'
            #Get the identify information for the given URL
            identifyResponse = objectIdentify(request)
            if identifyResponse.status_code == status.HTTP_200_OK:
                identifyData = identifyResponse.data
            else:
                raise OAIAPILabelledException(message=identifyResponse.data[APIMessage.label],
                                              status=identifyResponse.status_code)
            #Get the sets information for the given URL
            sets = listObjectSets(request)
            setsData = []
            if sets.status_code == status.HTTP_200_OK:
                setsData = sets.data
            elif sets.status_code != status.HTTP_204_NO_CONTENT:
                raise OAIAPILabelledException(message=sets.data[APIMessage.label], status=sets.status_code)
            #Get the metadata formats information for the given URL
            metadataformats = listObjectMetadataFormats(request)
            metadataformatsData = []
            if metadataformats.status_code == status.HTTP_200_OK:
                metadataformatsData = metadataformats.data
            elif metadataformats.status_code != status.HTTP_204_NO_CONTENT:
                raise OAIAPILabelledException(message=metadataformats.data[APIMessage.label],
                                              status=metadataformats.status_code)
            try:
                identify, registry = createRegistry(harvest, harvestrate, identifyData, url)
                createSetsForRegistry(registry, setsData)
                createMetadataformatsForRegistry(metadataformatsData, registry)
                registry.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                #Manual Rollback
                if identify:
                    identify.delete()
                OaiSet.objects(registry=registry.id).delete()
                OaiMetadataFormat.objects(registry=registry.id).delete()
                raise OAIAPILabelledException(message='An error occurred when trying to save document.%s'%e.message,
                                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()


################################################################################
#
# Function Name: createRegistry
# Inputs:        harvest, harvestrate, identifyData, url
# Outputs:       identify and registry
# Exceptions:
# Description:   OAI-PMH create registry
#
################################################################################
def createRegistry(harvest, harvestrate, identifyData, url):
    registry = OaiRegistry()
    # Get the raw XML from a dictionary
    try:
        identifyRaw = xmltodict.parse(identifyData['raw'])
    except:
        identifyRaw = {}
    identify = createOaiIdentify(identifyData, identifyRaw)
    setDataToRegistry(harvest, harvestrate, identify, registry, url)
    registry.save()
    return identify, registry


################################################################################
#
# Function Name: createMetadataformatsForRegistry
# Inputs:        metadataformatsData, registry
# Outputs:
# Exceptions:
# Description:   OAI-PMH save each metadataformat
#
################################################################################
def createMetadataformatsForRegistry(metadataformatsData, registry):
    for metadataformat in metadataformatsData:
        try:
            raw = xmltodict.parse(metadataformat['raw'])
            obj = OaiMetadataFormat(metadataPrefix=metadataformat['metadataPrefix'],
                                    metadataNamespace=metadataformat['metadataNamespace'],
                                    schema=metadataformat['schema'], raw=raw, registry=str(registry.id), harvest=True)
            http_response = requests.get(obj.schema)
            if http_response.status_code == status.HTTP_200_OK:
                setMetadataFormatXMLSchema(obj, metadataformat['metadataPrefix'], http_response.text)

            obj.save()
        except Exception, e:
            pass

################################################################################
#
# Function Name: createSetsForRegistry
# Inputs:        registry, setsData
# Outputs:
# Exceptions:
# Description:   OAI-PMH save each sets
#
################################################################################
def createSetsForRegistry(registry, setsData):
    for set in setsData:
        try:
            raw = xmltodict.parse(set['raw'])
            obj = OaiSet(setName=set['setName'], setSpec=set['setSpec'], raw=raw,
                         registry=str(registry.id), harvest=True)
            obj.save()
        except:
            pass


################################################################################
#
# Function Name: setDataToRegistry
# Inputs:        harvest, harvestrate, identify, registry, url
# Outputs:
# Exceptions:
# Description:   OAI-PMH set data in parameter to the registry
#
################################################################################
def setDataToRegistry(harvest, harvestrate, identify, registry, url):
    registry.identify = identify
    registry.name = identify.repositoryName
    registry.url = url
    registry.harvestrate = harvestrate
    registry.description = identify.description
    registry.harvest = harvest
    registry.isDeactivated = False


################################################################################
#
# Function Name: createOaiIdentify
# Inputs:        identifyData, identifyRaw
# Outputs:       OaiIdentify object.
# Exceptions:
# Description:   OAI-PMH create OaiIdentify object
#
################################################################################
def createOaiIdentify(identifyData, identifyRaw):
    return OaiIdentify(adminEmail=identifyData['adminEmail'],
                       baseURL=identifyData['baseURL'],
                       repositoryName=identifyData['repositoryName'],
                       deletedRecord=identifyData['deletedRecord'],
                       delimiter=identifyData['delimiter'],
                       description=identifyData['description'],
                       earliestDatestamp=identifyData['earliestDatestamp'],
                       granularity=identifyData['granularity'],
                       oai_identifier=identifyData['oai_identifier'],
                       protocolVersion=identifyData['protocolVersion'],
                       repositoryIdentifier=identifyData['repositoryIdentifier'],
                       sampleIdentifier=identifyData['sampleIdentifier'],
                       scheme=identifyData['scheme'],
                       raw=identifyRaw).save()


################################################################################
#
# Function Name: setMetadataFormatXMLSchema
# Inputs:        metadataFormat, metadataPrefix, stringXML
# Outputs:       -
# Exceptions:
# Description:   OAI-PMH. Set the XML schema for the metadata format in parameter
#                Try to associate the metadata format schema with an existing template
#                in database thanks to the schema hash
#
################################################################################
def setMetadataFormatXMLSchema(metadataFormat, metadataPrefix, stringXML):
    xmlSchema = stringXML
    metadataFormat.xmlSchema = xmlSchema
    hash = XSDhash.get_hash(stringXML)
    metadataFormat.hash = hash
    # TODO: Find a better solution to retrieve the corresponding template. The hash is not fully working because we can have different metadata prefixes with the same hash
    # We check if we have this metadata prefix in our server configuration.
    # If yes, we compare the xml hash with the related template hash. If it's a match, we retrieve the template
    template = None
    try:
        myMetadataFormat = OaiMyMetadataFormat.objects.get(metadataPrefix=metadataPrefix)
        if myMetadataFormat.template:
            if hash == myMetadataFormat.template.hash:
                template = myMetadataFormat.template
            else:
                # We check in the template collection thanks to the hash
                template = Template.objects(hash=hash).first()
    except MONGO_ERRORS.DoesNotExist, e:
        # We check in the template collection thanks to the hash
        template = Template.objects(hash=hash).first()
    if template != None:
        metadataFormat.template = template

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
            try:
                id = request.DATA['id']
                registry = OaiRegistry.objects.get(pk=id)
                harvestrate = request.DATA['harvestrate']
                registry.harvestrate = harvestrate
                harvest = request.DATA['harvest']
                registry.harvest =  harvest == 'True'
                #Save the modifications
                registry.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except MONGO_ERRORS.DoesNotExist:
                raise OAIAPILabelledException(message='No registry found with the given id.',
                                              status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                raise OAIAPILabelledException(message='Unable to update registry. \n%s'%e.message,
                                              status=status.HTTP_400_BAD_REQUEST)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()


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
            #We retrieve all information
            try:
                repositoryName = request.DATA['repositoryName']
                enableHarvesting = request.DATA['enableHarvesting'] == 'True'
                #Save the modifications
                information = OaiSettings.objects.get()
                information.repositoryName = repositoryName
                information.enableHarvesting = enableHarvesting
                information.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except MONGO_ERRORS.DoesNotExist:
                raise OAIAPILabelledException(message='No OAI-PMH configuration found.',
                                              status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                raise OAIAPILabelledException(message='Unable to update the registry. \n%s'%e.message,
                                              status=status.HTTP_400_BAD_REQUEST)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()

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
            try:
                #Get the ID
                id = request.DATA['RegistryId']
                registry = OaiRegistry.objects.get(pk=id)
                #Delete all ReferenceFields
                #Identify
                registry.identify.delete()
                #Records
                OaiRecord.objects(registry=id).delete()
                #Sets
                OaiSet.objects(registry=id).delete()
                #Metadata formats
                OaiMetadataFormat.objects(registry=id).delete()
                #We can now delete the registry
                registry.delete()
                content = APIMessage.getMessageLabelled("Registry deleted with success.")
                return Response(content, status=status.HTTP_200_OK)
            except MONGO_ERRORS.DoesNotExist:
                raise OAIAPILabelledException(message='No registry found with the given id.',
                                              status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                raise OAIAPILabelledException(message='Unable to delete the registry. \n%s'%e.message,
                                              status=status.HTTP_400_BAD_REQUEST)
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
            try:
                #Get the ID
                id = request.DATA['RegistryId']
                registry = OaiRegistry.objects.get(pk=id)
                registry.isDeactivated = True
                registry.save()
                content = APIMessage.getMessageLabelled("Registry deactivated with success.")
                return Response(content, status=status.HTTP_200_OK)
            except MONGO_ERRORS.DoesNotExist:
                raise OAIAPILabelledException(message='No registry found with the given id.',
                                              status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                raise OAIAPILabelledException(message='Unable to deactivate the registry. \n%s'%e.message,
                                              status=status.HTTP_400_BAD_REQUEST)
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
            try:
                #Get the ID
                id = request.DATA['RegistryId']
                registry = OaiRegistry.objects.get(pk=id)
                registry.isDeactivated = False
                registry.save()
                content = APIMessage.getMessageLabelled("Registry deactivated with success.")
                return Response(content, status=status.HTTP_200_OK)
            except MONGO_ERRORS.DoesNotExist:
                raise OAIAPILabelledException(message='No registry found with the given id.',
                                              status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                raise OAIAPILabelledException(message='Unable to reactivated the registry. \n%s'%e.message,
                                              status=status.HTTP_400_BAD_REQUEST)
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
                                                                 'metadata/')),
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
# Function Name: objectIdentifyByURL(request)
# Inputs:        request -
# Outputs:       200 Response successful.
# Exceptions:    400 Error getting URL.
#                401 Unauthorized.
#                500 An error occurred when attempting to identify resource.
# Description:   OAI-PMH Identify by URL
#
################################################################################
def objectIdentifyByURL(url):
    req = sickleObjectIdentify(url)
    if req.status_code == status.HTTP_200_OK:
        identifyData = req.data
        serializerIdentify = IdentifyObjectSerializer(data=identifyData)
        # If it's not valid, return with a bad request
        if not serializerIdentify.is_valid():
            raise OAIAPISerializeLabelledException(message="Identify serialization error.",
                                                   errors=serializerIdentify.errors,
                                                   status=status.HTTP_400_BAD_REQUEST)

        return Response(req.data, status=status.HTTP_200_OK)
    else:
        raise OAIAPILabelledException(message=req.data[APIMessage.label], status=req.status_code)


################################################################################
#
# Function Name: sickleObjectIdentify(request)
# Inputs:        request -
# Outputs:       200 Response successful.
# Exceptions:    500 An error occurred when attempting to identify resource.
# Description:   OAI-PMH Identify
#
################################################################################
def sickleObjectIdentify(url):
    try:
        sickle = Sickle(url)
        identify = sickle.Identify()
        rtn= {"adminEmail": identify.adminEmail,
              "baseURL": identify.baseURL,
              "repositoryName": identify.repositoryName,
              "deletedRecord": identify.deletedRecord,
              "delimiter": identify.delimiter,
              "description": identify.description,
              "earliestDatestamp": identify.earliestDatestamp,
              "granularity": identify.granularity,
              "oai_identifier": identify.oai_identifier,
              "protocolVersion": identify.protocolVersion,
              "repositoryIdentifier": identify.repositoryIdentifier,
              "sampleIdentifier": identify.sampleIdentifier,
              "scheme": identify.scheme,
              "raw": identify.raw}
        serializer = IdentifyObjectSerializer(rtn)
        return Response(serializer.data, status=status.HTTP_200_OK)
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
################################################################################
def listObjectMetadataFormatsByURL(url):
    req = sickleListObjectMetadataFormats(url)
    if req.status_code == status.HTTP_200_OK:
        metadataformatsData = req.data
        serializerMetadataFormat = MetadataFormatSerializer(data=metadataformatsData)
        if not serializerMetadataFormat.is_valid():
            raise OAIAPISerializeLabelledException(message="Metadata formats serialization error.",
                                                   errors=serializerMetadataFormat.errors,
                                                   status=status.HTTP_400_BAD_REQUEST)

        return Response(req.data, status=status.HTTP_200_OK)
    else:
        return Response(req.data, status=req.status_code)
################################################################################
#
# Function Name: sickleListObjectMetadataFormats(request)
# Inputs:        request -
# Outputs:       200 Response successful.
# Exceptions:    204 No metadata formats
#                500 An error occurred when attempting to identify resource.
# Description:   OAI-PMH List Object Metadata Formats
#
################################################################################
def sickleListObjectMetadataFormats(url):
    try:
        sickle = Sickle(url)
        rsp = sickle.ListMetadataFormats()
        rtn = []
        try:
            while True:
                obj = rsp.next()
                metadata = MetadataFormat(obj.xml)
                rtn.append({"metadataPrefix": metadata.metadataPrefix,
                          "metadataNamespace": metadata.metadataNamespace,
                          "schema": metadata.schema,
                          "raw": metadata.raw})
        except StopIteration:
            pass
        serializer = MetadataFormatSerializer(rtn)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except NoMetadataFormat as e:
        #This repository does not support sets
        content = APIMessage.getMessageLabelled('%s'%e.message)
        return Response(content, status=status.HTTP_204_NO_CONTENT)
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
# Function Name: listObjectSetsByURL(request)
# Inputs:        request -
# Outputs:       200 Response successful.
#                204 No Sets
# Exceptions:    400 Error(s) in required values value.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                500 An error occurred when attempting to identify resource.
# Description:   OAI-PMH List object Sets by URL
#
################################################################################
def listObjectSetsByURL(url):
    req = sickleListObjectSets(url)
    if req.status_code == status.HTTP_200_OK:
        setsData = req.data
        serializerSet = SetSerializer(data=setsData)
        if not serializerSet.is_valid():
            raise OAIAPISerializeLabelledException(message="Sets serialization error.",
                                                   errors=serializerSet.errors,
                                                   status=status.HTTP_400_BAD_REQUEST)

        return Response(req.data, status=status.HTTP_200_OK)
    else:
        return Response(req.data, status=req.status_code)

################################################################################
#
# Function Name: sickleListObjectSets(request)
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
def sickleListObjectSets(url):
    try:
        sickle = Sickle(url)
        rsp = sickle.ListSets()
        rtn = []
        try:
            while True:
                obj = rsp.next()
                set = Set(obj.xml)
                rtn.append({  "setName":set.setName,
                              "setSpec":set.setSpec,
                              "raw":set.raw})
        except StopIteration:
            pass
        serializer = SetSerializer(rtn)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except NoSetHierarchy as e:
        #This repository does not support sets
        content = APIMessage.getMessageLabelled('%s'%e.message)
        return Response(content, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        content = APIMessage.getMessageLabelled('An error occurred when attempting to identify resource: %s'%e.message)
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
            #We retrieve the registry (data provider)
            try:
                registry = OaiRegistry.objects(pk=registry_id).get()
                url = registry.url
            except:
                raise OAIAPILabelledException(message='No registry found with the given parameters.',
                                              status=status.HTTP_404_NOT_FOUND)
            #We are harvesting
            registry.isHarvesting = True
            registry.save()
            #Set the last update date
            harvestDate = datetime.datetime.now()
            #Get all available metadata formats
            metadataformats = OaiMetadataFormat.objects(registry=registry_id, harvest=True)
            #Get all sets
            registryAllSets = OaiSet.objects(registry=registry_id).order_by("setName")
            #Get all available  sets
            registrySetsToHarvest = OaiSet.objects(registry=registry_id, harvest=True).order_by("setName")
            #Check if we have to retrieve all sets or not. If all sets, no need to provide the set parameter in the
            #harvest request. Avoid to retrieve same records for nothing (If records are in many sets).
            searchBySets = len(registryAllSets) != len(registrySetsToHarvest)
            #Search by sets
            if searchBySets and len(registryAllSets) != 0:
                allErrors = harvestBySetsAndMF(registrySetsToHarvest, metadataformats, url, registry_id, registryAllSets)
            #If we don't have to search by set or the OAI Registry doesn't support sets
            else:
                allErrors = harvestByMF(registrySetsToHarvest, metadataformats, url, registry_id, registryAllSets)
            #Stop harvesting
            registry.isHarvesting = False
            #Set the last update date
            registry.lastUpdate = harvestDate
            registry.save()
            #Return the harvest status
            if len(allErrors) == 0:
                content = APIMessage.getMessageLabelled('Harvest data succeeded without errors.')
            else:
                content = APIMessage.getMessageLabelled(allErrors)

            return Response(content, status=status.HTTP_200_OK)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        registry.isHarvesting = False
        registry.save()
        content = APIMessage.getMessageLabelled('An error occurred during the harvest process: %s'%e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: harvestBySetsAndMF
# Inputs:        registrySetsToHarvest, metadataformats, url, registry_id, registryAllSets
# Outputs:       List of errors.
# Exceptions:    -
# Description:   Harvest data by sets and metadata format.
#                For each set, try to retrieve records for each metadata format
#
################################################################################
def harvestBySetsAndMF(registrySetsToHarvest, metadataformats, url, registry_id, registryAllSets):
    allErrors = []
    for metadataFormat in metadataformats:
        currentUpdateMF = datetime.datetime.now()
        errorsDuringUpdate = False
        for set in registrySetsToHarvest:
            currentUpdateSetMF = datetime.datetime.now()
            try:
                #Retrieve the last update for this metadata format and this set
                objOaiMFSets = OaiMetadataformatSet.objects(metadataformat=metadataFormat, set=set).get()
                lastUpdate = datestamp.datetime_to_datestamp(objOaiMFSets.lastUpdate)
            except:
                lastUpdate = None
            errors = harvestRecords(url, registry_id, metadataFormat, lastUpdate, registryAllSets, set)
            #If no exceptions was thrown and no errors occured, we can update the lastUpdate date
            if len(errors) == 0:
                OaiMetadataformatSet.objects.filter(metadataformat=metadataFormat, set=set)\
                        .update(set__metadataformat=metadataFormat, set__set=set, set__lastUpdate=currentUpdateSetMF,
                                upsert=True)
            else:
                errorsDuringUpdate = True
                allErrors.append(errors)
        #Set the last update date if no exceptions was thrown
        #Would be useful if we do a harvestByMF in the futur: we won't retrieve everything
        if not errorsDuringUpdate:
            metadataFormat.lastUpdate = currentUpdateMF
            metadataFormat.save()
    return allErrors

################################################################################
#
# Function Name: harvestByMF
# Inputs:        registrySetsToHarvest, metadataformats, url, registry_id, registryAllSets
# Outputs:       List of errors.
# Exceptions:    -
# Description:   Harvest data by metadata format.
#
################################################################################
def harvestByMF(registrySetsToHarvest, metadataformats, url, registry_id, registryAllSets):
    allErrors = []
    for metadataFormat in metadataformats:
        try:
            #Retrieve the last update for this metadata format
            lastUpdate = datestamp.datetime_to_datestamp(metadataFormat.lastUpdate)
        except:
            lastUpdate = None
        #Update the new date for the metadataFormat
        currentUpdateMF = datetime.datetime.now()
        errors = harvestRecords(url, registry_id, metadataFormat, lastUpdate, registryAllSets)
        #If no exceptions was thrown and no errors occured, we can update the lastUpdate date
        if len(errors) == 0:
            #Update the update date for all sets in the OaiMetadataformatSet Collection
            #Would be useful if we do a harvestBySetsAndMF in the futur: we won't retrieve everything
            if len(registrySetsToHarvest) != 0:
                for set in registrySetsToHarvest:
                    OaiMetadataformatSet.objects.filter(metadataformat=metadataFormat, set=set)\
                        .update(set__metadataformat=metadataFormat, set__set=set, set__lastUpdate=currentUpdateMF,
                                upsert=True)
            #Update the update date
            metadataFormat.lastUpdate = currentUpdateMF
            metadataFormat.save()
        else:
            allErrors.append(errors)
    return allErrors

################################################################################
#
# Function Name: harvestRecords(request)
# Inputs:        url, registry_id, metadataFormat, lastUpdate, registryAllSets, set=None -
# Outputs:       List of errors.
# Description:   Save OAI-PMH ListRecords (retrieved via OAI-PMH request) in Database
#
################################################################################
def harvestRecords(url, registry_id, metadataFormat, lastUpdate, registryAllSets, set=None):
    errors = []
    dataLeft = True
    resumptionToken = None
    #Get all records. Use of the resumption token
    while dataLeft:
        #Get the list of records
        if set != None:
            http_response, resumptionToken = getListRecords(url=url, metadataPrefix=metadataFormat.metadataPrefix, set_h=set.setSpec, fromDate=lastUpdate, resumptionToken=resumptionToken)
        else:
            http_response, resumptionToken = getListRecords(url=url, metadataPrefix=metadataFormat.metadataPrefix, fromDate=lastUpdate, resumptionToken=resumptionToken)
        if http_response.status_code == status.HTTP_200_OK:
            rtn = http_response.data
            for info in rtn:
                #Get corresponding sets
                sets = [x for x in registryAllSets if x.setSpec in info['sets']]
                raw = xmltodict.parse(info['raw'])
                metadata = xmltodict.parse(info['metadata'])
                try:
                    obj = OaiRecord.objects.filter(identifier=info['identifier'], metadataformat=metadataFormat).get()
                except:
                    obj = OaiRecord()
                obj.identifier=info['identifier']
                obj.datestamp=datestamp.datestamp_to_datetime(info['datestamp'])
                obj.deleted=info['deleted']
                obj.metadataformat=metadataFormat
                obj.sets=sets
                obj.raw=raw
                obj.registry=registry_id
                #Custom Save to keep the order of metadata's XML
                obj.save(metadata=metadata)
        #Else, we get the status code with the error message provided by the http_response
        else:
            error = {'status_code': http_response.status_code, 'error': http_response.data[APIMessage.label]}
            errors.append(error)
        #There is more records if we have a resumption token.
        dataLeft = resumptionToken != None and resumptionToken != ''

    return errors

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
            if isinstance(request.DATA, QueryDict):
                metadataFormats = request.DATA.getlist('metadataFormats')
                sets = request.DATA.getlist('sets')
            else:
                metadataFormats = request.DATA['metadataFormats']
                sets = request.DATA['sets']
            #Set harvest=False for all
            OaiMetadataFormat.objects(registry=id).update(set__harvest=False)
            OaiSet.objects(registry=id).update(set__harvest=False)
            #For each metadataFormats selected, set harvest=True
            if len(metadataFormats):
                OaiMetadataFormat.objects(pk__in=metadataFormats).update(set__harvest=True)
            #For each sets selected, set harvest=True
            if len(sets):
                OaiSet.objects(pk__in=sets).update(set__harvest=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
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
        registry = None
        #If it's valid
        if serializer.is_valid():
            registry_id = request.DATA['registry_id']
            try:
                registry = OaiRegistry.objects(pk=registry_id).get()
                url = registry.url
                registry.isUpdating = True
                registry.save()
                #Get the identify information for the given URL
                identify = objectIdentifyByURL(url)
                if identify.status_code == status.HTTP_200_OK:
                    identifyData = identify.data
                else:
                    raise OAIAPILabelledException(message=identify.data[APIMessage.label], status=identify.status_code)
                #Get the sets information for the given URL
                sets = listObjectSetsByURL(url)
                setsData = []
                #If status OK, we try to serialize data and check if it's valid
                if sets.status_code == status.HTTP_200_OK:
                    setsData = sets.data
                elif sets.status_code != status.HTTP_204_NO_CONTENT:
                    raise OAIAPILabelledException(message=sets.data[APIMessage.label], status=sets.status_code)
                #Get the metadata formats information for the given URL
                metadataformats = listObjectMetadataFormatsByURL(url)
                metadataformatsData = []
                #If status OK, we try to serialize data and check if it's valid
                if metadataformats.status_code == status.HTTP_200_OK:
                    metadataformatsData = metadataformats.data
                elif metadataformats.status_code != status.HTTP_204_NO_CONTENT:
                    raise OAIAPILabelledException(message=metadataformats.data[APIMessage.label],
                                                  status=metadataformats.status_code)
                #Modify information
                modifyRegistry(identifyData, registry)
                modifySetsForRegistry(registry, setsData)
                modifyMetadataformatsForRegistry(registry, metadataformatsData)
                #Save the registry
                registry.isUpdating = False
                registry.save()
                content = APIMessage.getMessageLabelled('Data provider updated with success.')

                return Response(content, status=status.HTTP_200_OK)
            except MONGO_ERRORS.DoesNotExist:
                raise OAIAPILabelledException(message='No registry found with the given parameters.',
                                      status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                raise OAIAPILabelledException(message='An error occurred during the Data Provider update. '
                                                      'Please contact your administrator. %s'%e.message,
                                                  status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors,
                                          status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        if registry is not None:
            registry.isUpdating = False
            registry.save()
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: modifyMetadataformatsForRegistry
# Inputs:        metadataformatsData, registry
# Outputs:
# Exceptions:
# Description:   OAI-PMH add or modify each metadata format
#
################################################################################
def modifyMetadataformatsForRegistry(registry, metadataformatsData):
    #Creation of each metadata format
    for metadataformat in metadataformatsData:
        try:
            #Try to retrieve this existing metadata format for this registry
            raw = xmltodict.parse(metadataformat['raw'])
            try:
                #Update
                obj = OaiMetadataFormat.objects(metadataPrefix=metadataformat['metadataPrefix'], registry=str(registry.id)).get()
                obj.metadataNamespace = metadataformat['metadataNamespace']
                obj.schema = metadataformat['schema']
                obj.raw = raw
            except:
                #New metadata format Creation
                obj = OaiMetadataFormat(metadataPrefix=metadataformat['metadataPrefix'],
                                        metadataNamespace=metadataformat['metadataNamespace'],
                                        schema=metadataformat['schema'], raw= raw, registry=str(registry.id),
                                        harvest=True)
            http_response = requests.get(obj.schema)
            if http_response.status_code == status.HTTP_200_OK:
                setMetadataFormatXMLSchema(obj, metadataformat['metadataPrefix'], http_response.text)
            obj.save()
        except:
            pass

################################################################################
#
# Function Name: modifySetsForRegistry
# Inputs:        registry, setsData
# Outputs:
# Exceptions:
# Description:   OAI-PMH modify or add sets
#
################################################################################
def modifySetsForRegistry(registry, setsData):
    #Creation or modification of each set
    for set in setsData:
        try:
            raw = xmltodict.parse(set['raw'])
            #Try to retrieve the existing set for this registry
            try:
                #Update
                obj = OaiSet.objects(setSpec=set['setSpec'], registry=str(registry.id)).get()
                obj.setName = set['setName']
                obj.raw = raw
            except:
                #New set. Creation
                obj = OaiSet(setName=set['setName'], setSpec=set['setSpec'], raw= raw,
                             registry=str(registry.id), harvest=True)
            obj.save()
        except:
            pass

################################################################################
#
# Function Name: modifyRegistry
# Inputs:        harvest, harvestrate, identifyData, url
# Outputs:       identify and registry
# Exceptions:
# Description:   OAI-PMH create registry
#
################################################################################
def modifyRegistry(identifyData, registry):
    # Get the raw XML from a dictionary
    try:
        identifyRaw = xmltodict.parse(identifyData['raw'])
    except:
        identifyRaw = {}
    identify = modifyOaiIdentify(identifyData, identifyRaw, registry.identify.id)
    registry.identify = identify
    registry.name = identify.repositoryName
    registry.description = identify.description
    registry.save()
    return identify, registry


################################################################################
#
# Function Name: modifyOaiIdentify
# Inputs:        identifyData, identifyRaw, identifyId
# Outputs:       OaiIdentify object.
# Exceptions:
# Description:   OAI-PMH modify OaiIdentify object
#
################################################################################
def modifyOaiIdentify(identifyData, identifyRaw, identifyId):
    return OaiIdentify(id=identifyId,
                       adminEmail=identifyData['adminEmail'],
                       baseURL=identifyData['baseURL'],
                       repositoryName=identifyData['repositoryName'],
                       deletedRecord=identifyData['deletedRecord'],
                       delimiter=identifyData['delimiter'],
                       description=identifyData['description'],
                       earliestDatestamp=identifyData['earliestDatestamp'],
                       granularity=identifyData['granularity'],
                       oai_identifier=identifyData['oai_identifier'],
                       protocolVersion=identifyData['protocolVersion'],
                       repositoryIdentifier=identifyData['repositoryIdentifier'],
                       sampleIdentifier=identifyData['sampleIdentifier'],
                       scheme=identifyData['scheme'],
                       raw=identifyRaw).save()

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
            http_response, token = getListRecords(url=url, metadataPrefix=metadataPrefix,
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
# Function Name: getListRecords(url, metadataPrefix, resumptionToken, set_h, fromDate, untilDate)
# Inputs:        request -
# Outputs:       200 Response successful.
# Exceptions:    400 Error(s) in required values value.
#                400 Serializer failed validation.
#                401 Unauthorized.
#                500 An error occurred when attempting to identify resource.
# Description:   OAI-PMH List Records
#
################################################################################
def getListRecords(url, metadataPrefix=None, resumptionToken=None, set_h=None, fromDate=None, untilDate=None):
    XMLParser = etree.XMLParser(remove_blank_text=True, recover=True)
    try:
        params = {'verb': 'ListRecords'}
        if resumptionToken != None:
            params['resumptionToken'] = resumptionToken
        else:
            params['metadataPrefix'] = metadataPrefix
            params['set'] = set_h
            params['from'] = fromDate
            params['until'] = untilDate
        rtn = []
        http_response = requests.get(url, params=params)
        resumptionToken = None
        if http_response.status_code == status.HTTP_200_OK:
            xml = http_response.text
            elements = etree.XML(xml.encode("utf8"),
                                 parser=XMLParser).iterfind('.//' + '{http://www.openarchives.org/OAI/2.0/}' + 'record')
            for elt in elements:
                record = Record(elt)
                rtn.append({"identifier": record.header.identifier,
                          "datestamp": record.header.datestamp,
                          "deleted": record.deleted,
                          "sets": record.header.setSpecs,
                          "metadataPrefix": metadataPrefix,
                          "metadata": etree.tostring(record.xml.find('.//' +
                                                     '{http://www.openarchives.org/OAI/2.0/}' + 'metadata/')),
                          "raw": record.raw})
            resumptionTokenElt = etree.XML(xml.encode("utf8"),
                                           parser=XMLParser).iterfind('.//' + '{http://www.openarchives.org/OAI/2.0/}' +
                                                                      'resumptionToken')
            for res in resumptionTokenElt:
                resumptionToken = res.text
        elif http_response.status_code == status.HTTP_404_NOT_FOUND:
            raise OAIAPILabelledException(message='Impossible to get data from the server. Server not found',
                                          status=status.HTTP_404_NOT_FOUND)
        else:
            raise OAIAPILabelledException(message='An error occurred while trying to get data from the server.',
                                          status=http_response.status_code)

        return Response(rtn, status=status.HTTP_200_OK), resumptionToken
    except OAIAPIException as e:
        return e.response(), resumptionToken
    except Exception as e:
        content = APIMessage.getMessageLabelled('An error occurred during the getListRecords process: %s'%e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR), resumptionToken

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
            try:
                metadataprefix = request.DATA['metadataPrefix']
                schema = request.DATA['schema']
                http_response = requests.get(schema)
                if http_response.status_code == status.HTTP_200_OK:
                    xml_schema = http_response.text
                    dom = etree.fromstring(xml_schema.encode('utf-8'))
                    if 'targetNamespace' in dom.find(".").attrib:
                        metadataNamespace = dom.find(".").attrib['targetNamespace'] or "namespace"
                    else:
                        metadataNamespace = "http://www.w3.org/2001/XMLSchema"
                     #Add in database
                    OaiMyMetadataFormat(metadataPrefix=metadataprefix, schema=schema,
                               metadataNamespace=metadataNamespace,
                               xmlSchema=xml_schema, isDefault=False).save()

                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    raise OAIAPILabelledException(message='Unable to add the new metadata format. '
                                                          'Impossible to retrieve the schema at the given URL',
                                                  status=status.HTTP_400_BAD_REQUEST)
            except XMLSyntaxError:
                raise OAIAPILabelledException(message='Unable to add the new metadata format.',
                                              status=status.HTTP_400_BAD_REQUEST)
            except MONGO_ERRORS.NotUniqueError as e:
                raise OAIAPILabelledException(message='Unable to create the metadata format. '
                                                      'The metadata format already exists.',
                                              status=status.HTTP_409_CONFLICT)
            except Exception as e:
                raise OAIAPILabelledException(message='Unable to add the new metadata format. \n%s'%e.message,
                                              status=status.HTTP_400_BAD_REQUEST)
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
            try:
                metadataprefix = request.DATA['metadataPrefix']
                template = request.DATA['template']
                template = Template.objects.get(pk=template)
                #Check if the XML is well formed
                xml_schema = template.content
                dom = etree.fromstring(xml_schema.encode('utf-8'))
                if 'targetNamespace' in dom.find(".").attrib:
                    metadataNamespace = dom.find(".").attrib['targetNamespace'] or "namespace"
                else:
                    metadataNamespace = "http://www.w3.org/2001/XMLSchema"
                #Create a schema URL
                schemaURL = OAI_HOST_URI + reverse('getXSD', args=[template.filename])
                #Add in database
                OaiMyMetadataFormat(metadataPrefix=metadataprefix,
                                   schema=schemaURL,
                                   metadataNamespace=metadataNamespace, xmlSchema='', isDefault=False,
                                   isTemplate=True, template=template).save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except XMLSyntaxError:
                raise OAIAPILabelledException(message='Unable to add the new metadata format. XML Synthax error.',
                                              status=status.HTTP_400_BAD_REQUEST)
            except MONGO_ERRORS.DoesNotExist, e:
                raise OAIAPILabelledException(message='Unable to add the new metadata format. '
                                                      'Impossible to retrieve the template with the given template',
                                              status=status.HTTP_404_NOT_FOUND)
            except MONGO_ERRORS.NotUniqueError as e:
                raise OAIAPILabelledException(message='Unable to create the metadata format. '
                                                      'The metadata format already exists.',
                                              status=status.HTTP_409_CONFLICT)
            except Exception as e:
                raise OAIAPILabelledException(message='Unable to add the new metadata format. \n%s'%e.message,
                                              status=status.HTTP_400_BAD_REQUEST)
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
            try:
                id = request.DATA['MetadataFormatId']
                metadataFormat = OaiMyMetadataFormat.objects.get(pk=id)
                #We can now delete the metadataFormat for my server
                metadataFormat.delete()
                content = APIMessage.getMessageLabelled("Deleted metadata format with success.")

                return Response(content, status=status.HTTP_200_OK)
            except MONGO_ERRORS.DoesNotExist as e:
                raise OAIAPILabelledException(message='No metadata format found with the given id.',
                                              status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                raise OAIAPILabelledException(message='Unable to delete the metadata format. \n%s'%e.message,
                                              status=status.HTTP_400_BAD_REQUEST)
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
            try:
                id = request.DATA['id']
                metadataFormat = OaiMyMetadataFormat.objects.get(pk=id)
                metadataprefix = request.DATA['metadataPrefix']
                metadataFormat.metadataPrefix = metadataprefix
                #Save the modifications
                metadataFormat.save()

                return Response(serializer.data, status=status.HTTP_200_OK)
            except MONGO_ERRORS.DoesNotExist:
                raise OAIAPILabelledException(message='No metadata format found with the given id.',
                                              status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                raise OAIAPILabelledException(message='Unable to update the metadata format. \n%s'%e.message,
                                              status=status.HTTP_400_BAD_REQUEST)
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
            try:
                #We retrieve all information
                setSpec = request.DATA['setSpec']
                setName = request.DATA['setName']
                if isinstance(request.DATA, QueryDict):
                    templates = request.DATA.getlist('templates')
                else:
                    templates = request.DATA['templates']
                description = request.DATA.get('description', None)
                OaiMySet(setSpec=setSpec, setName=setName, description=description, templates=templates).save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except MONGO_ERRORS.NotUniqueError as e:
                raise OAIAPILabelledException(message='Unable to add the new set. '
                                                      'The set already exists.',
                                              status=status.HTTP_409_CONFLICT)
            except Exception as e:
                raise OAIAPILabelledException(message='Unable to add the new set. \n%s'%e.message,
                                              status=status.HTTP_400_BAD_REQUEST)
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
            try:
                id = request.DATA['set_id']
                set = OaiMySet.objects.get(pk=id)
                set.delete()
                content = APIMessage.getMessageLabelled("Deleted set with success.")

                return Response(content, status=status.HTTP_200_OK)
            except MONGO_ERRORS.DoesNotExist:
                raise OAIAPILabelledException(message='No set found with the given id.',
                                              status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                raise OAIAPILabelledException(message='Unable to delete the set. \n%s'%e.message,
                                              status=status.HTTP_400_BAD_REQUEST)
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
            try:
                id = request.DATA['id']
                set = OaiMySet.objects.get(pk=id)
                set.setSpec = request.DATA['setSpec']
                set.setName = request.DATA['setName']
                description = request.DATA.get('description', None)
                if description is not None:
                    set.description = description
                if isinstance(request.DATA, QueryDict):
                    templates = request.DATA.getlist('templates', None)
                else:
                    templates = request.DATA.get('templates', None)
                if templates is not None:
                    set.templates = Template.objects(pk__in=templates).all()
                set.save()

                return Response(serializer.data, status=status.HTTP_200_OK)
            except MONGO_ERRORS.DoesNotExist:
                raise OAIAPILabelledException(message='No set found with the given id.',
                                              status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                raise OAIAPILabelledException(message='Unable to update the set. \n%s'%e.message,
                                                status=status.HTTP_400_BAD_REQUEST)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()


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
            try:
                name = request.DATA['name']
                filename = request.DATA['filename']
                xmlStr = request.DATA['content']
                etree.XML(xmlStr.encode('utf-8'))
                OaiXslt(name=name, filename=filename, content=xmlStr).save()
                content = APIMessage.getMessageLabelled("XSLT added with success.")

                return Response(content, status=status.HTTP_201_CREATED)
            except etree.ParseError as e:
                raise OAIAPILabelledException(message='An error occurred when attempting to parse the XSLT',
                                              status=status.HTTP_400_BAD_REQUEST)
            except NotUniqueError, e:
                raise OAIAPILabelledException(message='This XSLT name already exists. Please enter an other name.',
                                              status=status.HTTP_409_CONFLICT)
            except Exception as e:
                raise OAIAPILabelledException(message='An error occurred when attempting to save the XSLT',
                                              status=status.HTTP_400_BAD_REQUEST)
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
            try:
                id = request.DATA['xslt_id']
                xslt = OaiXslt.objects.get(pk=id)
                xslt.delete()
                content = APIMessage.getMessageLabelled("Deleted xslt with success.")

                return Response(content, status=status.HTTP_200_OK)
            except MONGO_ERRORS.DoesNotExist as e:
                raise OAIAPILabelledException(message='No xslt found with the given id.',
                                              status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                raise OAIAPILabelledException(message='An error occurred when attempting to delete the XSLT.',
                                              status=status.HTTP_400_BAD_REQUEST)
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
        serializer = DeleteXSLTSerializer(data=request.DATA)
        if serializer.is_valid():
            try:
                #Get the ID
                id = request.DATA['xslt_id']
                new_name = request.DATA['name']
                xslt = OaiXslt.objects.get(pk=id)
                xslt.update(set__name=str(new_name))
                content = APIMessage.getMessageLabelled("XSLT edited with success.")

                return Response(content, status=status.HTTP_200_OK)
            except MONGO_ERRORS.DoesNotExist as e:
                raise OAIAPILabelledException(message='No xslt found with the given id.',
                                              status=status.HTTP_404_NOT_FOUND)
            except MONGO_ERRORS.OperationError, e:
                raise OAIAPILabelledException(message='This XSLT name already exists. Please enter an other name.',
                                              status=status.HTTP_409_CONFLICT)
            except Exception as e:
                raise OAIAPILabelledException(message='An error occurred when attempting to edit the configuration.',
                                              status=status.HTTP_400_BAD_REQUEST)
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
            if xslt_id == None and activated == True:
                raise OAIAPILabelledException(message='Impossible to activate the configuration. Please provide '
                                              'a XSLT.', status=status.HTTP_400_BAD_REQUEST)
            try:
                OaiTemplMfXslt.objects.filter(myMetadataFormat=my_metadata_format_id, template=template_id)\
                    .update(set__myMetadataFormat = my_metadata_format_id, set__template = template_id,
                            set__xslt = xslt_id, set__activated = activated, upsert=True)
                content = APIMessage.getMessageLabelled("XSLT edited with success.")

                return Response(content, status=status.HTTP_200_OK)
            except Exception as e:
                raise OAIAPILabelledException(message='An error occurred when attempting to save the configuration',
                                              status=status.HTTP_400_BAD_REQUEST)
        else:
            raise OAIAPISerializeLabelledException(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except OAIAPIException as e:
        return e.response()
    except Exception as e:
        content = APIMessage.getMessageLabelled(e.message)
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
