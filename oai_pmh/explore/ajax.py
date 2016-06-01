################################################################################
#
# File Name: ajax.py
# Application: explore
# Purpose:   AJAX methods used for Explore purposes
#
# Author: Pierre Francois RIGODIAT
#         pierre-francois.rigodiat@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

import re
from django.http import HttpResponse
from django.conf import settings
from io import BytesIO
import xmltodict
import os
import json
import lxml.etree as etree
from mgi.models import Template, Instance, TemplateVersion, OaiRecord, OaiMetadataFormat, OaiRegistry
from django.template import loader, Context, RequestContext


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
        elif isinstance(value, unicode):
            if (len(value) >= 2 and value[0] == "/" and value[-1] == "/"):
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
    instance = Instance(name="Local", protocol=protocol, address=request.META['REMOTE_ADDR'], port=request.META['SERVER_PORT'], access_token="token", refresh_token="token")
    json_instances.append(instance.to_json())
    request.session['instancesExplore'] = json_instances
    sessionName = "resultsExploreOaiPMh" + instance['name']


    try:
        keyword = request.GET['keyword']
        schemas = request.GET.getlist('schemas[]')
        userSchemas = request.GET.getlist('userSchemas[]')
        refinements = refinements_to_mongo(request.GET.getlist('refinements[]'))
        if 'onlySuggestions' in request.GET:
            onlySuggestions = json.loads(request.GET['onlySuggestions'])
        else:
            onlySuggestions = False
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
    #We retrieve deactivated registries so as not to get their metadata formats
    deactivatedRegistries = [str(x.id) for x in OaiRegistry.objects(isDeactivated=True).order_by('id')]
    metadataFormatsID = OaiMetadataFormat.objects(template__in=templatesID, registry__not__in=deactivatedRegistries).distinct(field="id")


    instanceResults = OaiRecord.executeFullTextQuery(keyword, metadataFormatsID, refinements)
    if len(instanceResults) > 0:
        if not onlySuggestions:
            xsltPath = os.path.join(settings.SITE_ROOT, 'static/resources/xsl/xml2html.xsl')
            xslt = etree.parse(xsltPath)
            transform = etree.XSLT(xslt)
            template = loader.get_template('oai_pmh/explore/explore_result_keyword.html')

        #Retrieve schema and registries. Avoid to retrieve the information for each result
        registriesName = {}
        objMetadataFormats = {}
        listRegistriesID = set([x['registry'] for x in instanceResults])
        for registryId in listRegistriesID:
            obj = OaiRegistry.objects(pk=registryId).get()
            registriesName[str(registryId)] = obj.name
        listSchemaId = set([x['metadataformat'] for x in instanceResults])
        for schemaId in listSchemaId:
            obj = OaiMetadataFormat.objects(pk=schemaId).get()
            objMetadataFormats[str(schemaId)] = obj

        listItems = []
        xmltodictunparse = xmltodict.unparse
        appendResult = results.append
        toXML = etree.XML
        parse = etree.parse
        XSLT = etree.XSLT
        if not onlySuggestions:
            for instanceResult in instanceResults:
                custom_xslt = False
                appendResult({'title':instanceResult['identifier'], 'content':xmltodictunparse(instanceResult['metadata']),'id':str(instanceResult['_id'])})
                dom = toXML(str(xmltodictunparse(instanceResult['metadata']).encode('utf-8')))
                #Check if a custom list result XSLT has to be used
                try:
                    metadataFormat = objMetadataFormats[str(instanceResult['metadataformat'])]
                    if metadataFormat.template.ResultXsltList:
                        listXslt = parse(BytesIO(metadataFormat.template.ResultXsltList.content.encode('utf-8')))
                        listTransform = XSLT(listXslt)
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
                                   'title': instanceResult['identifier'],
                                   'custom_xslt': custom_xslt,
                                   'schema_name': metadataFormat.metadataPrefix,
                                   'registry_name': registriesName[instanceResult['registry']],
                                   'oai_pmh': True})


                resultString+= template.render(context)

        else:
            for instanceResult in instanceResults[:20]:
                wordList = re.sub("[^\w]", " ",  keyword).split()
                wordList = [x + "|" + x +"\w+" for x in wordList]
                wordList = '|'.join(wordList)
                listWholeKeywords = re.findall("\\b("+ wordList +")\\b", xmltodict.unparse(instanceResult['metadata']).encode('utf-8'), flags=re.IGNORECASE)
                labels = list(set(listWholeKeywords))

                for label in labels:
                    label = label.lower()
                    result_json = {}
                    result_json['label'] = label
                    result_json['value'] = label
                    if not result_json in resultsByKeyword:
                        resultsByKeyword.append(result_json)

    #We don't need those results in session
    # request.session[sessionName] = results
    print 'END def getResultsKeyword(request)'

    # return HttpResponse(json.dumps({'resultsByKeyword' : resultsByKeyword, 'resultString' : resultString, 'count' : len(instanceResults)}), content_type='application/javascript')
    return json.dumps({'resultsByKeyword' : resultsByKeyword, 'resultString' : resultString, 'count' : len(instanceResults)})



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
