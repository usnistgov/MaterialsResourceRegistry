################################################################################
#
# File Name: models.py
# Application: mgi
# Description: 
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
import numbers
from lxml import etree
from mongoengine import *
from django_mongoengine import fields as dme_fields, Document as dme_Document

# Specific to MongoDB ordered inserts
from collections import OrderedDict
from bson.objectid import ObjectId
import xmltodict
from pymongo import MongoClient, TEXT, DESCENDING, errors
import re
import datetime
from io import BytesIO

from mgi import common
from mgi.exceptions import MDCSError, XMLError, XSDError
from utils.XMLValidation.xml_schema import validate_xml_schema
from utils.XSDhash import XSDhash
import os
from django.utils.importlib import import_module
import json
from curate.models import SchemaElement
from utils.XSDflattener.XSDflattener import XSDFlattenerDatabaseOrURL

settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
MONGODB_URI = settings.MONGODB_URI
MGI_DB = settings.MGI_DB


class Status:
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    DELETED = 'deleted'


class Request(Document):
    """Represents a request sent by an user to get an account"""
    username = StringField(required=True)
    password = StringField(required=True)
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    email = StringField(required=True)


class Message(Document):
    """Represents a message sent via the Contact form"""
    name = StringField(max_length=100)
    email = EmailField()
    content = StringField()


class Exporter(Document):
    """Represents an exporter"""
    name = StringField(required=True, unique=True)
    url = StringField(required=True)
    available_for_all = BooleanField(required=True)


class ExporterXslt(Document):
    """Represents an xslt file for exporter"""
    name = StringField(required=True, unique=True)
    filename = StringField(required=True)
    content = StringField(required=True)
    available_for_all = BooleanField(required=True)


class ResultXslt(Document):
    """Represents an xslt file for result representation"""
    name = StringField(required=True, unique=True)
    filename = StringField(required=True)
    content = StringField(required=True)


class Template(dme_Document):
    """Represents an XML schema template that defines the structure of data for curation"""
    title = dme_fields.StringField()
    filename = dme_fields.StringField()
    content = dme_fields.StringField()
    templateVersion = dme_fields.StringField(blank=True)
    version = dme_fields.IntField(blank=True)
    hash = dme_fields.StringField()
    user = dme_fields.StringField(blank=True)
    dependencies = dme_fields.ListField(StringField(), blank=True)
    exporters = dme_fields.ListField(ReferenceField(Exporter, reverse_delete_rule=PULL), blank=True)
    XSLTFiles = dme_fields.ListField(ReferenceField(ExporterXslt, reverse_delete_rule=PULL), blank=True)
    ResultXsltList = dme_fields.ReferenceField(ResultXslt, reverse_delete_rule=NULLIFY, blank=True)
    ResultXsltDetailed = dme_fields.ReferenceField(ResultXslt, reverse_delete_rule=NULLIFY, blank=True)


def delete_template(object_id):
    from mgiutils import getListNameTemplateDependenciesRecordFormData
    listName = getListNameTemplateDependenciesRecordFormData(object_id)
    return listName if listName != '' else delete_template_and_version(object_id)


def delete_template_and_version(object_id):
    template = Template.objects(pk=object_id).get()
    version = TemplateVersion.objects(pk=template.templateVersion).get()
    version.delete()
    template.delete()


def delete_type(object_id):
    from mgiutils import getListNameTypeDependenciesTemplateType
    listName = getListNameTypeDependenciesTemplateType(object_id)
    return listName if listName != '' else delete_type_and_version(object_id)


def delete_type_and_version(object_id):
    type = Type.objects(pk=object_id).get()
    version = TypeVersion.objects(pk=type.typeVersion).get()
    version.delete()
    type.delete()


def is_schema_valid(object_type, content, name=None):
    # is the name unique?
    if name is not None:
        if object_type.lower() == 'template':
            names = Template.objects.all().values_list('title')
        elif object_type.lower() == 'type':
            names = Type.objects.all().values_list('title')
        if name in names:
            raise MDCSError('A {} with the same name already exists'.format(object_type))

    # is it a valid XML document?
    try:
        try:
            xsd_tree = etree.parse(BytesIO(content.encode('utf-8')))
        except Exception:
            xsd_tree = etree.parse(BytesIO(content))
    except Exception:
        raise XMLError('Uploaded file is not well formatted XML.')

    # is it supported by the MDCS?
    errors = common.getValidityErrorsForMDCS(xsd_tree, object_type)
    if len(errors) > 0:
        errors_str = ", ".join(errors)
        raise MDCSError(errors_str)

    # is it a valid XML schema?
    error = validate_xml_schema(xsd_tree)
    if error is not None:
        raise XSDError(error)


def create_template(content, name, filename, dependencies=[], user=None, validation=True):
    if validation:
        is_schema_valid('Template', content, name)
    flattener = XSDFlattenerDatabaseOrURL(content.encode('utf-8'))
    content_encoded = flattener.get_flat()
    hash_value = XSDhash.get_hash(content_encoded)
    # save the template
    template_versions = TemplateVersion(nbVersions=1, isDeleted=False).save()
    new_template = Template(title=name, filename=filename, content=content,
                            version=1, templateVersion=str(template_versions.id),
                            hash=hash_value, user=user, dependencies=dependencies).save()

    # Add default exporters
    try:
        exporters = Exporter.objects.filter(available_for_all=True)
        new_template.exporters = exporters
    except:
        pass

    template_versions.versions = [str(new_template.id)]
    template_versions.current = str(new_template.id)
    template_versions.save()
    new_template.save()
    return new_template


def create_type(content, name, filename, buckets=[], dependencies=[], user=None):
    is_schema_valid('Type', content, name)
    hash_value = XSDhash.get_hash(content)
    # save the type
    type_versions = TypeVersion(nbVersions=1, isDeleted=False).save()
    new_type = Type(title=name, filename=filename, content=content,
                    version=1, typeVersion=str(type_versions.id), hash=hash_value,
                    user=user, dependencies=dependencies).save()

    # Add to the selected buckets
    for bucket_id in buckets:
        bucket = Bucket.objects.get(pk=bucket_id)
        bucket.types.append(str(type_versions.id))
        bucket.save()

    type_versions.versions = [str(new_type.id)]
    type_versions.current = str(new_type.id)
    type_versions.save()
    new_type.save()
    return new_type


def create_template_version(content, filename, versions_id, dependencies=[]):
    is_schema_valid('Template', content)
    flattener = XSDFlattenerDatabaseOrURL(content.encode('utf-8'))
    content_encoded = flattener.get_flat()
    hash_value = XSDhash.get_hash(content_encoded)
    template_versions = TemplateVersion.objects.get(pk=versions_id)
    template_versions.nbVersions += 1
    current_template = Template.objects.get(pk=template_versions.current)
    new_template = Template(title=current_template.title, filename=filename, content=content,
                            version=template_versions.nbVersions, templateVersion=str(versions_id),
                            hash=hash_value, dependencies=dependencies).save()

    template_versions.versions.append(str(new_template.id))
    template_versions.save()

    return new_template


def create_type_version(content, filename, versions_id, dependencies=[]):
    is_schema_valid('Type', content)
    hash_value = XSDhash.get_hash(content)
    type_versions = TypeVersion.objects.get(pk=versions_id)
    type_versions.nbVersions += 1
    current_type = Type.objects.get(pk=type_versions.current)
    new_type = Type(title=current_type.title, filename=filename, content=content,
                    version=type_versions.nbVersions, typeVersion=str(versions_id),
                    hash=hash_value, dependencies=dependencies).save()

    type_versions.versions.append(str(new_type.id))
    type_versions.save()

    return new_type


def template_list_current():
    """
    List current templates
    :param request:
    :return:
    """
    current_template_versions = TemplateVersion.objects().values_list('current')

    current_templates = []
    for tpl_version in current_template_versions:
        tpl = Template.objects.get(pk=tpl_version)
        if tpl.user is None:
            current_templates.append(tpl)

    return current_templates


def type_list_current():
    """
    List current types
    :return:
    """
    current_type_versions = TypeVersion.objects().values_list('current')

    current_types = []
    for tpl_version in current_type_versions:
        tpl = Type.objects.get(pk=tpl_version)
        if tpl.user is None:
            current_types.append(tpl)

    return current_types


class TemplateVersion(Document):
    """Manages versions of templates"""
    versions = ListField(StringField())
    deletedVersions = ListField(StringField())
    current = StringField()
    nbVersions = IntField(required=True)
    isDeleted = BooleanField(required=True)


class Type(Document):    
    """Represents an XML schema type to use to compose XML Schemas"""
    title = StringField(required=True)
    filename = StringField(required=True)
    content = StringField(required=True)
    typeVersion = StringField(required=False)
    version = IntField(required=False)
    hash = StringField(required=True)
    user = StringField(required=False)
    dependencies = ListField(StringField())


class TypeVersion(Document):
    """Manages versions of types"""
    versions = ListField(StringField())
    deletedVersions = ListField(StringField())
    current = StringField()
    nbVersions = IntField(required=True)
    isDeleted = BooleanField(required=True)


class Instance(Document):
    """Represents an instance of a remote MDCS"""
    name = StringField(required=True, unique=True)
    protocol = StringField(required=True) 
    address = StringField(required=True) 
    port = IntField(required=True)
    access_token = StringField(required=True)
    refresh_token = StringField(required=True)
    expires = DateTimeField(required=True)


class QueryResults(Document):
    """Stores results from a query (Query By Example)"""
    results = ListField(required=True) 

    
class SavedQuery(Document):
    """Represents a query saved by the user (Query by Example)"""
    user = StringField(required=True)
    template = StringField(required=True)    
    query = StringField(required=True)
    displayedQuery = StringField(required=True)


class Module(Document):
    """Represents a module, that will replace an existing input during curation"""
    name = StringField(required=True)
    url = StringField(required=True)
    view = StringField(required=True)
    multiple = BooleanField(required=True)

    
class XML2Download(Document):
    """Temporarily stores the content of an XML document to download"""
    title = StringField(required=True)
    xml = StringField(required=True)    


class PrivacyPolicy(Document):
    """Privacy Policy of the MDCS"""
    content = StringField()


class TermsOfUse(Document):
    """Terms of Use of the MDCS"""
    content = StringField()


class Help(Document):
    """Help of the MDCS"""
    content = StringField()


class Bucket(dme_Document):
    """Represents a bucket to store types by domain"""
    label = dme_fields.StringField(unique=True)
    color = dme_fields.StringField(unique=True)
    types = dme_fields.ListField(blank=True)


class FormData(dme_Document):
    """Stores data being entered and not yet curated"""
    user = dme_fields.StringField()
    template = dme_fields.StringField()
    name = dme_fields.StringField(unique_with=['user', 'template'])
    schema_element_root = dme_fields.ReferenceField(SchemaElement, blank=True)
    xml_data = dme_fields.StringField(default='')
    xml_data_id = dme_fields.StringField(blank=True)
    isNewVersionOfRecord = dme_fields.BooleanField(default=False)


def postprocessor(path, key, value):
    """
    Called after XML to JSON transformation
    :param path:
    :param key:
    :param value:
    :return:
    """
    try:
        return key, int(value)
    except (ValueError, TypeError):
        try:
            return key, float(value)
        except (ValueError, TypeError):
            return key, value


def custom_parse_numbers(num_str):
    return str(num_str)


class XMLdata(object):
    """Wrapper to manage JSON Documents, like mongoengine would have manage them (but with ordered data)"""

    def __init__(self, schemaID=None, xml=None, json=None, title="", iduser=None, ispublished=False,
                 publicationdate=None, oai_datestamp=None):
        """                                                                                                                                                                                                                   
            initialize the object                                                                                                                                                                                             
            schema = ref schema (Document)                                                                                                                                                                                    
            xml = xml string 
            title = title of the document                                                                                                                                                                                                 
        """
        # create a connection                                                                                                                                                                                                 
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        self.xmldata = db['xmldata']
        # create a new dict to keep the mongoengine order                                                                                                                                                                     
        self.content = OrderedDict()
        # insert the ref to schema                                                                                                                                                                                            
        self.content['schema'] = schemaID
        # insert the title                                                                                                                                                                                                    
        self.content['title'] = title
        if (json is not None):
            # insert the json content after                                                                                                                                                                                       
            self.content['content'] = json
        else:
            # insert the json content after                                                                                                                                                                                       
            self.content['content'] = xmltodict.parse(xml, postprocessor=postprocessor)
        #id user
        if (iduser is not None):
            self.content['iduser'] = iduser

        self.content['ispublished'] = ispublished
        if (publicationdate is not None):
            self.content['publicationdate'] = publicationdate

        if oai_datestamp is not None:
            self.content['oai_datestamp'] = oai_datestamp

        self.content['status'] = Status.ACTIVE

    @staticmethod
    def unparse(json_dict):
        json_dump_string = json.dumps(json_dict)
        preprocessed_dict = json.loads(json_dump_string,
                               parse_float=custom_parse_numbers,
                               parse_int=custom_parse_numbers,
                               object_pairs_hook=OrderedDict)
        return xmltodict.unparse(preprocessed_dict)

    @staticmethod
    def initIndexes():
        #create a connection
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        # create the full text index
        xmldata.create_index([('$**', TEXT)], default_language="en", language_override="en")


    def save(self):
        """save into mongo db"""
        # insert the content into mongo db
        self.content['lastmodificationdate'] = datetime.datetime.now()
        docID = self.xmldata.insert(self.content)
        return docID

    @staticmethod
    def objects():        
        """
            returns all objects as a list of dicts
             /!\ Doesn't return the same kind of objects as mongoengine.Document.objects()
        """
        # create a connection
        client = MongoClient(MONGODB_URI, document_class=OrderedDict)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        # find all objects of the collection
        cursor = xmldata.find()
        # build a list with the objects        
        results = []
        for result in cursor:
            results.append(result)
        return results
    

    @staticmethod
    def find(params):        
        """
            returns all objects that match params as a list of dicts 
             /!\ Doesn't return the same kind of objects as mongoengine.Document.objects()
        """
        # create a connection
        client = MongoClient(MONGODB_URI, document_class=OrderedDict)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        # find all objects of the collection
        cursor = xmldata.find(params)
        # build a list with the objects        
        results = []
        for result in cursor:
            results.append(result)
        return results
    

    @staticmethod
    def executeQuery(query):
        """queries mongo db and returns results data"""
        # create a connection
        client = MongoClient(MONGODB_URI, document_class=OrderedDict)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        # query mongo db
        cursor = xmldata.find(query)
        # build a list with the xml representation of objects that match the query      
        queryResults = []
        for result in cursor:
            queryResults.append(result['content'])
        return queryResults
    

    @staticmethod
    def executeQueryFullResult(query):
        """queries mongo db and returns results data"""
        # create a connection
        client = MongoClient(MONGODB_URI, document_class=OrderedDict)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        # query mongo db
        cursor = xmldata.find(query)
        # build a list with the xml representation of objects that match the query
        results = []
        for result in cursor:
            results.append(result)
        return results

    @staticmethod
    def get(postID):
        """
            Returns the object with the given id
        """
        # create a connection
        client = MongoClient(MONGODB_URI, document_class=OrderedDict)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        return xmldata.find_one({'_id': ObjectId(postID)})


    @staticmethod
    def getByIDsAndDistinctBy(listIDs, distinctBy=None):
        """
            Returns the object with the given id
        """
        # create a connection
        client = MongoClient(MONGODB_URI, document_class=OrderedDict)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        listIDs = [ObjectId(x) for x in listIDs]
        return xmldata.find({'_id': {'$in': listIDs}}).distinct(distinctBy)

    @staticmethod
    def getMinValue(attr):
        """
            Returns the object with the given id
        """
        # create a connection
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        cursor = xmldata.aggregate(
           [
             {
               '$group':
               {
                 '_id': {},
                 'minAttr': {'$min': '$'+attr}
               }
             }
           ]
          );
        results = []
        for result in cursor['result']:
            results.append(result['minAttr'])

        return results[0] if results[0] else None

    @staticmethod
    def delete(postID):
        """
            Delete the object with the given id
        """
        # create a connection
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        xmldata.remove({'_id': ObjectId(postID)})
    
    # TODO: to be tested
    @staticmethod
    def update(postID, json=None, xml=None):
        """
            Update the object with the given id
        """
        # create a connection
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']

        data = None
        if (json is not None):
            data = json
            if '_id' in json:
                del json['_id']
        else:
            data = xmltodict.parse(xml, postprocessor=postprocessor)

        if data is not None:
            xmldata.update({'_id': ObjectId(postID)}, {"$set": data}, upsert=False)

    @staticmethod
    def update_content(postID, content=None, title=None):
        """
            Update the object with the given id
        """
        # create a connection
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
                
        json_content = xmltodict.parse(content, postprocessor=postprocessor)
        json = {'content': json_content, 'title': title, 'lastmodificationdate': datetime.datetime.now()}
        #TODO: DO NOT bind directly the field with the status
        status = json_content['Resource'].get('@status', None)
        if status:
            json.update({'status': status})
        xmldata.update({'_id': ObjectId(postID)}, {"$set":json})

    @staticmethod
    def update_publish(postID):
        """
            Update the object with the given id
        """
        # create a connection
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        now = datetime.datetime.now()
        xmldata.update({'_id': ObjectId(postID)}, {'$set': {'publicationdate': now,
                                                            'ispublished': True,
                                                            'oai_datestamp': now}}, upsert=False)

    @staticmethod
    def update_publish_draft(postID, content=None, user=None):
        """
            Update the object with the given id
        """
        # create a connection
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        json_content = xmltodict.parse(content, postprocessor=postprocessor)
        publicationdate = datetime.datetime.now()
        #TODO: DO NOT bind directly the field with the status
        status = json_content['Resource'].get('@status', None)
        xmldata.update({'_id': ObjectId(postID)}, {'$set':{'lastmodificationdate': publicationdate,
                                                           'publicationdate': publicationdate,
                                                           'oai_datestamp': publicationdate,
                                                           'ispublished': True,
                                                           'content': json_content,
                                                           'status': status,
                                                           'iduser': user}}, upsert=False)
        return publicationdate

    @staticmethod
    def update_unpublish(postID):
        """
            Update the object with the given id
        """
        # create a connection
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        xmldata.update({'_id': ObjectId(postID)}, {'$set': {'ispublished': False}}, upsert=False)

    @staticmethod
    def update_user(postID, user=None):
        """
            Update the object with the given id
        """
        # create a connection
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        xmldata.update({'_id': ObjectId(postID)}, {'$set': {'iduser': user}}, upsert=False)

    @staticmethod
    def executeFullTextQuery(text, templatesID, refinements={}, only_content=False):
        """
        Execute a full text query with possible refinements
        """
        # create a connection
        client = MongoClient(MONGODB_URI, document_class=OrderedDict)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        wordList = re.sub("[^\w]", " ", text).split()
        wordList = ['"{0}"'.format(x) for x in wordList]
        wordList = ' '.join(wordList)

        if len(wordList) > 0:
            full_text_query = {'$text': {'$search': wordList}, 'schema': {'$in': templatesID}, }
        else:
            full_text_query = {'schema': {'$in': templatesID}}

        if len(refinements.keys()) > 0:
            full_text_query.update(refinements)

        # only get published and active resources
        full_text_query.update({'ispublished': True, 'status': {'$ne': Status.DELETED}})
        if only_content:
            cursor = xmldata.find(full_text_query, {"content": 1}).sort('publicationdate', DESCENDING)
        else:
            cursor = xmldata.find(full_text_query).sort('publicationdate', DESCENDING)
        results = []
        for result in cursor:
            results.append(result)
        return results


    @staticmethod
    def change_status(id, status, ispublished=False):
        """
            Update the status of the object with the given id
        """
        # create a connection
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['xmldata']
        #TODO: DO NOT bind directly the field with the status
        update_query = {'status': status, 'content.Resource.@status': status}
        if ispublished:
            update_query.update({'oai_datestamp': datetime.datetime.now()})

        xmldata.update({'_id': ObjectId(id)}, {'$set': update_query}, upsert=False)


class OaiSettings(Document):
    repositoryName = StringField(required=True)
    repositoryIdentifier = StringField(required=True)
    enableHarvesting = BooleanField()


class OaiIdentify(Document):
    """
        An identity object
    """
    adminEmail = StringField(required=False)
    baseURL = URLField(required=True, unique=True)
    repositoryName = StringField(required=False)
    deletedRecord = StringField(required=False)
    delimiter = StringField(required=False)
    description = StringField(required=False)
    earliestDatestamp = StringField(required=False)
    granularity = StringField(required=False)
    oai_identifier = StringField(required=False)
    protocolVersion = StringField(required=False)
    repositoryIdentifier = StringField(required=False)
    sampleIdentifier = StringField(required=False)
    scheme = StringField(required=False)
    raw = DictField(required=False)


class OaiSet(dme_Document):
    """
        A set object
    """
    setSpec = dme_fields.StringField(unique=True)
    setName = dme_fields.StringField(unique=True)
    raw = dme_fields.DictField()
    registry = dme_fields.StringField(blank=True)
    harvest = dme_fields.BooleanField(blank=True)


class OaiMetadataFormat(dme_Document):
    """
        A OaiMetadataFormat object
    """
    metadataPrefix = dme_fields.StringField()
    schema = dme_fields.StringField()
    xmlSchema = dme_fields.StringField(blank=True)
    metadataNamespace = dme_fields.StringField()
    raw = dme_fields.DictField()
    template = dme_fields.ReferenceField(Template, reverse_delete_rule=PULL, blank=True)
    registry = dme_fields.StringField(blank=True)
    hash = dme_fields.StringField(blank=True)
    harvest = dme_fields.BooleanField(blank=True)
    lastUpdate = dme_fields.DateTimeField(blank=True)


class OaiMyMetadataFormat(Document):
    """
        A OaiMyMetadataFormat object
    """
    metadataPrefix = StringField(required=True, unique=True)
    schema = StringField(required=True)
    metadataNamespace = StringField(required=True)
    xmlSchema = StringField(required=True)
    isDefault = BooleanField(required=False)
    isTemplate = BooleanField()
    template = ReferenceField(Template, reverse_delete_rule=CASCADE)


class OaiMySet(Document):
    """
        A set object
    """
    setSpec  = StringField(required=True, unique=True)
    setName = StringField(required=True, unique=True)
    templates = ListField(ReferenceField(Template, reverse_delete_rule=PULL), required=True)
    description = StringField(required=False)


class OaiRecord(Document):
    """
        A record object
    """
    identifier = StringField(required=True)
    datestamp = DateTimeField(required=True)
    deleted = BooleanField()
    sets = ListField(ReferenceField(OaiSet, reverse_delete_rule=PULL))
    metadataformat = ReferenceField(OaiMetadataFormat, reverse_delete_rule=PULL)
    metadata = DictField(required=False)
    raw = DictField(required=True)
    registry = StringField(required=False)

    def getMetadataOrdered(self):
        """
            Returns the object with the given id
        """
        # create a connection
        client = MongoClient(MONGODB_URI, document_class=OrderedDict)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['oai_record']
        data = xmldata.find_one({'_id': ObjectId(self.id)})
        return data['metadata']

    def save(self, metadata=None, force_insert=False, validate=True, clean=True,
             write_concern=None,  cascade=None, cascade_kwargs=None,
             _refs=None, **kwargs):
        """Save the :class:`~mongoengine.Document` to the database. If the
        document already exists, it will be updated, otherwise it will be
        created.

        :param force_insert: only try to create a new document, don't allow
            updates of existing documents
        :param validate: validates the document; set to ``False`` to skip.
        :param clean: call the document clean method, requires `validate` to be
            True.
        :param write_concern: Extra keyword arguments are passed down to
            :meth:`~pymongo.collection.Collection.save` OR
            :meth:`~pymongo.collection.Collection.insert`
            which will be used as options for the resultant
            ``getLastError`` command.  For example,
            ``save(..., write_concern={w: 2, fsync: True}, ...)`` will
            wait until at least two servers have recorded the write and
            will force an fsync on the primary server.
        :param cascade: Sets the flag for cascading saves.  You can set a
            default by setting "cascade" in the document __meta__
        :param cascade_kwargs: (optional) kwargs dictionary to be passed throw
            to cascading saves.  Implies ``cascade=True``.
        :param _refs: A list of processed references used in cascading saves

        .. versionchanged:: 0.5
            In existing documents it only saves changed fields using
            set / unset.  Saves are cascaded and any
            :class:`~bson.dbref.DBRef` objects that have changes are
            saved as well.
        .. versionchanged:: 0.6
            Added cascading saves
        .. versionchanged:: 0.8
            Cascade saves are optional and default to False.  If you want
            fine grain control then you can turn off using document
            meta['cascade'] = True.  Also you can pass different kwargs to
            the cascade save using cascade_kwargs which overwrites the
            existing kwargs with custom values.
        """
        if validate:
            self.validate(clean=clean)

        if write_concern is None:
            write_concern = {"w": 1}

        doc = self.to_mongo()
        doc['metadata'] = metadata

        created = ('_id' not in doc or self._created or force_insert)

        try:
            collection = self._get_collection()

            if created:
                if force_insert:
                    object_id = collection.insert(doc, **write_concern)
                else:
                    object_id = collection.save(doc, **write_concern)
            else:
                object_id = doc['_id']
                updates, removals = self._delta()
                # Need to add shard key to query, or you get an error
                select_dict = {'_id': object_id}
                shard_key = self.__class__._meta.get('shard_key', tuple())
                for k in shard_key:
                    actual_key = self._db_field_map.get(k, k)
                    select_dict[actual_key] = doc[actual_key]

                def is_new_object(last_error):
                    if last_error is not None:
                        updated = last_error.get("updatedExisting")
                        if updated is not None:
                            return not updated
                    return created

                update_query = {}

                if updates:
                    #Always modified the metadata to have the lastest version. 'self._delta' not working with metadata field
                    updates['metadata'] = metadata
                    update_query["$set"] = updates
                if removals:
                    update_query["$unset"] = removals
                if updates or removals:
                    last_error = collection.update(select_dict, update_query,
                                                   upsert=True, **write_concern)
                    created = is_new_object(last_error)

            if cascade is None:
                cascade = self._meta.get('cascade', False) or cascade_kwargs is not None

            if cascade:
                kwargs = {
                    "force_insert": force_insert,
                    "validate": validate,
                    "write_concern": write_concern,
                    "cascade": cascade
                }
                if cascade_kwargs:  # Allow granular control over cascades
                    kwargs.update(cascade_kwargs)
                kwargs['_refs'] = _refs
                self.cascade_save(**kwargs)
        except errors.DuplicateKeyError, err:
            message = u'Tried to save duplicate unique keys (%s)'
            raise NotUniqueError(message % unicode(err))
        except errors.OperationFailure, err:
            message = 'Could not save document (%s)'
            if re.match('^E1100[01] duplicate key', unicode(err)):
                # E11000 - duplicate key error index
                # E11001 - duplicate key on update
                message = u'Tried to save duplicate unique keys (%s)'
                raise NotUniqueError(message % unicode(err))
            raise OperationError(message % unicode(err))
        id_field = self._meta['id_field']
        if id_field not in self._meta.get('shard_key', []):
            self[id_field] = self._fields[id_field].to_python(object_id)

        self._clear_changed_fields()
        self._created = False
        return self

    @staticmethod
    def initIndexes():
        #create a connection
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmldata = db['oai_record']
        # create the full text index
        xmldata.create_index([('$**', TEXT)], default_language="en", language_override="en")

    @staticmethod
    def executeFullTextQuery(text, listMetadataFormatId, refinements={}, only_content=False):
        """
        Execute a full text query with possible refinements
        """
        #create a connection
        client = MongoClient(MONGODB_URI, document_class=OrderedDict)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        xmlrecord = db['oai_record']
        wordList = re.sub("[^\w]", " ",  text).split()
        wordList = ['"{0}"'.format(x) for x in wordList]
        wordList = ' '.join(wordList)
        listMetadataFormatObjectId = [ObjectId(x) for x in listMetadataFormatId]

        if len(wordList) > 0:
            full_text_query = {'$text': {'$search': wordList}, 'metadataformat' : {'$in': listMetadataFormatObjectId}, }
        else:
            full_text_query = {'metadataformat' : {'$in': listMetadataFormatObjectId} }

        if len(refinements.keys()) > 0:
            full_text_query.update(refinements)

        # only no deleted records
        full_text_query.update({'deleted':  False})

        if only_content:
            cursor = xmlrecord.find(full_text_query, {"metadata": 1 })
        else:
            cursor = xmlrecord.find(full_text_query)

        results = []
        for result in cursor:
            results.append(result)
        return results


class OaiRegistry(Document):
    """
        A registry object
    """
    name = StringField(required=True)
    url = URLField(required=True, unique=True)
    harvestrate = IntField(required=False)
    identify = ReferenceField(OaiIdentify, reverse_delete_rule=NULLIFY)
    description = StringField(required=False)
    harvest = BooleanField()
    lastUpdate = DateTimeField(required=False)
    isHarvesting = BooleanField()
    isUpdating = BooleanField()
    isDeactivated = BooleanField(required=True)
    isQueued = BooleanField()


class OaiXslt(dme_Document):
    """Represents an xslt file for Oai-Pmh"""
    name = dme_fields.StringField(unique=True)
    filename = dme_fields.StringField()
    content = dme_fields.StringField()


class OaiTemplMfXslt(Document):
    """Represents an xslt file for Oai-Pmh"""
    template = ReferenceField(Template, reverse_delete_rule=CASCADE)
    myMetadataFormat = ReferenceField(OaiMyMetadataFormat, reverse_delete_rule=CASCADE)
    xslt = ReferenceField(OaiXslt, reverse_delete_rule=CASCADE, unique_with=['template', 'myMetadataFormat'])
    activated = BooleanField()


class OaiMetadataformatSet(Document):
    """
        A record object
    """
    set = ReferenceField(OaiSet, reverse_delete_rule=CASCADE)
    metadataformat = ReferenceField(OaiMetadataFormat, reverse_delete_rule=CASCADE)
    lastUpdate = DateTimeField(required=False)
