
################################################################################
#
# File Name: tests.py
# Application: oai_pmh/api
# Purpose:
#
# Author: Pierre Francois RIGODIAT
#         pierre-francois.rigodiat@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from oai_pmh.tests.models import OAI_PMH_Test
from oai_pmh.api.models import createOaiIdentify, setDataToRegistry, createMetadataformatsForRegistry,\
    sickleListObjectMetadataFormats, sickleListObjectSets, sickleObjectIdentify, createSetsForRegistry,\
    getListRecords, harvestRecords, harvestByMF, harvestBySetsAndMF, modifyRegistry, modifyOaiIdentify, \
    modifyMetadataformatsForRegistry, modifySetsForRegistry, createRegistry, setMetadataFormatXMLSchema
from mgi.models import OaiRegistry, OaiIdentify, OaiMetadataFormat, OaiMyMetadataFormat, OaiSettings, Template, OaiSet,\
    OaiMySet, OaiRecord, XMLdata, OaiTemplMfXslt, OaiMetadataformatSet, OaiXslt, Status
import xmltodict
from testing.models import URL_TEST, ADMIN_AUTH, ADMIN_AUTH_GET, USER_AUTH, TEMPLATE_VALID_CONTENT, \
    TEMPLATE_INVALID_CONTENT
from django.core.urlresolvers import reverse
from rest_framework import status
import mongoengine.errors as MONGO_ERRORS
from testing.models import FAKE_ID
from bson.objectid import ObjectId
import oai_pmh.datestamp as datestamp
URL_TEST_SERVER = URL_TEST + "/oai_pmh/server/"
import requests
import datetime
from django.conf import settings
import os
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
OAI_HOST_URI = settings.OAI_HOST_URI
from unittest import skip

class tests_OAI_PMH_API(OAI_PMH_Test):

    def test_dumps(self):
        self.dump_result_xslt()
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_xmldata()
        self.dump_oai_my_set()


############################### add_registry tests #############################
    def test_add_registry(self):
        self.dump_oai_settings()
        self.dump_oai_my_set()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        data = {"url": URL_TEST_SERVER, "harvestrate": 5000, "harvest": True}
        req = self.doRequestPost(url=reverse("api_add_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_201_CREATED)

    def test_add_registry_no_sets(self):
        self.dump_oai_settings()
        # self.dump_oai_my_set()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        data = {"url": URL_TEST_SERVER, "harvestrate": 5000, "harvest": True}
        req = self.doRequestPost(url=reverse("api_add_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_201_CREATED)

    def test_add_registry_no_metadataFormats(self):
        self.dump_oai_settings()
        self.dump_oai_my_set()
        # self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        data = {"url": URL_TEST_SERVER, "harvestrate": 5000, "harvest": True}
        req = self.doRequestPost(url=reverse("api_add_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_201_CREATED)


    def test_add_registry_unavailable(self):
        self.dump_oai_settings()
        self.setHarvest(False)
        data = {"url": URL_TEST_SERVER, "harvestrate": 5000, "harvest": True}
        req = self.doRequestPost(url=reverse("api_add_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


    def test_add_registry_unauthorized(self):
        self.dump_oai_settings()
        data = {"url": URL_TEST_SERVER, "harvestrate": 5000, "harvest": True}
        #No authentification
        req = self.doRequestPost(url=reverse("api_add_registry"), data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_registry_serializer_invalid(self):
        self.dump_oai_settings()
        data = {"urlBad": URL_TEST_SERVER, "harvestrate": 5000, "harvest": True}
        req = self.doRequestPost(url=reverse("api_add_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_registry_already_exists(self):
        self.dump_oai_settings()
        self.dump_oai_my_set()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        data = {"url": URL_TEST_SERVER, "harvestrate": 5000, "harvest": True}
        req = self.doRequestPost(url=reverse("api_add_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_201_CREATED)
        data = {"url": URL_TEST_SERVER, "harvestrate": 5000, "harvest": True}
        req = self.doRequestPost(url=reverse("api_add_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_409_CONFLICT)

    def test_add_registry_identify(self):
        self.dump_oai_settings()
        data = {"url": URL_TEST_SERVER, "harvestrate": 5000, "harvest": True}
        #No harvest TRUE Identify will fail
        req = self.doRequestPost(url=reverse("api_add_registry"), data=data, auth=ADMIN_AUTH)
        self.assertNotEquals(req.status_code, status.HTTP_200_OK)

    def test_add_registry_metadata_format(self):
        self.dump_oai_settings()
        self.setHarvest(True)
        self.dump_oai_my_metadata_format()
        #Change an xml schema to make fail the treatment
        metadataFormat = OaiMyMetadataFormat.objects.all()[0]
        metadataFormat.schema = "http://noserver.com"
        metadataFormat.save()
        data = {"url": URL_TEST_SERVER, "harvestrate": 5000, "harvest": True}
        #No harvest TRUE Identify will fail
        req = self.doRequestPost(url=reverse("api_add_registry"), data=data, auth=ADMIN_AUTH)
        self.assertNotEquals(req.status_code, status.HTTP_200_OK)

    def test_add_registry_bad_identify(self):
        self.dump_oai_settings_bad()
        self.setHarvest(True)
        data = {"url": URL_TEST_SERVER, "harvestrate": 5000, "harvest": True}
        req = self.doRequestPost(url=reverse("api_add_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_registry_bad_metadata_format(self):
        self.dump_oai_settings()
        self.dump_oai_my_set()
        self.dump_oai_my_metadata_format_bad()
        self.setHarvest(True)
        data = {"url": URL_TEST_SERVER, "harvestrate": 5000, "harvest": True}
        req = self.doRequestPost(url=reverse("api_add_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_registry_bad_sets(self):
        self.dump_oai_settings()
        self.dump_oai_my_set_bad()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        data = {"url": URL_TEST_SERVER, "harvestrate": 5000, "harvest": True}
        req = self.doRequestPost(url=reverse("api_add_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)


################################################################################

########################## createRegistry tests ################################

    def test_createRegistry_function(self):
        #Call the function to create the registry
        identify, registry = self.call_createRegistry()
        self.assert_OaiIdentify(identify)
        #Check with the OaiRegistry returned by the function
        self.assert_OaiRegistry(registry=registry, objIdentify=identify)
        #Check with the OaiRegistry saved in database
        objInDatabase = OaiRegistry.objects.get(pk=registry.id)
        self.assert_OaiRegistry(registry=objInDatabase, objIdentify=identify)

    def test_createRegistry_function_bad_raw(self):
        #Call the function to create the registry
        strUrl, harvest, harvestrate = self.getRegistryData()
        identifyData = self.getIdentifyData()
        identifyData['raw'] = "<test>badXMLtest/>"
        identify, registry = createRegistry(harvest=harvest, harvestrate=harvestrate, identifyData=identifyData,
                                            url=strUrl)
        self.assertEqual(identify['raw'], {})


    def test_setDataToRegistry_function(self):
        #Get registry data
        strUrl, harvest, harvestrate = self.getRegistryData()
        registry = OaiRegistry()
        #Create the identity
        objIdentify = self.call_createOaiIdentify()
        #Test the method
        setDataToRegistry(harvest=harvest, harvestrate=harvestrate, identify=objIdentify, registry=registry,
                          url=strUrl)
        self.assert_OaiRegistry(registry=registry, objIdentify=objIdentify)

    def test_createOaiIdentify_function(self):
        #Call the function to create the identify
        objIdentify = self.call_createOaiIdentify()
        #Check with the OaiIdentify saved in database
        objInDatabase = OaiIdentify.objects.get(pk=objIdentify.id)
        self.assert_OaiIdentify(objInDatabase)

################################################################################


############################## objectIdentify tests ############################

    def test_objectIdentify(self):
        self.dump_oai_settings()
        self.setHarvest(True)
        data = {"url": URL_TEST_SERVER}
        req = self.doRequestPost(url=reverse("api_objectIdentify"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        retrievedSetsData = req.data
        self.assert_OaiIdentify_Settings(retrievedSetsData)

    def test_objectIdentify_unavailable(self):
        self.dump_oai_settings()
        self.setHarvest(False)
        data = {"url": URL_TEST_SERVER}
        req = self.doRequestPost(url=reverse("api_objectIdentify"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_objectIdentify_unauthorized(self):
        self.dump_oai_settings()
        data = {"url": URL_TEST_SERVER}
        #No authentification
        req = self.doRequestPost(url=reverse("api_objectIdentify"), data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_objectIdentify_serializer_invalid(self):
        self.dump_oai_settings()
        #Bad URL name
        data = {"urlBad": URL_TEST_SERVER}
        req = self.doRequestPost(url=reverse("api_objectIdentify"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sickleObjectIdentify(self):
        self.dump_oai_settings()
        self.setHarvest(True)
        url = URL_TEST_SERVER
        req = sickleObjectIdentify(url)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        retrievedIdentify = req.data
        self.assert_OaiIdentify_Settings(retrievedIdentify)

    def test_sickleObjectIdentify_unavailable(self):
        self.dump_oai_settings()
        self.setHarvest(False)
        url = URL_TEST_SERVER
        req = sickleObjectIdentify(url)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################

############################## listObjectSets tests ############################

    def test_listObjectSets(self):
        self.dump_oai_settings()
        self.dump_oai_my_set()
        self.setHarvest(True)
        data = {"url": URL_TEST_SERVER}
        req = self.doRequestPost(url=reverse("api_listObjectSets"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        retrievedSetsData = req.data
        self.assert_OaiSet(retrievedSetsData)

    def test_listObjectSets_unavailable(self):
        self.dump_oai_settings()
        self.setHarvest(False)
        data = {"url": URL_TEST_SERVER}
        req = self.doRequestPost(url=reverse("api_listObjectSets"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_listObjectSets_unauthorized(self):
        self.dump_oai_settings()
        self.dump_oai_my_set()
        data = {"url": URL_TEST_SERVER}
        #No authentification
        req = self.doRequestPost(url=reverse("api_listObjectSets"), data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listObjectSets_serializer_invalid(self):
        self.dump_oai_settings()
        self.dump_oai_my_set()
        #Bad URL name
        data = {"urlBad": URL_TEST_SERVER}
        req = self.doRequestPost(url=reverse("api_listObjectSets"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sickleListObjectSets(self):
        self.dump_oai_settings()
        self.dump_oai_my_set()
        self.setHarvest(True)
        url = URL_TEST_SERVER
        req = sickleListObjectSets(url)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        retrievedSetsData = req.data
        self.assert_OaiSet(retrievedSetsData)

    def test_sickleListObjectSets_unavailable(self):
        self.dump_oai_settings()
        self.setHarvest(False)
        url = URL_TEST_SERVER
        req = sickleListObjectSets(url)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_sickleListObjectSets_no_content(self):
        self.dump_oai_settings()
        #DO NOT LOAD SETS
        self.setHarvest(True)
        url = URL_TEST_SERVER
        req = sickleListObjectSets(url)
        self.assertEquals(req.status_code, status.HTTP_204_NO_CONTENT)

################################################################################


######################## listObjectMetadataFormats tests #######################

    def test_listObjectMetadataFormats(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        data = {"url": URL_TEST_SERVER}
        req = self.doRequestPost(url=reverse("api_listObjectMetadataFormats"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        retrievedMetadataformatsData = req.data
        self.assert_OaiMetadataFormat(retrievedMetadataformatsData)

    def test_listObjectMetadataFormats_unavailable(self):
        self.dump_oai_settings()
        self.setHarvest(False)
        data = {"url": URL_TEST_SERVER}
        req = self.doRequestPost(url=reverse("api_listObjectMetadataFormats"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_listObjectMetadataFormats_unauthorized(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        data = {"url": URL_TEST_SERVER}
        #No authentification
        req = self.doRequestPost(url=reverse("api_listObjectMetadataFormats"), data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listObjectMetadataFormats_serializer_invalid(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        #Bad URL name
        data = {"urlBad": URL_TEST_SERVER}
        req = self.doRequestPost(url=reverse("api_listObjectMetadataFormats"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sickleListObjectMetadataFormats(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        url = URL_TEST_SERVER
        req = sickleListObjectMetadataFormats(url)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        retrievedMetadataformatsData = req.data
        self.assert_OaiMetadataFormat(retrievedMetadataformatsData)


    def test_sickleListObjectMetadataFormats_no_content(self):
        self.dump_oai_settings()
        #DO NOT LOAD METADATA FORMATS
        self.setHarvest(True)
        url = URL_TEST_SERVER
        req = sickleListObjectMetadataFormats(url)
        self.assertEquals(req.status_code, status.HTTP_204_NO_CONTENT)

    def test_sickleListObjectMetadataFormats_unavailable(self):
        self.dump_oai_settings()
        self.setHarvest(False)
        url = URL_TEST_SERVER
        req = sickleListObjectMetadataFormats(url)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_sickleListObjectMetadataFormats_no_identify(self):
        self.dump_oai_settings()
        #SERVER not available, harvest False
        self.setHarvest(False)
        url = URL_TEST_SERVER
        req = sickleListObjectMetadataFormats(url)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################


########################## createSetsForRegistry tests #########################
    def test_createSetsForRegistry_function(self):
        registry = self.createFakeRegistry()
        setData = self.getSetData()
        createSetsForRegistry(registry, setData)
        for set in setData:
            objInDatabase = OaiSet.objects.get(setSpec=set['setSpec'],
                                                          registry=str(registry.id))
            self.assertEquals(set['setSpec'], objInDatabase.setSpec)
            self.assertEquals(set['setName'], objInDatabase.setName)
            self.assertEquals(str(registry.id), objInDatabase.registry)
            self.assertEquals(True, objInDatabase.harvest)
            # self.assertEquals(set['raw'], objInDatabase.raw)

    def test_createSetsForRegistry_function_bad_raw(self):
        registry = self.createFakeRegistry()
        setData = self.getSetDataBadRaw()
        createSetsForRegistry(registry, setData)
        with self.assertRaises(MONGO_ERRORS.DoesNotExist):
            OaiSet.objects.get(setSpec=setData[0]['setSpec'],
                                                          registry=str(registry.id))

################################################################################

################### createMetadataformatsForRegistry tests #####################

    def test_createMetadataformatsForRegistry_function(self):
        self.dump_template()
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        identify, registry = self.call_createRegistry()
        metadataformatsData = self.getMetadataFormatData()
        createMetadataformatsForRegistry(metadataformatsData, registry)
        self.assert_OaiMetadataFormat_Registry(metadataformatsData, registry)


    def test_createMetadataformatsForRegistry_function_bad_raw(self):
        self.dump_oai_settings()
        self.setHarvest(True)
        identify, registry = self.call_createRegistry()
        metadataformatsData = self.getMetadataFormatDataBadRaw()
        createMetadataformatsForRegistry(metadataformatsData, registry)
        with self.assertRaises(MONGO_ERRORS.DoesNotExist):
            OaiMetadataFormat.objects.get(metadataPrefix=metadataformatsData[0]['metadataPrefix'],
                                                          registry=str(registry.id))

    ###
    ### Add other data provider metadata format already existing in the server's metadata format
    ###
    def test_setMetadataFormatXMLSchema_existent_metadata(self):
        self.dump_template()
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        self.process_setMetadataFormatXMLSchema()

    def test_setMetadataFormatXMLSchema_metadataPrefix_exists_but_not_same_schema(self):
        self.dump_template()
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        #Get the template
        template = Template.objects.get(filename='AllResources.xsd')
        #Get AllResources.xsd metadata format
        metadataformat = self.getMetadataFormatDataAllResources()
        raw = xmltodict.parse(metadataformat['raw'])
        #Create an object
        obj = OaiMetadataFormat(metadataPrefix=metadataformat['metadataPrefix'],
                                metadataNamespace=metadataformat['metadataNamespace'],
                                schema=metadataformat['schema'], raw=raw, registry=FAKE_ID, harvest=True)
        #Get the schema
        xmlSchema = '<test>Not the same hash</test>'
        setMetadataFormatXMLSchema(obj, metadataformat['metadataPrefix'], xmlSchema)
        self.assertNotEquals(template.content, obj.xmlSchema)
        self.assertNotEquals(template.hash, obj.hash)
        self.assertEquals(None, obj.template)


    def test_setMetadataFormatXMLSchema_inexistent_metadata(self):
        self.dump_template()
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        #Delete the metadata format from the server's configuration
        OaiMyMetadataFormat.objects.get(metadataPrefix='oai_all').delete()
        self.process_setMetadataFormatXMLSchema()

    def process_setMetadataFormatXMLSchema(self):
        #Get the template
        template = Template.objects.get(filename='AllResources.xsd')
        #Get AllResources.xsd metadata format
        metadataformat = self.getMetadataFormatDataAllResources()
        raw = xmltodict.parse(metadataformat['raw'])
        #Create an object
        obj = OaiMetadataFormat(metadataPrefix=metadataformat['metadataPrefix'],
                                metadataNamespace=metadataformat['metadataNamespace'],
                                schema=metadataformat['schema'], raw=raw, registry=FAKE_ID, harvest=True)
        #Get the schema
        http_response = requests.get(obj.schema)
        if http_response.status_code == status.HTTP_200_OK:
            setMetadataFormatXMLSchema(obj, metadataformat['metadataPrefix'], http_response.text)
            self.assertEquals(template.content, obj.xmlSchema)
            self.assertEquals(template.hash, obj.hash)
            self.assertEquals(template, obj.template)

################################################################################


############################## Select registry tests ###########################

    def test_select_all_registries_zero(self):
        self.assertEquals(len(OaiRegistry.objects()), 0)
        req = self.doRequestGet(url="/oai_pmh/api/select/all/registries", auth=ADMIN_AUTH_GET)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        registriesData = req.content
        self.assertEquals(registriesData, '[]')


    def test_select_all_registries_one(self):
        self.createFakeRegistry()
        self.assertEquals(len(OaiRegistry.objects()), 1)
        req = self.doRequestGet(url="/oai_pmh/api/select/all/registries", auth=ADMIN_AUTH_GET)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        registriesData = req.content
        self.assertNotEquals(registriesData, '[]')

    def test_select_all_registries_unauthorized(self):
        req = self.doRequestGet(url="/oai_pmh/api/select/all/registries", auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    @skip("Find smthg to stop the database")
    def test_select_all_registries_error_database(self):
        self.assertEquals(len(OaiRegistry.objects()), 0)
        req = self.doRequestGet(url="/oai_pmh/api/select/all/registries", auth=ADMIN_AUTH_GET)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)


    def test_select_registry_one(self):
        self.createFakeRegistry()
        self.assertEquals(len(OaiRegistry.objects()), 1)
        params = {"name": "Fake registry"}
        req = self.doRequestGet(url="/oai_pmh/api/select/registry", params=params, auth=ADMIN_AUTH_GET)
        self.assertEquals(req.status_code, status.HTTP_200_OK)

    def test_select_registry_zero(self):
        self.assertEquals(len(OaiRegistry.objects()), 0)
        params = {"name": "Fake registry"}
        req = self.doRequestGet(url="/oai_pmh/api/select/registry", params=params, auth=ADMIN_AUTH_GET)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_select_registry_unauthorized(self):
        params = {"name": "Fake registry"}
        req = self.doRequestGet(url="/oai_pmh/api/select/registry", params=params, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_select_registry_serializer_invalid(self):
        params = {"nameBad": "Fake registry"}
        req = self.doRequestGet(url="/oai_pmh/api/select/registry", params=params, auth=ADMIN_AUTH_GET)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

################################################################################


############################## Update registry tests ###########################
    def test_update_registry(self):
        registry = self.createFakeRegistry()
        self.assertEquals(registry.harvestrate, None)
        self.assertEquals(registry.harvest, None)
        data = {"id": str(registry.id), "harvestrate": 1000, "harvest": "True"}
        req = self.doRequestPut(url="/oai_pmh/api/update/registry", data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        objInDatabase = OaiRegistry.objects.get(pk=registry.id)
        self.assertEquals(objInDatabase.harvestrate, 1000)
        self.assertEquals(objInDatabase.harvest, True)

    def test_update_registry_bad_id(self):
        registry = self.createFakeRegistry()
        self.assertNotEquals(registry.id, FAKE_ID)
        data = {"id": FAKE_ID, 'harvestrate': 1000, 'harvest': 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/registry", data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_all_registries_unauthorized(self):
        data = {"id": FAKE_ID, 'harvestrate': 1000, 'harvest': 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/registry", data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_all_registries_unauthorized_user(self):
        data = {"id": FAKE_ID, 'harvestrate': 1000, 'harvest': 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/registry", data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_select_all_registries_serializer_invalid(self):
        data = {"idd": FAKE_ID, 'harvestrate': 1000, 'harvest': 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/registry", data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"id": FAKE_ID, 'harvestrate': 1000}#, 'harvest': 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/registry", data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"id": FAKE_ID, 'harvest': 'True'}#, 'harvestrate': 1000}
        req = self.doRequestPut(url="/oai_pmh/api/update/registry", data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_select_all_registries_bad_entries(self):
        data = {"id": "badIdEntry", 'harvestrate': 'abcdde', 'harvest': 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/registry", data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"id": FAKE_ID, 'harvestrate': 'badHarvestrateEntry', 'harvest': 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/registry", data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

################################################################################

############################# Update my registry tests #########################
    def test_update_my_registry(self):
        self.dump_oai_settings()
        self.setHarvest(False)
        information = OaiSettings.objects.get()
        modifiedRepositoryName = "modifiedRepositoryName"
        self.assertNotEquals(information.repositoryName, modifiedRepositoryName)
        self.assertEquals(information.enableHarvesting, False)
        data = {"repositoryName": modifiedRepositoryName, "enableHarvesting": 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/my-registry", data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        objInDatabase = OaiSettings.objects.get()
        self.assertEquals(objInDatabase.repositoryName, modifiedRepositoryName)
        self.assertEquals(objInDatabase.enableHarvesting, True)


    def test_update_my_registry_unauthorized(self):
        self.dump_oai_settings()
        modifiedRepositoryName = "modifiedRepositoryName"
        data = {"repositoryName": modifiedRepositoryName, "enableHarvesting": 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/my-registry", data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_my_registry_unauthorized_user(self):
        self.dump_oai_settings()
        modifiedRepositoryName = "modifiedRepositoryName"
        data = {"repositoryName": modifiedRepositoryName, "enableHarvesting": 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/my-registry", data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_my_registry_serializer_invalid(self):
        self.dump_oai_settings()
        modifiedRepositoryName = "modifiedRepositoryName"
        data = {"repositoryNName": modifiedRepositoryName, "enableHarvesting": 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/my-registry", data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"repositoryName": modifiedRepositoryName, "enableHHarvesting": 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/my-registry", data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"repositoryName": modifiedRepositoryName}
        req = self.doRequestPut(url="/oai_pmh/api/update/my-registry", data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"enableHarvesting": 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/my-registry", data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_my_registry_bad_entries(self):
        self.dump_oai_settings()
        data = {"repositoryName": 1000, "enableHarvesting": 'True'}
        req = self.doRequestPut(url="/oai_pmh/api/update/my-registry", data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

################################################################################

############################## Delete registry tests ###########################

    def test_delete_registry(self):
        self.dump_oai_settings()
        self.dump_oai_registry()
        registry = OaiRegistry.objects.get()
        data = {"RegistryId": str(registry.id)}
        req = self.doRequestPost(url=reverse("api_delete_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        self.assertEquals(len(OaiRegistry.objects()), 0)
        self.assertEquals(len(OaiIdentify.objects()), 0)
        self.assertEquals(len(OaiMetadataFormat.objects()), 0)
        self.assertEquals(len(OaiSet.objects()), 0)
        self.assertEquals(len(OaiRecord.objects()), 0)

    def test_delete_registry_unauthorized(self):
        data = {"RegistryId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_delete_registry"), data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_registry_unauthorized_user(self):
        data = {"RegistryId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_delete_registry"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_registry_not_found(self):
        data = {"RegistryId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_delete_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_registry_serializer_invalid(self):
        data = {"RRegistryId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_delete_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_registry_bad_entries(self):
        data = {"RegistryId": 1000}
        req = self.doRequestPost(url=reverse("api_delete_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)


################################################################################

###################### Deactivate / Activate registry tests ####################

    def test_deactivate_registry(self):
        self.dump_oai_settings()
        self.dump_oai_registry()
        registry = OaiRegistry.objects.get()
        self.assertEquals(registry.isDeactivated, False)
        data = {"RegistryId": str(registry.id)}
        req = self.doRequestPost(url=reverse("api_deactivate_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        objInDatabase = OaiRegistry.objects.get(pk=registry.id)
        self.assertEquals(objInDatabase.isDeactivated, True)

    def test_deactivate_registry_unauthorized(self):
        data = {"RegistryId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_deactivate_registry"), data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deactivate_registry_unauthorized_user(self):
        data = {"RegistryId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_deactivate_registry"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deactivate_registry_not_found(self):
        data = {"RegistryId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_deactivate_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_deactivate_registry_serializer_invalid(self):
        data = {"RRegistryId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_deactivate_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deactivate_registry_bad_entries(self):
        data = {"RegistryId": 1000}
        req = self.doRequestPost(url=reverse("api_deactivate_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reactivate_registry(self):
        self.dump_oai_settings()
        self.dump_oai_registry()
        registry = OaiRegistry.objects.get()
        registry.isDeactivated = True
        registry.save()
        objInDatabase = OaiRegistry.objects.get(pk=registry.id)
        self.assertEquals(objInDatabase.isDeactivated, True)
        data = {"RegistryId": str(registry.id)}
        req = self.doRequestPost(url=reverse("api_reactivate_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        objInDatabase = OaiRegistry.objects.get(pk=registry.id)
        self.assertEquals(objInDatabase.isDeactivated, False)

    def test_reactivate_registry_unauthorized(self):
        data = {"RegistryId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_reactivate_registry"), data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reactivate_registry_unauthorized_user(self):
        data = {"RegistryId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_reactivate_registry"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reactivate_registry_not_found(self):
        data = {"RegistryId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_reactivate_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_reactivate_registry_serializer_invalid(self):
        data = {"RRegistryId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_reactivate_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reactivate_registry_bad_entries(self):
        data = {"RegistryId": 1000}
        req = self.doRequestPost(url=reverse("api_reactivate_registry"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)


################################################################################

######################### Update registry harvest tests ########################
    def test_update_registry_harvest(self):
        self.dump_oai_settings()
        self.dump_oai_registry()
        registry = OaiRegistry.objects.get()
        OaiMetadataFormat.objects(registry=str(registry.id)).update(set__harvest=False)
        OaiSet.objects(registry=str(registry.id)).update(set__harvest=False)
        twoFirstMF = [str(x.id) for x in OaiMetadataFormat.objects(registry=str(registry.id)).limit(2)]
        twoFirstSet = [str(x.id) for x in OaiSet.objects(registry=str(registry.id)).limit(2)]
        data = {"id": str(registry.id), 'metadataFormats': twoFirstMF, 'sets': twoFirstSet}
        req = self.doRequestPut(url=reverse("api_update_registry_harvest"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        metadataFormatsInDatabaseModified = OaiMetadataFormat.objects(registry=str(registry.id), pk__in=twoFirstMF).all()
        setsInDatabaseModified = OaiSet.objects(registry=str(registry.id), pk__in=twoFirstSet).all()
        metadataFormatsInDatabase = OaiMetadataFormat.objects(registry=str(registry.id), pk__nin=twoFirstMF).all()
        setsInDatabase = OaiSet.objects(registry=str(registry.id), pk__nin=twoFirstSet).all()
        for metadataF in metadataFormatsInDatabaseModified:
            self.assertEquals(metadataF.harvest, True)
        for set in setsInDatabaseModified:
            self.assertEquals(set.harvest, True)
        for metadataF in metadataFormatsInDatabase:
            self.assertEquals(metadataF.harvest, False)
        for set in setsInDatabase:
            self.assertEquals(set.harvest, False)

    def test_update_registry_harvest_unauthorized(self):
        data = {"id": FAKE_ID, 'metadataFormats': [], 'sets': []}
        req = self.doRequestPut(url=reverse("api_update_registry_harvest"), data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_update_registry_harvest_unauthorized_user(self):
        data = {"id": FAKE_ID, 'metadataFormats': [], 'sets': []}
        req = self.doRequestPut(url=reverse("api_update_registry_harvest"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_registry_harvest_serializer_invalid(self):
        data = {"idd": FAKE_ID, 'metadataFormats': []}
        req = self.doRequestPut(url=reverse("api_update_registry_harvest"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"id": FAKE_ID, 'mmetadataFormats': []}
        req = self.doRequestPut(url=reverse("api_update_registry_harvest"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"id": FAKE_ID}
        req = self.doRequestPut(url=reverse("api_update_registry_harvest"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"metadataFormats": []}
        req = self.doRequestPut(url=reverse("api_update_registry_harvest"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    @skip("Control charfield")
    def test_update_registry_harvest_bad_entries(self):
        data = {"id": 1000, 'metadataFormats': 1000, 'sets': 200}
        req = self.doRequestPut(url=reverse("api_update_registry_harvest"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)



################################################################################

########################### listObjectAllRecords tests #########################

    def test_listObjectAllRecords(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_xslt()
        self.setHarvest(True)
        metadataPrefix = "oai_soft"
        data = {"url": URL_TEST_SERVER, "metadataprefix": metadataPrefix}
        req = self.doRequestPost(url=reverse("api_listObjectAllRecords"), data=data, auth=ADMIN_AUTH)
        self.isStatusOK(req.status_code)
        self.assert_OaiListRecords(metadataPrefix, req.data)

    def test_listObjectAllRecords_with_deleted_inactive(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_xslt()
        self.dump_template()
        self.addNewSoftwareXmlDataDeleted()
        self.addNewSoftwareXmlDataInactive()
        self.setHarvest(True)
        metadataPrefix = "oai_soft"
        data = {"url": URL_TEST_SERVER, "metadataprefix": metadataPrefix}
        req = self.doRequestPost(url=reverse("api_listObjectAllRecords"), data=data, auth=ADMIN_AUTH)
        self.isStatusOK(req.status_code)
        self.assert_OaiListRecords(metadataPrefix, req.data)

    def test_listObjectAllRecords_unauthorized(self):
        self.dump_oai_settings()
        data = {"url": URL_TEST_SERVER}
        #No authentification
        req = self.doRequestPost(url=reverse("api_listObjectAllRecords"), data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listObjectAllRecords_server_not_found(self):
        self.dump_oai_settings()
        url= "http://127.0.0.1:8082/noserver"
        metadataPrefix = "oai_dc"
        data = {"url": url, "metadataprefix": metadataPrefix}
        req = self.doRequestPost(url=reverse("api_listObjectAllRecords"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_listObjectAllRecords_internal_error(self):
        self.dump_oai_settings()
        url= "http://127.0.0.2.:8000/noserver"
        metadataPrefix = "oai_dc"
        req, resumptionToken = getListRecords(url, metadataPrefix)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_listObjectAllRecords_serializer_invalid(self):
        self.dump_oai_settings()
        data = {"urlBad": URL_TEST_SERVER, "metadataprefix": "oai_soft"}
        req = self.doRequestPost(url=reverse("api_listObjectAllRecords"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

###############################################################################

############################### Get Record tests ##############################
    def test_getRecord(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.setHarvest(True)
        metadataPrefix = "oai_soft"
        myMetadataFormat = OaiMyMetadataFormat.objects().get(metadataPrefix=metadataPrefix)
        query = dict()
        query['schema'] = str(myMetadataFormat.template.id)
        #Get all records for this template
        dataInDatabase = XMLdata.executeQueryFullResult(query)
        for elt in dataInDatabase:
            identifier = '%s:%s:id/%s' % (settings.OAI_SCHEME, settings.OAI_REPO_IDENTIFIER, str(elt['_id']))
            data = {"url": URL_TEST_SERVER, "metadataprefix": metadataPrefix, "identifier": identifier}
            req = self.doRequestPost(url=reverse("api_getRecord"), data=data, auth=ADMIN_AUTH)
            if elt['ispublished'] == True:
                self.isStatusOK(req.status_code)
                self.assertTrue(len(req.data) == 1)
                self.assert_OaiRecord(metadataPrefix, req.data[0])
            else:
                self.isStatusInternalError(req.status_code)

    def test_getRecord_deleted_inactive(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_template()
        self.addNewSoftwareXmlDataDeleted()
        self.addNewSoftwareXmlDataInactive()
        self.setHarvest(True)
        metadataPrefix = "oai_soft"
        myMetadataFormat = OaiMyMetadataFormat.objects().get(metadataPrefix=metadataPrefix)
        query = dict()
        query['schema'] = str(myMetadataFormat.template.id)
        #Get all records for this template
        dataInDatabase = XMLdata.executeQueryFullResult(query)
        for elt in dataInDatabase:
            identifier = '%s:%s:id/%s' % (settings.OAI_SCHEME, settings.OAI_REPO_IDENTIFIER, str(elt['_id']))
            data = {"url": URL_TEST_SERVER, "metadataprefix": metadataPrefix, "identifier": identifier}
            req = self.doRequestPost(url=reverse("api_getRecord"), data=data, auth=ADMIN_AUTH)
            if elt['ispublished'] == True:
                self.isStatusOK(req.status_code)
                self.assertTrue(len(req.data) == 1)
                self.assert_OaiRecord(metadataPrefix, req.data[0])
            else:
                self.isStatusInternalError(req.status_code)

    def test_getRecord_unauthorized(self):
        self.dump_oai_settings()
        metadataPrefix = "oai_soft"
        identifier = "dummyIdentifier"
        data = {"url": URL_TEST_SERVER, "metadataprefix": metadataPrefix, "identifier": identifier}
        #No authentification
        req = self.doRequestPost(url=reverse("api_getRecord"), data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_getRecord_serializer_invalid(self):
        self.dump_oai_settings()
        metadataPrefix = "oai_soft"
        identifier = "dummyIdentifier"
        data = {"uurl": URL_TEST_SERVER}
        req = self.doRequestPost(url=reverse("api_getRecord"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"url": URL_TEST_SERVER, "metadataprefix": metadataPrefix}
        req = self.doRequestPost(url=reverse("api_getRecord"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"url": URL_TEST_SERVER, "identifier": identifier}
        req = self.doRequestPost(url=reverse("api_getRecord"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"identifier": identifier}
        req = self.doRequestPost(url=reverse("api_getRecord"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"metadataprefix": metadataPrefix}
        req = self.doRequestPost(url=reverse("api_getRecord"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"metadataprefix": metadataPrefix, "identifier": identifier}
        req = self.doRequestPost(url=reverse("api_getRecord"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_getRecord_bad_entries(self):
        self.dump_oai_settings()
        data = {"url": 1000, "metadataprefix": "oai_soft", "identifier": "dummyIdentifier"}
        req = self.doRequestPost(url=reverse("api_getRecord"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_getRecord_internal_error(self):
        #The value of the identifier argument (dummyIdentifier) is unknown or illegal in this repository.
        data = {"url": URL_TEST_SERVER, "metadataprefix": "oai_soft", "identifier": "dummyIdentifier"}
        req = self.doRequestPost(url=reverse("api_getRecord"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

###############################################################################

############################### listIdentifiers tests ##############################

    def test_listIdentifiers(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.setHarvest(True)
        metadataPrefix = "oai_soft"
        data = {"url": URL_TEST_SERVER, "metadataprefix": metadataPrefix}
        req = self.doRequestPost(url=reverse("api_listIdentifiers"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        self.assert_OaiListIdentifiers(metadataPrefix, req.data)

    def test_listIdentifiers_deleted_inactive(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_template()
        self.addNewSoftwareXmlDataDeleted()
        self.addNewSoftwareXmlDataInactive()
        self.setHarvest(True)
        metadataPrefix = "oai_soft"
        data = {"url": URL_TEST_SERVER, "metadataprefix": metadataPrefix}
        req = self.doRequestPost(url=reverse("api_listIdentifiers"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        self.assert_OaiListIdentifiers(metadataPrefix, req.data)


    def test_listIdentifiers_set(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_xslt()
        self.dump_xmldata()
        self.setHarvest(True)
        metadataPrefix = "oai_dc"
        set = "soft"
        data = {"url": URL_TEST_SERVER, "metadataprefix": metadataPrefix, "set": set}
        req = self.doRequestPost(url=reverse("api_listIdentifiers"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)

    def test_listIdentifiers_unauthorized(self):
        self.dump_oai_settings()
        metadataPrefix = "oai_soft"
        data = {"url": URL_TEST_SERVER, "metadataprefix": metadataPrefix}
        #No authentification
        req = self.doRequestPost(url=reverse("api_listIdentifiers"), data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listIdentifiers_serializer_invalid(self):
        self.dump_oai_settings()
        metadataPrefix = "oai_soft"
        data = {"uurl": URL_TEST_SERVER, "metadataprefix": metadataPrefix}
        req = self.doRequestPost(url=reverse("api_listIdentifiers"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"url": URL_TEST_SERVER, "mmetadataprefix": metadataPrefix}
        req = self.doRequestPost(url=reverse("api_listIdentifiers"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"url": URL_TEST_SERVER}
        req = self.doRequestPost(url=reverse("api_listIdentifiers"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"metadataprefix": metadataPrefix}
        req = self.doRequestPost(url=reverse("api_listIdentifiers"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_listIdentifiers_bad_entries(self):
        self.dump_oai_settings()
        data = {"url": 1000, "metadataprefix": "oai_soft"}
        req = self.doRequestPost(url=reverse("api_listIdentifiers"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_listIdentifiers_internal_error(self):
        #'The metadata format identified by the value given for the metadataPrefix argument (oai_xsoft)
        # is not supported by the item or by the repository.'
        self.dump_oai_settings()
        data = {"url": URL_TEST_SERVER, "metadataprefix": "oai_xsoft"}
        req = self.doRequestPost(url=reverse("api_listIdentifiers"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#
# ################################################################################

################################## getData tests ###############################

    def test_getData(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.setHarvest(True)
        metadataPrefix = "oai_soft"
        data = {"url": URL_TEST_SERVER + "?ListRecords&metadataprefix="+metadataPrefix}
        req = self.doRequestPost(url=reverse("api_get_data"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        self.assertNotEquals(req.data, '')

    def test_getData_deleted_inactive(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.addNewSoftwareXmlDataDeleted()
        self.addNewSoftwareXmlDataInactive()
        self.setHarvest(True)
        metadataPrefix = "oai_soft"
        data = {"url": URL_TEST_SERVER + "?ListRecords&metadataprefix="+metadataPrefix}
        req = self.doRequestPost(url=reverse("api_get_data"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        self.assertNotEquals(req.data, '')


    def test_getData_server_not_found(self):
        self.dump_oai_settings()
        url = "http://127.0.0.1:8082/noserver"
        metadataPrefix = "oai_soft"
        data = {"url": url + "?metadataprefix="+metadataPrefix}
        req = self.doRequestPost(url=reverse("api_get_data"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_getData_unauthorized(self):
        self.dump_oai_settings()
        metadataPrefix = "oai_soft"
        data = {"url": URL_TEST_SERVER + "?metadataprefix="+metadataPrefix}
        #No authentification
        req = self.doRequestPost(url=reverse("api_get_data"), data=data, auth=None)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_getData_bad_url_no_args(self):
        self.dump_oai_settings()
        url= "http://127.0.0.1:8082/noserver"
        data = {"url": url}
        req = self.doRequestPost(url=reverse("api_get_data"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_getData_serializer_invalid(self):
        self.dump_oai_settings()
        url= "http://127.0.0.1:8082/noserver"
        data = {}
        req = self.doRequestPost(url=reverse("api_get_data"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)


################################################################################


################################## Harvest tests ###############################

    #Harvest all sets = harvest by MF
    def test_harvest_by_MF(self):
        self.initDataBaseHarvest()
        allMetadataPrefixes = [x.metadataPrefix for x in OaiMyMetadataFormat.objects.all()]
        allSets = [x.setSpec for x in OaiMySet.objects.all()]
        self.harvest(allMetadataPrefixes, allSets)

    def test_harvest_by_MF_deleted_inactive(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_xslt()
        self.dump_oai_registry(dumpRecords=False)
        self.dump_template()
        self.addNewSoftwareXmlDataDeleted()
        self.addNewSoftwareXmlDataInactive()
        allMetadataPrefixes = [x.metadataPrefix for x in OaiMyMetadataFormat.objects.all()]
        allSets = [x.setSpec for x in OaiMySet.objects.all()]
        self.harvest(allMetadataPrefixes, allSets)


    def test_harvest_by_Set_MF(self):
        self.initDataBaseHarvest()
        allMetadataPrefixes = [x.metadataPrefix for x in OaiMyMetadataFormat.objects.all().limit(3)]
        allSets = [x.setSpec for x in OaiMySet.objects.all().limit(3)]
        self.harvest(allMetadataPrefixes, allSets)

    def test_harvest_by_Set_MF_deleted_inactive(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_xslt()
        self.dump_oai_registry(dumpRecords=False)
        self.dump_template()
        self.addNewSoftwareXmlDataDeleted()
        self.addNewSoftwareXmlDataInactive()
        allMetadataPrefixes = [x.metadataPrefix for x in OaiMyMetadataFormat.objects.all().limit(3)]
        allSets = [x.setSpec for x in OaiMySet.objects.all().limit(3)]
        self.harvest(allMetadataPrefixes, allSets)

    def test_harvest_bad_url(self):
        self.initDataBaseHarvest()
        #Modify server url, bad port
        registry = OaiRegistry.objects.get()
        registry.url = "http://127.0.0.1:8000/api_pmh/server"
        registry.save()
        data = {"registry_id": str(registry.id)}
        req = self.doRequestPost(url=reverse("api_harvest"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)

    def harvest(self, metadataPrefixes, setSpecs):
        metadataPrefixes = metadataPrefixes
        setSpecs = setSpecs
        registrySetsToHarvest, metadataformatsToHarvest, registry_id, registryAllSets = self.initHarvest(metadataPrefixes, setSpecs)
        data = {"registry_id": registry_id}
        req = self.doRequestPost(url=reverse("api_harvest"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        self.assert_harvest_lastUpdate_not_none(metadataformatsToHarvest, registrySetsToHarvest)
        for metadataFormat in metadataformatsToHarvest:
            for set in registrySetsToHarvest:
                self.assert_OaiRecords_In_Database(metadataPrefix=metadataFormat.metadataPrefix, setSpec=set.setSpec)

    def test_harvest_unauthorized(self):
        self.dump_oai_settings()
        data = {"registry_id": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_harvest"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_harvest_not_found(self):
        self.dump_oai_settings()
        data = {"registry_id": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_harvest"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_harvest_serializer_invalid(self):
        self.dump_oai_settings()
        data = {"registry_idd": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_harvest"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {}
        req = self.doRequestPost(url=reverse("api_harvest"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_harvestBySetsAndMF_function(self):
        self.initDataBaseHarvest()
        url = URL_TEST_SERVER
        metadataPrefixes = ["oai_dc"]
        setSpecs = ["soft"]
        registrySetsToHarvest, metadataformatsToHarvest, registry_id, registryAllSets = self.initHarvest(metadataPrefixes, setSpecs)
        allErrors = harvestBySetsAndMF(registrySetsToHarvest, metadataformatsToHarvest, url, registry_id, registryAllSets)
        self.assertEquals(len(allErrors), 0)
        self.assert_harvest_lastUpdate_not_none(metadataformatsToHarvest, registrySetsToHarvest)
        for metadataFormat in metadataformatsToHarvest:
            for set in registrySetsToHarvest:
                self.assert_OaiRecords_In_Database(metadataPrefix=metadataFormat.metadataPrefix, setSpec=set.setSpec)
        beforeDataInDatabase = len(OaiRecord.objects.all())
        #Add new record
        self.addNewSoftwareXmlData()
        allErrors = harvestBySetsAndMF(registrySetsToHarvest, metadataformatsToHarvest, url, registry_id, registryAllSets)
        self.assertEquals(len(allErrors), 0)
        afterDataInDatabase = len(OaiRecord.objects.all())
        self.assertEquals(afterDataInDatabase, beforeDataInDatabase+1)

    def test_harvestBySetsAndMF_function_add_wrong_set(self):
        self.initDataBaseHarvest()
        url = URL_TEST_SERVER
        metadataPrefixes = ["oai_dc"]
        setSpecs = ["soft"]
        registrySetsToHarvest, metadataformatsToHarvest, registry_id, registryAllSets = self.initHarvest(metadataPrefixes, setSpecs)
        allErrors = harvestBySetsAndMF(registrySetsToHarvest, metadataformatsToHarvest, url, registry_id, registryAllSets)
        self.assertEquals(len(allErrors), 0)
        self.assert_harvest_lastUpdate_not_none(metadataformatsToHarvest, registrySetsToHarvest)
        for metadataFormat in metadataformatsToHarvest:
            for set in registrySetsToHarvest:
                self.assert_OaiRecords_In_Database(metadataPrefix=metadataFormat.metadataPrefix, setSpec=set.setSpec)
        beforeDataInDatabase = len(OaiRecord.objects.all())
        #Add new record
        self.addNewDataCollectionXmlData()
        allErrors = harvestBySetsAndMF(registrySetsToHarvest, metadataformatsToHarvest, url, registry_id, registryAllSets)
        self.assertEquals(len(allErrors), 0)
        afterDataInDatabase = len(OaiRecord.objects.all())
        #Same number of OaiRecords
        self.assertEquals(afterDataInDatabase, beforeDataInDatabase)

    def test_harvestBySetsAndMF_function_bad_url(self):
        self.initDataBaseHarvest()
        url = ""
        metadataPrefixes = ["oai_dc"]
        setSpecs = ["soft"]
        registrySetsToHarvest, metadataformatsToHarvest, registry_id, registryAllSets = self.initHarvest(metadataPrefixes, setSpecs)
        allErrors = harvestBySetsAndMF(registrySetsToHarvest, metadataformatsToHarvest, url, registry_id, registryAllSets)
        self.assertTrue(len(allErrors) > 0)
        #No lastUpdate modification
        self.assert_harvest_lastUpdate_none(metadataformatsToHarvest, registrySetsToHarvest)

    def test_harvestByMF_function(self):
        self.initDataBaseHarvest()
        url = URL_TEST_SERVER
        metadataPrefixes = ["oai_soft"]
        registrySetsToHarvest, metadataformatsToHarvest, registry_id, registryAllSets = self.initHarvest(metadataPrefixes)
        allErrors = harvestByMF(registrySetsToHarvest, metadataformatsToHarvest, url, registry_id, registryAllSets)
        self.assertEquals(len(allErrors), 0)
        self.assert_harvest_lastUpdate_not_none(metadataformatsToHarvest, registrySetsToHarvest)
        for metadataFormat in metadataformatsToHarvest:
            self.assert_OaiRecords_In_Database(metadataFormat.metadataPrefix)
        beforeDataInDatabase = len(OaiRecord.objects.all())
        #Add new record
        self.addNewSoftwareXmlData()
        allErrors = harvestByMF(registrySetsToHarvest, metadataformatsToHarvest, url, registry_id, registryAllSets)
        self.assertEquals(len(allErrors), 0)
        afterDataInDatabase = len(OaiRecord.objects.all())
        self.assertEquals(afterDataInDatabase, beforeDataInDatabase+1)

    def test_harvestByMF_function_bad_url(self):
        self.initDataBaseHarvest()
        url = ""
        metadataPrefixes = ["oai_soft"]
        registrySetsToHarvest, metadataformatsToHarvest, registry_id, registryAllSets = self.initHarvest(metadataPrefixes)
        allErrors = harvestByMF(registrySetsToHarvest, metadataformatsToHarvest, url, registry_id, registryAllSets)
        self.assertTrue(len(allErrors) > 0)
        #No lastUpdate modification
        self.assert_harvest_lastUpdate_none(metadataformatsToHarvest, registrySetsToHarvest)

    def initHarvest(self, metadataPrefixes, setSpecs=[]):
        registry = OaiRegistry.objects.get()
        registry.url = URL_TEST_SERVER
        registry.save()
        registry_id = str(registry.id)
        #Disable all MF
        OaiMetadataFormat.objects.filter(registry=registry_id).update(set__harvest=False, set__lastUpdate=None)
        #Enable MF in parameter
        OaiMetadataFormat.objects.filter(registry=registry_id, metadataPrefix__in=metadataPrefixes).update(set__harvest=True)
        #Disable all sets
        OaiSet.objects.filter(registry=registry_id).update(set__harvest=False)
        #Enable sets in parameter
        OaiSet.objects.filter(registry=registry_id, setSpec__in=setSpecs).update(set__harvest=True)
        #Get all available MF
        metadataformatsToHarvest = OaiMetadataFormat.objects(registry=registry_id, harvest=True).all()
        #Get all available  sets
        registrySetsToHarvest = OaiSet.objects(registry=registry_id, harvest=True).order_by("setName")
        #Get all sets
        registryAllSets = OaiSet.objects(registry=registry_id).order_by("setName")
        return registrySetsToHarvest, metadataformatsToHarvest, registry_id, registryAllSets
#
    def initDataBaseHarvest(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_xslt()
        self.dump_oai_registry(dumpRecords=False)

    # ####
    def test_harvestRecords_function_mf(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.dump_oai_registry(dumpRecords=False)
        dataInDatabase = OaiRecord.objects.all()
        self.assertEquals(len(dataInDatabase), 0)
        self.harvestRecords_function_mf_process()

    def test_harvestRecords_function_mf_last_update(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.dump_oai_registry(dumpRecords=False)
        dataInDatabase = OaiRecord.objects.all()
        self.assertEquals(len(dataInDatabase), 0)
        beforeDataInDatabase = len(OaiRecord.objects.all())
        self.assertEquals(beforeDataInDatabase, 0)
        lastUpdate = datetime.datetime.now()
        lastUpdate = str(datestamp.datetime_to_datestamp(lastUpdate))
        self.harvestRecords_function_mf_process()
        beforeDataInDatabase = len(OaiRecord.objects.all())
        self.assertTrue(beforeDataInDatabase > 0)
        #Add new record
        self.addNewSoftwareXmlData()
        #Harvest it
        self.harvestRecords_function_mf_process(lastUpdate=lastUpdate)
        afterDataInDatabase = len(OaiRecord.objects.all())
        self.assertEquals(afterDataInDatabase, beforeDataInDatabase+1)

    def harvestRecords_function_mf_process(self, lastUpdate=None):
        registry = OaiRegistry.objects.get()
        registry_id = str(registry.id)
        url = URL_TEST_SERVER
        metadataPrefix = "oai_soft"
        metadataformat = OaiMetadataFormat.objects(metadataPrefix=metadataPrefix).get()
        registryAllSets = OaiSet.objects(registry=registry_id).order_by("setName")
        allErrors = harvestRecords(url=url, registry_id=registry_id, metadataFormat=metadataformat, lastUpdate=lastUpdate,
                       registryAllSets=registryAllSets, set=None)
        self.assertEquals(len(allErrors), 0)
        dataInDatabase = OaiRecord.objects.all()
        self.assertTrue(len(dataInDatabase) > 0)
        self.assert_OaiRecords_In_Database(metadataPrefix)

    def test_harvestRecords_function_set(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_xslt()
        self.dump_oai_registry(dumpRecords=False)
        dataInDatabase = OaiRecord.objects.all()
        self.assertEquals(len(dataInDatabase), 0)
        registry = OaiRegistry.objects.get()
        registry_id = str(registry.id)
        url = URL_TEST_SERVER
        metadataPrefix = "oai_dc"
        metadataformat = OaiMetadataFormat.objects(metadataPrefix=metadataPrefix).get()
        set = OaiMySet.objects(setSpec="soft").get()
        registryAllSets = OaiSet.objects(registry=registry_id).order_by("setName")
        allErrors = harvestRecords(url=url, registry_id=registry_id, metadataFormat=metadataformat, lastUpdate=None,
               registryAllSets=registryAllSets, set=set)
        self.assertEquals(len(allErrors), 0)
        dataInDatabase = OaiRecord.objects.all()
        self.assertTrue(len(dataInDatabase) > 0)
        self.assert_OaiRecords_In_Database(metadataPrefix, setSpec="soft")


    def test_harvestRecords_function_bad_url(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_registry(dumpRecords=False)
        registry = OaiRegistry.objects.get()
        registry_id = str(registry.id)
        url = ""
        metadataPrefix = "oai_dc"
        metadataformat = OaiMetadataFormat.objects(metadataPrefix=metadataPrefix).get()
        registryAllSets = OaiSet.objects(registry=registry_id).order_by("setName")
        allErrors = harvestRecords(url=url, registry_id=registry_id, metadataFormat=metadataformat, lastUpdate=None,
               registryAllSets=registryAllSets)
        self.assertTrue(len(allErrors) > 0)

    def test_getListRecords_function_metadataPrefix(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_xslt()
        self.setHarvest(True)
        url= URL_TEST_SERVER
        metadataPrefix = "oai_soft"
        req, resumptionToken = getListRecords(url=url, metadataPrefix=metadataPrefix)
        self.isStatusOK(req.status_code)
        self.assert_OaiListRecords(metadataPrefix, req.data)

    def test_getListRecords_function_set(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_xslt()
        self.setHarvest(True)
        url= URL_TEST_SERVER
        metadataPrefix = "oai_dc"
        setSpec = "soft"
        req, resumptionToken = getListRecords(url=url, metadataPrefix=metadataPrefix, set_h=setSpec)
        self.isStatusOK(req.status_code)
        self.assert_OaiListRecords(metadataPrefix, req.data, setSpec)

    def test_getListRecords_function_from(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_xslt()
        self.setHarvest(True)
        url= URL_TEST_SERVER
        metadataPrefix = "oai_dc"
        setSpec = "soft"
        fromDate = "2016-05-04T15:23:00Z"
        req, resumptionToken = getListRecords(url=url, metadataPrefix=metadataPrefix, fromDate=fromDate)
        self.isStatusOK(req.status_code)
        self.assert_OaiListRecords(metadataPrefix, req.data, fromDate=fromDate)
        fromDate = "2016-05-04T20:23:00Z"
        req, resumptionToken = getListRecords(url=url, metadataPrefix=metadataPrefix, fromDate=fromDate)
        self.isStatusOK(req.status_code)
        self.assert_OaiListRecords(metadataPrefix, req.data, fromDate=fromDate)

    def test_getListRecords_function_dummy_resumptionToken(self):
        self.dump_oai_settings()
        self.setHarvest(True)
        url= URL_TEST_SERVER
        metadataPrefix = "oai_dc"
        resumptionToken = "dummyResumptionToken"
        req, resumptionToken = getListRecords(url=url, metadataPrefix=metadataPrefix, resumptionToken=resumptionToken)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        #No data
        self.assertTrue(len(req.data) == 0)

    def test_getListRecords_function_server_not_found(self):
        self.dump_oai_settings()
        url= "http://127.0.0.1:8082/noserver"
        metadataPrefix = "oai_dc"
        req, resumptionToken = getListRecords(url, metadataPrefix)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_getListRecords_function_internal_error(self):
        self.dump_oai_settings()
        url= "http://127.0.0.2.:8000/noserver"
        metadataPrefix = "oai_dc"
        req, resumptionToken = getListRecords(url, metadataPrefix)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

###############################################################################

######################## update_registry_info tests ###########################


    def test_update_registry_info(self):
        self.dump_oai_settings()
        self.dump_oai_registry(dumpRecords=False, dumpSets=False, dumpMetadataFormats=False)
        self.setHarvest(True)
        lenBeforeMF = len(OaiMetadataFormat.objects.all())
        lenBeforeSets = len(OaiSet.objects.all())
        self.assertEquals(lenBeforeMF, 0)
        self.assertEquals(lenBeforeSets, 0)
        #Dump new MF and Set for the server
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        registry = OaiRegistry.objects.get()
        registry.url = URL_TEST_SERVER
        registry.save()
        registry_id = str(registry.id)
        data = {"registry_id": registry_id}
        #Update the information
        req = self.doRequestPut(url=reverse("api_update_registry_info"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        #Check the update
        lenAfterMF = len(OaiMetadataFormat.objects.all())
        lenAfterSets = len(OaiSet.objects.all())
        lenMyMF = len(OaiMyMetadataFormat.objects.all())
        lenMySets = len(OaiMySet.objects.all())
        self.assertTrue(lenAfterMF,lenMyMF)
        self.assertTrue(lenAfterSets, lenMySets)


    def test_update_registry_info_no_set(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        # self.dump_oai_my_set()
        self.dump_xmldata()
        self.dump_oai_registry()
        self.setHarvest(True)
        registry = OaiRegistry.objects.get()
        registry.url = URL_TEST_SERVER
        registry.save()
        registry_id = str(registry.id)
        data = {"registry_id": registry_id}
        req = self.doRequestPut(url=reverse("api_update_registry_info"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)

    def test_update_registry_info_no_mf(self):
        self.dump_oai_settings()
        # self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.dump_oai_registry()
        self.setHarvest(True)
        registry = OaiRegistry.objects.get()
        registry.url = URL_TEST_SERVER
        registry.save()
        registry_id = str(registry.id)
        data = {"registry_id": registry_id}
        req = self.doRequestPut(url=reverse("api_update_registry_info"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)

    def test_update_registry_info_bad_identify(self):
        self.dump_oai_settings_bad()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_oai_registry()
        registry = OaiRegistry.objects.get()
        registry.url = URL_TEST_SERVER
        registry.save()
        registry_id = str(registry.id)
        data = {"registry_id": registry_id}
        req = self.doRequestPut(url=reverse("api_update_registry_info"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_update_registry_info_bad_mf(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format_bad()
        self.dump_oai_my_set()
        self.dump_oai_registry()
        registry = OaiRegistry.objects.get()
        registry.url = URL_TEST_SERVER
        registry.save()
        registry_id = str(registry.id)
        data = {"registry_id": registry_id}
        req = self.doRequestPut(url=reverse("api_update_registry_info"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


    def test_update_registry_info_bad_set(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set_bad()
        self.dump_oai_registry()
        registry = OaiRegistry.objects.get()
        registry.url = URL_TEST_SERVER
        registry.save()
        registry_id = str(registry.id)
        data = {"registry_id": registry_id}
        req = self.doRequestPut(url=reverse("api_update_registry_info"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


    def test_update_registry_info_server_bad_url(self):
        self.dump_oai_settings()
        self.dump_oai_registry()
        registry = OaiRegistry.objects.get()
        url= "http://127.0.0.1:8082/noserver"
        registry.url = url
        registry.save()
        registry_id = str(registry.id)
        data = {"registry_id": registry_id}
        req = self.doRequestPut(url=reverse("api_update_registry_info"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_update_registry_info_unauthorized(self):
        self.dump_oai_settings()
        data = {"registry_id": FAKE_ID}
        req = self.doRequestPut(url=reverse("api_update_registry_info"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_registry_info_serializer_invalid(self):
        self.dump_oai_settings()
        data = {"rrrrrregistry_id": FAKE_ID}
        req = self.doRequestPut(url=reverse("api_update_registry_info"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_registry_info_registry_not_found(self):
        self.dump_oai_settings()
        data = {"registry_id": FAKE_ID}
        req = self.doRequestPut(url=reverse("api_update_registry_info"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_modifyRegistry(self):
        #Call the function to create the registry
        identify, registry = self.call_createRegistry()
        self.assert_OaiIdentify(identify)
        modifiedIdentifyData = self.getModifiedIdentifyData()
        identify, registry = modifyRegistry(modifiedIdentifyData, registry)
        self.assert_OaiIdentify(identify, modifiedIdentifyData)
        self.assertEqual(identify, registry.identify)
        self.assertEqual(identify.repositoryName, registry.name)
        self.assertEqual(identify.description, registry.description)

    def test_modifyRegistry_bad_raw(self):
        #Call the function to create the registry
        identify, registry = self.call_createRegistry()
        self.assert_OaiIdentify(identify)
        identifyData = self.getIdentifyData()
        identifyData['raw'] = '<test>hello<test>'
        identifyData['repositoryName'] = "New fake name"
        modifyRegistry(identifyData, registry)
        identify = OaiRegistry.objects.get(pk=registry.id).identify
        self.assert_OaiIdentify(identify, identifyData)

    def test_modifyOaiIdentify(self):
        identify, registry = self.call_createRegistry()
        self.assert_OaiIdentify(identify)
        identifyData = self.getModifiedIdentifyData()
        raw = identifyData['raw']
        identifyRaw = xmltodict.parse(raw)
        modifiedIdentity = modifyOaiIdentify(identifyData, identifyRaw, identify.id)
        self.assert_OaiIdentify(modifiedIdentity, identifyData)

    def test_modifyMetadataformatsForRegistry(self):
        self.dump_template()
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        identify, registry = self.call_createRegistry()
        metadataformatsData = self.getMetadataFormatData()
        createMetadataformatsForRegistry(metadataformatsData, registry)
        self.assert_OaiMetadataFormat_Registry(metadataformatsData, registry)
        modifiedMetadataformatsData = self.getModifiedMetadataFormatData()
        modifyMetadataformatsForRegistry(registry, modifiedMetadataformatsData)
        self.assert_OaiMetadataFormat_Registry(modifiedMetadataformatsData, registry)

    def test_modifyMetadataformatsForRegistry_new_MF(self):
        self.dump_template()
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        identify, registry = self.call_createRegistry()
        metadataformatsData = self.getMetadataFormatData()
        createMetadataformatsForRegistry(metadataformatsData, registry)
        self.assert_OaiMetadataFormat_Registry(metadataformatsData, registry)
        modifiedMetadataformatsData = self.getNewMetadataFormatData()
        lenBeforeMF = len(OaiMetadataFormat.objects.all())
        modifyMetadataformatsForRegistry(registry, modifiedMetadataformatsData)
        lenAfterMF = len(OaiMetadataFormat.objects.all())
        self.assertEqual(lenAfterMF, lenBeforeMF + 1)
        self.assert_OaiMetadataFormat_Registry(modifiedMetadataformatsData, registry)

    def test_modifyMetadataformatsForRegistry_bad_new_MF(self):
        self.dump_template()
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        identify, registry = self.call_createRegistry()
        metadataformatsData = self.getMetadataFormatData()
        createMetadataformatsForRegistry(metadataformatsData, registry)
        self.assert_OaiMetadataFormat_Registry(metadataformatsData, registry)
        modifiedMetadataformatsData = self.getBadNewMetadataFormatData()
        lenBeforeMF = len(OaiMetadataFormat.objects.all())
        modifyMetadataformatsForRegistry(registry, modifiedMetadataformatsData)
        lenAfterMF = len(OaiMetadataFormat.objects.all())
        self.assertEqual(lenAfterMF, lenBeforeMF)

    def test_modifySetsForRegistry(self):
        self.dump_template()
        self.dump_oai_settings()
        self.dump_oai_my_set()
        self.setHarvest(True)
        identify, registry = self.call_createRegistry()
        setsData = self.getSetData()
        createSetsForRegistry(registry, setsData)
        self.assert_OaiSet_Registry(setsData, registry)
        modifiedSetsData = self.getModifiedSetData()
        modifySetsForRegistry(registry, modifiedSetsData)
        self.assert_OaiSet_Registry(modifiedSetsData, registry)

    def test_modifySetsForRegistry_new_set(self):
        self.dump_template()
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        identify, registry = self.call_createRegistry()
        setsData = self.getSetData()
        createSetsForRegistry(registry, setsData)
        self.assert_OaiSet_Registry(setsData, registry)
        modifiedSetsData = self.getNewSetData()
        lenBeforeSet = len(OaiSet.objects.all())
        modifySetsForRegistry(registry, modifiedSetsData)
        lenAfterSet = len(OaiSet.objects.all())
        self.assertEqual(lenAfterSet, lenBeforeSet + 1)
        self.assert_OaiSet_Registry(modifiedSetsData, registry)

    def test_modifySetsForRegistry_bad_new_set(self):
        self.dump_template()
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.setHarvest(True)
        identify, registry = self.call_createRegistry()
        setsData = self.getSetData()
        createSetsForRegistry(registry, setsData)
        self.assert_OaiSet_Registry(setsData, registry)
        modifiedSetsData = self.getBadNewSetData()
        lenBeforeSet = len(OaiSet.objects.all())
        modifySetsForRegistry(registry, modifiedSetsData)
        lenAfterSet = len(OaiSet.objects.all())
        self.assertEqual(lenAfterSet, lenBeforeSet)

###############################################################################


####################### add_my_metadataFormat tests ###########################

    def test_add_my_metadataFormat(self):
        self.dump_oai_settings()
        self.dump_template()
        before = OaiMyMetadataFormat.objects.all()
        self.assertEqual(len(before), 0)
        metadataPrefix = 'oai_test'
        schema = 'http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd'
        data = {"metadataPrefix": metadataPrefix, 'schema': schema}
        req = self.doRequestPost(url=reverse("api_add_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_201_CREATED)
        after = OaiMyMetadataFormat.objects.all()
        self.assertEquals(len(after), 1)
        obj = after[0]
        self.assertEquals(obj.metadataPrefix, metadataPrefix)
        self.assertEquals(obj.schema, schema)
        self.assertNotEquals(obj.metadataNamespace, '')
        self.assertEquals(obj.isDefault, False)
        self.assertNotEquals(obj.xmlSchema, '')

    def test_add_my_metadataFormat_target_namespace(self):
        self.dump_oai_settings()
        templateVersion = self.createTemplateVersion()
        template = self.createTemplateWithTemplateVersionValidContent(str(templateVersion.id))
        metadataPrefix = 'oai_test'
        schema = 'http://127.0.0.1:8082/oai_pmh/server/XSD/' + template.filename
        data = {"metadataPrefix": metadataPrefix, 'schema': schema}
        req = self.doRequestPost(url=reverse("api_add_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_201_CREATED)
        after = OaiMyMetadataFormat.objects.all()
        self.assertEquals(len(after), 1)
        obj = after[0]
        self.assertNotEquals(obj.metadataNamespace, 'http://www.w3.org/2001/XMLSchema')

    @skip("Not working if launched with other tests")
    def test_add_my_metadataFormat_duplicate(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_template()
        self.dump_oai_registry()
        self.setHarvest(True)
        data = {"metadataPrefix": 'oai_dc', 'schema':'http://www.openarchives.org/OAI/2.0/oai_dc.xsd'}
        req = self.doRequestPost(url=reverse("api_add_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_409_CONFLICT)

    def test_add_my_metadataFormat_bad_server_url(self):
        self.dump_oai_settings()
        self.dump_template()
        data = {"metadataPrefix": 'oai_test', 'schema':'http://test:8082/oai_pmh/server/XSD/Fake.xsd'}
        req = self.doRequestPost(url=reverse("api_add_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_my_metadataFormat_bad_xml_url(self):
        self.dump_oai_settings()
        self.dump_template()
        data = {"metadataPrefix": 'oai_test', 'schema':'http://127.0.0.1:8082/oai_pmh/server/XSD/Fake.xsd'}
        req = self.doRequestPost(url=reverse("api_add_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_my_metadataFormat_bad_xml_syntax(self):
        self.dump_oai_identify()
        templateVersion = self.createTemplateVersion()
        template = self.createTemplateWithTemplateVersionInvalidContent(str(templateVersion.id))
        #Add a bad xml
        data = {"metadataPrefix": 'oai_test', 'schema':'http://127.0.0.1:8082/oai_pmh/server/XSD/'+ template.filename}
        req = self.doRequestPost(url=reverse("api_add_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_my_metadataFormat_invalid_serializer(self):
        self.dump_oai_settings()
        self.dump_template()
        data = {"mmetadataPrefix": 'oai_test', 'schema':'http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd'}
        req = self.doRequestPost(url=reverse("api_add_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"metadataPrefix": 'oai_test', 'sschema':'http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd'}
        req = self.doRequestPost(url=reverse("api_add_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_my_metadataFormat_unauthorized(self):
        self.dump_oai_settings()
        self.dump_template()
        data = {"metadataPrefix": 'oai_test', 'schema':'http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd'}
        req = self.doRequestPost(url=reverse("api_add_my_metadataFormat"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

################################################################################

######################## add_my_template_metadataFormat tests ###########################

    def test_add_my_template_metadataFormat(self):
        self.dump_oai_settings()
        template = self.createTemplate()
        metadataPrefix = 'oai_test'
        data = {"metadataPrefix": metadataPrefix, 'template': str(template.id)}
        req = self.doRequestPost(url=reverse("api_add_my_template_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_201_CREATED)
        after = OaiMyMetadataFormat.objects.all()
        self.assertEquals(len(after), 1)
        obj = after[0]
        self.assertEquals(obj.metadataPrefix, metadataPrefix)
        self.assertEquals(obj.schema, OAI_HOST_URI + reverse('getXSD', args=[template.filename]))
        self.assertNotEquals(obj.metadataNamespace, '')
        self.assertEquals(obj.isDefault, False)
        self.assertEquals(obj.isTemplate, True)
        self.assertEquals(obj.template, template)
        self.assertEquals(obj.xmlSchema, '')

    def test_add_my_template_metadataFormat_target_namespace(self):
        self.dump_oai_settings()
        templateVersion = self.createTemplateVersion()
        template = self.createTemplateWithTemplateVersionValidContent(str(templateVersion.id))
        metadataPrefix = 'oai_test'
        data = {"metadataPrefix": metadataPrefix,'template': str(template.id)}
        req = self.doRequestPost(url=reverse("api_add_my_template_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_201_CREATED)
        after = OaiMyMetadataFormat.objects.all()
        self.assertEquals(len(after), 1)
        obj = after[0]
        self.assertNotEquals(obj.metadataNamespace, 'http://www.w3.org/2001/XMLSchema')

    @skip("Not working if launched with other tests")
    def test_add_my_template_metadataFormat_duplicate(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_template()
        self.dump_oai_registry()
        template = Template.objects(filename='Software.xsd').get()
        data = {"metadataPrefix": 'oai_soft', 'template': str(template.id)}
        req = self.doRequestPost(url=reverse("api_add_my_template_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_409_CONFLICT)

    def test_add_my_template_metadataFormat_bad_template(self):
        self.dump_oai_settings()
        self.dump_template()
        data = {"metadataPrefix": 'oai_test', 'template':FAKE_ID}
        req = self.doRequestPost(url=reverse("api_add_my_template_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_my_template_metadataFormat_bad_xml_synthax(self):
        self.dump_oai_identify()
        templateVersion = self.createTemplateVersion()
        template = self.createTemplateWithTemplateVersionInvalidContent(str(templateVersion.id))
        #Add a bad xml
        data = {"metadataPrefix": 'oai_test', 'template': str(template.id)}
        req = self.doRequestPost(url=reverse("api_add_my_template_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_my_template_metadataFormat_invalid_serializer(self):
        self.dump_oai_settings()
        self.dump_template()
        data = {"mmetadataPrefix": 'oai_test', 'template':FAKE_ID}
        req = self.doRequestPost(url=reverse("api_add_my_template_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"metadataPrefix": 'oai_test', 'ttemplate': FAKE_ID}
        req = self.doRequestPost(url=reverse("api_add_my_template_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_my_template_metadataFormat_unauthorized(self):
        self.dump_oai_settings()
        template = self.createTemplate()
        data = {"metadataPrefix": 'oai_test', 'template': str(template.id)}
        req = self.doRequestPost(url=reverse("api_add_my_template_metadataFormat"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

################################################################################

###################### delete_my_metadataFormat tests ##########################

    def test_delete_my_metadataFormat(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        all = OaiMyMetadataFormat.objects.all()
        beforeAllRecords = len(all)
        #Delete the first
        data = {"MetadataFormatId": str(all[0].id)}
        req = self.doRequestPost(url=reverse("api_delete_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        afterAllRecords = len(OaiMyMetadataFormat.objects.all())
        self.assertEquals(afterAllRecords, beforeAllRecords - 1)

    def test_delete_my_metadataFormat_not_found(self):
        self.dump_oai_settings()
        data = {"MetadataFormatId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_delete_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_my_metadataFormat_invalid_serializer(self):
        self.dump_oai_settings()
        data = {"MMetadataFormatId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_delete_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_my_metadataFormat_unauthorized(self):
        self.dump_oai_settings()
        data = {"MetadataFormatId": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_delete_my_metadataFormat"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

################################################################################


###################### update_my_metadataFormat tests ##########################

    def test_update_my_metadataFormat(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        firstMF = OaiMyMetadataFormat.objects.first()
        newMetadataPrefix = 'oai_test'
        self.assertNotEquals(firstMF.metadataPrefix, newMetadataPrefix)
        #Delete the first
        data = {"id": str(firstMF.id), "metadataPrefix": newMetadataPrefix}
        req = self.doRequestPut(url=reverse("api_update_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        objInDatabase =  OaiMyMetadataFormat.objects(pk=firstMF.id).get()
        self.assertEquals(objInDatabase.metadataPrefix, newMetadataPrefix)

    def test_update_my_metadataFormat_not_found(self):
        self.dump_oai_settings()
        data = {"id": FAKE_ID, "metadataPrefix": 'oai_test'}
        req = self.doRequestPut(url=reverse("api_update_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_my_metadataFormat_invalid_serializer(self):
        self.dump_oai_settings()
        data = {"iid": FAKE_ID, "metadataPrefix": 'oai_test'}
        req = self.doRequestPut(url=reverse("api_update_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"id": FAKE_ID, "mmetadataPrefix": 'oai_test'}
        req = self.doRequestPut(url=reverse("api_update_my_metadataFormat"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_my_metadataFormat_unauthorized(self):
        self.dump_oai_settings()
        data = {"id": FAKE_ID, "metadataPrefix": 'oai_test'}
        req = self.doRequestPut(url=reverse("api_update_my_metadataFormat"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

################################################################################

################################ Set tests #####################################

    def test_add_my_set(self):
        self.dump_oai_settings()
        self.dump_template()
        self.dump_oai_my_set()
        setSpec = "test"
        setName = "test set"
        description = "set description"
        templates = [str(x.id) for x in Template.objects.all().limit(3)]
        data = {"setSpec": setSpec, "setName": setName, "templates": templates, "description": description}
        req = self.doRequestPost(url=reverse("api_add_my_set"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_201_CREATED)
        objInDatabase = OaiMySet.objects(setSpec=setSpec).get()
        self.assertEquals(objInDatabase.setSpec, setSpec)
        self.assertEquals(objInDatabase.setName, setName)
        self.assertEquals([str(x.id) for x in objInDatabase.templates], templates)
        self.assertEquals(objInDatabase.description, description)

    @skip("Not working if launched with other tests")
    def test_add_my_set_not_unique(self):
        self.dump_oai_settings()
        self.dump_template()
        self.dump_oai_my_set()
        setSpec = "soft"
        setName = "software"
        templates = [str(Template.objects(title=setName).get().id)]
        data = {"setSpec": setSpec, "setName": setName, "templates": templates, "description": 'set description'}
        req = self.doRequestPost(url=reverse("api_add_my_set"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_409_CONFLICT)

    def test_add_my_set_invalid_serializer(self):
        self.dump_oai_settings()
        self.dump_template()
        setSpec = "test"
        setName = "test set"
        templates = [str(x.id) for x in Template.objects.all().limit(3)]
        data = {"ssetSpec": setSpec, "setName": setName, "templates": templates}
        req = self.doRequestPost(url=reverse("api_add_my_set"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"setSpec": setSpec, "ssetName": setName, "templates": templates}
        req = self.doRequestPost(url=reverse("api_add_my_set"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"setSpec": setSpec, "setName": setName, "ttemplates": templates}
        req = self.doRequestPost(url=reverse("api_add_my_set"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_my_set_unauthorized(self):
        self.dump_oai_settings()
        self.dump_template()
        setSpec = "test"
        setName = "test set"
        templates = [str(x.id) for x in Template.objects.all().limit(3)]
        data = {"setSpec": setSpec, "setName": setName, "templates": templates, "description": 'set description'}
        req = self.doRequestPost(url=reverse("api_add_my_set"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_delete_my_set(self):
        self.dump_oai_settings()
        self.dump_template()
        self.dump_oai_my_set()
        set = OaiMySet.objects.first()
        data = {"set_id": str(set.id)}
        req = self.doRequestPost(url=reverse("api_delete_my_set"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        with self.assertRaises(MONGO_ERRORS.DoesNotExist):
            OaiSet.objects.get(pk=set.id)

    def test_delete_my_set_not_found(self):
        self.dump_oai_settings()
        data = {"set_id": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_delete_my_set"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_my_set_invalid_serializer(self):
        self.dump_oai_settings()
        data = {"sset_id": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_delete_my_set"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_my_set_unauthorized(self):
        self.dump_oai_settings()
        data = {"set_id": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_delete_my_set"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_update_my_set(self):
        self.dump_oai_settings()
        self.dump_oai_my_set()
        self.dump_template()
        setSpec = "modified setSpec"
        setName = "modified name"
        description = "modified description"
        set = OaiMySet.objects.first()
        templates = [str(x.id) for x in Template.objects.all().limit(3)]
        data = {"id": str(set.id), "setSpec": setSpec, "setName": setName, "templates": templates,
                "description": description}
        req = self.doRequestPut(url=reverse("api_update_my_set"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        objInDatabase = OaiMySet.objects.get(pk=set.id)
        self.assertEquals(objInDatabase.setSpec, setSpec)
        self.assertEquals(objInDatabase.setName, setName)
        self.assertEquals([str(x.id) for x in objInDatabase.templates], templates)
        self.assertEquals(objInDatabase.description, description)
#
    def test_update_my_set_not_found(self):
        self.dump_oai_settings()
        self.dump_oai_my_set()
        self.dump_template()
        setSpec = "modified setSpec"
        setName = "modified name"
        description = "modified description"
        templates = [str(x.id) for x in Template.objects.all().limit(3)]
        data = {"id": FAKE_ID, "setSpec": setSpec, "setName": setName, "templates": templates,
                "description": description}
        req = self.doRequestPut(url=reverse("api_update_my_set"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_my_set_invalid_serializer(self):
        self.dump_oai_settings()
        self.dump_template()
        setSpec = "modified setSpec"
        setName = "modified name"
        description = "modified description"
        templates = [str(x.id) for x in Template.objects.all().limit(3)]
        data = {"iid": FAKE_ID, "setSpec": setSpec, "setName": setName, "templates": templates,
                "description": description}
        req = self.doRequestPut(url=reverse("api_update_my_set"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"id": FAKE_ID, "ssetSpec": setSpec, "setName": setName, "templates": templates,
                "description": description}
        req = self.doRequestPut(url=reverse("api_update_my_set"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"id": FAKE_ID, "setSpec": setSpec, "ssetName": setName, "templates": templates,
                "description": description}
        req = self.doRequestPut(url=reverse("api_update_my_set"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_my_set_unauthorized(self):
        self.dump_oai_settings()
        self.dump_oai_my_set()
        self.dump_template()
        setSpec = "modified setSpec"
        setName = "modified name"
        description = "modified description"
        set = OaiMySet.objects.first()
        templates = [str(x.id) for x in Template.objects.all().limit(3)]
        data = {"id": str(set.id), "setSpec": setSpec, "setName": setName, "templates": templates,
                "description": description}
        req = self.doRequestPut(url=reverse("api_update_my_set"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)


################################################################################


############################ oai_pmh_xslt tests ################################

    def test_upload_oai_pmh_xslt(self):
        self.dump_oai_settings()
        name = "testXslt"
        fileName = "testXslt.xsd"
        content = TEMPLATE_VALID_CONTENT
        data = {"name": name, "filename": fileName, "content": content}
        req = self.doRequestPost(url=reverse("api_upload_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_201_CREATED)
        obj = OaiXslt.objects.get()
        self.assertEquals(obj.name, name)
        self.assertEquals(obj.filename, fileName)
        self.assertEquals(obj.content, content)

    @skip("Not working if launched with other tests")
    def test_upload_oai_pmh_xslt_not_unique(self):
        self.dump_oai_settings()
        name = "testXslt"
        fileName = "testXslt.xsd"
        content = TEMPLATE_VALID_CONTENT
        data = {"name": name, "filename": fileName, "content": content}
        req = self.doRequestPost(url=reverse("api_upload_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_201_CREATED)
        req = self.doRequestPost(url=reverse("api_upload_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_409_CONFLICT)

    def test_upload_oai_pmh_xslt_invalid_xml(self):
        self.dump_oai_settings()
        name = "testXslt"
        fileName = "testXslt.xsd"
        content = TEMPLATE_INVALID_CONTENT
        data = {"name": name, "filename": fileName, "content": content}
        req = self.doRequestPost(url=reverse("api_upload_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_oai_pmh_xslt_invalid_serializer(self):
        self.dump_oai_settings()
        self.dump_template()
        name = "testXslt"
        fileName = "testXslt.xsd"
        content = TEMPLATE_VALID_CONTENT
        data = {"nname": name, "filename": fileName, "content": content}
        req = self.doRequestPost(url=reverse("api_upload_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"name": name, "ffilename": fileName, "content": content}
        req = self.doRequestPost(url=reverse("api_upload_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"name": name, "filename": fileName, "ccontent": content}
        req = self.doRequestPost(url=reverse("api_upload_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_oai_pmh_xslt_unauthorized(self):
        self.dump_oai_settings()
        name = "testXslt"
        fileName = "testXslt.xsd"
        content = TEMPLATE_VALID_CONTENT
        data = {"name": name, "filename": fileName, "content": content}
        req = self.doRequestPost(url=reverse("api_upload_oai_pmh_xslt"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_delete_oai_pmh_xslt(self):
        self.dump_oai_settings()
        self.dump_oai_xslt()
        xslt = OaiXslt.objects.first()
        data = {"xslt_id": str(xslt.id)}
        req = self.doRequestPost(url=reverse("api_delete_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        with self.assertRaises(MONGO_ERRORS.DoesNotExist):
            OaiXslt.objects.get(pk=xslt.id)

    def test_delete_oai_pmh_xslt_not_found(self):
        self.dump_oai_settings()
        data = {"xslt_id": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_delete_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_oai_pmh_xslt_invalid_serializer(self):
        self.dump_oai_settings()
        data = {"xxslt_id": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_delete_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_oai_pmh_xslt_unauthorized(self):
        self.dump_oai_settings()
        data = {"xslt_id": FAKE_ID}
        req = self.doRequestPost(url=reverse("api_delete_oai_pmh_xslt"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_edit_oai_pmh_xslt(self):
        self.dump_oai_settings()
        self.dump_oai_xslt()
        xslt = OaiXslt.objects.first()
        name = "modified name"
        data = {"xslt_id": str(xslt.id), "name": name}
        req = self.doRequestPut(url=reverse("api_edit_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        objInDatabase = OaiXslt.objects.get(pk=xslt.id)
        self.assertEquals(objInDatabase.name, name)

    @skip("Not working if launched with other tests")
    def test_edit_oai_pmh_xslt_not_unique(self):
        self.dump_oai_settings()
        self.dump_oai_xslt()
        modifedName = "badName"
        OaiXslt(name="badName", filename='BadName.xsd', content='').save()
        xslt = OaiXslt.objects.first()
        data = {"xslt_id": str(xslt.id), "name": modifedName}
        req = self.doRequestPut(url=reverse("api_edit_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_409_CONFLICT)

    def test_edit_oai_pmh_xslt_not_found(self):
        self.dump_oai_settings()
        self.dump_oai_xslt()
        name = "modified name"
        data = {"xslt_id": FAKE_ID, "name": name}
        req = self.doRequestPut(url=reverse("api_edit_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_404_NOT_FOUND)

    def test_edit_oai_pmh_xslt_invalid_serializer(self):
        self.dump_oai_settings()
        self.dump_oai_xslt()
        xslt = OaiXslt.objects.first()
        name = "modified name"
        data = {"xxslt_id": str(xslt.id), "name": name}
        req = self.doRequestPut(url=reverse("api_edit_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"xslt_id": str(xslt.id), "nname": name}
        req = self.doRequestPut(url=reverse("api_edit_oai_pmh_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_oai_pmh_xslt_unauthorized(self):
        self.dump_oai_settings()
        self.dump_oai_xslt()
        xslt = OaiXslt.objects.first()
        name = "modified name"
        data = {"xslt_id": str(xslt.id), "name": name}
        req = self.doRequestPut(url=reverse("api_edit_oai_pmh_xslt"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)


################################################################################

############################# oai_pmh_conf tests ###############################

    def test_oai_pmh_conf_xslt(self):
        self.dump_oai_settings()
        self.dump_template()
        self.dump_oai_xslt()
        self.dump_oai_my_metadata_format()
        self.assertEqual(len(OaiTemplMfXslt.objects.all()), 0)
        template = Template.objects.first()
        myMetadataFormat = OaiMyMetadataFormat.objects.first()
        xslt = OaiXslt.objects.first()
        activated = True
        data = {"template_id": str(template.id), "my_metadata_format_id": str(myMetadataFormat.id),
                "xslt_id": xslt.id, "activated": str(activated)}
        req = self.doRequestPost(url=reverse("api_oai_pmh_conf_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_200_OK)
        objInDatabase = OaiTemplMfXslt.objects.get()
        self.assertEquals(objInDatabase.template, template)
        self.assertEquals(objInDatabase.myMetadataFormat, myMetadataFormat)
        self.assertEquals(objInDatabase.xslt, xslt)
        self.assertEquals(objInDatabase.activated, activated)


    def test_oai_pmh_conf_xslt_activated_but_no_xslt(self):
        self.dump_oai_settings()
        data = {"template_id": FAKE_ID, "my_metadata_format_id": FAKE_ID, "activated": "True"}
        req = self.doRequestPost(url=reverse("api_oai_pmh_conf_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_oai_pmh_conf_xslt_invalid_serializer(self):
        self.dump_oai_settings()
        data = {"ttemplate_id": FAKE_ID, "my_metadata_format_id": FAKE_ID, "activated": "False"}
        req = self.doRequestPost(url=reverse("api_oai_pmh_conf_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"template_id": FAKE_ID, "mmy_metadata_format_id": FAKE_ID, "activated": "False"}
        req = self.doRequestPost(url=reverse("api_oai_pmh_conf_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"template_id": FAKE_ID, "my_metadata_format_id": FAKE_ID, "aactivated": "False"}
        req = self.doRequestPost(url=reverse("api_oai_pmh_conf_xslt"), data=data, auth=ADMIN_AUTH)
        self.assertEquals(req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_oai_pmh_conf_xslt_unauthorized(self):
        self.dump_oai_settings()
        data = {"template_id": FAKE_ID, "my_metadata_format_id": FAKE_ID, "xslt_id": FAKE_ID, "activated": "True"}
        req = self.doRequestPost(url=reverse("api_oai_pmh_conf_xslt"), data=data, auth=USER_AUTH)
        self.assertEquals(req.status_code, status.HTTP_401_UNAUTHORIZED)

################################################################################

################################################################################
########################## Common assert controls ##############################
################################################################################

    def assert_OaiIdentify_Settings(self, retrievedIdentifyData):
        information = OaiSettings.objects.get()
        # self.assertEquals(retrievedIdentifyData['adminEmail'], (email for name, email in settings.OAI_ADMINS))
        self.assertEquals(retrievedIdentifyData['baseURL'], URL_TEST_SERVER)
        self.assertEquals(retrievedIdentifyData['repositoryName'], information.repositoryName)
        self.assertEquals(retrievedIdentifyData['deletedRecord'], settings.OAI_DELETED_RECORD)
        self.assertEquals(retrievedIdentifyData['granularity'], settings.OAI_GRANULARITY)
        self.assertEquals(retrievedIdentifyData['protocolVersion'], settings.OAI_PROTOCOLE_VERSION)
        self.assertEquals(retrievedIdentifyData['repositoryIdentifier'], information.repositoryIdentifier)
        self.assertEquals(retrievedIdentifyData['sampleIdentifier'], settings.OAI_SAMPLE_IDENTIFIER)
        self.assertEquals(retrievedIdentifyData['scheme'], settings.OAI_SCHEME)


    def assert_OaiIdentify(self, objIdentify, identifyData=None):
        if identifyData is not None:
            identifyData = identifyData
        else:
            identifyData = self.getIdentifyData()
        #objInDatabaseXmlTree = etree.XML(xmltodict.unparse(objIdentify.raw).encode('utf-8'))
        #objInDatabaseXmlString = etree.tostring(objInDatabaseXmlTree, xml_declaration=False)
        self.assertEquals(identifyData['adminEmail'], objIdentify.adminEmail)
        self.assertEquals(identifyData['baseURL'], objIdentify.baseURL)
        self.assertEquals(identifyData['repositoryName'], objIdentify.repositoryName)
        self.assertEquals(identifyData['deletedRecord'], objIdentify.deletedRecord)
        self.assertEquals(identifyData['description'], objIdentify.description)
        self.assertEquals(identifyData['earliestDatestamp'], objIdentify.earliestDatestamp)
        self.assertEquals(identifyData['granularity'], objIdentify.granularity)
        self.assertEquals(identifyData['oai_identifier'], objIdentify.oai_identifier)
        self.assertEquals(identifyData['protocolVersion'], objIdentify.protocolVersion)
        self.assertEquals(identifyData['repositoryIdentifier'], objIdentify.repositoryIdentifier)
        self.assertEquals(identifyData['sampleIdentifier'], objIdentify.sampleIdentifier)
        self.assertEquals(identifyData['scheme'], objIdentify.scheme)
        #TODO Keep the oriaginal XML order: OrderedDict
        # self.assertEquals(identifyData['raw'], objInDatabaseXmlString)

    def assert_OaiRegistry(self, registry, objIdentify):
        strUrl, harvest, harvestrate = self.getRegistryData()
        self.assertEquals(registry.identify, objIdentify)
        self.assertEquals(registry.name, objIdentify.repositoryName)
        self.assertEquals(registry.url, strUrl)
        self.assertEquals(registry.description, objIdentify.description)
        self.assertEquals(registry.harvest, harvest)
        self.assertEquals(registry.harvestrate, harvestrate)
        self.assertEquals(registry.isDeactivated, False)


    def assert_OaiMetadataFormat(self, retrievedMetadataformatsData):
        #Get metadata format in database
        metadataFormatsInDatabase = OaiMyMetadataFormat.objects.all()
        #Check with what we just retrieve
        for metadataFormat in metadataFormatsInDatabase:
            el = [x for x in retrievedMetadataformatsData if x['metadataPrefix'] == metadataFormat.metadataPrefix][0]
            self.assertNotEquals(el, None)
            self.assertEquals(el['metadataNamespace'], metadataFormat.metadataNamespace)
            self.assertEquals(el['schema'], metadataFormat.schema)
            # self.assertEquals(el['raw'], metadataFormat.raw)

    def assert_OaiMetadataFormat_Registry(self, metadataformatsData, registry):
        for metadataformat in metadataformatsData:
            objInDatabase = OaiMetadataFormat.objects.get(metadataPrefix=metadataformat['metadataPrefix'],
                                                          registry=str(registry.id))
            self.assertEquals(metadataformat['metadataPrefix'], objInDatabase.metadataPrefix)
            self.assertEquals(metadataformat['metadataNamespace'], objInDatabase.metadataNamespace)
            self.assertEquals(metadataformat['schema'], objInDatabase.schema)
            self.assertEquals(str(registry.id), objInDatabase.registry)
            self.assertEquals(True, objInDatabase.harvest)
            # self.assertEquals(metadataformat['raw'], objInDatabase.raw)

    def assert_OaiSet_Registry(self, setsData, registry):
        #Get metadata format in database
        setsInDatabase = OaiSet.objects(registry=str(registry.id)).all()
        for set in setsInDatabase:
            el = [x for x in setsData if x['setSpec'] == set.setSpec][0]
            self.assertNotEquals(el, None)
            self.assertEquals(el['setName'], set.setName)

    def assert_OaiSet(self, retrievedSetsData):
        #Get metadata format in database
        setsInDatabase = OaiMySet.objects.all()
        #Check with what we just retrieve
        for set in setsInDatabase:
            el = [x for x in retrievedSetsData if x['setSpec'] == set.setSpec][0]
            self.assertNotEquals(el, None)
            self.assertEquals(el['setName'], set.setName)
            # self.assertEquals(el['raw'], set.raw)

    def assert_OaiListRecords(self, metadataPrefix, data, setSpec=None, fromDate=None):
        myMetadataFormat = OaiMyMetadataFormat.objects().get(metadataPrefix=metadataPrefix)
        if myMetadataFormat.isTemplate:
            templates = [str(myMetadataFormat.template.id)]
        else:
            oaiTemlXslt =  OaiTemplMfXslt.objects(myMetadataFormat=myMetadataFormat.id,
                                                  activated=True).distinct(field='template')
            templates = [str(x.id) for x in oaiTemlXslt]
        if setSpec:
            mySetTemplates = OaiMySet.objects().get(setSpec=setSpec)
            templatesInSet = [str(x.id) for x in mySetTemplates.templates]
            templates = list(set.intersection(set(templates), set(templatesInSet)))
        query = dict()
        query['schema'] = { '$in': templates }
        query['ispublished'] = True
        if fromDate:
            startDate = datestamp.datestamp_to_datetime(fromDate)
            query['oai_datestamp'] = { "$gte" : startDate}
        #Get all records for this template
        dataInDatabase = XMLdata.executeQueryFullResult(query)
        self.assertEquals(len(dataInDatabase), len(data))
        for obj in data:
            self.assert_OaiRecord(metadataPrefix, obj)

    def assert_OaiRecord(self, metadataPrefix, data):
        identifier = data['identifier'].split('/')[1]
        objInDatabase = XMLdata.get(identifier)
        if 'oai_datestamp' in objInDatabase:
            date = str(datestamp.datetime_to_datestamp(objInDatabase['oai_datestamp']))
            self.assertEquals(date, data['datestamp'])
        self.assertEquals(objInDatabase['status'] == Status.DELETED, data['deleted'])
        sets = OaiMySet.objects(templates__in=[str(objInDatabase['schema'])]).all()
        if sets:
            setSpecs = [x.setSpec for x in sets]
            self.assertEquals(setSpecs, data['sets'])
        self.assertEquals(metadataPrefix, data['metadataPrefix'])
        self.assertNotEquals(data['metadata'], '')
        self.assertNotEquals(data['raw'], '')

    def assert_harvest_lastUpdate_not_none(self, metadataformatsToHarvest, registrySetsToHarvest):
        #lastUpdate modification
        for metadataformat in metadataformatsToHarvest:
            for set in registrySetsToHarvest:
                try:
                    obj = OaiMetadataformatSet.objects.get(metadataformat=metadataformat, set=set)
                    self.assertNotEquals(obj, None)
                except MONGO_ERRORS.DoesNotExist:
                    self.assertTrue(True)
            self.assertNotEquals(metadataformat.lastUpdate, None)

    def assert_harvest_lastUpdate_none(self, metadataformatsToHarvest, registrySetsToHarvest):
        #lastUpdate modification
        for metadataformat in metadataformatsToHarvest:
            for set in registrySetsToHarvest:
                try:
                    obj = OaiMetadataformatSet.objects.get(metadataformat=metadataformat, set=set)
                    self.assertTrue(False)
                except MONGO_ERRORS.DoesNotExist:
                    self.assertTrue(True)
            self.assertEquals(metadataformat.lastUpdate, None)

    def assert_OaiRecords_In_Database(self, metadataPrefix, lastUpdate=None, setSpec=None):
        myMetadataFormat = OaiMyMetadataFormat.objects().get(metadataPrefix=metadataPrefix)
        if myMetadataFormat.isTemplate:
            templates = [str(myMetadataFormat.template.id)]
        else:
            oaiTemlXslt =  OaiTemplMfXslt.objects(myMetadataFormat=myMetadataFormat.id,
                                                  activated=True).distinct(field='template')
            templates = [str(x.id) for x in oaiTemlXslt]
        if setSpec:
            mySet = OaiMySet.objects().get(setSpec=setSpec)
            templatesInSet = [str(x.id) for x in mySet.templates]
            templates = list(set.intersection(set(templates), set(templatesInSet)))
        query = dict()
        query['schema'] = { '$in': templates }
        query['ispublished'] = True
        if lastUpdate:
            startDate = datestamp.datestamp_to_datetime(lastUpdate)
            query['oai_datestamp'] = { "$gte" : startDate}
        #Get all records for this template
        dataInDatabase = XMLdata.executeQueryFullResult(query)
        for dataDB in dataInDatabase:
            identifier = '%s:%s:id/%s' % (settings.OAI_SCHEME, settings.OAI_REPO_IDENTIFIER, str(dataDB['_id']))
            records = OaiRecord.objects(identifier=identifier).all()
            for record in records:
                if 'oai_datestamp' in dataDB:
                    self.assertEquals(str(datestamp.datetime_to_datestamp(record.datestamp)),
                                      str(datestamp.datetime_to_datestamp(dataDB['oai_datestamp'])))
                self.assertEquals(record.deleted, dataDB['status'] == Status.DELETED)
                sets = OaiMySet.objects(templates__in=[str(dataDB['schema'])]).all().distinct('setSpec')
                if sets:
                    recordSets = [x.setSpec for x in record.sets]
                    self.assertEquals(recordSets, sets)
                # self.assertEquals(metadataPrefix, data['metadataPrefix'])
                self.assertNotEquals(record['metadata'], '')
                self.assertNotEquals(record['raw'], '')

    def assert_OaiListIdentifiers(self, metadataPrefix, data):
        myMetadataFormat = OaiMyMetadataFormat.objects().get(metadataPrefix=metadataPrefix)
        query = dict()
        query['schema'] = str(myMetadataFormat.template.id)
        query['ispublished'] = True
        #Get all records for this template
        dataInDatabase = XMLdata.executeQueryFullResult(query)
        self.assertEquals(len(dataInDatabase), len(data))
        for obj in data:
            identifier = obj['identifier'].split('/')[1]
            objInDatabase = next(x for x in dataInDatabase if x['_id'] == ObjectId(identifier))
            self.assertTrue(objInDatabase != None)
            if 'oai_datestamp' in objInDatabase:
                date = str(datestamp.datetime_to_datestamp(objInDatabase['oai_datestamp']))
                self.assertEquals(date, obj['datestamp'])
            sets = OaiMySet.objects(templates__in=[str(objInDatabase['schema'])]).all()
            if sets:
                setSpecs = [x.setSpec for x in sets]
                self.assertEquals(setSpecs, obj['setSpecs'])

################################################################################
################################################################################
################################################################################

################################################################################
############################# Common methods ###################################
################################################################################

    def setHarvest(self, value):
        information = OaiSettings.objects.get()
        information.enableHarvesting = value
        information.save()

    def getIdentifyData(self):
        identifyData = {"adminEmail": "test@oai-pmh.us",
              "baseURL": "http://127.0.0.1:8000/oai_pmh/server/",
              "repositoryName": "X Repository",
              "deletedRecord": "no",
              "delimiter": ":",
              "description": "One OAI-PMH server",
              "earliestDatestamp": '1989-12-31T15:23:00Z',
              "granularity": 'YYYY-MM-DDThh:mm:ssZ',
              "oai_identifier": 'oai-identifier',
              "protocolVersion": '2.0',
              "repositoryIdentifier": 'server-127.0.0.1',
              "sampleIdentifier": "oai:server-127.0.0.1:id/12345678a123aff6ff5f2d9e",
              "scheme": 'oai',
              "raw": '<Identify xmlns="http://www.openarchives.org/OAI/2.0/" '
                     'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                     '<repositoryName>X Repository</repositoryName>'
                     '<baseURL>http://127.0.0.1:8000/oai_pmh/server/</baseURL>'
                     '<protocolVersion>2.0</protocolVersion>'
                     '<adminEmail>test@oai-pmh.us</adminEmail>'
                     '<earliestDatestamp>1989-12-31T15:23:00Z</earliestDatestamp>'
                     '<deletedRecord>no</deletedRecord>'
                     '<granularity>YYYY-MM-DDThh:mm:ssZ</granularity>'
                     '<description><oai-identifier xmlns="http://www.openarchives.org/OAI/2.0/oai-identifier" '
                     'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                     'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai-identifier '
                     'http://www.openarchives.org/OAI/2.0/oai-identifier.xsd"><scheme>oai</scheme>'
                     '<repositoryIdentifier>server-127.0.0.1</repositoryIdentifier><delimiter>:</delimiter>'
                     '<sampleIdentifier>oai:server-127.0.0.1:id/12345678a123aff6ff5f2d9e</sampleIdentifier>'
                     '</oai-identifier></description>'
                     '</Identify>'
        }
        return identifyData


    def getModifiedIdentifyData(self):
        identifyData = {"adminEmail": "test10@oai-pmh.us",
              "baseURL": "http://127.0.0.1:8888/oai_pmh/server/",
              "repositoryName": "Y Repository",
              "deletedRecord": "yes",
              "delimiter": "/",
              "description": "One OAI-PMH server modified",
              "earliestDatestamp": '1991-03-16T08:23Z',
              "granularity": 'YY-MM-DDThh:mmZ',
              "oai_identifier": 'oai-identifier-modified',
              "protocolVersion": '22.0',
              "repositoryIdentifier": 'server-127.0.0.1-modified',
              "sampleIdentifier": "oai:server-127.0.0.1-modified:id/12345678a123aff6ff5f2d9e",
              "scheme": 'oaii',
              "raw": '<Identify xmlns="http://www.openarchives.org/OAI/2.0/" '
                     'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                     '<repositoryName>Y Repository</repositoryName>'
                     '<baseURL>http://127.0.0.1:88888/oai_pmh/server/</baseURL>'
                     '<protocolVersion>22.0</protocolVersion>'
                     '<adminEmail>test10@oai-pmh.us</adminEmail>'
                     '<earliestDatestamp>1991-03-16T15:23Z</earliestDatestamp>'
                     '<deletedRecord>yes</deletedRecord>'
                     '<granularity>YYYY-MM-DDThh:mmZ</granularity>'
                     '<description><oai-identifier xmlns="http://www.openarchives.org/OAI/2.0/oai-identifier" '
                     'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                     'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai-identifier '
                     'http://www.openarchives.org/OAI/2.0/oai-identifier.xsd"><scheme>oaii</scheme>'
                     '<repositoryIdentifier>server-127.0.0.1-modified</repositoryIdentifier><delimiter>/</delimiter>'
                     '<sampleIdentifier>oai:server-127.0.0.1-modified:id/12345678a123aff6ff5f2d9e</sampleIdentifier>'
                     '</oai-identifier></description>'
                     '</Identify>'
        }
        return identifyData


    def getMetadataFormatData(self):
        metadataFormatData = [{'metadataPrefix': 'oai_dc',
                               'metadataNamespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                               'schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc/</metadataNamespace>'
                                      '<metadataPrefix>oai_dc</metadataPrefix>'
                                      '<schema>http://www.openarchives.org/OAI/2.0/oai_dc.xsd</schema></metadataFormat>'},
                              {'metadataPrefix': 'oai_all',
                               'metadataNamespace': 'http://www.w3.org/2001/XMLSchema',
                               'schema': 'http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.w3.org/2001/XMLSchema</metadataNamespace>'
                                      '<metadataPrefix>oai_all</metadataPrefix>'
                                      '<schema>http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd</schema></metadataFormat>'},
                              {'metadataPrefix': 'oai_soft',
                               'metadataNamespace': 'http://www.w3.org/2001/XMLSchema',
                               'schema': 'http://127.0.0.1:8082/oai_pmh/server/XSD/Software.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.w3.org/2001/XMLSchema</metadataNamespace>'
                                      '<metadataPrefix>oai_soft</metadataPrefix>'
                                      '<schema>http://127.0.0.1:8082/oai_pmh/server/XSD/Software.xsd</schema></metadataFormat>'}
                            ]
        return metadataFormatData


    def getModifiedMetadataFormatData(self):
        metadataFormatData = [{'metadataPrefix': 'oai_all',
                               'metadataNamespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                               'schema': 'http://127.0.0.1:8082/oai_pmh/server/XSD/Software.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc/</metadataNamespace>'
                                      '<metadataPrefix>oai_dc</metadataPrefix>'
                                      '<schema>http://www.openarchives.org/OAI/2.0/oai_dc.xsd</schema></metadataFormat>'},
                              {'metadataPrefix': 'oai_soft',
                               'metadataNamespace': 'http://www.w3.org/2001/XMLSchema',
                               'schema': 'http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.w3.org/2001/XMLSchema</metadataNamespace>'
                                      '<metadataPrefix>oai_all</metadataPrefix>'
                                      '<schema>http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd</schema></metadataFormat>'},
                              {'metadataPrefix': 'oai_dc',
                               'metadataNamespace': 'http://www.w3.org/2001/XMLSchema',
                               'schema': 'http://127.0.0.1:8082/oai_pmh/server/XSD/Software.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.w3.org/2001/XMLSchema</metadataNamespace>'
                                      '<metadataPrefix>oai_soft</metadataPrefix>'
                                      '<schema>http://127.0.0.1:8082/oai_pmh/server/XSD/Software.xsd</schema></metadataFormat>'}
                            ]
        return metadataFormatData


    def getNewMetadataFormatData(self):
        metadataFormatData = [{'metadataPrefix': 'oai_dc',
                               'metadataNamespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                               'schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc/</metadataNamespace>'
                                      '<metadataPrefix>oai_dc</metadataPrefix>'
                                      '<schema>http://www.openarchives.org/OAI/2.0/oai_dc.xsd</schema></metadataFormat>'},
                              {'metadataPrefix': 'oai_all',
                               'metadataNamespace': 'http://www.w3.org/2001/XMLSchema',
                               'schema': 'http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.w3.org/2001/XMLSchema</metadataNamespace>'
                                      '<metadataPrefix>oai_all</metadataPrefix>'
                                      '<schema>http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd</schema></metadataFormat>'},
                              {'metadataPrefix': 'oai_soft',
                               'metadataNamespace': 'http://www.w3.org/2001/XMLSchema',
                               'schema': 'http://127.0.0.1:8082/oai_pmh/server/XSD/Software.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.w3.org/2001/XMLSchema</metadataNamespace>'
                                      '<metadataPrefix>oai_soft</metadataPrefix>'
                                      '<schema>http://127.0.0.1:8082/oai_pmh/server/XSD/Software.xsd</schema></metadataFormat>'},
                              {'metadataPrefix': 'oai_dataset',
                               'metadataNamespace': 'http://www.w3.org/2001/XMLSchema',
                               'schema': 'http://127.0.0.1:8082/oai_pmh/server/XSD/Dataset.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.w3.org/2001/XMLSchema</metadataNamespace>'
                                      '<metadataPrefix>oai_dataset</metadataPrefix>'
                                      '<schema>http://127.0.0.1:8082/oai_pmh/server/XSD/Dataset.xsd</schema></metadataFormat>'}
                            ]
        return metadataFormatData

    def getBadNewMetadataFormatData(self):
        metadataFormatData = [{'metadataPrefix': 'oai_dc',
                               'metadataNamespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                               'schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc/</metadataNamespace>'
                                      '<metadataPrefix>oai_dc</metadataPrefix>'
                                      '<schema>http://www.openarchives.org/OAI/2.0/oai_dc.xsd</schema></metadataFormat>'},
                              {'metadataPrefix': 'oai_all',
                               'metadataNamespace': 'http://www.w3.org/2001/XMLSchema',
                               'schema': 'http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.w3.org/2001/XMLSchema</metadataNamespace>'
                                      '<metadataPrefix>oai_all</metadataPrefix>'
                                      '<schema>http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd</schema></metadataFormat>'},
                              {'metadataPrefix': 'oai_soft',
                               'metadataNamespace': 'http://www.w3.org/2001/XMLSchema',
                               'schema': 'http://127.0.0.1:8082/oai_pmh/server/XSD/Software.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.w3.org/2001/XMLSchema</metadataNamespace>'
                                      '<metadataPrefix>oai_soft</metadataPrefix>'
                                      '<schema>http://127.0.0.1:8082/oai_pmh/server/XSD/Software.xsd</schema></metadataFormat>'},
                              {'metadataPrefix': 'oai_dataset',
                               'metadataNamespace': 'http://www.w3.org/2001/XMLSchema',
                               'schema': 'http://127.0.0.1:80000088/oai_pmh/server/XSD/Dataset.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.w3.org/2001/XMLSchema</metadataNamespace>'
                                      '<metadataPrefix>oai_dataset</metadataPrefix>'
                                      '<schema>http://127.0.0.1:8082/oai_pmh/server/XSD/Dataset.xsd</schema></metadataFormat>'}
                            ]
        return metadataFormatData


    def getSetData(self):
        setData = [{'setName': 'all', 'setSpec': 'all',
                    'raw': '<set xmlns="http://www.openarchives.org/OAI/2.0/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                           '<setSpec>all</setSpec>'
                           '<setName>all</setName>'
                           '<setDescription><oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
                           'xmlns:dc="http://purl.org/dc/elements/1.1/"'
                           ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                           'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/            '
                           ' http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
                           '<dc:description xml:lang="en">'
                           '\n                    Get all records\n                </dc:description>'
                           '</oai_dc:dc></setDescription></set>'},
                   {'setName': 'software', 'setSpec': 'soft',
                    'raw': '<set xmlns="http://www.openarchives.org/OAI/2.0/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                           '<setSpec>soft</setSpec>'
                           '<setName>software</setName>'
                           '<setDescription><oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
                           'xmlns:dc="http://purl.org/dc/elements/1.1/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                           'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/             '
                           'http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
                           '<dc:description xml:lang="en">\n                    Get software records\n                '
                           '</dc:description></oai_dc:dc></setDescription></set>'}
                   ]
        return setData

    def getModifiedSetData(self):
        setData = [{'setName': 'alll', 'setSpec': 'all',
                    'raw': '<set xmlns="http://www.openarchives.org/OAI/2.0/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                           '<setSpec>all</setSpec>'
                           '<setName>alll</setName>'
                           '<setDescription><oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
                           'xmlns:dc="http://purl.org/dc/elements/1.1/"'
                           ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                           'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/            '
                           ' http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
                           '<dc:description xml:lang="en">'
                           '\n                    Get all recordssss\n                </dc:description>'
                           '</oai_dc:dc></setDescription></set>'},
                   {'setName': 'softwaree', 'setSpec': 'soft',
                    'raw': '<set xmlns="http://www.openarchives.org/OAI/2.0/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                           '<setSpec>soft</setSpec>'
                           '<setName>softwaree</setName>'
                           '<setDescription><oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
                           'xmlns:dc="http://purl.org/dc/elements/1.1/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                           'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/             '
                           'http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
                           '<dc:description xml:lang="en">\n                    Get software recordsssss\n                '
                           '</dc:description></oai_dc:dc></setDescription></set>'}
                   ]
        return setData

    def getNewSetData(self):
        setData = [{'setName': 'all', 'setSpec': 'all',
                    'raw': '<set xmlns="http://www.openarchives.org/OAI/2.0/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                           '<setSpec>all</setSpec>'
                           '<setName>all</setName>'
                           '<setDescription><oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
                           'xmlns:dc="http://purl.org/dc/elements/1.1/"'
                           ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                           'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/            '
                           ' http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
                           '<dc:description xml:lang="en">'
                           '\n                    Get all records\n                </dc:description>'
                           '</oai_dc:dc></setDescription></set>'},
                   {'setName': 'software', 'setSpec': 'soft',
                    'raw': '<set xmlns="http://www.openarchives.org/OAI/2.0/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                           '<setSpec>soft</setSpec>'
                           '<setName>software</setName>'
                           '<setDescription><oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
                           'xmlns:dc="http://purl.org/dc/elements/1.1/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                           'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/             '
                           'http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
                           '<dc:description xml:lang="en">\n                    Get software records\n                '
                           '</dc:description></oai_dc:dc></setDescription></set>'},
                   {'setName': 'toto', 'setSpec': 'to',
                    'raw': '<set xmlns="http://www.openarchives.org/OAI/2.0/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                           '<setSpec>to</setSpec>'
                           '<setName>toto</setName>'
                           '<setDescription><oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
                           'xmlns:dc="http://purl.org/dc/elements/1.1/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                           'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/             '
                           'http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
                           '<dc:description xml:lang="en">\n                    Get software records new\n                '
                           '</dc:description></oai_dc:dc></setDescription></set>'}
                   ]
        return setData

    def getBadNewSetData(self):
        setData = [{'setName': 'all', 'setSpec': 'all',
                    'raw': '<set xmlns="http://www.openarchives.org/OAI/2.0/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                           '<setSpec>all</setSpec>'
                           '<setName>all</setName>'
                           '<setDescription><oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
                           'xmlns:dc="http://purl.org/dc/elements/1.1/"'
                           ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                           'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/            '
                           ' http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
                           '<dc:description xml:lang="en">'
                           '\n                    Get all records\n                </dc:description>'
                           '</oai_dc:dc></setDescription></set>'},
                   {'setName': 'software', 'setSpec': 'soft',
                    'raw': '<set xmlns="http://www.openarchives.org/OAI/2.0/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                           '<setSpec>soft</setSpec>'
                           '<setName>software</setName>'
                           '<setDescription><oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
                           'xmlns:dc="http://purl.org/dc/elements/1.1/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                           'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/             '
                           'http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
                           '<dc:description xml:lang="en">\n                    Get software records\n                '
                           '</dc:description></oai_dc:dc></setDescription></set>'},
                   {'setName': 'toto', 'setSpec': 'to',
                    'raw': '<set xmlns="http://www.openarchives.org/OAI/2.0/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                           '<setSpec>to</setSpec>'
                           '<setName>toto</setName>'
                           '<setDescription><oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
                           'xmlns:dc="http://purl.org/dc/elements/1.1/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                           'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/             '
                           'http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
                           '<dc:description xml:lang="en">\n                    Get software records new\n                '
                           '</dc:description></oai_dc:dc></setDescription>set>'}
                   ]
        return setData

    def getSetDataBadRaw(self):
        setData = [{'setName': 'software', 'setSpec': 'soft',
                    'raw': '<set xmlns="http://www.openarchives.org/OAI/2.0/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                           '<setSpec>soft</setSpec>'
                           '<setName>software</setName>'
                           '<setDescription><oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
                           'xmlns:dc="http://purl.org/dc/elements/1.1/" '
                           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                           'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/             '
                           'http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
                           '<dc:description xml:lang="en">\n                    Get software records\n                '
                           '</dc:description></oai_dc:dc></setDescription>/set>'}
                   ]
        return setData


    def getMetadataFormatDataAllResources(self):
        metadataFormatData = {'metadataPrefix': 'oai_all',
                               'metadataNamespace': 'http://www.w3.org/2001/XMLSchema',
                               'schema': 'http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.w3.org/2001/XMLSchema</metadataNamespace>'
                                      '<metadataPrefix>oai_all</metadataPrefix>'
                                      '<schema>http://127.0.0.1:8082/oai_pmh/server/XSD/AllResources.xsd</schema></metadataFormat>'}

        return metadataFormatData

    def getMetadataFormatDataBadRaw(self):
        metadataFormatData = [{'metadataPrefix': 'oai_dc',
                               'metadataNamespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                               'schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                               'raw': '<metadataFormat xmlns="http://www.openarchives.org/OAI/2.0/" '
                                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                      '<metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc/</metadataNamespace>'
                                      '<metadataPrefix>oai_dc</metadataPrefix>'
                                      '<schema>http://www.openarchives.org/OAI/2.0/oai_dc.xsd</schema>/metadataFormat>'}
                            ]
        return metadataFormatData


    def addNewSoftwareXmlData(self):
        template = Template.objects.get(filename="Software.xsd")
        xml = "<Resource localid='' status='active'><identity>" \
               "<title>My new software</title></identity><curation><publisher>PF</publisher><contact><name></name>" \
               "</contact></curation><content><description>This is a new record</description><subject></subject>" \
               "<referenceURL></referenceURL></content></Resource>"
        schemaId = str(template.id)
        now = datetime.datetime.now()
        data = XMLdata(schemaID=schemaId, xml=xml, title='newRecord', iduser=1, ispublished=True,
                publicationdate=now, oai_datestamp=now).save()

    def addNewSoftwareXmlDataDeleted(self):
        template = Template.objects.get(filename="Software.xsd")
        xml = "<Resource localid='' status='deleted'><identity>" \
               "<title>My new software</title></identity><curation><publisher>PF</publisher><contact><name></name>" \
               "</contact></curation><content><description>This is a new record</description><subject></subject>" \
               "<referenceURL></referenceURL></content></Resource>"
        schemaId = str(template.id)
        now = datetime.datetime.now()
        data = XMLdata(schemaID=schemaId, xml=xml, title='newRecord', iduser=1, ispublished=True,
                publicationdate=now, oai_datestamp=now).save()

    def addNewSoftwareXmlDataInactive(self):
        template = Template.objects.get(filename="Software.xsd")
        xml = "<Resource localid='' status='inactive'><identity>" \
               "<title>My new software</title></identity><curation><publisher>PF</publisher><contact><name></name>" \
               "</contact></curation><content><description>This is a new record</description><subject></subject>" \
               "<referenceURL></referenceURL></content></Resource>"
        schemaId = str(template.id)
        now = datetime.datetime.now()
        data = XMLdata(schemaID=schemaId, xml=xml, title='newRecord', iduser=1, ispublished=True,
                publicationdate=now, oai_datestamp=now).save()

    def addNewDataCollectionXmlData(self):
        template = Template.objects.get(filename="DataCollection.xsd")
        xml = "<Resource localid='' status='active'><identity>" \
               "<title>My new software</title></identity><curation><publisher>PF</publisher><contact><name></name>" \
               "</contact></curation><content><description>This is a data collection</description><subject></subject>" \
               "<referenceURL></referenceURL></content></Resource>"
        schemaId = str(template.id)
        now = datetime.datetime.now()
        data = XMLdata(schemaID=schemaId, xml=xml, title='newDataCollection', iduser=1, ispublished=True,
                publicationdate=now, oai_datestamp=now).save()


    def getRegistryData(self):
        strUrl = "http://127.0.0.1:8000/oai_pmh/server/"
        harvest = True
        harvestrate = 200
        return strUrl, harvest, harvestrate

    def call_createOaiIdentify(self):
        identifyData = self.getIdentifyData()
        identifyRaw = xmltodict.parse(identifyData['raw'])
        objIdentify = createOaiIdentify(identifyData, identifyRaw)
        return objIdentify

    def call_createRegistry(self):
        strUrl, harvest, harvestrate = self.getRegistryData()
        identifyData = self.getIdentifyData()
        identify, registry = createRegistry(harvest=harvest, harvestrate=harvestrate, identifyData=identifyData,
                                            url=strUrl)
        return identify, registry


    def createFakeRegistry(self):
        registry = OaiRegistry()
        registry.name = "Fake registry"
        registry.isDeactivated = False
        registry.url = "http://fakeserver.com"
        registry.save()
        return registry

################################################################################
################################################################################
################################################################################
