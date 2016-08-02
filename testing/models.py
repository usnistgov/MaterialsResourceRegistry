################################################################################
#
# File Name: models.py
# Application: testing
# Purpose:
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from django.test import LiveServerTestCase
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import requests
from datetime import datetime, timedelta
from mgi.models import Instance, XMLdata, Template, TemplateVersion, ResultXslt, OaiMyMetadataFormat, OaiMySet, OaiSettings,Type, TypeVersion, FormData
from utils.XSDhash import XSDhash
from django.contrib.auth.models import User
from oauth2_provider.models import Application
from admin_mdcs import discover
import os
from django.utils.importlib import import_module
from bson import decode_all
from os.path import join
from django.test import Client
import base64
import json
from lxml import etree
from django.test import TestCase

settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
MONGODB_URI = settings.MONGODB_URI
MGI_DB = settings.MGI_DB
BASE_DIR = settings.BASE_DIR
OAI_SCHEME = settings.OAI_SCHEME
OAI_REPO_IDENTIFIER = settings.OAI_REPO_IDENTIFIER

URL_TEST = "http://127.0.0.1:8082"
OPERATION_GET = "get"
OPERATION_POST = "post"
OPERATION_DELETE = "delete"
OPERATION_POST = "post"

TEMPLATE_VALID_CONTENT = '<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:mgi="urn:nist.gov/nmrr.res/1.0wd" targetNamespace="urn:nist.gov/nmrr.res/1.0wd"> <xsd:element name="root" type="mgi:test"/> <xsd:complexType name="test"> <xsd:sequence> </xsd:sequence> </xsd:complexType> </xsd:schema>'
TEMPLATE_INVALID_CONTENT = 'd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"> :element name="root" type="test"/> <xsd:complexType name="test"> <xsd:sequence> </xsd:sequence> </xsd:complexType> </xsd:schema>'
XMLDATA_VALID_CONTENT  = '<?xml version="1.0" encoding="utf-8"?><root xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:nist.gov/nmrr.res/1.0wd"/>'
FAKE_ID = '12345678a123aff6ff5f2d9e'

DUMP_OAI_PMH_TEST_PATH = os.path.join(BASE_DIR, 'oai_pmh', 'tests', 'dump')
DUMP_TEST_PATH = os.path.join(BASE_DIR, 'testing', 'dump')

# Constante for application token
CLIENT_ID_ADMIN = 'client_id'
CLIENT_SECRET_ADMIN = 'client_secret'
CLIENT_ID_USER = 'client_id_user'
CLIENT_SECRET_USER = 'client_secret_user'
USER_APPLICATION = 'remote_mdcs'
ADMIN_APPLICATION = 'remote_mdcs'
ADMIN_AUTH = 'admin:admin'
USER_AUTH = 'user:user'
ADMIN_AUTH_GET = ('admin', 'admin')

XMLParser = etree.XMLParser(remove_blank_text=True, recover=True)


class RegressionTest(LiveServerTestCase, TestCase):

    def setUp(self):
        self.clean_db()

        discover.init_rules()

        user, userCreated = User.objects.get_or_create(username='user')
        if userCreated:
            user.set_password('user')
            user.save()

        admin, adminCreated = User.objects.get_or_create(username='admin', is_staff=1, is_superuser=1)
        if adminCreated:
            admin.set_password('admin')
            admin.save()

    def getUser(self):
        return User.objects.get_by_natural_key(username='user')

    def getAdmin(self):
        return User.objects.get_by_natural_key(username='admin')

    def getClient(self, auth=None):
        client = Client()
        if auth is not None:
            credentials = base64.b64encode(auth)
            client.defaults['HTTP_AUTHORIZATION'] = 'Basic ' + credentials
        return client

    def doRequestPostAdminClientLogged(self, url, data=None, params=None):
        client = self.getClient('admin:admin')
        client.login(username='admin', password='admin')
        return client.post(URL_TEST + url, data=data, params=params)

    def doRequestGetAdminClientLogged(self, url, data=None, params=None):
        self.client = self.getClient('admin:admin')
        self.client.login(username='admin', password='admin')
        return self.client.get(URL_TEST + url, data=data, params=params)

    def doRequestGetUserClientLogged(self, url, data=None, params=None):
        self.client = self.getClient('user:user')
        self.client.login(username='user', password='user')
        return self.client.get(URL_TEST + url, data=data, params=params)

    def doRequestPostUserClientLogged(self, url, data=None, params=None):
        self.client = self.getClient('user:user')
        self.client.login(username='user', password='user')
        return self.client.post(URL_TEST + url, data=data, params=params)

    def doRequestGet(self, url, data=None, params=None, auth=None):
        return requests.get(URL_TEST + url, data=data, params=params, auth=auth)

    def doRequestPost(self, url, data=None, params=None, auth=None):
        client = self.getClient(auth)
        return client.post(URL_TEST + url, data=data, params=params)

    def doRequestPut(self, url, data=None, params=None, auth=None, content_type='application/json'):
        client = self.getClient(auth)
        return client.put(URL_TEST + url, data=json.dumps(data), params=params, content_type=content_type)

    def dump_result_xslt(self):
        self.assertEquals(len(ResultXslt.objects()), 0)
        self.restoreDump(join(DUMP_TEST_PATH, 'result_xslt.bson'), 'result_xslt')
        self.assertTrue(len(ResultXslt.objects()) > 0)

    def dump_template_version(self):
        self.assertEquals(len(TemplateVersion.objects()), 0)
        self.restoreDump(join(DUMP_TEST_PATH, 'template_version.bson'), 'template_version')
        self.assertTrue(len(TemplateVersion.objects()) > 0)

    def dump_template(self):
        self.assertEquals(len(Template.objects()), 0)
        self.dump_template_version()
        self.restoreDump(join(DUMP_TEST_PATH, 'template.bson'), 'template')
        self.assertTrue(len(Template.objects()) > 0)

    def dump_xmldata(self):
        self.assertEquals(len(XMLdata.objects()), 0)
        self.dump_template()
        self.restoreDump(join(DUMP_TEST_PATH, 'xmldata.bson'), 'xmldata')
        self.assertTrue(len(XMLdata.objects()) > 0)

    def restoreDump(self, file, collectionName):
        client = MongoClient(MONGODB_URI)
        db = client[MGI_DB]
        target_collection = db[collectionName]
        re = open(file, 'rb').read()
        target_collection.insert(decode_all(re))

    def createFormData(self, user='', template='', name='', xml_data=None, xml_data_id=None):
        countFormData = len(FormData.objects())
        formData = FormData(user=str(user), template=template, name=name, xml_data=xml_data, xml_data_id=xml_data_id).save()
        self.assertEquals(len(FormData.objects()), countFormData + 1)
        return formData

    def createXMLData(self, schemaID='', ispublished=False, iduser='1'):
        return XMLdata(schemaID=str(schemaID), xml='<test>test xmldata</test>', title='test', iduser=str(iduser), ispublished=ispublished).save()

    def createType(self, title='test', filename='test', user=None):
        countType = len(Type.objects())
        hash = XSDhash.get_hash('<test>test xmldata</test>')
        objectVersions = self.createTypeVersion()
        type = Type(title=title, filename=filename, content='<test>test xmldata</test>', version=1, typeVersion=str(objectVersions.id), hash=hash, user=str(user)).save()
        self.assertEquals(len(Type.objects()), countType + 1)
        return type

    def createTemplate(self, title='test', filename='test', user=None):
        countTemplate = len(Template.objects())
        hash = XSDhash.get_hash('<test>test xmldata</test>')
        objectVersions = self.createTemplateVersion()
        template = Template(title=title, filename=filename, content='<test>test xmldata</test>', version=1, templateVersion=str(objectVersions.id), hash=hash, user=str(user)).save()
        self.assertEquals(len(Template.objects()), countTemplate + 1)
        return template

    def createTemplateWithTemplateVersion(self, templateVersionId):
        hash = XSDhash.get_hash('<test>test xmldata</test>')
        return Template(title='test', filename='test', content='<test>test xmldata</test>', version=1, templateVersion=templateVersionId, hash=hash).save()

    def createTemplateWithTemplateVersionValidContent(self, templateVersionId):
        hash = XSDhash.get_hash(TEMPLATE_VALID_CONTENT)
        template = Template(title='test', filename='test', content=TEMPLATE_VALID_CONTENT, version=1, templateVersion=templateVersionId, hash=hash).save()
        TemplateVersion.objects.get(pk=templateVersionId).update(set__current=template.id)
        return template

    def createTemplateWithTemplateVersionInvalidContent(self, templateVersionId):
        hash = XSDhash.get_hash(TEMPLATE_VALID_CONTENT)
        template = Template(title='test', filename='test', content=TEMPLATE_INVALID_CONTENT, version=1, templateVersion=templateVersionId, hash=hash).save()
        TemplateVersion.objects.get(pk=templateVersionId).update(set__current=template.id)
        return template

    def createTemplateVersion(self):
        countTemplateVersion = len(TemplateVersion.objects())
        templateVersion = TemplateVersion(nbVersions=1, isDeleted=False, current=FAKE_ID).save()
        self.assertEquals(len(TemplateVersion.objects()), countTemplateVersion + 1)
        return templateVersion

    def createTypeVersion(self):
        countTypeVersion = len(TypeVersion.objects())
        typeVersion = TypeVersion(nbVersions=1, isDeleted=False, current=FAKE_ID).save()
        self.assertEquals(len(TypeVersion.objects()), countTypeVersion + 1)
        return typeVersion

    def createTemplateVersionDeleted(self):
        return TemplateVersion(nbVersions=1, isDeleted=True).save()

    def checkTagErrorCode(self, text, error):
        self.checkTagExist(text, 'error')
        for tag in etree.XML(text.encode("utf8"), parser=XMLParser).iterfind('.//' + '{http://www.openarchives.org/OAI/2.0/}' + 'error'):
            self.assertEqual(tag.attrib['code'], error)

    def checkTagExist(self, text, checkTag):
        tagFound = False
        for tag in etree.XML(text.encode("utf8"), parser=XMLParser).iterfind('.//' + '{http://www.openarchives.org/OAI/2.0/}' + checkTag):
                tagFound = True
        self.assertTrue(tagFound)

    def checkTagWithParamExist(self, text, checkTag, checkParam):
        tagFound = False
        for tag in etree.XML(text.encode("utf8"), parser=XMLParser).iterfind('.//' + '{http://www.openarchives.org/OAI/2.0/}' + checkTag + '[@' + checkParam + ']'):
            tagFound = True
        self.assertTrue(tagFound)

    def checkTagCount(self, text, checkTag, number):
        count = 0
        for tag in etree.XML(text.encode("utf8"), parser=XMLParser).iterfind('.//' + '{http://www.openarchives.org/OAI/2.0/}' + checkTag):
            count+=1
        self.assertEquals(number, count)

    def tearDown(self):
        self.clean_db()

    def clean_db(self):
        # create a connection
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi.test'
        db = client[MGI_DB]
        # clear all collections
        for collection in db.collection_names():
            try:
                if collection != 'system.indexes':
                    db.drop_collection(collection)
            except OperationFailure:
                pass

    def isStatusOK(self, code):
        self.assertEqual(code, 200)

    def isStatusNotFound(self, code):
        self.assertEqual(code, 404)

    def isStatusBadRequest(self, code):
        self.assertEqual(code, 400)

    def isStatusUnauthorized(self, code):
        self.assertEqual(code, 401)

    def isStatusNoContent(self, code):
        self.assertEqual(code, 204)

    def isStatusCreated(self, code):
        self.assertEqual(code, 201)

    def isStatusInternalError(self, code):
        self.assertEqual(code, 500)

class TokenTest(RegressionTest):

    def setUp(self):
        super(TokenTest, self).setUp()
        self.createApplication(User.objects.get(username='user'), USER_APPLICATION, CLIENT_ID_USER, CLIENT_SECRET_USER)
        self.createApplication(User.objects.get(username='admin'), ADMIN_APPLICATION, CLIENT_ID_ADMIN, CLIENT_SECRET_ADMIN)

    def createApplication(self, user, name, id, secret):
        application = Application()
        application.user = user
        application.client_type = 'confidential'
        application.authorization_grant_type = 'password'
        application.name = name
        application.client_id = id
        application.client_secret = secret
        application.save()

    def get_token(self, username, password, client_id, client_secret, application):
        try:
            url = URL_TEST + "/o/token/"
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            data = {
                'grant_type': 'password',
                'username': username,
                'password': password,
                'client_id': client_id,
                'client_secret': client_secret
            }
            r = requests.post(url=url, data=data, headers=headers, timeout=int(310000))
            if r.status_code == 200:
                now = datetime.now()
                delta = timedelta(seconds=int(json.loads(r.content)["expires_in"]))
                expires = now + delta

                token = Instance(name=application, protocol='http', address='127.0.0.1', port='8082',
                                 access_token=json.loads(r.content)["access_token"],
                                 refresh_token=json.loads(r.content)["refresh_token"], expires=expires).save()
                return token
            else:
                return ''
        except Exception, e:
            return ''

    def get_token_admin(self):
        return self.get_token('admin', 'admin', CLIENT_ID_ADMIN, CLIENT_SECRET_ADMIN, ADMIN_APPLICATION)

    def get_token_user(self):
        return self.get_token('user', 'user', CLIENT_ID_USER, CLIENT_SECRET_USER, USER_APPLICATION)

    def doRequestGet(self, token, url, data=None, params=None):
        if token == '':
            self.assertTrue(False)
        headers = {'Authorization': 'Bearer ' + token.access_token}
        return requests.get(URL_TEST + url, data=data, params=params, headers=headers)

    def doRequestPost(self, token, url, data=None, params=None):
        if token == '':
            self.assertTrue(False)
        headers = {'Authorization': 'Bearer ' + token.access_token}
        return requests.post(URL_TEST + url, data=data, params=params, headers=headers)

    def doRequestDelete(self, token, url, data=None, params=None):
        if token == '':
            self.assertTrue(False)
        headers = {'Authorization': 'Bearer ' + token.access_token}
        return requests.delete(URL_TEST + url, data=data, params=params, headers=headers)
