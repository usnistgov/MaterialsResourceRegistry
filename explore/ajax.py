################################################################################
#
# File Name: ajax.py
# Application: explore
# Purpose:   AJAX methods used for Explore purposes
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume Sousa Amaral
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from django.http import HttpResponse
from django.conf import settings
from io import BytesIO
from django.template.context import Context
from lxml import html
from collections import OrderedDict
import requests
import os
import json
import copy
import lxml.etree as etree
import re
from oai_pmh.explore import ajax as OAIExplore
from mgi.common import LXML_SCHEMA_NAMESPACE
from curate.models import SchemaElement
from explore.models import CustomTemplate
from mgi import common
from mgi.common import SCHEMA_NAMESPACE, xpath_to_dot_notation
from mgi.models import Template, SavedQuery, XMLdata, Instance, TemplateVersion
from django.template import loader, RequestContext
from django.contrib import messages
from utils.XSDParser.parser import generate_form
from utils.XSDParser.renderer import DefaultRenderer
from utils.XSDParser.renderer.checkbox import CheckboxRenderer


# Class definition
class ElementInfo:
    """
    Store information about element from the XML schema
    """
    def __init__(self, type="", path=""):
        self.type = type
        self.path = path
    
    def __to_json__(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class CriteriaInfo:
    """
    Store information about a criteria from the query builder
    """
    def __init__(self, elementInfo=None, queryInfo=None):
        self.elementInfo = elementInfo
        self.queryInfo = queryInfo
    
    def __to_json__(self):
        jsonDict = dict()
        if self.elementInfo == None:
            jsonDict["elementInfo"] = None
        else:
            jsonDict["elementInfo"] = self.elementInfo.__to_json__()
        if self.queryInfo == None:
            jsonDict["queryInfo"] = None
        else:
            jsonDict["queryInfo"] = self.queryInfo.__to_json__()
        return json.dumps(jsonDict)


class QueryInfo:
    """
    Store information about a query
    """
    def __init__(self, query="", displayedQuery=""):
        self.query = query
        self.displayedQuery = displayedQuery

    def __to_json__(self):        
        return json.dumps(self, default=lambda o: o.__dict__)
 

class BranchInfo:
    """
    Store information about a branch from the xml schema while it is being processed for customization
    """
    def __init__(self, keepTheBranch, selectedLeave):
        self.keepTheBranch = keepTheBranch
        self.selectedLeave = selectedLeave


################################################################################
# 
# Function Name: set_current_template(request):
# Inputs:        request - 
# Outputs:       JSON data with success or failure
# Exceptions:    None
# Description:   Set the current template to input argument.  Template is read into
#                an xsdDocTree for use later.
#
################################################################################
def set_current_template(request):
    print 'BEGIN def setCurrentTemplate(request)'    

    template_id = request.POST['templateID']

    setCurrentTemplate(request, template_id)

    print 'END def setCurrentTemplate(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: setCurrentTemplate(request):
# Inputs:        request - 
#                template_filename - name of the template
#                template_id - id of the template
# Outputs:       
# Exceptions:    None
# Description:   Set the current template to input argument.  Template is read into
#                an xsdDocTree for use later.
#
################################################################################
def setCurrentTemplate(request, template_id):
    print 'BEGIN def setCurrentTemplate(request)'    

    # reset global variables
    request.session['formStringExplore'] = ""
    request.session['customFormStringExplore'] = ""

    request.session['exploreCurrentTemplateID'] = template_id
    request.session.modified = True

    templateObject = Template.objects.get(pk=template_id)
    xmlDocData = templateObject.content

    XMLtree = etree.parse(BytesIO(xmlDocData.encode('utf-8')))
    request.session['xmlDocTreeExplore'] = etree.tostring(XMLtree)

    print 'END def setCurrentTemplate(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: set_current_user_template(request,):
# Inputs:        request - 
# Outputs:       JSON data with success or failure
# Exceptions:    None
# Description:   Set the current template to input argument.  Template is read into
#                an xsdDocTree for use later.
#
################################################################################
def set_current_user_template(request):
    print 'BEGIN def setCurrentTemplate(request)'    

    template_id = request.POST['templateID']
    
    # reset global variables
    request.session['formStringExplore'] = ""
    request.session['customFormStringExplore'] = ""
        
    request.session['exploreCurrentTemplateID'] = template_id
    request.session.modified = True

    templateObject = Template.objects.get(pk=template_id)

    xmlDocData = templateObject.content

    XMLtree = etree.parse(BytesIO(xmlDocData.encode('utf-8')))
    request.session['xmlDocTreeExplore'] = etree.tostring(XMLtree)

    print 'END def setCurrentTemplate(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: verify_template_is_selected(request)
# Inputs:        request - 
# Outputs:       JSON data with templateSelected 
# Exceptions:    None
# Description:   Verifies the current template is selected.
# 
################################################################################
def verify_template_is_selected(request):
    print 'BEGIN def verifyTemplateIsSelected(request)'
    if 'exploreCurrentTemplateID' in request.session:
        templateSelected = 'yes'
    else:
        templateSelected = 'no'

    print 'END def verifyTemplateIsSelected(request)'
    
    response_dict = {'templateSelected': templateSelected}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


def load_config():
    """
    Load Configuration for the parser
    :return:
    """
    return {
        'PARSER_APPLICATION': 'EXPLORE',
        'PARSER_MIN_TREE': False,
        'PARSER_IGNORE_MODULES': True,
        'PARSER_COLLAPSE': False,
        'PARSER_AUTO_KEY_KEYREF': False,
        'PARSER_IMPLICIT_EXTENSION_BASE': False,
    }


################################################################################
# 
# Function Name: generate_xsd_tree_for_querying_data(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Generate an HTML tree from the XSD to select the fields being used in the query
#
################################################################################
def generate_xsd_tree_for_querying_data(request): 
    print 'BEGIN def generateXSDTreeForQueryingData(request)'

    if 'formStringExplore' in request.session:
        formString = request.session['formStringExplore']
    else:
        formString = ''
    if 'xmlDocTreeExplore' in request.session:
        xmlDocTreeStr = request.session['xmlDocTreeExplore'] 
    else:
        xmlDocTreeStr = ""
    
    templateID = request.session['exploreCurrentTemplateID']
    
    # get the namespaces of the schema and the default prefix
    xmlDocTree = etree.fromstring(xmlDocTreeStr)

    for prefix, url in xmlDocTree.nsmap.iteritems():
        if url == SCHEMA_NAMESPACE:
            request.session['defaultPrefixExplore'] = prefix
            break
    
    if xmlDocTreeStr == "":
        setCurrentTemplate(request, templateID)        

    if formString == "":
        try:
            # custom template already exists
            try:
                custom_template = CustomTemplate.objects.get(user=str(request.user.id), template=templateID)
                root_element_id = custom_template.root.id
            # custom template doesn't exist
            except:
                root_element_id = generate_form(request, xmlDocTreeStr, config=load_config())
                custom_template = CustomTemplate(user=str(request.user.id), template=templateID, root=root_element_id).save()

            root_element = SchemaElement.objects.get(pk=root_element_id)
            renderer = CheckboxRenderer(root_element, request)
            html_form = renderer.render()

            formString = "<form id=\"dataQueryForm\" name=\"xsdForm\">"
            formString += html_form
            formString += "</form>"
        except Exception as e:
            renderer = DefaultRenderer(None, {})
            formString = renderer._render_form_error(e.message)

    print 'END def generateXSDTreeForQueryingData(request)'
    response_dict = {'xsdForm': formString}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: execute_query(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   execute a query in Mongo db
#
################################################################################
def execute_query(request):
    print 'BEGIN def executeQuery(request)'        
    
    query_form = request.POST['queryForm']
    fed_of_queries = request.POST['fedOfQueries']
    
    request.session['savedQueryFormExplore'] = query_form    
    
    response_dict = {}
    queryFormTree = html.fromstring(query_form)
    errors = checkQueryForm(request, queryFormTree)
    if len(errors) == 0:
        instances = getInstances(request, fed_of_queries)
        if len(instances) == 0:
            response_dict = {'errors': 'zero'}
        else:
            htmlTree = html.fromstring(query_form)
            query = fieldsToQuery(request, htmlTree)            
            request.session['queryExplore'] = query
            json_instances = []
            for instance in instances:
                json_instances.append(instance.to_json()) 
            request.session['instancesExplore'] = json_instances
    else:
        errorsString = ""
        for error in errors:
            errorsString += "<p>" + error + "</p>"    
        response_dict = {'listErrors': errorsString}        

    print 'END def executeQuery(request, queryForm, queryBuilder, fedOfQueries)'
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: getInstances(request, fedOfQueries)
# Inputs:        request -
#                fedOfQueries - html list of repositories
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Get the selected instances from the the repositories section
#
################################################################################
def getInstances(request, fedOfQueries):
    
    instances = []
    fedOfQueriesTree = html.fromstring(fedOfQueries)    
    instancesCheckboxes = fedOfQueriesTree.findall(".//input[@type='checkbox']")
    
    for checkbox in instancesCheckboxes:
        if 'checked' in checkbox.attrib:
            if checkbox.attrib['value'] == "Local":
                if 'HTTPS' in request.META['SERVER_PROTOCOL']:
                    protocol = "https"
                else:
                    protocol = "http"
                instances.append(Instance(name="Local", protocol=protocol,
                                          address=request.META['REMOTE_ADDR'],
                                          port=request.META['SERVER_PORT'],
                                          access_token="token",
                                          refresh_token="token"))
            else:
                instances.append(Instance.objects.get(name=checkbox.attrib['value']))
    
    return instances  


################################################################################
# 
# Function Name: get_results(request)
# Inputs:        request -
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Get the results of a query
#
################################################################################
def get_results(request):
    instances = request.session['instancesExplore']    
    response_dict = {'numInstance': str(len(instances))}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: getResults(query)
# Inputs:        query -
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Transform the query to get rid of Regex object 
#
################################################################################
def manageRegexBeforeExe(query):
    for key, value in query.iteritems():
        if key == "$and" or key == "$or":
            for subValue in value:
                manageRegexBeforeExe(subValue)
        elif isinstance(value, unicode) or isinstance(value, str):
            if len(value) >= 2 and value[0] == "/" and value[-1] == "/":
                query[key] = re.compile(value[1:-1])
        elif isinstance(value, dict):
            manageRegexBeforeExe(value)


################################################################################
#
# Function Name: get_results_by_instance_keyword(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Get results of a query for a specific keyword
#
################################################################################
def get_results_by_instance_keyword(request):
    print 'BEGIN def getResultsKeyword(request)'
    resultsByKeyword = []
    results = []
    resultString = ""

    #Instance
    json_instances = []
    if 'HTTPS' in request.META['SERVER_PROTOCOL']:
        protocol = "https"
    else:
        protocol = "http"
    instance = Instance(name="Local",
                        protocol=protocol,
                        address=request.META['REMOTE_ADDR'],
                        port=request.META['SERVER_PORT'],
                        access_token="token",
                        refresh_token="token")
    json_instances.append(instance.to_json())
    request.session['instancesExplore'] = json_instances
    sessionName = "resultsExplore" + instance['name']


    try:
        keyword = request.GET['keyword']
        schemas = request.GET.getlist('schemas[]')
        userSchemas = request.GET.getlist('userSchemas[]')
        refinements = refinements_to_mongo(request.GET.getlist('refinements[]'))
        onlySuggestions = json.loads(request.GET['onlySuggestions'])
    except:
        keyword = ''
        schemas = []
        userSchemas = []
        refinements = {}
        onlySuggestions = True

    #We get all template versions for the given schemas
    #First, we take care of user defined schema
    templatesIDUser = Template.objects(title__in=userSchemas).distinct(field="id")
    templatesIDUser = [str(x) for x in templatesIDUser]

    #Take care of the rest, with versions
    templatesVersions = Template.objects(title__in=schemas).distinct(field="templateVersion")

    #We get all templates ID, for all versions
    allTemplatesIDCommon = TemplateVersion.objects(pk__in=templatesVersions, isDeleted=False).distinct(field="versions")
    #We remove the removed version
    allTemplatesIDCommonRemoved = TemplateVersion.objects(pk__in=templatesVersions, isDeleted=False).distinct(field="deletedVersions")
    templatesIDCommon = list(set(allTemplatesIDCommon) - set(allTemplatesIDCommonRemoved))

    templatesID = templatesIDUser + templatesIDCommon
    instanceResults = XMLdata.executeFullTextQuery(keyword, templatesID, refinements)
    if len(instanceResults) > 0:
        if not onlySuggestions:
            xsltPath = os.path.join(settings.SITE_ROOT, 'static/resources/xsl/xml2html.xsl')
            xslt = etree.parse(xsltPath)
            transform = etree.XSLT(xslt)
            template = loader.get_template('explore/explore_result_keyword.html')

        for instanceResult in instanceResults:
            if not onlySuggestions:
                custom_xslt = False
                results.append({'title': instanceResult['title'],
                                'content': XMLdata.unparse(instanceResult['content']),
                                'id': str(instanceResult['_id'])})
                dom = etree.XML(str(XMLdata.unparse(instanceResult['content']).encode('utf-8')))
                #Check if a custom list result XSLT has to be used
                try:
                    schema = Template.objects.get(pk=instanceResult['schema'])
                    if schema.ResultXsltList:
                        listXslt = etree.parse(BytesIO(schema.ResultXsltList.content.encode('utf-8')))
                        listTransform = etree.XSLT(listXslt)
                        newdom = listTransform(dom)
                        custom_xslt = True
                    else:
                        newdom = transform(dom)
                except Exception, e:
                    #We use the default one
                    newdom = transform(dom)
                    custom_xslt = False

                context = RequestContext(request, {'id': str(instanceResult['_id']),
                                                   'xml': str(newdom),
                                                   'title': instanceResult['title'],
                                                   'custom_xslt': custom_xslt,
                                                   'template_name': schema.title})

                resultString += template.render(context)
            else:
                wordList = re.sub("[^\w]", " ",  keyword).split()
                wordList = [x + "|" + x + "\w+" for x in wordList]
                wordList = '|'.join(wordList)
                listWholeKeywords = re.findall("\\b(" + wordList + ")\\b", XMLdata.unparse(instanceResult['content']).encode('utf-8'), flags=re.IGNORECASE)
                labels = list(set(listWholeKeywords))

                for label in labels:
                    label = label.lower()
                    result_json = {}
                    result_json['label'] = label
                    result_json['value'] = label
                    if not result_json in resultsByKeyword:
                        resultsByKeyword.append(result_json)

        result_json = {}
        result_json['resultString'] = resultString

    request.session[sessionName] = results

    #Call to OAI-PMH keyword search
    nbOAI = 0
    try:
        dumpJson = OAIExplore.get_results_by_instance_keyword(request)
        info = json.loads(dumpJson)
        resultsByKeyword.append(info['resultsByKeyword'])
        resultString = resultString + info['resultString']
        nbOAI = info['count']
    except Exception, e:
        pass

    print 'END def getResultsKeyword(request)'

    return HttpResponse(json.dumps({'resultsByKeyword' : resultsByKeyword, 'resultString' : resultString, 'count' : len(instanceResults) + nbOAI}), content_type='application/javascript')


################################################################################
# 
# Function Name: get_results_by_instance(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Get results of a query for a specific instance (Local or others)
#
################################################################################
def get_results_by_instance(request):
    print 'BEGIN def getResults(request)'
    num_instance = request.GET['numInstance']
    instances = request.session['instancesExplore']
    resultString = ""

    for i in range(int(num_instance)):
        results = []
        instance = json.loads(instances[int(i)])
        sessionName = "resultsExplore" + instance['name']
        resultString += "<p style='font-weight:bold; color:#369;'>From " + instance['name'] + ":</p>"
        if instance['name'] == "Local":
            query = copy.deepcopy(request.session['queryExplore'])
            manageRegexBeforeExe(query)
            
            selected_template_id = request.session['exploreCurrentTemplateID']
            template = Template.objects().get(pk=selected_template_id)
            
            # template is user defined
            if template.user is not None:
                # update the query
                query.update({'schema': str(selected_template_id)})
            else:
                # template is global
                template_version_id = template.templateVersion
                # get version manager
                template_version = TemplateVersion.objects().get(pk=template_version_id)
                # get all versions, not deleted
                versions = [version for version in template_version.versions if version not in template_version.deletedVersions]
                # update the query
                query.update({'schema': {'$in': versions}})
            
            instanceResults = XMLdata.executeQueryFullResult(query)

            if len(instanceResults) > 0:
                template = loader.get_template('explore/explore_result.html')
                xsltPath = os.path.join(settings.SITE_ROOT, 'static/resources/xsl/xml2html.xsl')
                xslt = etree.parse(xsltPath)
                transform = etree.XSLT(xslt)
                for instanceResult in instanceResults:
                    custom_xslt = False
                    results.append({'title': instanceResult['title'],
                                    'content': XMLdata.unparse(instanceResult['content']),
                                    'id': str(instanceResult['_id'])})
                    #dom = etree.fromstring(str(xmltodict.unparse(instanceResult['content']).replace('<?xml version="1.0" encoding="utf-8"?>\n',"")))
                    dom = etree.XML(str(XMLdata.unparse(instanceResult['content']).encode('utf-8')))
                    #Check if a custom list result XSLT has to be used
                    try:
                        schema = Template.objects.get(pk=instanceResult['schema'])
                        if schema.ResultXsltList:
                            listXslt = etree.parse(BytesIO(schema.ResultXsltList.content.encode('utf-8')))
                            listTransform = etree.XSLT(listXslt)
                            newdom = listTransform(dom)
                            custom_xslt = True
                        else:
                            newdom = transform(dom)
                    except Exception, e:
                        #We use the default one
                        newdom = transform(dom)
                        custom_xslt = False

                    context = RequestContext(request, {'id':str(instanceResult['_id']),
                                               'xml': str(newdom),
                                               'title': instanceResult['title'],
                                               'custom_xslt': custom_xslt,
                                               'template_name': schema.title})

                    resultString+= template.render(context)

                resultString += "<br/>"
            else:
                resultString += "<span style='font-style:italic; color:red;'> No Results found... </span><br/><br/>"

        else:
            url = instance['protocol'] + "://" + instance['address'] + ":" + str(instance['port']) + "/rest/explore/query-by-example"
            query = copy.deepcopy(request.session['queryExplore'])
            data = {"query":str(query)}
            headers = {'Authorization': 'Bearer ' + instance['access_token']}
            r = requests.post(url, data=data, headers=headers)   
            result = r.text
            instanceResults = json.loads(result,object_pairs_hook=OrderedDict)
            if len(instanceResults) > 0:
                template = loader.get_template('explore_result.html')
                xsltPath = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'xml2html.xsl')
                xslt = etree.parse(xsltPath)
                transform = etree.XSLT(xslt)
                for instanceResult in instanceResults:
                    custom_xslt = False
                    results.append({'title':instanceResult['title'], 'content':instanceResult['content'],'id':str(instanceResult['_id'])})
                    dom = etree.XML(str(XMLdata.unparse(instanceResult['content']).encode('utf-8')))
                    #Check if a custom list result XSLT has to be used
                    try:
                        schema = Template.objects.get(pk=instanceResult['schema'])
                        if schema.ResultXsltList:
                            listXslt = etree.parse(BytesIO(schema.ResultXsltList.content.encode('utf-8')))
                            listTransform = etree.XSLT(listXslt)
                            newdom = listTransform(dom)
                            custom_xslt = True
                        else:
                            newdom = transform(dom)
                    except Exception, e:
                        #We use the default one
                        newdom = transform(dom)
                        custom_xslt = False

                    context = RequestContext(request, {'id': str(instanceResult['_id']),
                                                       'xml': str(newdom),
                                                       'title': instanceResult['title'],
                                                       'custom_xslt': custom_xslt})

                    resultString += template.render(context)
                resultString += "<br/>"
            else:
                resultString += "<span style='font-style:italic; color:red;'> No Results found... </span><br/><br/>"
            
        request.session[sessionName] = results
    
    print 'END def getResults(request)'
    response_dict = {'results': resultString}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
 
 
################################################################################
# 
# Function Name: manageRegexBeforeAPI(query, queryStr)
# Inputs:        query - 
#                queryStr -
# Outputs:       
# Exceptions:    None
# Description:   Can't do a deep copy of a dictionary containing pattern objects (deepcopy bug).
#                This function is no longer in use
#
################################################################################
def manageRegexBeforeAPI(query, queryStr):
    for key, value in query.iteritems():
        if key == "$and" or key == "$or":
            for subValue in value:
                queryStr = manageRegexBeforeAPI(subValue, queryStr)
        elif isinstance(value, re._pattern_type):
            queryStr = queryStr.replace(str(value), "'/" + str(value.pattern) + "/'")
        elif isinstance(value, dict):
            queryStr = manageRegexBeforeAPI(value, queryStr)
    return queryStr


################################################################################
# 
# Function Name: intCriteria(path, comparison, value, isNot=False)
# Inputs:        path - 
#                comparison -
#                value -
#                isNot -
# Outputs:       a criteria
# Exceptions:    None
# Description:   Build a criteria for mongo db for the type integer
#
################################################################################
def intCriteria(path, comparison, value):
    criteria = dict()

    if comparison == "=":
        criteria[path] = int(value)
    else:
        criteria[path] = json.loads('{{"${0}": {1} }}'.format(comparison, value))

    return criteria


################################################################################
# 
# Function Name: floatCriteria(path, comparison, value, isNot=False)
# Inputs:        path - 
#                comparison -
#                value -
# Outputs:       a criteria
# Exceptions:    None
# Description:   Build a criteria for mongo db for the type float
#
################################################################################
def floatCriteria(path, comparison, value):
    criteria = dict()

    if comparison == "=":
        criteria[path] = float(value)
    else:
        criteria[path] = json.loads('{{"${0}": {1} }}'.format(comparison, value))

    return criteria


################################################################################
# 
# Function Name: stringCriteria(path, comparison, value)
# Inputs:        path - 
#                comparison -
#                value -
# Outputs:       a criteria
# Exceptions:    None
# Description:   Build a criteria for mongo db for the type string
#
################################################################################
def stringCriteria(path, comparison, value):
    criteria = dict()
    
    if comparison == "is":
        criteria[path] = value
    elif comparison == "like":
        criteria[path] = "/" + value + "/"
    
    return criteria


################################################################################
# 
# Function Name: queryToCriteria(query, isNot=False)
# Inputs:        query -
#                isNot -
# Outputs:       a criteria
# Exceptions:    None
# Description:   Build a criteria for mongo db for a query
#
################################################################################
def queryToCriteria(query, isNot=False):
    if isNot:
        return invertQuery(query.copy())
    else:
        return query


################################################################################
# 
# Function Name: invertQuery(query)
# Inputs:        query - 
# Outputs:       
# Exceptions:    None
# Description:   Invert each field of the query to build NOT(query)
#
################################################################################
def invertQuery(query):
    for key, value in query.iteritems():
        if key == "$and" or key == "$or":
            # invert the query for the case value can be found at element:value or at element.#text:value
            # second case appends when the element has attributes or namespace information
            if len(value) == 2 and len(value[0].keys()) == 1 and len(value[1].keys()) == 1 and \
                            value[1].keys()[0] == "{}.#text".format(value[0].keys()[0]):
                # second query is the same as the first
                if key == "$and":
                    return {"$or": [invertQuery(value[0]), invertQuery(value[1])]}
                elif key == "$or":
                    return {"$and": [invertQuery(value[0]), invertQuery(value[1])]}
            for sub_value in value:
                invertQuery(sub_value)
        else:            
            # lt, lte, =, gte, gt, not, ne
            if isinstance(value, dict):
                if value.keys()[0] == "$not" or value.keys()[0] == "$ne":
                    query[key] = (value[value.keys()[0]])                    
                else:
                    saved_value = value
                    query[key] = dict()
                    query[key]["$not"] = saved_value
            else:
                saved_value = value
                if is_regex_expression(value):
                    query[key] = dict()
                    query[key]["$not"] = saved_value
                else:
                    query[key] = dict()
                    query[key]["$ne"] = saved_value
    return query


def is_regex_expression(expr):
    """
    Looks if the expression is a regular expression
    :param expr
    """
    if isinstance(expr, re._pattern_type):
        return True
    try:
        if expr.startswith('/') and expr.endswith('/'):
            return True
        else:
            return False
    except:
        return False


################################################################################
# 
# Function Name: enumCriteria(path, value, isNot=False)
# Inputs:        path -
#                value -
#                isNot -
# Outputs:       criteria
# Exceptions:    None
# Description:   Build a criteria for mongo db for an enumeration
#
################################################################################
def enumCriteria(path, value, isNot=False):
    criteria = dict()
    
    if isNot:
        criteria[path] = json.loads('{{"ne": "{0}" }}'.format(repr(value)))
    else:
        criteria[path] = value
            
    return criteria


################################################################################
# 
# Function Name: ANDCriteria(criteria1, criteria2)
# Inputs:        criteria1 -
#                criteria2 -
# Outputs:       criteria
# Exceptions:    None
# Description:   Build a criteria that is the result of criteria1 and criteria2
#
################################################################################
def ANDCriteria(criteria1, criteria2):
    ANDcriteria = dict()
    ANDcriteria["$and"] = []
    ANDcriteria["$and"].append(criteria1)
    ANDcriteria["$and"].append(criteria2)
    return ANDcriteria


################################################################################
# 
# Function Name: ORCriteria(criteria1, criteria2)
# Inputs:        criteria1 -
#                criteria2 -
# Outputs:       criteria
# Exceptions:    None
# Description:   Build a criteria that is the result of criteria1 or criteria2
#
################################################################################
def ORCriteria(criteria1, criteria2):
    ORcriteria = dict()
    ORcriteria["$or"] = []
    ORcriteria["$or"].append(criteria1)
    ORcriteria["$or"].append(criteria2)
    return ORcriteria


################################################################################
# 
# Function Name: build_criteria(elemPath, comparison, value, elemType, isNot=False)
# Inputs:        elemPath -
#                comparison -
#                value -
#                elemType - 
#                isNot - 
# Outputs:       criteria
# Exceptions:    None
# Description:   Look at element type and route to the right function to build the criteria
#
################################################################################
def build_criteria(element_path, comparison, value, element_type, default_prefix, isNot=False):
    # build the query: value can be found at element:value or at element.#text:value
    # second case appends when the element has attributes or namespace information
    if (element_type in ['{0}:byte'.format(default_prefix),
                         '{0}:int'.format(default_prefix),
                         '{0}:integer'.format(default_prefix),
                         '{0}:long'.format(default_prefix),
                         '{0}:negativeInteger'.format(default_prefix),
                         '{0}:nonNegativeInteger'.format(default_prefix),
                         '{0}:nonPositiveInteger'.format(default_prefix),
                         '{0}:positiveInteger'.format(default_prefix),
                         '{0}:short'.format(default_prefix),
                         '{0}:unsignedLong'.format(default_prefix),
                         '{0}:unsignedInt'.format(default_prefix),
                         '{0}:unsignedShort'.format(default_prefix),
                         '{0}:unsignedByte'.format(default_prefix)]):
        element_query = intCriteria(element_path, comparison, value)
        attribute_query = intCriteria("{}.#text".format(element_path), comparison, value)
    elif (element_type in ['{0}:float'.format(default_prefix),
                           '{0}:double'.format(default_prefix),
                           '{0}:decimal'.format(default_prefix)]):
        element_query = floatCriteria(element_path, comparison, value)
        attribute_query = floatCriteria("{}.#text".format(element_path), comparison, value)
    elif element_type == '{0}:string'.format(default_prefix):
        element_query = stringCriteria(element_path, comparison, value)
        attribute_query = stringCriteria("{}.#text".format(element_path), comparison, value)
    else:
        element_query = stringCriteria(element_path, comparison, value)
        attribute_query = stringCriteria("{}.#text".format(element_path), comparison, value)

    criteria = ORCriteria(element_query, attribute_query)

    if isNot:
        return invertQuery(criteria)
    else:
        return criteria


################################################################################
# 
# Function Name: fieldsToQuery(htmlTree)
# Inputs:        htmlTree -
# Outputs:       query
# Exceptions:    None
# Description:   Take values from the html tree and create a query with them
#
################################################################################
def fieldsToQuery(request, htmlTree):
    
    mapCriterias = request.session['mapCriteriasExplore']
    
    fields = htmlTree.findall("./p")
    
    query = dict()
    for field in fields:        
        boolComp = field[0].value
        if boolComp == 'NOT':
            isNot = True
        else:
            isNot = False
            
        criteriaInfo = json.loads(mapCriterias[field.attrib['id']])
        if criteriaInfo['elementInfo'] is None:
            elementInfo = None
        else:
            elementInfo = json.loads(criteriaInfo['elementInfo'])
        if criteriaInfo['queryInfo'] is None:
            queryInfo = None
        else:
            queryInfo = json.loads(criteriaInfo['queryInfo'])
        elemType = elementInfo['type']
        if elemType == "query":
            queryValue = queryInfo['query']
            criteria = queryToCriteria(queryValue, isNot)
        elif elemType == "enum":
            element = elementInfo['path']
            value = field[2][0].value            
            criteria = enumCriteria(element, value, isNot)
        else:                
            element = elementInfo['path']
            comparison = field[2][0].value
            value = field[2][1].value
            default_prefix = request.session['defaultPrefixExplore']
            criteria = build_criteria(element, comparison, value, elemType, default_prefix, isNot)

        if boolComp == 'OR':
            query = ORCriteria(query, criteria)
        elif boolComp == 'AND':
            query = ANDCriteria(query, criteria)
        else:
            if fields.index(field) == 0:
                query.update(criteria)
            else:
                query = ANDCriteria(query, criteria)
        
    return query


################################################################################
# 
# Function Name: checkQueryForm(htmlTree)
# Inputs:        htmlTree -
# Outputs:       query
# Exceptions:    None
# Description:   Check that values entered by the user match each element type
#
################################################################################
def checkQueryForm(request, htmlTree):
    
    mapCriterias = request.session['mapCriteriasExplore']
    
    # get the prefix/namespace used in the schema
    if 'defaultPrefixExplore' in request.session:
        defaultPrefix = request.session['defaultPrefixExplore']
    else:
        xmlDocTreeStr = request.session['xmlDocTreeExplore']
        xmlDocTree = etree.fromstring(xmlDocTreeStr)

        for prefix, url in xmlDocTree.nsmap.iteritems():
            if url == SCHEMA_NAMESPACE:
                request.session['defaultPrefixExplore'] = prefix
                defaultPrefix = prefix
                break

    # check if there are no errors in the query
    errors = []
    fields = htmlTree.findall("./p")
    if len(mapCriterias) != len(fields):
        errors.append("Some fields are empty !")
    else:
        for field in fields:
            criteriaInfo = json.loads(mapCriterias[field.attrib['id']])
            elementInfo = json.loads(criteriaInfo['elementInfo'])
            elemType = elementInfo['type']
            
            if (elemType in ['{0}:float'.format(defaultPrefix), 
                       '{0}:double'.format(defaultPrefix),
                       '{0}:decimal'.format(defaultPrefix)]):
                value = field[2][1].value
                try:
                    float(value)
                except ValueError:
                    elementPath = elementInfo['path']
                    element = elementPath.split('.')[-1]
                    errors.append(element + " must be a number !")
                        
            elif (elemType in ['{0}:byte'.format(defaultPrefix),
                               '{0}:int'.format(defaultPrefix),
                               '{0}:integer'.format(defaultPrefix),
                               '{0}:long'.format(defaultPrefix),
                               '{0}:negativeInteger'.format(defaultPrefix),
                               '{0}:nonNegativeInteger'.format(defaultPrefix),
                               '{0}:nonPositiveInteger'.format(defaultPrefix),
                               '{0}:positiveInteger'.format(defaultPrefix),
                               '{0}:short'.format(defaultPrefix),
                               '{0}:unsignedLong'.format(defaultPrefix),
                               '{0}:unsignedInt'.format(defaultPrefix),
                               '{0}:unsignedShort'.format(defaultPrefix),
                               '{0}:unsignedByte'.format(defaultPrefix)]):
                value = field[2][1].value
                try:
                    int(value)
                except ValueError:
                    elementPath = elementInfo['path']
                    element = elementPath.split('.')[-1]
                    errors.append(element + " must be an integer !")
                    
            elif elemType == "{0}:string".format(defaultPrefix):
                comparison = field[2][0].value
                value = field[2][1].value
                elementPath = elementInfo['path']
                element = elementPath.split('.')[-1]
                if comparison == "like":
                    try:
                        re.compile(value)
                    except Exception, e:
                        errors.append(element + " must be a valid regular expression ! (" + str(e) + ")")
                    
    return errors
                
    
################################################################################
# 
# Function Name: add_field(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Add an empty field to the query builder
#
################################################################################
def add_field(request):
    
    html_form = request.POST['htmlForm']
    htmlTree = html.fromstring(html_form)
    
    fields = htmlTree.findall("./p")    
    fields[-1].remove(fields[-1].find("./span[@class='icon add']"))      
    if len(fields) == 1:
        criteriaID = fields[0].attrib['id']
        minusButton = html.fragment_fromstring("""<span class="icon remove" onclick="removeField('""" + str(criteriaID) +"""')"></span>""")
        fields[0].append(minusButton)
    
    # get the id of the last field (get the value of the increment, remove crit)
    lastID = fields[-1].attrib['id'][4:]
    tag_id = int(lastID) + 1

    template = loader.get_template('explore/query_builder/new_criteria.html')
    context = Context({'tagID':tag_id})
    element = html.fragment_fromstring(template.render(context))
    
    # insert before the 3 buttons (save, clear, execute)
    htmlTree.insert(-3, element)
    
    response_dict = {'queryForm': html.tostring(htmlTree)}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: remove_field(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Remove a field from the query builder
#
################################################################################
def remove_field(request):
    criteria_id = request.POST['criteriaID']
    query_form = request.POST['queryForm']
    
    htmlTree = html.fromstring(query_form)
    
    currentElement = htmlTree.get_element_by_id(criteria_id)
    fields = htmlTree.findall("./p")

    # suppress last element => give the + to the previous
    if fields[-1].attrib['id'] == criteria_id:
        plusButton = html.fragment_fromstring("""<span class="icon add" onclick="addField()"></span>""")
        fields[-2].append(plusButton)
    # only one element left => remove the -
    if len(fields) == 2:
        fields[-1].remove(fields[-1].find("./span[@class='icon remove']"))
        fields[-2].remove(fields[-2].find("./span[@class='icon remove']"))
        
    htmlTree.remove(currentElement)
    
    # replace the bool of the first element by the 2 choices input (YES/NOT) if it was an element with 3 inputs (AND/OR/NOT)
    fields = htmlTree.findall("./p")
    if len(fields[0][0].value_options) is not 2:
        if fields[0][0].value == 'NOT':
            fields[0][0] = html.fragment_fromstring(renderYESORNOT())
            fields[0][0].value = 'NOT'
        else:
            fields[0][0] = html.fragment_fromstring(renderYESORNOT())
        
    try:
        mapCriterias = request.session['mapCriteriasExplore']
        del mapCriterias[criteria_id]
        request.session['mapCriteriasExplore'] = mapCriterias
    except:
        pass

    response_dict = {'queryForm': html.tostring(htmlTree)}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: renderYESORNOT()
# Inputs:        
# Outputs:       Yes or Not select string
# Exceptions:    None
# Description:   Returns a string that represents an html select with yes or not options
#
################################################################################
def renderYESORNOT():
    template = loader.get_template('explore/query_builder/yes_no.html')
    return template.render(Context())


################################################################################
# 
# Function Name: renderANDORNOT()
# Inputs:        
# Outputs:       AND OR NOT select string
# Exceptions:    None
# Description:   Returns a string that represents an html select with AND, OR, NOT options
#
################################################################################
def renderANDORNOT():
    template = loader.get_template('explore/query_builder/and_or_not.html')
    return template.render(Context())


################################################################################
# 
# Function Name: renderNumericSelect()
# Inputs:        
# Outputs:       numeric select string
# Exceptions:    None
# Description:   Returns a string that represents an html select with numeric comparisons
#
################################################################################
def renderNumericSelect():
    template = loader.get_template('explore/query_builder/numeric_select.html')
    return template.render(Context())


################################################################################
# 
# Function Name: renderValueInput()
# Inputs:        
# Outputs:       input for a value
# Exceptions:    None
# Description:   Returns an input to type a value
#
################################################################################
def renderValueInput():
    template = loader.get_template('explore/query_builder/input.html')
    return template.render(Context())


################################################################################
# 
# Function Name: renderValueInput()
# Inputs:        
# Outputs:       input for a value
# Exceptions:    None
# Description:   Returns an input to type a value
#
################################################################################
def renderStringSelect():
    template = loader.get_template('explore/query_builder/string_select.html')
    return template.render(Context())


################################################################################
# 
# Function Name: renderEnum()
# Inputs:        
# Outputs:       render an html select from an enumeration
# Exceptions:    None
# Description:   Returns html select from an enumeration
#
################################################################################
def renderEnum(request, enums):
    template = loader.get_template('explore/query_builder/enum.html')
    context = RequestContext(request, {
        'enums': enums,
    })
    return template.render(context)


################################################################################
# 
# Function Name: buildPrettyCriteria(elementName, comparison, value, isNot=False)
# Inputs:        elementName - 
#                comparison - 
#                value -
#                isNot - 
# Outputs:       render a criteria in a pretty form
# Exceptions:    None
# Description:   Returns a pretty representation of the criteria
#
################################################################################
def buildPrettyCriteria(elementName, comparison, value, isNot=False):
    prettyCriteria = ""
    
    if isNot:
        prettyCriteria += "NOT("
        
    prettyCriteria += elementName
    if comparison == "lt":
        prettyCriteria += " &lt; "
    elif comparison == "lte":
        prettyCriteria += " &le; "
    elif comparison == "=":
        prettyCriteria += "="
    elif comparison == "gte":
        prettyCriteria += " &ge; "
    elif comparison == "gt":
        prettyCriteria += " &gt; "
    elif comparison == "is":
        prettyCriteria += " is "
    elif comparison == "like":
        prettyCriteria += " like "
    
    if value == "":
        prettyCriteria += ' &ldquo;  &ldquo;'
    else:
        prettyCriteria += value
    
    if isNot:
        prettyCriteria += ")"
    
    return prettyCriteria


################################################################################
# 
# Function Name: queryToPrettyCriteria(queryValue, isNot)
# Inputs:        queryValue - 
#                isNot - 
# Outputs:       render a query in a pretty form
# Exceptions:    None
# Description:   Returns a pretty representation of the query
#
################################################################################
def queryToPrettyCriteria(queryValue, isNot):
    if isNot:
        return "NOT(" + queryValue + ")"
    else:
        return queryValue


################################################################################
# 
# Function Name: enumToPrettyCriteria(element, value, isNot=False)
# Inputs:        element - 
#                value - 
#                isNot - 
# Outputs:       render an enumeration value in a pretty form
# Exceptions:    None
# Description:   Returns a pretty representation of the enumeration value
#
################################################################################
def enumToPrettyCriteria(element, value, isNot=False):
    if isNot:
        return "NOT(" + element + " is " + value + ")"
    else:
        return element + " is " + value


################################################################################
# 
# Function Name: ORPrettyCriteria(query, criteria)
# Inputs:        query - 
#                criteria - 
# Outputs:       render a OR in a pretty form
# Exceptions:    None
# Description:   Returns a pretty representation of the OR
#
################################################################################
def ORPrettyCriteria(query, criteria):
    return "(" + query + " OR " + criteria + ")"


################################################################################
# 
# Function Name: ANDPrettyCriteria(query, criteria)
# Inputs:        query - 
#                criteria - 
# Outputs:       render a AND in a pretty form
# Exceptions:    None
# Description:   Returns a pretty representation of the AND
#
################################################################################
def ANDPrettyCriteria(query, criteria):
    return "(" + query + " AND " + criteria + ")"


################################################################################
# 
# Function Name: fieldsToPrettyQuery(request, queryFormTree)
# Inputs:        request - 
#                queryFormTree - 
# Outputs:       
# Exceptions:    None
# Description:   Tranforms fields from the HTML form into pretty representation
#
################################################################################
def fieldsToPrettyQuery(request, queryFormTree):
    
    mapCriterias = request.session['mapCriteriasExplore']
    
    fields = queryFormTree.findall("./p")
    query = ""

    for field in fields:        
        boolComp = field[0].value
        if boolComp == 'NOT':
            isNot = True
        else:
            isNot = False
                
        criteriaInfo = json.loads(mapCriterias[field.attrib['id']])
        if criteriaInfo['elementInfo'] is None:
            elementInfo = None
        else:
            elementInfo = json.loads(criteriaInfo['elementInfo'])
        if criteriaInfo['queryInfo'] is None:
            queryInfo = None
        else:
            queryInfo = json.loads(criteriaInfo['queryInfo'])
        elemType = elementInfo['type']
        if elemType == "query":
            queryValue = queryInfo['displayedQuery']
            criteria = queryToPrettyCriteria(queryValue, isNot)
        elif elemType == "enum":
            elementPath = elementInfo['path']
            element = elementPath.split('.')[-1]
            value = field[2][0].value            
            criteria = enumToPrettyCriteria(element, value, isNot)
        else:                 
            elementPath = elementInfo['path']
            element = elementPath.split('.')[-1]
            comparison = field[2][0].value
            value = field[2][1].value
            criteria = buildPrettyCriteria(element, comparison, value, isNot)
        
        if boolComp == 'OR':
            query = ORPrettyCriteria(query, criteria)
        elif boolComp == 'AND':
            query = ANDPrettyCriteria(query, criteria)
        else:
            if fields.index(field) == 0:
                query += criteria
            else:
                query = ANDPrettyCriteria(query, criteria)
        
    return query    


################################################################################
# 
# Function Name: save_query(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   save a query into mongo db and update the html display
#
################################################################################
def save_query(request):
    query_form = request.POST['queryForm']
    
    mapQueryInfo = request.session['mapQueryInfoExplore']
    queryFormTree = html.fromstring(query_form)

    # Check that the user can save a query
    errors = []
    if '_auth_user_id' in request.session:
        userID = request.session['_auth_user_id']
        if 'exploreCurrentTemplateID' in request.session:
            templateID = request.session['exploreCurrentTemplateID'] 
        else:
            errors = ['You have to select a template before you can save queries (Step 1 : Select Template).']
    else:
        errors = ['You have to login to save a query.']
    
    response_dict = {}
    if len(errors)== 0:
        # Check that the query is valid      
        errors = checkQueryForm(request, queryFormTree)
        if len(errors) == 0:
            query = fieldsToQuery(request, queryFormTree)    
            displayedQuery = fieldsToPrettyQuery(request, queryFormTree) 
        
            #save the query in the data base
            savedQuery = SavedQuery(str(userID), str(templateID), json.dumps(query), displayedQuery)
            savedQuery.save()
            
            queryInfo = QueryInfo(query, displayedQuery)
            mapQueryInfo[str(savedQuery.id)] = queryInfo.__to_json__()
            request.session['mapQueryInfoExplore'] = mapQueryInfo
        else:
            errorsString = ""
            for error in errors:
                errorsString += "<p>" + error + "</p>"  
            response_dict = {'listErrors': errorsString}
    else:
        errorsString = ""
        for error in errors:
            errorsString += "<p>" + error + "</p>"            
        response_dict = {'listErrors': errorsString}

    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: manageRegexBeforeSave(query)
# Inputs:        query
# Outputs:       
# Exceptions:    None
# Description:   Replaces the Regex objects before saving into mongo db
#
################################################################################
def manageRegexBeforeSave(query):
    for key, value in query.iteritems():
        if key == "$and" or key == "$or":
            for subValue in value:
                manageRegexBeforeSave(subValue)
        elif isinstance(value, re._pattern_type):
            query[key] = "/" + str(value.pattern) + "/"
        elif isinstance(value, dict):
            manageRegexBeforeSave(value)


################################################################################
# 
# Function Name: delete_query(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Deletes a query and update the HTML display
#
################################################################################
def delete_query(request):
    saved_query_id = request.POST['savedQueryID']
    SavedQuery(id=saved_query_id[5:]).delete()
    
    mapQueryInfo = request.session['mapQueryInfoExplore']
    del mapQueryInfo[saved_query_id[5:]]
    request.session['mapQueryInfoExplore'] = mapQueryInfo
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: update_user_inputs(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Update the user input of the query builder according to the type of the selected element
#
################################################################################  
def update_user_inputs(request):   
    html_form = request.POST['html'] 
    from_element_id = request.POST['fromElementID']
    criteria_id = request.POST['criteriaID']

    mapCriterias = request.session['mapCriteriasExplore']
    defaultPrefix = request.session['defaultPrefixExplore']
    
    toCriteriaID = "crit" + str(criteria_id)
    
    criteria_info = CriteriaInfo()

    # get schema element
    schema_element = SchemaElement.objects().get(pk=from_element_id)

    # get the xml type of the element
    xml_xpath = schema_element.options['xpath']['xml']
    # convert xml path to mongo dot notation
    namespaces = common.get_namespaces(BytesIO(str(request.session['xmlDocTreeExplore'])))
    dot_notation = "content" + xpath_to_dot_notation(xml_xpath, namespaces)

    htmlTree = html.fromstring(html_form)
    currentCriteria = htmlTree.get_element_by_id(toCriteriaID)

    try:
        currentCriteria[1].attrib['class'] = currentCriteria[1].attrib['class'].replace('queryInput', 'elementInput')
    except:
        pass

    # criteria id = crit%d
    criteriaIDIncr = toCriteriaID[4:]
    user_inputs = currentCriteria.find("./span/[@id='ui" + str(criteriaIDIncr) + "']")

    for element in user_inputs.findall("*"):
        user_inputs.remove(element)

    element_type = schema_element.options['type']
    try:
        if element_type.startswith("{0}:".format(defaultPrefix)):
            # numeric
            if (element_type in ["{0}:byte".format(defaultPrefix),
                                 "{0}:decimal".format(defaultPrefix),
                                 "{0}:int".format(defaultPrefix),
                                 "{0}:integer".format(defaultPrefix),
                                 "{0}:long".format(defaultPrefix),
                                 "{0}:negativeInteger".format(defaultPrefix),
                                 "{0}:nonNegativeInteger".format(defaultPrefix),
                                 "{0}:nonPositiveInteger".format(defaultPrefix),
                                 "{0}:positiveInteger".format(defaultPrefix),
                                 "{0}:short".format(defaultPrefix),
                                 "{0}:unsignedLong".format(defaultPrefix),
                                 "{0}:unsignedInt".format(defaultPrefix),
                                 "{0}:unsignedShort".format(defaultPrefix),
                                 "{0}:unsignedByte".format(defaultPrefix),
                                 "{0}:double".format(defaultPrefix),
                                 "{0}:float".format(defaultPrefix)]):
                form = html.fragment_fromstring(renderNumericSelect())
                inputs = html.fragment_fromstring(renderValueInput())
                user_inputs.append(form)
                user_inputs.append(inputs)
            # string
            else:
                form = html.fragment_fromstring(renderStringSelect())
                inputs = html.fragment_fromstring(renderValueInput())
                user_inputs.append(form)
                user_inputs.append(inputs)
        else:
            # enumeration
            while schema_element.tag != 'simple_type':
                schema_element = schema_element.children[0]
            schema_element = schema_element.children[0]
            enums = []
            for enum_element in schema_element.children:
                if enum_element.tag == 'enumeration':
                    enums.append(enum_element.value)
            element_type = 'enum'
            form = html.fragment_fromstring(renderEnum(request, enums))
            user_inputs.append(form)
    except:
        # default renders string
        element_type = "{}:string".format(defaultPrefix)
        form = html.fragment_fromstring(renderStringSelect())
        inputs = html.fragment_fromstring(renderValueInput())
        user_inputs.append(form)
        user_inputs.append(inputs)

    criteria_info.elementInfo = ElementInfo(path=dot_notation, type=element_type)
    mapCriterias[toCriteriaID] = criteria_info.__to_json__()
    request.session['mapCriteriasExplore'] = mapCriterias

    response_dict = {'queryForm': html.tostring(htmlTree)}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    
    
################################################################################
# 
# Function Name: add_saved_query_to_form(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Adds the selected query to query builder
#
################################################################################ 
def add_saved_query_to_form(request):
    query_form = request.POST['queryForm']
    saved_query_id = request.POST['savedQueryID']

    mapQueryInfo = request.session['mapQueryInfoExplore']
    queryTree = html.fromstring(query_form)
    
    fields = queryTree.findall("./p")
    fields[-1].remove(fields[-1].find("./span[@class='icon add']"))      
    if len(fields) == 1:
        criteriaID = fields[0].attrib['id']
        minusButton = html.fragment_fromstring("""<span class="icon remove" onclick="removeField('""" + str(criteriaID) +"""')"></span>""")
        fields[0].append(minusButton)
        
    lastID = fields[-1].attrib['id'][4:]
    queryInfo = json.loads(mapQueryInfo[saved_query_id[5:]])
    query = queryInfo['displayedQuery']
    if len(fields) == 1 and fields[0][1].value == "":
        queryTree.remove(fields[0])
        tag_id = int(lastID)

        template = loader.get_template('explore/query_builder/new_query.html')
        context = Context({'tagID': tag_id, 'query': query, 'first': True})
        element = html.fragment_fromstring(template.render(context))
    else:
        tag_id = int(lastID) + 1
        template = loader.get_template('explore/query_builder/new_query.html')
        context = Context({'tagID': tag_id, 'query': query})
        element = html.fragment_fromstring(template.render(context))

    # insert before the 3 buttons (save, clear, execute)
    queryTree.insert(-3,element)
    
    mapCriterias = request.session['mapCriteriasExplore']
    criteriaInfo = CriteriaInfo()
    criteriaInfo.queryInfo = QueryInfo(query=json.loads(mapQueryInfo[saved_query_id[5:]])['query'],
                                       displayedQuery=json.loads(mapQueryInfo[saved_query_id[5:]])['displayedQuery'])
    criteriaInfo.elementInfo = ElementInfo("query")
    mapCriterias['crit' + str(tag_id)] = criteriaInfo.__to_json__()
    request.session['mapCriteriasExplore'] = mapCriterias

    response_dict = {'queryForm': html.tostring(queryTree)}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    
    
################################################################################
# 
# Function Name: renderInitialForm()
# Inputs:        
# Outputs:       
# Exceptions:    None
# Description:   Renders the initial Query Builder
#
################################################################################ 
def renderInitialForm():
    template = loader.get_template('explore/query_builder/initial_form.html')
    return template.render(Context())


################################################################################
# 
# Function Name: clear_criterias(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Clears the Query Builder
#
################################################################################ 
def clear_criterias(request):
    """ Reset Saved Criterias """
    
    query_form = request.POST['queryForm']
    
    # Load the criterias tree     
    queryTree = html.fromstring(query_form)
    
    fields = queryTree.findall("./p")
    for field in fields:
        queryTree.remove(field)
    
    initialForm = html.fragment_fromstring(renderInitialForm())
    queryTree.insert(0,initialForm)  
    
    request.session['mapCriteriasExplore'] = dict()

    response_dict = {'queryForm': html.tostring(queryTree)}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: clear_queries(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Delete all saved queries
#
################################################################################ 
def clear_queries(request):
    """ Reset Saved Queries """
    
    mapQueryInfo = request.session['mapQueryInfoExplore']
       
    for queryID in mapQueryInfo.keys():
        SavedQuery(id=queryID).delete()
            
    request.session['mapQueryInfoExplore'] = dict()
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: manageRegexFromDB(query)
# Inputs:        query - 
# Outputs:       
# Exceptions:    None
# Description:   Restore Regex from Mongo db
#
################################################################################ 
def manageRegexFromDB(query):
    for key, value in query.iteritems():
        if key == "$and" or key == "$or":
            for subValue in value:
                manageRegexFromDB(subValue)
        elif isinstance(value, str):
            if len(value) >= 2 and value[0] == "/" and value[-1] == "/":
                query[key] = re.compile(value[1:-1])
        elif isinstance(value, dict):
            manageRegexFromDB(value)


################################################################################
# 
# Function Name: get_custom_form(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Get the form customized by the user to select the fields
#
################################################################################ 
def get_custom_form(request):
    if 'savedQueryFormExplore' in request.session:
        savedQueryForm = request.session['savedQueryFormExplore']
    else:
        savedQueryForm = ""
    customFormString = request.session['customFormStringExplore']
    
    response_dict = {}
    #delete criterias if user comes from another page than results
    if 'keepCriterias' in request.session:
        del request.session['keepCriterias']
        if savedQueryForm != "" :
            response_dict['queryForm'] = savedQueryForm
            request.session['savedQueryFormExplore'] = ""
    else:
        request.session['mapCriteriasExplore'] = dict()
    
    #Get saved queries of an user
    mapQueryInfo = dict()
    request.session['mapQueryInfoExplore'] = dict()
    if '_auth_user_id' in request.session and 'exploreCurrentTemplateID' in request.session:
        userID = request.session['_auth_user_id']
        templateID = request.session['exploreCurrentTemplateID']
        userQueries = SavedQuery.objects(user=str(userID),template=str(templateID))
        for savedQuery in userQueries:
            query = json.loads(savedQuery.query)
#            manageRegexFromDB(query)     
            queryInfo = QueryInfo(query, savedQuery.displayedQuery)
            mapQueryInfo[str(savedQuery.id)] = queryInfo.__to_json__()
            request.session['mapQueryInfoExplore'] = mapQueryInfo

    if customFormString != "":
        customForm = customFormString
    else:
        customFormErrorMsg = "<p style='color:red;'>You should customize the template first. <a href='/explore/customize-template' style='color:red;font-weight:bold;'>Go back to Step 2 </a> and select the elements that you want to use in your queries.</p>"
        customForm = customFormErrorMsg
    
    response_dict['customForm'] = customForm

    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: save_custom_data(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Saves the custom template with fields selected by the user
#                
#
################################################################################
def save_custom_data(request):
    print '>>>>  BEGIN def saveCustomData(request)'
    
    form_content = request.POST['formContent']
    request.session['formStringExplore'] = form_content

    # modify the form string to only keep the selected elements
    htmlTree = html.fromstring(form_content)
    createCustomTreeForQuery(request, htmlTree)

    anyChecked = request.session['anyCheckedExplore']
    if anyChecked:
        request.session['customFormStringExplore'] = html.tostring(htmlTree)
    else:
        request.session['customFormStringExplore'] = ""
    
    request.session['anyCheckedExplore'] = False 

    print '>>>> END def saveCustomData(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: createCustomTreeForQuery(request,htmlTree)
# Inputs:        request - 
#                htmlTree - 
# Outputs:       
# Exceptions:    None
# Description:   Creates a custom HTML tree from fields chosen by the user
#                
#
################################################################################
def createCustomTreeForQuery(request, htmlTree):
    request.session['anyCheckedExplore'] = False

    for li in htmlTree.findall("./ul/li"):
        manage_li_for_query(request, li)


################################################################################
#
# Function Name: manage_ul_for_query(request, ul)
# Inputs:        request - 
#                ul - 
# Outputs:       
# Exceptions:    None
# Description:   Process the ul element of an HTML list
#                
################################################################################
def manage_ul_for_query(request, ul):
    branch_info = BranchInfo(keepTheBranch=False, selectedLeave=[])

    for li in ul.findall("./li"):
        li_branch_info = manage_li_for_query(request, li)
        if li_branch_info.keepTheBranch:
            branch_info.keepTheBranch = True
        if len(li_branch_info.selectedLeave) > 0:
            branch_info.selectedLeave.extend(li_branch_info.selectedLeave)

    checkbox = ul.find("./input[@type='checkbox']")
    if checkbox is not None:
        checkbox.attrib['style'] = "display:none;"
        if 'value' in checkbox.attrib and checkbox.attrib['value'] == 'true':
            request.session['anyCheckedExplore'] = True
            # remove the checkbox and make the element clickable
            ul.getparent().attrib['style'] = "color:orange;font-weight:bold;cursor:pointer;"
            ul.getparent().attrib['onclick'] = "selectElement('" + ul.getparent().attrib['class'] + "')"
            # tells to keep this branch until this leave
            branch_info.keepTheBranch = True
            branch_info.selectedLeave.append(ul.getparent().attrib['class'])

    if not branch_info.keepTheBranch:
        ul.attrib['style'] = "display:none;"
        
    return branch_info


################################################################################
#
# Function Name: manage_li_for_query(request, li)
# Inputs:        request - 
#                li - 
# Outputs:       
# Exceptions:    None
# Description:   Process the li element of an HTML list
#                
################################################################################
def manage_li_for_query(request, li):
    list_ul = li.findall("./ul")
    branch_info = BranchInfo(keepTheBranch=False, selectedLeave=[])
    if len(list_ul) != 0:
        selected_leaves = []
        for ul in list_ul:
            ul_branch_info = manage_ul_for_query(request, ul)
            if ul_branch_info.keepTheBranch:
                branch_info.keepTheBranch = True
            if len(ul_branch_info.selectedLeave) > 0:
                selected_leaves.extend(ul_branch_info.selectedLeave)
        # sub element queries, starting at 2 because 1 is the regular case
        if len(selected_leaves) > 1:
            # not for the choices
            if li[0].tag != 'select':
                if 'style' not in li.attrib:
                    leaves_id = ""
                    for leave in selected_leaves[:-1]:
                        leaves_id += leave + " "
                    leaves_id += selected_leaves[-1]
                    # get the node text
                    li_text = li[0].tail if li[0].tail is not None else ''
                    li[0].tail = ""
                    # insert span with selectParent
                    # (cannot put it on li node directly or all children will call the JS onclick)
                    li.insert(0, html.fragment_fromstring("""<span style="color:purple;font-weight:bold;cursor:pointer;"
                                                                onclick="selectParent('""" + leaves_id + """')">""" +
                                                          li_text + """</span>"""))
        if not branch_info.keepTheBranch:
            li.attrib['style'] = "display:none;"
        return branch_info
    else:
        try:
            checkbox = li.find("./input[@type='checkbox']")
            if checkbox.attrib['value'] == 'false':
                li.attrib['style'] = "display:none;"
                return branch_info
            else:
                request.session['anyCheckedExplore'] = True
                # remove the checkbox and make the element clickable
                li.attrib['style'] = "color:orange;font-weight:bold;cursor:pointer;"
                li.attrib['onclick'] = "selectElement('" + li.attrib['class'] + "')"
                checkbox.attrib['style'] = "display:none;"
                # tells to keep this branch until this leave
                branch_info.keepTheBranch = True
                branch_info.selectedLeave.append(li.attrib['class'])
                return branch_info
        except:
            return branch_info
  

################################################################################
#
# Function Name: back_to_query(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Allows to come back to the query definition keeping the criterias
#                
################################################################################
def back_to_query(request):         
    request.session['keepCriterias'] = True
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: set_current_criteria(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Set the id of the criteria that is currently set
#                
################################################################################
def set_current_criteria(request):
    
    request.session['criteriaIDExplore'] = request.POST['currentCriteriaID']
    return HttpResponse(json.dumps({}), content_type='application/javascript')
    

################################################################################
#
# Function Name: select_element(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Select an element in the custom tree
#                
################################################################################
def select_element(request):

    element_id = request.POST['elementID']

    schema_element = SchemaElement.objects().get(pk=element_id)

    criteria_id = request.session['criteriaIDExplore']
    response_dict = {"criteriaTagID": criteria_id,
                     "criteriaID": str(criteria_id[4:]),
                     "elementName": schema_element.options['label']}
    
    request.session['criteriaIDExplore'] = ""

    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: prepare_sub_element_query(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Build the form for queries on a same subelement 
#                
################################################################################
def prepare_sub_element_query(request):
    leaves_id = request.GET['leavesID']
    
    defaultPrefix = request.session['defaultPrefixExplore']
    
    list_leaves_id = leaves_id.split(" ")

    # get the parent name using the first schema element of the list
    first_element = SchemaElement.objects().get(pk=list_leaves_id[0])
    # get the xml type of the element
    first_element_xml_xpath = first_element.options['xpath']['xml']
    # convert xml path to mongo dot notation
    namespaces = common.get_namespaces(BytesIO(str(request.session['xmlDocTreeExplore'])))
    first_element_dot_notation = xpath_to_dot_notation(first_element_xml_xpath, namespaces)
    parent_path = ".".join(first_element_dot_notation.split(".")[:-1])
    parent_name = parent_path.split(".")[-1]

    subElementQueryBuilderStr = "<p><b>" + parent_name + "</b></p>"
    subElementQueryBuilderStr += "<ul>"
    for leaveID in list_leaves_id:
        schema_element = SchemaElement.objects().get(pk=leaveID)
        # get the xml type of the element
        xml_xpath = schema_element.options['xpath']['xml']
        # convert xml path to mongo dot notation
        namespaces = common.get_namespaces(BytesIO(str(request.session['xmlDocTreeExplore'])))
        dot_notation = xpath_to_dot_notation(xml_xpath, namespaces)
        element_type = schema_element.options['type']

        element_name = dot_notation.split(".")[-1]
        subElementQueryBuilderStr += "<li><input type='checkbox' style='margin-right:4px;margin-left:2px;' checked/>"
        subElementQueryBuilderStr += renderYESORNOT()
        subElementQueryBuilderStr += element_name + ": "
        try:
            if element_type.startswith("{0}:".format(defaultPrefix)):
                # numeric
                if (element_type in ["{0}:byte".format(defaultPrefix),
                                     "{0}:decimal".format(defaultPrefix),
                                     "{0}:int".format(defaultPrefix),
                                     "{0}:integer".format(defaultPrefix),
                                     "{0}:long".format(defaultPrefix),
                                     "{0}:negativeInteger".format(defaultPrefix),
                                     "{0}:nonNegativeInteger".format(defaultPrefix),
                                     "{0}:nonPositiveInteger".format(defaultPrefix),
                                     "{0}:positiveInteger".format(defaultPrefix),
                                     "{0}:short".format(defaultPrefix),
                                     "{0}:unsignedLong".format(defaultPrefix),
                                     "{0}:unsignedInt".format(defaultPrefix),
                                     "{0}:unsignedShort".format(defaultPrefix),
                                     "{0}:unsignedByte".format(defaultPrefix),
                                     "{0}:double".format(defaultPrefix),
                                     "{0}:float".format(defaultPrefix)]):
                    subElementQueryBuilderStr += renderNumericSelect()
                    subElementQueryBuilderStr += renderValueInput()
                else:
                    subElementQueryBuilderStr += renderStringSelect()
                    subElementQueryBuilderStr += renderValueInput()
            else:
                # enumeration
                while schema_element.tag != 'simple_type':
                    schema_element = schema_element.children[0]
                schema_element = schema_element.children[0]
                enums = []
                for enum_element in schema_element.children:
                    if enum_element.tag == 'enumeration':
                        enums.append(enum_element.value)
                subElementQueryBuilderStr += renderEnum(request, enums)
        except:
            subElementQueryBuilderStr += renderStringSelect()
            subElementQueryBuilderStr += renderValueInput()
        subElementQueryBuilderStr += "</li><br/>"
    subElementQueryBuilderStr += "</ul>"

    response_dict = {'subElementQueryBuilder': subElementQueryBuilderStr}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: insert_sub_element_query(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Inserts a query for a sub element in the query builder  
#                
################################################################################
def insert_sub_element_query(request):
    form = request.POST['form']
    leaves_id = request.POST['leavesID']

    mapCriterias = request.session['mapCriteriasExplore']
    criteriaID = request.session['criteriaIDExplore']
    
    htmlTree = html.fromstring(form)
    listLi = htmlTree.findall("ul/li")
    list_leaves_id = leaves_id.split(" ")
    
    i = 0
    nbSelected = 0
    errors = []
    for li in listLi:
        if li[0].attrib['value'] == 'true':
            nbSelected += 1

            schema_element = SchemaElement.objects().get(pk=list_leaves_id[i])
            # get the xml type of the element
            xml_xpath = schema_element.options['xpath']['xml']
            # convert xml path to mongo dot notation
            namespaces = common.get_namespaces(BytesIO(str(request.session['xmlDocTreeExplore'])))
            dot_notation = xpath_to_dot_notation(xml_xpath, namespaces)
            element_type = schema_element.options['type']

            element_name = dot_notation.split(".")[-1]

            error = checkSubElementField(request, li, element_name, element_type)
            if error != "":
                errors.append(error)
        i += 1
    
    if nbSelected < 2:
        errors = ["Please select at least two elements."]
    
    if len(errors) == 0:
        query = subElementfieldsToQuery(request, listLi, list_leaves_id)
        prettyQuery = subElementfieldsToPrettyQuery(request, listLi, list_leaves_id)
        criteriaInfo = CriteriaInfo()
        criteriaInfo.queryInfo = QueryInfo(query, prettyQuery)
        criteriaInfo.elementInfo = ElementInfo("query")
        mapCriterias[criteriaID] = criteriaInfo.__to_json__()
        request.session['mapCriteriasExplore'] = mapCriterias
        uiID = "ui" + criteriaID[4:]
        response_dict = {'criteriaID': criteriaID,
                         'prettyQuery': prettyQuery,
                         'uiID': uiID}    
    else:
        errorsString = ""
        for error in errors:
            errorsString += "<p>" + error + "</p>"
        response_dict = {'listErrors': errorsString}
    
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: checkSubElementField(request, liElement, elementName, elementType)
# Inputs:        request -
#                liElement -
#                elementName - 
#                elementType - 
# Outputs:       
# Exceptions:    None
# Description:   Checks that the fields of the subelement query are of the good type
#                
################################################################################
def checkSubElementField(request, liElement, elementName, elementType):   
    error = ""
    defaultPrefix = request.session['defaultPrefixExplore']
    
    if (elementType in ['{0}:float'.format(defaultPrefix), 
                        '{0}:double'.format(defaultPrefix),
                        '{0}:decimal'.format(defaultPrefix)]):
        value = liElement[3].value
        try:
            float(value)
        except ValueError:
            error = elementName + " must be a number !"
                
    elif (elementType in ['{0}:byte'.format(defaultPrefix),
                          '{0}:int'.format(defaultPrefix),
                          '{0}:integer'.format(defaultPrefix),
                          '{0}:long'.format(defaultPrefix),
                          '{0}:negativeInteger'.format(defaultPrefix),
                          '{0}:nonNegativeInteger'.format(defaultPrefix),
                          '{0}:nonPositiveInteger'.format(defaultPrefix),
                          '{0}:positiveInteger'.format(defaultPrefix),
                          '{0}:short'.format(defaultPrefix),
                          '{0}:unsignedLong'.format(defaultPrefix),
                          '{0}:unsignedInt'.format(defaultPrefix),
                          '{0}:unsignedShort'.format(defaultPrefix),
                          '{0}:unsignedByte'.format(defaultPrefix)]):
        value = liElement[3].value
        try:
            int(value)
        except ValueError:
            error = elementName + " must be an integer !"
            
    elif elementType == "{0}:string".format(defaultPrefix):
        comparison = liElement[2].value
        value = liElement[3].value
        if comparison == "like":
            try:
                re.compile(value)
            except Exception, e:
                error = elementName + " must be a valid regular expression ! (" + str(e) + ")"    

    return error


################################################################################
#
# Function Name: subElementfieldsToQuery(request, liElement, listLeavesId)
# Inputs:        request -
#                liElement -
#                listLeavesId - 
# Outputs:       
# Exceptions:    None
# Description:   Tranforms HTML fields in a subelement query for mongo db
#                
################################################################################
def subElementfieldsToQuery(request, liElements, list_leaves_id):
    defaultPrefix = request.session['defaultPrefixExplore']
    elem_match = dict()
    i = 0

    # get the parent path using the first element of the list
    first_element = SchemaElement.objects().get(pk=list_leaves_id[0])
    # get the xml type of the element
    first_element_xml_xpath = first_element.options['xpath']['xml']
    # convert xml path to mongo dot notation
    namespaces = common.get_namespaces(BytesIO(str(request.session['xmlDocTreeExplore'])))
    first_element_dot_notation = xpath_to_dot_notation(first_element_xml_xpath, namespaces)
    parent_path = "content" + ".".join(first_element_dot_notation.split(".")[:-1])
    
    for li in liElements:        
        if li[0].attrib['value'] == 'true':
            boolComp = li[1].value
            if boolComp == 'NOT':
                isNot = True
            else:
                isNot = False

            schema_element = SchemaElement.objects().get(pk=list_leaves_id[i])
            xml_xpath = schema_element.options['xpath']['xml']
            namespaces = common.get_namespaces(BytesIO(str(request.session['xmlDocTreeExplore'])))
            dot_notation = xpath_to_dot_notation(xml_xpath, namespaces)
            element_name = dot_notation.split(".")[-1]
            element_type = schema_element.options['type']

            try:
                if element_type.startswith("{0}:".format(defaultPrefix)):
                    comparison = li[2].value
                    value = li[3].value
                    default_prefix = request.session['defaultPrefixExplore']
                    criteria = build_criteria(element_name, comparison, value, element_type, default_prefix, isNot)
                else:
                    value = li[2].value
                    criteria = enumCriteria(element_name, value, isNot)
            except:
                comparison = li[2].value
                value = li[3].value
                default_prefix = request.session['defaultPrefixExplore']
                criteria = build_criteria(element_name, comparison, value, element_type, default_prefix, isNot)

            elem_match.update(criteria)

        i += 1
         
    query = dict()
    query[parent_path] = dict()
    query[parent_path]["$elemMatch"] = elem_match

    return query


################################################################################
#
# Function Name: subElementfieldsToQuery(request, liElement, listLeavesId)
# Inputs:        request -
#                liElement -
#                listLeavesId - 
# Outputs:       
# Exceptions:    None
# Description:   Tranforms HTML fields in a pretty subelement query
#                
################################################################################
def subElementfieldsToPrettyQuery(request, liElements, list_leaves_id):
    defaultPrefix = request.session['defaultPrefixExplore']
    elem_match = "("
    i = 0

    # get the parent path using the first element of the list
    first_element = SchemaElement.objects().get(pk=list_leaves_id[0])
    # get the xml type of the element
    first_element_xml_xpath = first_element.options['xpath']['xml']
    # convert xml path to mongo dot notation
    namespaces = common.get_namespaces(BytesIO(str(request.session['xmlDocTreeExplore'])))
    first_element_dot_notation = xpath_to_dot_notation(first_element_xml_xpath, namespaces)
    parent_name = first_element_dot_notation.split(".")[-2]

    for li in liElements:        
        if li[0].attrib['value'] == 'true':
            boolComp = li[1].value
            if boolComp == 'NOT':
                isNot = True
            else:
                isNot = False
                
            schema_element = SchemaElement.objects().get(pk=list_leaves_id[i])
            xml_xpath = schema_element.options['xpath']['xml']
            namespaces = common.get_namespaces(BytesIO(str(request.session['xmlDocTreeExplore'])))
            dot_notation = xpath_to_dot_notation(xml_xpath, namespaces)
            element_name = dot_notation.split(".")[-1]
            element_type = schema_element.options['type']

            try:
                if element_type.startswith("{0}:".format(defaultPrefix)):
                    comparison = li[2].value
                    value = li[3].value
                    criteria = buildPrettyCriteria(element_name, comparison, value, isNot)
                else:
                    value = li[2].value
                    criteria = enumToPrettyCriteria(element_name, value, isNot)
            except:
                comparison = li[2].value
                value = li[3].value
                criteria = buildPrettyCriteria(element_name, comparison, value, isNot)

            if elem_match != "(":
                elem_match += ", "
            elem_match += criteria
        i += 1
        
    elem_match += ")"
    
    query = parent_name + elem_match
        
    return query 


################################################################################
#
# Function Name: load_refinements(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Load refinements criterias from selected schemas
#
################################################################################
def load_refinements(request):
    schema_name = request.GET['schema']
    schemas = Template.objects(title=schema_name)
    schema_id = TemplateVersion.objects().get(pk=schemas[0].templateVersion).current

    schema = Template.objects().get(pk=schema_id)

    xmlDocTree = etree.parse(BytesIO(schema.content.encode('utf-8')))

    # find the namespaces
    namespaces = common.get_namespaces(BytesIO(schema.content.encode('utf-8')))

    target_ns_prefix = common.get_target_namespace_prefix(namespaces, xmlDocTree)
    target_ns_prefix = "{}:".format(target_ns_prefix) if target_ns_prefix != '' else ''

    # building refinement options based on the schema
    refinement_options = "<a onclick='clearRefinements();' style='cursor:pointer;'>Clear Refinements</a> <br/><br/>"

    # TODO: change enumeration look up by something more generic (using annotations in the schema)
    # looking for enumerations
    simple_types = xmlDocTree.findall("./{0}simpleType".format(LXML_SCHEMA_NAMESPACE))
    for simple_type in simple_types:
        try:
            enums = simple_type.findall("./{0}restriction/{0}enumeration".format(LXML_SCHEMA_NAMESPACE))
            refinement = ""
            if len(enums) > 0:
                # build dot notation query
                # find the element using the enumeration
                element = xmlDocTree.findall(".//{0}element[@type='{1}']".format(LXML_SCHEMA_NAMESPACE,
                                                                                 target_ns_prefix + simple_type.attrib['name']))
                if len(element) > 1:
                    print "error: more than one element using the enumeration (" + str(len(element)) + ")"
                else:
                    element = element[0]

                    # get the label of refinements
                    app_info = common.getAppInfo(element)
                    label = app_info['label'] if 'label' in app_info else element.attrib['name']
                    label = label if label is not None else ''
                    query = []
                    while element is not None:
                        if element.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
                            query.insert(0, element.attrib['name'])
                        elif element.tag == "{0}simpleType".format(LXML_SCHEMA_NAMESPACE)\
                                or element.tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):
                            try:
                                element = xmlDocTree.findall(".//{0}element[@type='{1}']".format(LXML_SCHEMA_NAMESPACE,
                                                                                                 target_ns_prefix + element.attrib['name']))
                                if len(element) > 1:
                                    print "error: more than one element using the enumeration (" + str(len(element)) + ")"
                                else:
                                    element = element[0]
                                    query.insert(0, element.attrib['name'])
                            except:
                                pass
                        elif element.tag == "{0}extension".format(LXML_SCHEMA_NAMESPACE):
                            try:
                                element = xmlDocTree.findall(".//{0}element[@type='{1}']".format(LXML_SCHEMA_NAMESPACE,
                                                                                                 element.attrib['base']))
                                if len(element) > 1:
                                    print "error: more than one element using the enumeration (" + str(len(element)) + ")"
                                else:
                                    element = element[0]
                                    query.insert(0, element.attrib['name'])
                            except:
                                pass
                        element = element.getparent()

                dot_query = ".".join(query)

                # get the name of the enumeration
                refinement += "<div class='refine_criteria' query='" + dot_query + "'>" + label + ": <br/>"
                for enum in sorted(enums, key=lambda x: x.attrib['value']):
                    refinement += "<input type='checkbox' value='" + enum.attrib['value'] + "' onchange='get_results_keyword_refined();'> " + enum.attrib['value'].title() + "<br/>"
                refinement += "<br/>"
                refinement += "</div>"
        except:
            print "ERROR AUTO GENERATION OF REFINEMENTS."
        refinement_options += refinement

    return HttpResponse(json.dumps({'refinements': refinement_options}), content_type='application/javascript')


################################################################################
#
# Function Name: refinements_to_mongo(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Build a refined mongo query (AND between types + OR between values of the same type)
#
################################################################################
def refinements_to_mongo(refinements):
    try:
        # transform the refinement in mongo query
        mongo_queries = dict()
        mongo_in = {}
        for refinement in refinements:
            splited_refinement = refinement.split(':')
            dot_notation = splited_refinement[0]
            dot_notation = "content." + dot_notation
            value = splited_refinement[1]
            if dot_notation in mongo_queries:
                mongo_queries[dot_notation].append(value)
            else:
                mongo_queries[dot_notation] = [value]

        for query in mongo_queries:
            key = query
            values = ({ '$in' : mongo_queries[query]})
            mongo_in[key] = values

        mongo_or = {'$and' : [mongo_in]}
        return mongo_or
    except:
        return []


################################################################################
#
# Function Name: custom_view(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Build Custom View
#
################################################################################
def custom_view(request):
    schema_name = request.GET['schema']

    schema = Template.objects().get(title=schema_name)

    xmlDocTree = etree.parse(BytesIO(schema.content.encode('utf-8')))

    # find the namespaces
    namespaces = common.get_namespaces(BytesIO(schema.content.encode('utf-8')))
    for prefix, url in namespaces.items():
        if url == SCHEMA_NAMESPACE:
            defaultPrefix = prefix
            break

    # building custom fields based on the schema
    custom_fields = ""

    # look for elements
    elements = xmlDocTree.findall(".//{0}element".format(LXML_SCHEMA_NAMESPACE))
    added_element_names = []
    for element in elements:
        if element.attrib['name'] not in added_element_names:
            added_element_names.append(element.attrib['name'])
            if is_field(element, xmlDocTree, defaultPrefix):
                app_info = common.getAppInfo(element)
                label = app_info['label'] if 'label' in app_info else element.attrib['name']
                label = label if label is not None else ''
                value = 'line_' + element.attrib['name']
                custom_fields += "<input type='checkbox' value='" + value + "'> " + label + "<br/>"

    # look for attributes
    attributes = xmlDocTree.findall(".//{0}attribute".format(LXML_SCHEMA_NAMESPACE))
    added_attribute_names = []
    for attribute in attributes:
        if attribute.attrib['name'] not in added_attribute_names:
            added_attribute_names.append(attribute.attrib['name'])
            if is_field(attribute, xmlDocTree, defaultPrefix):
                app_info = common.getAppInfo(attribute)
                label = app_info['label'] if 'label' in app_info else attribute.attrib['name']
                label = label if label is not None else ''
                value = 'line_' + attribute.attrib['name']
                custom_fields += "<input type='checkbox' value='" + value + "'> " + label + "<br/>"

    return HttpResponse(json.dumps({'custom_fields': custom_fields}), content_type='application/javascript')


################################################################################
#
# Function Name: is_field(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Look if the element is a field, and not a node
#
################################################################################
def is_field(element, xmlDocTree, defaultPrefix):
    # the element has a type
    if 'type' in element.attrib:
        # the element's type i
        if element.attrib['type'] in common.getXSDTypes(defaultPrefix):
            return True
        else:
            simple_type = xmlDocTree.find(".//{0}simpleType[@name='{1}']".format(LXML_SCHEMA_NAMESPACE, element.attrib['type']))
            if simple_type is not None:
                return True
            else:
                complex_type = xmlDocTree.find(".//{0}complexType[@name='{1}']".format(LXML_SCHEMA_NAMESPACE, element.attrib['type']))
                if complex_type is not None:
                    simple_content = complex_type.find("./{0}simpleContent".format(LXML_SCHEMA_NAMESPACE))
                    if simple_content is not None:
                        return True
    else:
        simple_type = xmlDocTree.find("./{0}simpleType".format(LXML_SCHEMA_NAMESPACE))
        if simple_type is not None:
            return True
        else:
            complex_type = xmlDocTree.find(".//{0}complexType".format(LXML_SCHEMA_NAMESPACE))
            if complex_type is not None:
                simple_content = complex_type.find("./{0}simpleContent".format(LXML_SCHEMA_NAMESPACE))
                if simple_content is not None:
                    return True
    return False


################################################################################
#
# Function Name: delete_result(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Delete an XML document from the database
#
################################################################################
def delete_result(request):
    result_id = request.GET['result_id']

    try:
        if request.user.is_superuser:
            XMLdata.delete(result_id)
            messages.add_message(request, messages.INFO, 'Resource deleted with success.')
    except:
        # XML can't be found
        pass

    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: update_publish(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Publish and update the publish date of an XMLdata
#
################################################################################
def update_publish(request):
    XMLdata.update_publish(request.GET['result_id'])
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: update_unpublish(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Unpublish an XMLdata
#
################################################################################
def update_unpublish(request):
    XMLdata.update_unpublish(request.GET['result_id'])
    return HttpResponse(json.dumps({}), content_type='application/javascript')
