################################################################################
#
# File Name: views.py
# Application: api
# Purpose:   
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

# REST Framework
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
# Models
from mgi.common import LXML_SCHEMA_NAMESPACE
from mgi.models import SavedQuery, XMLdata, Template, TemplateVersion, Type, TypeVersion, Instance, Exporter, \
    ExporterXslt, create_template_version, create_template, create_type_version, create_type
from exporter.builtin.models import XSLTExporter
from django.contrib.auth.models import User
# Serializers
from api.serializers import exporterSerializer, exporterXSLTSerializer, jsonExportSerializer, jsonExportResSerializer,\
    jsonXSLTSerializer, savedQuerySerializer, jsonDataSerializer, querySerializer, schemaSerializer, \
    templateSerializer, typeSerializer, resTypeSerializer, TemplateVersionSerializer, TypeVersionSerializer, \
    instanceSerializer, resInstanceSerializer, UserSerializer, insertUserSerializer, resSavedQuerySerializer,\
    updateUserSerializer, newInstanceSerializer
from lxml import etree
from django.conf import settings
import os
from mongoengine import *
from pymongo import MongoClient
from mgi.settings import MONGODB_URI, MGI_DB
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
MONGODB_URI = settings.MONGODB_URI
MGI_DB = settings.MGI_DB
BLOB_HOSTER = settings.BLOB_HOSTER
BLOB_HOSTER_URI = settings.BLOB_HOSTER_URI
BLOB_HOSTER_USER = settings.BLOB_HOSTER_USER
BLOB_HOSTER_PSWD = settings.BLOB_HOSTER_PSWD
MDCS_URI = settings.MDCS_URI
from bson.objectid import ObjectId
import re
import requests
from mongoengine.queryset.visitor import Q
import operator
import json
from collections import OrderedDict
from StringIO import StringIO
from django.http.response import HttpResponse
from utils.XMLValidation.xml_schema import validate_xml_schema
from io import BytesIO
from utils.APIschemaLocator.APIschemaLocator import getSchemaLocation
from datetime import datetime
from datetime import timedelta
from mgi import common
from utils.BLOBHoster.BLOBHosterFactory import BLOBHosterFactory
from mimetypes import guess_type
from exporter import get_exporter
import zipfile
import mongoengine.errors as MONGO_ERRORS
from admin_mdcs.models import api_permission_required, api_staff_member_required
import mgi.rights as RIGHTS


################################################################################
# 
# Function Name: select_all_savedqueries(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get all saved queries
# 
################################################################################
@api_view(['GET'])
@api_permission_required(RIGHTS.explore_content_type, RIGHTS.explore_access)
def select_all_savedqueries(request):
    """
    GET http://localhost/rest/saved_queries/select/all
    """
    queries = SavedQuery.objects()
    serializer = savedQuerySerializer(queries)
    return Response(serializer.data, status=status.HTTP_200_OK)


################################################################################
# 
# Function Name: select_savedquery(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get saved queries that match the parameters
# 
################################################################################
@api_view(['GET'])
@api_permission_required(RIGHTS.explore_content_type, RIGHTS.explore_access)
def select_savedquery(request):
    """
    GET http://localhost/rest/saved_queries/select
    id: string (ObjectId)
    user: string 
    template: string
    query: string
    displayedQuery: string
    """
    id = request.QUERY_PARAMS.get('id', None)
    user = request.QUERY_PARAMS.get('user', None)
    template = request.QUERY_PARAMS.get('template', None)
    dbquery = request.QUERY_PARAMS.get('query', None)
    displayedQuery = request.QUERY_PARAMS.get('displayedQuery', None)

    try:
        # create a connection
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        savedQueries = db['saved_query']
        query = dict()
        if id is not None:
            query['_id'] = ObjectId(id)
        if user is not None:
            if len(user) >= 2 and user[0] == '/' and user[-1] == '/':
                query['user'] = re.compile(user[1:-1])
            else:
                query['user'] = user
        if template is not None:
            if len(template) >= 2 and template[0] == '/' and template[-1] == '/':
                query['template'] = re.compile(template[1:-1])
            else:
                query['template'] = template
        if dbquery is not None:
            if len(dbquery) >= 2 and dbquery[0] == '/' and dbquery[-1] == '/':
                query['query'] = re.compile(dbquery[1:-1])
            else:
                query['query'] = dbquery
        if displayedQuery is not None:
            if len(displayedQuery) >= 2 and displayedQuery[0] == '/' and displayedQuery[-1] == '/':
                query['displayedQuery'] = re.compile(displayedQuery[1:-1])
            else:
                query['displayedQuery'] = displayedQuery
        if len(query.keys()) == 0:
            content = {'message':'No parameters given.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            cursor = savedQueries.find(query)
            listSavedQueries = []
            for resultSavedQuery in cursor:
                resultSavedQuery['id'] = resultSavedQuery['_id']
                del resultSavedQuery['_id']
                listSavedQueries.append(resultSavedQuery)
            serializer = resSavedQuerySerializer(listSavedQueries)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        content = {'message':'No saved query found with the given parameters.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

################################################################################
# 
# Function Name: add_savedquery(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Add a saved query
# 
################################################################################
@api_view(['POST'])
@api_permission_required(RIGHTS.explore_content_type, RIGHTS.explore_save_query)
def add_savedquery(request):
    """
    POST http://localhost/rest/saved_queries/add
    POST data user="user", template="template" query="query", displayedQuery="displayedQuery"
    """
    serializer = resSavedQuerySerializer(data=request.DATA)
    if serializer.is_valid():
        errors = ""
        try:
            json_object = json.loads(request.DATA["query"])
        except ValueError:
            errors += "Invalid query."
        try:
            template = Template.objects.get(pk=request.DATA["template"])
        except Exception:
            errors += "Unknown template."
        try:
            user = User.objects.get(pk=request.DATA["user"])
        except Exception:
            errors += "Unknown user."

        if errors != "":
            content = {'message':errors}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            SavedQuery(user=request.DATA["user"],template=request.DATA["template"],query=request.DATA["query"],displayedQuery=request.DATA["displayedQuery"]).save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception, e:
            content = {'message':e.message}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


################################################################################
# 
# Function Name: delete_savedquery(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Delete a saved query
# 
################################################################################
@api_view(['DELETE'])
@api_permission_required(RIGHTS.explore_content_type, RIGHTS.explore_delete_query)
def delete_savedquery(request):
    """
    GET http://localhost/rest/saved_queries/delete?id=id
    URL parameters: 
    id: string 
    """
    id = request.QUERY_PARAMS.get('id', None)
    if id is not None:
        try:
            query = SavedQuery.objects.get(pk=id)
            query.delete()
            content = {'message':"Query deleted with success."}
            return Response(content, status=status.HTTP_200_OK)
        except:
            content = {'message':"No query found with the given id."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':"No id provided."}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


################################################################################
# 
# Function Name: explore(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get all XML data
# 
################################################################################
@api_view(['GET'])
@api_permission_required(RIGHTS.explore_content_type, RIGHTS.explore_access)
def explore(request):
    """
    GET http://localhost/rest/explore/select/all
    dataformat: [xml,json]
    """
    dataformat = request.QUERY_PARAMS.get('dataformat', None)

    jsonData = XMLdata.objects()
    
    if dataformat== None or dataformat=="xml":
        for jsonDoc in jsonData:
            jsonDoc['content'] = XMLdata.unparse(jsonDoc['content'])
        serializer = jsonDataSerializer(jsonData)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif dataformat == "json":
        serializer = jsonDataSerializer(jsonData)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        content = {'message':'The specified format is not accepted.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

################################################################################
# 
# Function Name: explore_detail(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get XML data that match the parameters
# 
################################################################################
@api_view(['GET'])
@api_permission_required(RIGHTS.explore_content_type, RIGHTS.explore_access)
def explore_detail(request):
    """
    GET http://localhost/rest/explore/select
    id: string (ObjectId)
    schema: string (ObjectId)
    title: string
    dataformat: [xml,json]
    """        
    id = request.QUERY_PARAMS.get('id', None)
    schema = request.QUERY_PARAMS.get('schema', None)
    title = request.QUERY_PARAMS.get('title', None)
    dataformat = request.QUERY_PARAMS.get('dataformat', None)

    try:        
        query = dict()
        if id is not None:            
            query['_id'] = ObjectId(id)            
        if schema is not None:
            if len(schema) >= 2 and schema[0] == '/' and schema[-1] == '/':
                query['schema'] = re.compile(schema[1:-1])
            else:
                query['schema'] = schema
        if title is not None:
            if len(title) >= 2 and title[0] == '/' and title[-1] == '/':
                query['title'] = re.compile(title[1:-1])
            else:
                query['title'] = title
        if len(query.keys()) == 0:
            content = {'message':'No parameters given.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            jsonData = XMLdata.executeQueryFullResult(query)
        
            if dataformat== None or dataformat=="xml":
                for jsonDoc in jsonData:
                    jsonDoc['content'] = XMLdata.unparse(jsonDoc['content'])
                serializer = jsonDataSerializer(jsonData)
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif dataformat == "json":
                serializer = jsonDataSerializer(jsonData)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                content = {'message':'The specified format is not accepted.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
    except:
        content = {'message':'No data found with the given parameters.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


################################################################################
#
# Function Name: explore_detail_data_download(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Download document content
#
################################################################################
@api_view(['GET'])
@api_permission_required(RIGHTS.explore_content_type, RIGHTS.explore_access)
def explore_detail_data_download(request):
    """
    GET http://localhost/rest/explore/data/download
    id: string (ObjectId)
    dataformat: [xml,json]
    """
    id = request.QUERY_PARAMS.get('id', None)
    dataformat = request.QUERY_PARAMS.get('dataformat', None)

    try:
        query = dict()
        if id is not None:
            query['_id'] = ObjectId(id)
        if len(query.keys()) == 0:
            content = {'message':'No parameters given.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            jsonData = XMLdata.executeQueryFullResult(query)
            jsonData = jsonData.pop()
            #We remove the extension
            filename = os.path.splitext(jsonData['title'])[0]

            if dataformat== None or dataformat=="xml":
                jsonData['content'] = XMLdata.unparse(jsonData['content'])
                contentEncoded = jsonData['content'].encode('utf-8')
                fileObj = StringIO(contentEncoded)
                response = HttpResponse(fileObj, content_type='application/xml')
                response['Content-Disposition'] = 'attachment; filename=' + filename
                return response
            elif dataformat == "json":
                contentEncoded = json.dumps(jsonData['content'])
                fileObj = StringIO(contentEncoded)
                response = HttpResponse(fileObj, content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename=' + filename
                return response
            else:
                content = {'message':'The specified format is not accepted.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
    except:
        content = {'message':'No data found with the given parameters.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

################################################################################
# 
# Function Name: explore_delete(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Delete the XML data with the provided id
# 
################################################################################
@api_view(['DELETE'])
@api_permission_required(RIGHTS.curate_content_type, RIGHTS.curate_delete_document)
def explore_delete(request):
    """
    GET http://localhost/rest/explore/delete
    id: string (ObjectId)
    """        
    id = request.QUERY_PARAMS.get('id', None)
     
    try:        
        query = dict()
        if id is not None:            
            query['_id'] = ObjectId(id)            
        if len(query.keys()) == 0:
            content = {'message':'No id given.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            XMLdata.delete(id)
            content = {'message':'Data deleted with success.'}
            return Response(content, status=status.HTTP_204_NO_CONTENT)
    except:
        content = {'message':'No data found with the given id.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

################################################################################
# 
# Function Name: manageRegexInAPI(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Compile the regex in a query
# 
################################################################################
def manageRegexInAPI(query):
    for key, value in query.iteritems():
        if key == "$and" or key == "$or":
            for subValue in value:
                manageRegexInAPI(subValue)
        elif isinstance(value, str) or isinstance(value, unicode):
            if (len(value) >= 2 and value[0] == "/" and value[-1] == "/"):
                query[key] = re.compile(value[1:-1])
        elif isinstance(value, dict):
            manageRegexInAPI(value)

################################################################################
# 
# Function Name: query_by_example(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Submit a query to MongoDB
# 
################################################################################
@api_view(['POST'])
@api_permission_required(RIGHTS.explore_content_type, RIGHTS.explore_access)
def query_by_example(request):
    """
    POST http://localhost/rest/explore/query-by-example
    POST data query="{'path_to_element':'value','schema':'id'}" repositories="Local,Server1,Server2" dataformat: [xml,json]
    {"query":"{'content.root.property1.value':'xxx','schema':'id'}"}
    """
         
    dataformat = None
    if 'dataformat' in request.DATA:
        dataformat = request.DATA['dataformat']
    
    qSerializer = querySerializer(data=request.DATA)
    if qSerializer.is_valid():
        if 'repositories' in request.DATA:
            instanceResults = []
            repositories = request.DATA['repositories'].strip().split(",")
            if len(repositories) == 0:
                content = {'message':'Repositories keyword found but the list is empty.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            else:
                instances = []
                local = False
                for repository in repositories:
                    if repository == "Local":
                        local = True
                    else:
                        try:
                            instance = Instance.objects.get(name=repository)
                            instances.append(instance)
                        except:
                            content = {'message':'Unknown repository.'}
                            return Response(content, status=status.HTTP_400_BAD_REQUEST)
                if local:
                    try:
                        query = eval(request.DATA['query'])
                        manageRegexInAPI(query)
                        instanceResults = instanceResults + XMLdata.executeQueryFullResult(query)                        
                    except:
                        content = {'message':'Bad query: use the following format {\'element\':\'value\'}'}
                        return Response(content, status=status.HTTP_400_BAD_REQUEST)
                for instance in instances:
                    url = instance.protocol + "://" + instance.address + ":" + str(instance.port) + "/rest/explore/query-by-example"   
                    query = request.DATA['query']              
                    data = {"query":query}
                    headers = {'Authorization': 'Bearer ' + instance['access_token']}
                    r = requests.post(url, data=data, headers=headers)
                    result = r.text
                    instanceResults = instanceResults + json.loads(result,object_pairs_hook=OrderedDict)
            
                if dataformat== None or dataformat=="xml":
                    for jsonDoc in instanceResults:
                        jsonDoc['content'] = XMLdata.unparse(jsonDoc['content'])
                    serializer = jsonDataSerializer(instanceResults)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                elif dataformat == "json":
                    serializer = jsonDataSerializer(instanceResults)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    content = {'message':'The specified format is not accepted.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                query = eval(request.DATA['query'])
                manageRegexInAPI(query)
                results = XMLdata.executeQueryFullResult(query)
            
                if dataformat== None or dataformat=="xml":
                    for jsonDoc in results:
                        jsonDoc['content'] = XMLdata.unparse(jsonDoc['content'])
                    serializer = jsonDataSerializer(results)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                elif dataformat == "json":
                    serializer = jsonDataSerializer(results)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    content = {'message':'The specified format is not accepted.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
            except:
                content = {'message':'Bad query: use the following format {\'element\':\'value\'}'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
    return Response(qSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


  

################################################################################
# 
# Function Name: curate(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Curate an XML document: save the data in MongoDB and Jena
# 
################################################################################
@api_view(['POST'])
@api_permission_required(RIGHTS.curate_content_type, RIGHTS.curate_access)
def curate(request):
    """
    POST http://localhost/rest/curate
    POST data title="title", schema="schemaID", content="<root>...</root>"
    """        
    serializer = jsonDataSerializer(data=request.DATA)
    if serializer.is_valid():
        try:
            schema = Template.objects.get(pk=ObjectId(request.DATA['schema']))
            templateVersion = TemplateVersion.objects.get(pk=ObjectId(schema.templateVersion))
            if str(schema.id) in templateVersion.deletedVersions:
                content = {'message: The provided template is currently deleted.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except:
            content = {'message: No template found with the given id.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
        xmlStr = request.DATA['content']
        docID = None
        try:
            try:
                common.validateXMLDocument(xmlStr, schema.content)
            except etree.XMLSyntaxError, xse:
                #xmlParseEntityRef exception: use of & < > forbidden
                content= {'message': "Validation Failed. May be caused by : Syntax problem, use of forbidden symbols like '&' or '<' or '>'"}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            except Exception, e:
                content = {'message': e.message}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            jsondata = XMLdata(schemaID = request.DATA['schema'], xml = xmlStr, title = request.DATA['title'], iduser=str(request.user.id))
            docID = jsondata.save()            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            if docID is not None:
                jsondata.delete(docID)
            content = {'message: Unable to insert data.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

################################################################################
# 
# Function Name: add_schema(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Add a template or a version of a template
# 
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def add_schema(request):
    """
    POST http://localhost/rest/templates/add
    POST data title="title", filename="filename", content="<xsd:schema>...</xsd:schema>" templateVersion="id", dependencies{}="id,id"
    """

    sSerializer = schemaSerializer(data=request.DATA)
    if sSerializer.is_valid():
        xsdContent = request.DATA['content']

        # is this a valid XMl document?
        try:
            xmlTree = etree.parse(BytesIO(xsdContent.encode('utf-8')))
        except Exception, e:
            content = {'message':'This is not a valid XML document.' + e.message.replace("'","")}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        # check that the schema is valid for the MDCS
        errors = common.getValidityErrorsForMDCS(xmlTree, "Template")
        if len(errors) > 0:
            content = {'message':'This template is not supported by the current version of the MDCS.', 'errors': errors}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # manage the dependencies
        includes = xmlTree.findall("{}include".format(LXML_SCHEMA_NAMESPACE))
        idxInclude = 0
        dependencies = []

        if 'dependencies[]' in request.DATA:
            dependencies = request.DATA['dependencies[]'].strip().split(",")
            if len(dependencies) == len(includes):
                listTypesId = []
                for typeId in Type.objects.all().values_list('id'):
                    listTypesId.append(str(typeId))

                # replace includes/imports by API calls
                for dependency in dependencies:
                    if dependency in listTypesId:
                        includes[idxInclude].attrib['schemaLocation'] = getSchemaLocation(str(dependency))
                        idxInclude += 1
                    else:
                        content = {'message':'One or more dependencies can not be found in the database.'}
                        return Response(content, status=status.HTTP_400_BAD_REQUEST)

                # validate the schema
                error = validate_xml_schema(xmlTree)

                if error is not None:
                    content = {'message':'This is not a valid XML schema.' + error.replace("'","")}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                else:
                    xsdContent = etree.tostring(xmlTree)
            else:
                content = {'message':'The number of given dependencies (' + str(len(dependencies)) + ')  is different from the actual number of dependencies found in the uploaded template (' + str(len(includes)) + ').'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            if len(includes) > 0:
                content = {'message':'The template that you are trying to upload has some dependencies. Use the "dependencies" keyword to register a template with its dependencies.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            else:
                # validate the schema
                error = validate_xml_schema(xmlTree)

                if error is not None:
                    content = {'message':'This is not a valid XML schema.' + error.replace("'","")}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # a template version is provided: if it exists, add the schema as a new version and manage the version numbers
        if "templateVersion" in request.DATA:
            try:
                templateVersions = TemplateVersion.objects.get(pk=request.DATA['templateVersion'])
                if templateVersions.isDeleted == True:
                    content = {'message':'This template version belongs to a deleted template. You are not allowed to add a template to it.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                new_template = create_template_version(xsdContent, request.DATA['filename'], str(templateVersions.id))
            except:
                content = {'message':'No template version found with the given id.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            new_template = create_template(xsdContent, request.DATA['title'], request.DATA['filename'], dependencies)

        return Response(eval(new_template.to_json()), status=status.HTTP_201_CREATED)
    return Response(sSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


################################################################################
# 
# Function Name: select_schema(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get templates that match the parameters
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def select_schema(request):
    """
    GET http://localhost/rest/templates/select?param1=value1&param2=value2
    URL parameters: 
    id: string (ObjectId)
    filename: string
    content: string
    title: string
    version: integer
    templateVersion: string (ObjectId)
    hash: string
    For string fields, you can use regular expressions: /exp/
    """
    
    id = request.QUERY_PARAMS.get('id', None)
    filename = request.QUERY_PARAMS.get('filename', None)
    content = request.QUERY_PARAMS.get('content', None)
    title = request.QUERY_PARAMS.get('title', None)
    version = request.QUERY_PARAMS.get('version', None)
    templateVersion = request.QUERY_PARAMS.get('templateVersion', None)
    hash = request.QUERY_PARAMS.get('hash', None)
    
    try:        
        query = dict()
        if id is not None:
            query['id'] = ObjectId(id)
        if filename is not None:
            if len(filename) >= 2 and filename[0] == '/' and filename[-1] == '/':
                query['filename'] = re.compile(filename[1:-1])
            else:
                query['filename'] = filename            
        if content is not None:
            if len(content) >= 2 and content[0] == '/' and content[-1] == '/':
                query['content'] = re.compile(content[1:-1])
            else:
                query['content'] = content
        if title is not None:
            if len(title) >= 2 and title[0] == '/' and title[-1] == '/':
                query['title'] = re.compile(title[1:-1])
            else:
                query['title'] = title
        if version is not None:
            query['version'] = version
        if templateVersion is not None:
            if len(templateVersion) >= 2 and templateVersion[0] == '/' and templateVersion[-1] == '/':
                query['templateVersion'] = re.compile(templateVersion[1:-1])
            else:
                query['templateVersion'] = templateVersion
        if hash is not None:
            if len(hash) >= 2 and hash[0] == '/' and hash[-1] == '/':
                query['hash'] = re.compile(hash[1:-1])
            else:
                query['hash'] = hash
        q_list = {Q(**({key:value})) for key, value in query.iteritems()}
        if len(q_list) > 0:
            try:
                templates = Template.objects(reduce(operator.and_, q_list)).all()
                #If no templates available
                if len(templates) == 0:
                    content = {'message':'No template found with the given parameters.'}
                    return Response(content, status=status.HTTP_404_NOT_FOUND)
            except Exception, e:
                content = {'message':'No template found with the given parameters.'}
                return Response(content, status=status.HTTP_404_NOT_FOUND)
        else:
           content = {'message':'No parameters given.'}
           return Response(content, status=status.HTTP_400_BAD_REQUEST)


        serializer = templateSerializer(templates)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        content = {'message':'No template found with the given parameters.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


################################################################################
# 
# Function Name: select_all_schemas(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get all schemas
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def select_all_schemas(request):
    """
    GET http://localhost/rest/templates/select/all
    """
    templates = Template.objects
    serializer = templateSerializer(templates)
    return Response(serializer.data, status=status.HTTP_200_OK)

################################################################################
# 
# Function Name: select_all_schemas_versions(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get all template version managers
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def select_all_schemas_versions(request):
    """
    GET http://localhost/rest/schemas/versions/select/all
    """
    templateVersions = TemplateVersion.objects
    serializer = TemplateVersionSerializer(templateVersions)
    return Response(serializer.data, status=status.HTTP_200_OK)

################################################################################
# 
# Function Name: current_template_version(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Set the current version of a template
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def current_template_version(request):
    """
    GET http://localhost/rest/templates/versions/current?id=IdToBeCurrent
    """
    id = request.QUERY_PARAMS.get('id', None)
    if id is not None:
        try:
            template = Template.objects.get(pk=id)
        except:
            content = {'message':'No template found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No template id provided to be current.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    templateVersion = TemplateVersion.objects.get(pk=template.templateVersion)
    if templateVersion.isDeleted == True:
        content = {'message':'This template version belongs to a deleted template. You are not allowed to restore it. Please restore the template first (id:'+ str(templateVersion.id) +').'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if templateVersion.current == id:
        content = {'message':'The selected template is already the current template.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if id in templateVersion.deletedVersions:
        content = {'message':'The selected template is deleted. Please restore it first to make it current.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    templateVersion.current = id
    templateVersion.save()
    content = {'message':'Current template set with success.'}
    return Response(content, status=status.HTTP_200_OK)

################################################################################
# 
# Function Name: delete_schema(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Delete a template
# 
################################################################################
@api_view(['DELETE'])
@api_staff_member_required()
def delete_schema(request):
    """
    GET http://localhost/rest/templates/delete?id=IDtodelete&next=IDnextCurrent
    GET http://localhost/rest/templates/delete?templateVersion=IDtodelete
    URL parameters: 
    id: string (ObjectId)
    next: string (ObjectId)
    templateVersion: string (ObjectId)
    """
    # if request.user.is_staff is True:
    id = request.QUERY_PARAMS.get('id', None)
    next = request.QUERY_PARAMS.get('next', None)
    versionID = request.QUERY_PARAMS.get('templateVersion', None)

    if versionID is not None:
        if id is not None or next is not None:
            content = {'message':'Wrong parameters combination.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                templateVersion = TemplateVersion.objects.get(pk=versionID)
                if templateVersion.isDeleted == False:
                    templateVersion.deletedVersions.append(templateVersion.current)
                    templateVersion.isDeleted = True
                    templateVersion.save()
                    content = {'message':'Template version deleted with success.'}
                    return Response(content, status=status.HTTP_200_OK)
                else:
                    content = {'message':'Template version already deleted.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
            except:
                content = {'message':'No template version found with the given id.'}
                return Response(content, status=status.HTTP_404_NOT_FOUND)

    if id is not None:
        try:
            template = Template.objects.get(pk=id)
        except:
            content = {'message':'No template found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No template id provided to delete.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if next is not None:
        try:
            nextCurrent = Template.objects.get(pk=next)
            if nextCurrent.templateVersion != template.templateVersion:
                content = {'message':'The specified next current template is not a version of the current template.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except:
            content = {'message':'No template found with the given id to be the next current.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

    templateVersion = TemplateVersion.objects.get(pk=template.templateVersion)
    if templateVersion.isDeleted == True:
        content = {'message':'This template version belongs to a deleted template. You are not allowed to delete it. Please restore the template first (id:'+ str(templateVersion.id) +').'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if templateVersion.current == str(template.id) and next is None:
        content = {'message':'The selected template is the current. It can\'t be deleted. If you still want to delete this template, please provide the id of the next current template using \'next\' parameter'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif templateVersion.current == str(template.id) and next is not None and str(template.id) == str(nextCurrent.id):
        content = {'message':'Template id to delete and next id are the same.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif templateVersion.current != str(template.id) and next is not None:
        content = {'message':'You should only provide the next parameter when you want to delete a current version of a template.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif templateVersion.current == str(template.id) and next is not None:
        if next in templateVersion.deletedVersions:
            content = {'message':'The template is deleted, it can\'t become current.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        templateVersion.deletedVersions.append(str(template.id))
        templateVersion.current = str(nextCurrent.id)
        templateVersion.save()
        content = {'message':'Current template deleted with success. A new version is current.'}
        return Response(content, status=status.HTTP_204_NO_CONTENT)
    else:
#             del templateVersion.versions[templateVersion.versions.index(str(template.id))]
#             template.delete()
        if str(template.id) in templateVersion.deletedVersions:
            content = {'message':'This template is already deleted.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        templateVersion.deletedVersions.append(str(template.id))
        templateVersion.save()
        content = {'message':'Template deleted with success.'}
        return Response(content, status=status.HTTP_204_NO_CONTENT)
    # else:
    #     content = {'message':'Only an administrator can use this feature.'}
    #     return Response(content, status=status.HTTP_401_UNAUTHORIZED)
    
################################################################################
# 
# Function Name: restore_schema(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Restore a template or a template version manager
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def restore_schema(request):
    """
    GET http://localhost/rest/templates/restore?id=IDtorestore
    GET http://localhost/rest/templates/restore?templateVersion=IDtorestore
    URL parameters: 
    id: string (ObjectId)
    templateVersion: string (ObjectId)
    """
    # if request.user.is_staff is True:
    id = request.QUERY_PARAMS.get('id', None)
    versionID = request.QUERY_PARAMS.get('templateVersion', None)

    if versionID is not None:
        if id is not None:
            content = {'message':'Wrong parameters combination.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                templateVersion = TemplateVersion.objects.get(pk=versionID)
                if templateVersion.isDeleted == False:
                    content = {'message':'Template version not deleted. No need to be restored.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                else:
                    templateVersion.isDeleted = False
                    del templateVersion.deletedVersions[templateVersion.deletedVersions.index(templateVersion.current)]
                    templateVersion.save()
                    content = {'message':'Template restored with success.'}
                    return Response(content, status=status.HTTP_200_OK)
            except:
                content = {'message':'No template version found with the given id.'}
                return Response(content, status=status.HTTP_404_NOT_FOUND)

    if id is not None:
        try:
            template = Template.objects.get(pk=id)
        except:
            content = {'message':'No template found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No template id provided to restore.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    templateVersion = TemplateVersion.objects.get(pk=template.templateVersion)
    if templateVersion.isDeleted == True:
        content = {'message':'This template version belongs to a deleted template. You are not allowed to restore it. Please restore the template first (id:'+ str(templateVersion.id) +').'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if id in templateVersion.deletedVersions:
        del templateVersion.deletedVersions[templateVersion.deletedVersions.index(id)]
        templateVersion.save()
        content = {'message':'Template version restored with success.'}
        return Response(content, status=status.HTTP_200_OK)
    else:
        content = {'message':'Template version not deleted. No need to be restored.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     content = {'message':'Only an administrator can use this feature.'}
    #     return Response(content, status=status.HTTP_401_UNAUTHORIZED)
    
################################################################################
# 
# Function Name: add_type(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Add a type
# 
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def add_type(request):
    """
    POST http://localhost/rest/types/add
    POST data title="title", filename="filename", content="..." typeVersion="id" dependencies[]="id,id"
    """

    oSerializer = typeSerializer(data=request.DATA)
    if oSerializer.is_valid():
        xsdContent = request.DATA['content']

        # is this a valid XMl document?
        try:
            xmlTree = etree.parse(BytesIO(xsdContent.encode('utf-8')))
        except Exception, e:
            content = {'message':'This is not a valid XML document.' + e.message.replace("'","")}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # check that the schema is valid for the MDCS
        errors = common.getValidityErrorsForMDCS(xmlTree, "Type")
        if len(errors) > 0:
            content = {'message':'This type is not supported by the current version of the MDCS.', 'errors': errors}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # manage the dependencies
        includes = xmlTree.findall("{}include".format(LXML_SCHEMA_NAMESPACE))
        idxInclude = 0
        dependencies = []

        if 'dependencies[]' in request.DATA:
            dependencies = request.DATA['dependencies[]'].strip().split(",")
            if len(dependencies) == len(includes):
                listTypesId = []
                for typeId in Type.objects.all().values_list('id'):
                    listTypesId.append(str(typeId))

                # replace includes/imports by API calls
                for dependency in dependencies:
                    if dependency in listTypesId:
                        includes[idxInclude].attrib['schemaLocation'] = getSchemaLocation(str(dependency))
                        idxInclude += 1
                    else:
                        content = {'message':'One or more dependencies can not be found in the database.'}
                        return Response(content, status=status.HTTP_400_BAD_REQUEST)

                # validate the schema
                error = validate_xml_schema(xmlTree)

                if error is not None:
                    content = {'message':'This is not a valid XML schema.' + error.replace("'","")}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                else:
                    xsdContent = etree.tostring(xmlTree)
            else:
                content = {'message':'The number of given dependencies (' + str(len(dependencies)) + ') is different from the actual number of dependencies found in the uploaded template (' + str(len(includes)) + ').'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            if len(includes) > 0:
                content = {'message':'The template that you are trying to upload has some dependencies. Use the "dependencies" keyword to register a template with its dependencies.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            else:
                # validate the schema
                error = validate_xml_schema(xmlTree)

                if error is not None:
                    content = {'message':'This is not a valid XML schema.' + error.replace("'","")}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # a type version is provided: if it exists, add the type as a new version and manage the version numbers
        if "typeVersion" in request.DATA:
            try:
                typeVersions = TypeVersion.objects.get(pk=request.DATA['typeVersion'])
                if typeVersions.isDeleted == True:
                    content = {'message':'This type version belongs to a deleted type. You can not add a type to it.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

                new_type = create_type_version(xsdContent, request.DATA['filename'], str(typeVersions.id))
            except:
                content = {'message':'No type version found with the given id.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            new_type = create_type(xsdContent, request.DATA['title'], request.DATA['filename'], [], dependencies)

        return Response(eval(new_type.to_json()), status=status.HTTP_201_CREATED)
    return Response(oSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

################################################################################
# 
# Function Name: select_type(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Select types that match parameters
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def select_type(request):
    """
    GET http://localhost/rest/types/select?param1=value1&param2=value2
    URL parameters: 
    id: string (ObjectId)
    filename: string
    content: string
    title: string
    version: integer
    typeVersion: string (ObjectId)
    For string fields, you can use regular expressions: /exp/
    """
    id = request.QUERY_PARAMS.get('id', None)
    filename = request.QUERY_PARAMS.get('filename', None)
    content = request.QUERY_PARAMS.get('content', None)
    title = request.QUERY_PARAMS.get('title', None)
    version = request.QUERY_PARAMS.get('version', None)
    typeVersion = request.QUERY_PARAMS.get('typeVersion', None)
    
    try:        
        # create a connection                                                                                                                                                                                                 
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        type = db['type']
        query = dict()
        if id is not None:            
            query['_id'] = ObjectId(id)            
        if filename is not None:
            if len(filename) >= 2 and filename[0] == '/' and filename[-1] == '/':
                query['filename'] = re.compile(filename[1:-1])
            else:
                query['filename'] = filename            
        if content is not None:
            if len(content) >= 2 and content[0] == '/' and content[-1] == '/':
                query['content'] = re.compile(content[1:-1])
            else:
                query['content'] = content
        if title is not None:
            if len(title) >= 2 and title[0] == '/' and title[-1] == '/':
                query['title'] = re.compile(title[1:-1])
            else:
                query['title'] = title
        if version is not None:
            query['version'] = version
        if typeVersion is not None:
            if len(typeVersion) >= 2 and typeVersion[0] == '/' and typeVersion[-1] == '/':
                query['typeVersion'] = re.compile(typeVersion[1:-1])
            else:
                query['typeVersion'] = typeVersion
        if len(query.keys()) == 0:
            content = {'message':'No parameters given.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            cursor = type.find(query)
            types = []
            for resultType in cursor:
                resultType['id'] = resultType['_id']
                del resultType['_id']
                types.append(resultType)
            serializer = resTypeSerializer(types)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        content = {'message':'No type found with the given parameters.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

################################################################################
# 
# Function Name: select_all_types(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get all types
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def select_all_types(request):
    """
    GET http://localhost/rest/types/select/all
    """
    types = Type.objects
    serializer = resTypeSerializer(types)
    return Response(serializer.data, status=status.HTTP_200_OK)

################################################################################
# 
# Function Name: select_all_types_versions(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get all type versions managers
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def select_all_types_versions(request):
    """
    GET http://localhost/rest/types/versions/select/all
    """
    typeVersions = TypeVersion.objects
    serializer = TypeVersionSerializer(typeVersions)
    return Response(serializer.data, status=status.HTTP_200_OK)

################################################################################
# 
# Function Name: current_type_version(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Set the current version of a type
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def current_type_version(request):
    """
    GET http://localhost/rest/types/versions/current?id=IdToBeCurrent
    """
    # if request.user.is_staff is True:
    id = request.QUERY_PARAMS.get('id', None)
    if id is not None:
        try:
            type = Type.objects.get(pk=id)
        except:
            content = {'message':'No type found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No type id provided to be current.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    typeVersion = TypeVersion.objects.get(pk=type.typeVersion)
    if typeVersion.isDeleted == True:
        content = {'message':'This type version belongs to a deleted type. You are not allowed to restore it. Please restore the type first (id:'+ str(typeVersion.id) +').'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if typeVersion.current == id:
        content = {'message':'The selected type is already the current type.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if id in typeVersion.deletedVersions:
        content = {'message':'The selected type is deleted. Please restore it first to make it current.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    typeVersion.current = id
    typeVersion.save()
    content = {'message':'Current type set with success.'}
    return Response(content, status=status.HTTP_200_OK)
    # else:
    #     content = {'message':'Only an administrator can use this feature.'}
    #     return Response(content, status=status.HTTP_401_UNAUTHORIZED)
    
    
################################################################################
# 
# Function Name: delete_type(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Delete a type
# 
################################################################################
@api_view(['DELETE'])
@api_staff_member_required()
def delete_type(request):
    """
    GET http://localhost/rest/types/delete?id=IDtodelete&next=IDnextCurrent
    GET http://localhost/rest/types/delete?typeVersion=IDtodelete
    URL parameters: 
    id: string (ObjectId)
    next: string (ObjectId)
    typeVersion: string (ObjectId)
    """
    # if request.user.is_staff is True:
    id = request.QUERY_PARAMS.get('id', None)
    next = request.QUERY_PARAMS.get('next', None)
    versionID = request.QUERY_PARAMS.get('typeVersion', None)

    if versionID is not None:
        if id is not None or next is not None:
            content = {'message':'Wrong parameters combination.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                typeVersion = TypeVersion.objects.get(pk=versionID)
                if typeVersion.isDeleted == False:
                    typeVersion.deletedVersions.append(typeVersion.current)
                    typeVersion.isDeleted = True
                    typeVersion.save()
                    content = {'message':'Type version deleted with success.'}
                    return Response(content, status=status.HTTP_200_OK)
                else:
                    content = {'message':'Type version already deleted.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
            except:
                content = {'message':'No type version found with the given id.'}
                return Response(content, status=status.HTTP_404_NOT_FOUND)

    if id is not None:
        try:
            type = Type.objects.get(pk=id)
        except:
            content = {'message':'No type found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No type id provided to delete.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if next is not None:
        try:
            nextCurrent = Type.objects.get(pk=next)
            if nextCurrent.typeVersion != type.typeVersion:
                content = {'message':'The specified next current type is not a version of the current type.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except:
            content = {'message':'No type found with the given id to be the next current.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

    typeVersion = TypeVersion.objects.get(pk=type.typeVersion)
    if typeVersion.isDeleted == True:
        content = {'message':'This type version belongs to a deleted type. You are not allowed to delete it. please restore the type first (id='+ str(typeVersion.id) +')'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if typeVersion.current == str(type.id) and next is None:
        content = {'message':'The selected type is the current. It can\'t be deleted. If you still want to delete this type, please provide the id of the next current type using \'next\' parameter'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif typeVersion.current == str(type.id) and next is not None and str(type.id) == str(nextCurrent.id):
        content = {'message':'Type id to delete and next id are the same.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif typeVersion.current != str(type.id) and next is not None:
        content = {'message':'You should only provide the next parameter when you want to delete a current version of a type.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif typeVersion.current == str(type.id) and next is not None:
        if next in typeVersion.deletedVersions:
            content = {'message':'The type is deleted, it can\'t become current.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        typeVersion.deletedVersions.append(str(type.id))
        typeVersion.current = str(nextCurrent.id)
        typeVersion.save()
        content = {'message':'Current type deleted with success. A new version is current.'}
        return Response(content, status=status.HTTP_204_NO_CONTENT)
    else:
        if str(type.id) in typeVersion.deletedVersions:
            content = {'message':'This type is already deleted.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        typeVersion.deletedVersions.append(str(type.id))
        typeVersion.save()
        content = {'message':'Type deleted with success.'}
        return Response(content, status=status.HTTP_204_NO_CONTENT)
    # else:
    #     content = {'message':'Only an administrator can use this feature.'}
    #     return Response(content, status=status.HTTP_401_UNAUTHORIZED)
    

################################################################################
# 
# Function Name: restore_type(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Restore a type
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def restore_type(request):
    """
    GET http://localhost/rest/types/restore?id=IDtorestore
    GET http://localhost/rest/types/restore?typeVersion=IDtorestore
    URL parameters: 
    id: string (ObjectId)
    typeVersion: string (ObjectId)
    """
    # if request.user.is_staff is True:
    id = request.QUERY_PARAMS.get('id', None)
    versionID = request.QUERY_PARAMS.get('typeVersion', None)

    if versionID is not None:
        if id is not None:
            content = {'message':'Wrong parameters combination.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                typeVersion = TypeVersion.objects.get(pk=versionID)
                if typeVersion.isDeleted == False:
                    content = {'message':'Type version not deleted. No need to be restored.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                else:
                    typeVersion.isDeleted = False
                    del typeVersion.deletedVersions[typeVersion.deletedVersions.index(typeVersion.current)]
                    typeVersion.save()
                    content = {'message':'Type restored with success.'}
                    return Response(content, status=status.HTTP_200_OK)
            except:
                content = {'message':'No type version found with the given id.'}
                return Response(content, status=status.HTTP_404_NOT_FOUND)

    if id is not None:
        try:
            type = Type.objects.get(pk=id)
        except:
            content = {'message':'No type found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No type id provided to restore.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    typeVersion = TypeVersion.objects.get(pk=type.typeVersion)
    if typeVersion.isDeleted == True:
        content = {'message':'This type version belongs to a deleted type. You are not allowed to restore it. Please restore the type first (id:'+ str(typeVersion.id) +').'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if id in typeVersion.deletedVersions:
        del typeVersion.deletedVersions[typeVersion.deletedVersions.index(id)]
        typeVersion.save()
        content = {'message':'Type version restored with success.'}
        return Response(content, status=status.HTTP_200_OK)
    else:
        content = {'message':'Type version not deleted. No need to be restored.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     content = {'message':'Only an administrator can use this feature.'}
    #     return Response(content, status=status.HTTP_401_UNAUTHORIZED)
    

################################################################################
# 
# Function Name: select_all_repositories(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get all repositories
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def select_all_repositories(request):
    """
    GET http://localhost/rest/repositories/select/all
    """
    instances = Instance.objects
    serializer = instanceSerializer(instances)
    return Response(serializer.data, status=status.HTTP_200_OK)

################################################################################
# 
# Function Name: select_repository(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get repositories that match the parameters
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def select_repository(request):
    """
    GET http://localhost/rest/repositories/select?param1=value1&param2=value2
    URL parameters: 
    id: string (ObjectId)
    name: string
    protocol: string
    address: string
    port: integer
    For string fields, you can use regular expressions: /exp/
    """
    id = request.QUERY_PARAMS.get('id', None)
    name = request.QUERY_PARAMS.get('filename', None)
    protocol = request.QUERY_PARAMS.get('protocol', None)
    address = request.QUERY_PARAMS.get('address', None)
    port = request.QUERY_PARAMS.get('port', None)
    
    try:        
        # create a connection                                                                                                                                                                                                 
        client = MongoClient(MONGODB_URI)
        # connect to the db 'mgi'
        db = client[MGI_DB]
        # get the xmldata collection
        instance = db['instance']
        query = dict()
        if id is not None:            
            query['_id'] = ObjectId(id)            
        if name is not None:
            if len(name) >= 2 and name[0] == '/' and name[-1] == '/':
                query['name'] = re.compile(name[1:-1])
            else:
                query['name'] = name            
        if protocol is not None:
            if len(protocol) >= 2 and protocol[0] == '/' and protocol[-1] == '/':
                query['protocol'] = re.compile(protocol[1:-1])
            else:
                query['protocol'] = protocol
        if address is not None:
            if len(address) >= 2 and address[0] == '/' and address[-1] == '/':
                query['address'] = re.compile(address[1:-1])
            else:
                query['address'] = address
        if port is not None:
            query['port'] = port

        if len(query.keys()) == 0:
            content = {'message':'No parameters given.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            cursor = instance.find(query)
            instances = []
            for resultInstance in cursor:
                resultInstance['id'] = resultInstance['_id']
                del resultInstance['_id']
                instances.append(resultInstance)
            serializer = resInstanceSerializer(instances)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        content = {'message':'No instance found with the given parameters.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

################################################################################
# 
# Function Name: add_repository(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Add a repository
# 
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def add_repository(request):
    """
    POST http://localhost/rest/repositories/add
    POST data name="name", protocol="protocol", address="address", port=port, user="user", password="password", client_id="client_id", client_secret="client_secret"
    """
    # if request.user.is_staff is True:
    iSerializer = newInstanceSerializer(data=request.DATA)
    if iSerializer.is_valid():
        errors = ""
        # test if the protocol is HTTP or HTTPS
        if request.DATA['protocol'].upper() not in ['HTTP','HTTPS']:
            errors += 'Allowed protocol are HTTP and HTTPS.'
        # test if the name is "Local"
        if (request.DATA['name'] == ""):
            errors += "The name cannot be empty."
        elif (request.DATA['name'].upper() == "LOCAL"):
            errors += 'By default, the instance named Local is the instance currently running.'
        else:
            # test if an instance with the same name exists
            instance = Instance.objects(name=request.DATA['name'])
            if len(instance) != 0:
                errors += "An instance with the same name already exists."
        regex = re.compile("^[0-9]{1,5}$")
        if not regex.match(str(request.DATA['port'])):
            errors += "The port number is not valid."
        regex = re.compile("^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        if not regex.match(request.DATA['address']):
            errors += "The address is not valid."
        # test if new instance is not the same as the local instance
        if request.DATA['address'] == request.META['REMOTE_ADDR'] and str(request.DATA['port']) == request.META['SERVER_PORT']:
            errors += "The address and port you entered refer to the instance currently running."
        else:
            # test if an instance with the same address/port exists
            instance = Instance.objects(address=request.DATA['address'], port=request.DATA['port'])
            if len(instance) != 0:
                errors += "An instance with the address/port already exists."

        if errors != "":
            content = {'message': errors}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


        try:
            url = request.DATA["protocol"] + "://" + request.DATA["address"] + ":" + request.DATA["port"] + "/o/token/"
            data="grant_type=password&username=" + request.DATA["user"] + "&password=" + request.DATA["password"]
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            r = requests.post(url=url,data=data, headers=headers,  auth=(request.DATA["client_id"], request.DATA["client_secret"]))
            if r.status_code == 200:
                now = datetime.now()
                delta = timedelta(seconds=int(eval(r.content)["expires_in"]))
                expires = now + delta
                instance = Instance(name=request.DATA["name"], protocol=request.DATA["protocol"], address=request.DATA["address"], port=request.DATA["port"], access_token=eval(r.content)["access_token"], refresh_token=eval(r.content)["refresh_token"], expires=expires).save()
            else:
                errors += "Unable to get access to the remote instance using these parameters."
        except Exception:
            errors += "Unable to get access to the remote instance using these parameters."

        if errors != "":
            content = {'message': errors}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(eval(instance.to_json()), status=status.HTTP_201_CREATED)
    return Response(iSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     content = {'message':'Only an administrator can use this feature.'}
    #     return Response(content, status=status.HTTP_401_UNAUTHORIZED)
################################################################################
# 
# Function Name: delete_repository(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Delete a repository
# 
################################################################################
@api_view(['DELETE'])
@api_staff_member_required()
def delete_repository(request):
    """
    GET http://localhost/rest/repositories/delete?id=IDtodelete
    """
    id = request.QUERY_PARAMS.get('id', None)

    if id is not None:
        try:
            instance = Instance.objects.get(pk=id)
        except:
            content = {'message':'No instance found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No instance id provided to restore.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    instance.delete()
    content = {'message':'Instance deleted with success.'}
    return Response(content, status=status.HTTP_404_NOT_FOUND)

    
################################################################################
# 
# Function Name: select_all_users(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get all users
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def select_all_users(request):
    """
    GET http://localhost/rest/users/select/all
    """
    users = User.objects.all()
    serializer = UserSerializer(users)
    return Response(serializer.data, status=status.HTTP_200_OK)

################################################################################
# 
# Function Name: select_user(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Select users that match parameters
# 
################################################################################
@api_view(['GET'])
@api_staff_member_required()
def select_user(request):
    """
    GET http://localhost/rest/users/select?param1=value1&param2=value2
    URL parameters: 
    username: string
    first_name: string
    last_name: string
    email: string    
    For string fields, you can use regular expressions: /exp/
    """
    username = request.QUERY_PARAMS.get('username', None)
    first_name = request.QUERY_PARAMS.get('first_name', None)
    last_name = request.QUERY_PARAMS.get('last_name', None)
    email = request.QUERY_PARAMS.get('email', None)

    predicates = []
    if username is not None:
        if len(username) >= 2 and username[0] == '/' and username[-1] == '/':
            predicates.append(['username__regex',username[1:-1]])
        else:
            predicates.append(['username',username])
    if first_name is not None:
        if len(first_name) >= 2 and first_name[0] == '/' and first_name[-1] == '/':
            predicates.append(['first_name__regex',first_name[1:-1]])
        else:
            predicates.append(['first_name',first_name])
    if last_name is not None:
        if len(last_name) >= 2 and last_name[0] == '/' and last_name[-1] == '/':
            predicates.append(['last_name__regex',last_name[1:-1]])
        else:
            predicates.append(['last_name',last_name])
    if email is not None:
        if len(email) >= 2 and email[0] == '/' and email[-1] == '/':
            predicates.append(['email__regex',email[1:-1]])
        else:
            predicates.append(['email',email])

    q_list = [Q(x) for x in predicates]
    if len(q_list) != 0:
        try:
            users = User.objects.get(reduce(operator.and_, q_list))
        except:
            users = []
    else:
        users = []
    serializer = UserSerializer(users)
    return Response(serializer.data, status=status.HTTP_200_OK)

################################################################################
# 
# Function Name: add_user(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Add an user to the system
# 
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def add_user(request):
    """
    POST http://localhost/rest/users/add
    POST data username="username", password="password" first_name="first_name", last_name="last_name", port=port, email="email"
    """
    serializer = insertUserSerializer(data=request.DATA)
    if serializer.is_valid():
        username = request.DATA['username']
        password = request.DATA['password']
        if 'first_name' in request.DATA:
            first_name = request.DATA['first_name']
        else:
            first_name = ""
        if 'last_name' in request.DATA:
            last_name = request.DATA['last_name']
        else:
            last_name = ""
        if 'email' in request.DATA:
            email = request.DATA['email']
        else:
            email = ""
        try:
            user = User.objects.create_user(username=username,password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception, e:
            content = {'message':e.message}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


################################################################################
# 
# Function Name: delete_user(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Delete an user
# 
################################################################################
@api_view(['DELETE'])
@api_staff_member_required()
def delete_user(request):
    """
    GET http://localhost/rest/users/delete?username=username
    URL parameters: 
    username: string
    """
    username = request.QUERY_PARAMS.get('username', None)
    if username is not None:
        try:
            user = User.objects.get(username=username)
            user.delete()
            content = {'message':"User deleted with success."}
            return Response(content, status=status.HTTP_200_OK)
        except:
            content = {'message':"The given username does not exist."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':"No username provided."}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


################################################################################
# 
# Function Name: update_user(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Update user's information
# 
################################################################################  
@api_view(['PUT'])
@api_staff_member_required()
def update_user(request):
    """
    PUT http://localhost/rest/users/update?username=userToUpdate
    PUT data first_name="first_name", last_name="last_name", email="email"
    """
    username = request.QUERY_PARAMS.get('username', None)

    if username is not None:
        try:
            user = User.objects.get(username=username)
        except:
            content = {'message':'No user found with the given username.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No username provided to restore.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    serializer = updateUserSerializer(data=request.DATA)
    if serializer.is_valid():
        try:
            if 'first_name' in request.DATA:
                user.first_name = request.DATA['first_name']
            if 'last_name' in request.DATA:
                user.last_name = request.DATA['last_name']
            if 'email' in request.DATA:
                user.email = request.DATA['email']
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception, e:
            content = {'message':e.message}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
################################################################################
# 
# Function Name: docs(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Gives the link to the API documentation
# 
################################################################################
@api_view(['GET'])
def docs(request):
    content={'message':'Invalid command','docs':'http://'+str(request.get_host())+'/docs/api'}
    return Response(content, status=status.HTTP_400_BAD_REQUEST)

################################################################################
# 
# Function Name: ping(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Ping the API
# 
################################################################################
@api_view(['GET'])
def ping(request):
    content={'message':'Endpoint reached'}
    return Response(content, status=status.HTTP_200_OK)


################################################################################
# 
# Function Name: get_dependency(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get a template dependency using its mongodb id
# 
################################################################################   
@api_view(['GET'])
def get_dependency(request):
    """
    GET http://localhost/rest/types/get-dependency?id=id
    """  
    # TODO: can change to the hash
    id = request.QUERY_PARAMS.get('id', None)
    
    if id is None:
        content={'message':'No dependency id provided.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            try:
                type = Type.objects.get(pk=str(id))
                content = type.content
            except:
                template = Template.objects.get(pk=str(id))
                content = template.content
            
            xsdEncoded = content.encode('utf-8')
            fileObj = StringIO(xsdEncoded)
            response = HttpResponse(fileObj, content_type='application/xml')
            response['Content-Disposition'] = 'attachment; filename=' + str(id)
            return response
        except: 
            content={'message':'No dependency could be found with the given id.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


################################################################################
# 
# Function Name: blob(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Get a file from its handle
# 
################################################################################   
@api_view(['GET', 'POST'])
def blob(request):
    """
    GET    http://localhost/rest/blob?id=id
    
    POST   http://localhost/rest/blob
    POST data: {'blob': FILE}
    """  
    
    if request.method == 'GET':
        blob_id = request.QUERY_PARAMS.get('id', None)
        if blob_id is None:
            content={'message':'No id provided.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                bh_factory = BLOBHosterFactory(BLOB_HOSTER, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD, MDCS_URI)
                blob_hoster = bh_factory.createBLOBHoster()
                try:
                    blob = blob_hoster.get(request.get_full_path())
                    response = HttpResponse(blob, content_type=guess_type(blob.filename))
                    response['Content-Disposition'] = 'attachment; filename=' + str(blob.filename)
                    return response
                except:
                    content={'message':'No file could be found with the given id.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)                            
            except: 
                content={'message':'No file could be found with the given id.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':
        try:
            blob = request.FILES.get('blob')
            try:        
                bh_factory = BLOBHosterFactory(BLOB_HOSTER, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD, MDCS_URI)
                blob_hoster = bh_factory.createBLOBHoster()
                try:
                    handle = blob_hoster.save(blob=blob, filename=blob.name, userid=str(request.user.id))
                    content={'handle': handle}
                    return Response(content, status=status.HTTP_201_CREATED)
                except:
                    content={'message':'Something went wrong with BLOB upload.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
            except:
                content={'message':'Something went wrong with BLOB Hoster Initialization. Please check the settings.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except:
            content={'message':'blob parameter not found'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
    
    
        
################################################################################
#
# Function Name: select_all_exporters(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Get all exporters
#
################################################################################
@api_view(['GET'])
@api_permission_required(RIGHTS.explore_content_type, RIGHTS.explore_access)
def select_all_exporters(request):
    """
    GET http://localhost/rest/exporter/select/all
    """
    exporters = Exporter.objects(name__ne='XSLT')
    serializer = exporterSerializer(exporters)
    exporters = ExporterXslt.objects
    serializerXSLT = exporterXSLTSerializer(exporters)

    data = serializer.data + serializerXSLT.data
    return Response(data, status=status.HTTP_200_OK)


################################################################################
#
# Function Name: select_exporter(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Get exporter that match the parameters
#
################################################################################
@api_view(['GET'])
@api_permission_required(RIGHTS.explore_content_type, RIGHTS.explore_access)
def select_exporter(request):
    """
    GET http://localhost/rest/exporter/select?param1=value1&amp;param2=value2
    URL parameters:
    id: string (ObjectId)
    name: string

    For string fields, you can use regular expressions: /exp/
    """
    id = request.QUERY_PARAMS.get('id', None)
    name = request.QUERY_PARAMS.get('name', None)

    try:
        query = dict()
        if id is not None:
            query['id'] = ObjectId(id)
        if name is not None:
            if len(name) >= 2 and name[0] == '/' and name[-1] == '/':
                query['name'] = re.compile(name[1:-1])
            else:
                query['name'] = name

        q_list = {Q(**({key:value})) for key, value in query.iteritems()}
        if len(q_list) > 0:
            try:
                exporters = Exporter.objects(name__ne='XSLT').filter(reduce(operator.and_, q_list))
                exportersXSLT = ExporterXslt.objects.filter(reduce(operator.and_, q_list))
                if len(exporters) == 0 and len(exportersXSLT) == 0:
                    raise
            except:
                content = {'message':'No exporter found with the given parameters.'}
                return Response(content, status=status.HTTP_404_NOT_FOUND)
        else:
           content = {'message':'No parameters given.'}
           return Response(content, status=status.HTTP_400_BAD_REQUEST)


        serializer = exporterSerializer(exporters)
        serializerXSLT = exporterXSLTSerializer(exportersXSLT)
        data = serializer.data + serializerXSLT.data

        return Response(data, status=status.HTTP_200_OK)
    except Exception, e:
        content = {'message':'No exporter found with the given parameters.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)



################################################################################
#
# Function Name: add_xslt(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Add a xslt
#
################################################################################
@api_view(['POST'])
@api_staff_member_required()
def add_xslt(request):
    """
    POST http://localhost/rest/exporter/xslt/add
    POST data name="name", filename="filename", content="...", available_for_all="True or False"
    """
    serializer = jsonXSLTSerializer(data=request.DATA)
    if serializer.is_valid():
        xmlStr = request.DATA['content']
        try:
            try:
                etree.XML(xmlStr.encode('utf-8'))
            except Exception, e:
                content = {'message':e.message}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            try:
                available = request.DATA['available_for_all'] == 'True'
                jsondata = ExporterXslt(name=request.DATA['name'], filename=request.DATA['filename'], content=request.DATA['content'], available_for_all=available)
                docID = jsondata.save()
                #IF it's available for all templates, we add the reference for all templates using the XSLT exporter
                if available:
                    xslt_exporter = None
                    try:
                        xslt_exporter = Exporter.objects.get(name='XSLT')
                    except:
                        None

                    if xslt_exporter != None:
                        Template.objects(exporters__all=[xslt_exporter]).update(push__XSLTFiles=docID)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except NotUniqueError, e:
                content = {'message: This XSLT name already exists. Please enter an other name.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except:
            if docID is not None:
                jsondata.delete(docID)
            content = {'message: Unable to insert XSLT.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

################################################################################
#
# Function Name: delete_xslt(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Delete a xslt
#
################################################################################
@api_view(['DELETE'])
@api_staff_member_required()
def delete_xslt(request):
    """
    GET http://localhost/rest/exporter/xslt/delete?id=id
    URL parameters:
    id: string
    """
    id = request.QUERY_PARAMS.get('id', None)
    if id is not None:
        try:
            xslt = ExporterXslt.objects.get(pk=id)
            xslt.delete()
            content = {'message':"XSLT deleted with success."}
            return Response(content, status=status.HTTP_200_OK)
        except:
            content = {'message':"No XSLT found with the given id."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':"No id provided."}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

################################################################################
#
# Function Name: export(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   export an XML document: save the data in MongoDB and Jena
#
################################################################################
@api_view(['POST'])
@api_permission_required(RIGHTS.explore_content_type, RIGHTS.explore_access)
def export(request):
    """
    POST http://localhost/rest/exporter/export
    POST data files[]="fileID,fileID,...", exporter="exporterID", dataformat: [json,zip]
    """
    dataXML = []
    serializer = jsonExportSerializer(data=request.DATA)
    if serializer.is_valid():
        #We retrieve files to export
        try:
            files = []
            filesId = re.sub('[\s+]', '', request.DATA['files[]']).split(",")
            idExporter = request.DATA['exporter']
            if "dataformat" in request.DATA:
                dataformat = request.DATA['dataformat']
            else:
                dataformat =  None
            for fileId in filesId:
                fileTmp = file = XMLdata.get(fileId)
                if file == None:
                    content = {'message: No file found with the given id: ' + fileId}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                else:
                    files.append(fileTmp)
            #We retrieve the good exporter
            #Standard exporter
            try:
                exporter = Exporter.objects.get(pk=idExporter)
                exporter = get_exporter(exporter.url)
            except MONGO_ERRORS.DoesNotExist, e:
                #Exporter not found in standard exporters collection.
                #XSLT exporter
                try:
                    xslt = ExporterXslt.objects.get(pk=idExporter)
                    exporter = XSLTExporter(xslt.content)
                except MONGO_ERRORS.DoesNotExist, e:
                    content = {'message: No exporter found with the given id.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

            #Retrieve the XML content
            for file in files:
                xmlStr = XMLdata.unparse(file['content'])
                dataXML.append({'title':file['title'], 'content': str(xmlStr)})

            #Transformation
            if dataformat== None or dataformat=="json":
                try:
                    contentRes = exporter._transform(dataXML)
                    serializerBis = jsonExportResSerializer(contentRes)
                    response = Response(serializerBis.data, status=status.HTTP_200_OK)
                except:
                    content = {'message' : 'Unable to export data in JSON. Could be a format issue'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
            elif dataformat=="zip":
                in_memory = StringIO()
                zip = zipfile.ZipFile(in_memory, "a")
                exporter._transformAndZip(None, dataXML, zip)
                zip.close()
                #ZIP file to be downloaded
                in_memory.seek(0)
                response = HttpResponse(in_memory.read())
                response["Content-Disposition"] = "attachment; filename=Results.zip"
                response['Content-Type'] = 'application/x-zip'
            else:
                content = {'message':'The specified format is not accepted.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            return response
        except Exporter, e:
            content = {'message: Unable to export data.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
