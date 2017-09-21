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
from django.conf import settings
from io import BytesIO
import os
import json
import lxml.etree as etree
from mgi.models import Template, Instance, TemplateVersion, OaiRecord, OaiMetadataFormat, OaiRegistry, XMLdata
from django.template import loader, Context, RequestContext
from urlparse import urlparse
import hashlib
from itertools import groupby
from utils.XSDRefinements import Tree
from collections import OrderedDict

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

    keyword = request.POST.get('keyword', '')
    schemas = request.POST.getlist('schemas[]', [])
    user_schemas = request.POST.getlist('userSchemas[]', [])
    refinements = refinements_to_mongo(json.loads(request.POST.get('refinements', '{}')))
    registries = request.POST.getlist('registries[]', [])
    if 'onlySuggestions' in request.POST:
        onlySuggestions = json.loads(request.POST['onlySuggestions'])
    else:
        onlySuggestions = False

    metadata_format_ids = _get_metadata_formats_id(schemas=schemas, user_schemas=user_schemas, registries=registries)
    instanceResults = OaiRecord.executeFullTextQuery(keyword, metadata_format_ids, refinements)
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
        registriesURL = {}
        for registryId in listRegistriesID:
            obj = OaiRegistry.objects(pk=registryId).get()
            registriesName[str(registryId)] = obj.name
            registriesURL[str(registryId)] = obj.url
        listSchemaId = set([x['metadataformat'] for x in instanceResults])
        for schemaId in listSchemaId:
            obj = OaiMetadataFormat.objects(pk=schemaId).get()
            objMetadataFormats[str(schemaId)] = obj

        listItems = []
        xmltodictunparse = XMLdata.unparse
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

                registry_name = registriesName[instanceResult['registry']]
                if len(registry_name) > 30:
                    registry_name = "{0}...".format(registry_name[:30])

                url = urlparse(registriesURL[instanceResult['registry']])
                context = RequestContext(request, {'id':str(instanceResult['_id']),
                                   'xml': str(newdom),
                                   'title': instanceResult['identifier'],
                                   'custom_xslt': custom_xslt,
                                   'template_name': metadataFormat.template.title,
                                   'registry_name': registry_name,
                                   'registry_url': "{0}://{1}".format(url.scheme, url.netloc),
                                   'oai_pmh': True})


                resultString+= template.render(context)

        else:
            for instanceResult in instanceResults[:20]:
                wordList = re.sub("[^\w]", " ",  keyword).split()
                wordList = [x + "|" + x +"\w+" for x in wordList]
                wordList = '|'.join(wordList)
                listWholeKeywords = re.findall("\\b("+ wordList +")\\b", XMLdata.unparse(instanceResult['metadata']).encode('utf-8'), flags=re.IGNORECASE)
                labels = list(set(listWholeKeywords))

                for label in labels:
                    label = label.lower()
                    result_json = {}
                    result_json['label'] = label
                    result_json['value'] = label
                    if not result_json in resultsByKeyword:
                        resultsByKeyword.append(result_json)

    print 'END def getResultsKeyword(request)'
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
    mongo_or = []
    mongo_and = {}
    try:
        # transform the refinement in mongo query
        for refinement in refinements:
            mongo_queries = dict()
            mongo_in = {}
            ref_value = refinement['value']
            for elt in ref_value:
                splited_refinement = elt.split('==')
                dot_notation = splited_refinement[0]
                dot_notation = "metadata." + dot_notation
                value = splited_refinement[1]
                if dot_notation in mongo_queries:
                    mongo_queries[dot_notation].append(value)
                else:
                    mongo_queries[dot_notation] = [value]

            for query in mongo_queries:
                key = query
                values = ({'$in': mongo_queries[query]})
                mongo_in[key] = values
                # Case of the element has attributes
                mongo_in[key + ".#text"] = values

            mongo_or.append({'$or': [{x: mongo_in[x]} for x in mongo_in]})

        if len(mongo_or) > 0:
            mongo_and = {'$and': mongo_or}

        return mongo_and
    except:
        return {}


def get_results_occurrences(request):
    print 'BEGIN def getResultsKeyword(request)'

    tree_info = []
    tree_count = []
    cache_instances = {}
    keyword = request.POST.get('keyword', '')
    schemas = request.POST.getlist('schemas[]', [])
    user_schemas = request.POST.getlist('userSchemas[]', [])
    refinements = json.loads(request.POST.get('refinements', '{}'))
    all_refinements = json.loads(request.POST.get('allRefinements', {}))
    registries = request.POST.getlist('registries[]', [])
    splitter = ":"

    metadata_format_ids = _get_metadata_formats_id(schemas=schemas, user_schemas=user_schemas, registries=registries)
    try:
        for current in all_refinements:
            refine = []
            for x in refinements:
                if x['key'] != current['key']:
                    refine.append(x)

            list_refinements = refinements_to_mongo(refine)
            json_refinements = json.dumps(list_refinements)
            if not cache_instances.has_key(json_refinements):
                instance_results = OaiRecord.executeFullTextQuery(keyword, metadata_format_ids, list_refinements,
                                                                  only_content=True)
                cache_instances[json_refinements] = instance_results
            else:
                instance_results = cache_instances[json_refinements]
            for refinement in current['value']:
                ids = _get_list_ids_for_refinement(instance_results, refinement)
                tree_count.append({"refinement": refinement, "ids": ids})
                result_json = {'text_id': hashlib.sha1(refinement).hexdigest(), 'nb_occurrences': len(ids)}
                tree_info.append(result_json)

            # For categories
            max_level = max(len(x['refinement'].split(splitter)) for x in tree_count)
            for i in range(max_level, 0, -1):
                grouper = lambda x: ":".join(x['refinement'].split(splitter)[:i])
                for key, grp in groupby(sorted(tree_count, key=grouper), grouper):
                    if len(key.split(splitter)) == i:
                        ids = []
                        for item in grp:
                            ids.extend(item["ids"])
                        key_category = "{0}_{1}".format(key, Tree.TreeInfo.get_category_label())
                        result_json = {'text_id': hashlib.sha1(key_category).hexdigest(),
                                       'nb_occurrences': len(sorted(set(ids)))}
                        tree_info.append(result_json)


    except Exception, e:
        pass

    return json.dumps({'items': tree_info})


def _get_metadata_formats_id(schemas, user_schemas, registries):
    # We get all template versions for the given schemas
    # First, we take care of user defined schema
    templates_id_user = Template.objects(title__in=user_schemas).distinct(field="id")
    templates_id_user = [str(x) for x in templates_id_user]
    # Take care of the rest, with versions
    templates_versions = Template.objects(title__in=schemas).distinct(field="templateVersion")
    # We get all templates ID, for all versions
    all_templates_id_common = TemplateVersion.objects(pk__in=templates_versions, isDeleted=False)\
        .distinct(field="versions")
    # We remove the removed version
    all_templates_id_common_removed = TemplateVersion.objects(pk__in=templates_versions, isDeleted=False)\
        .distinct( field="deletedVersions")
    templates_id_common = list(set(all_templates_id_common) - set(all_templates_id_common_removed))
    templates_id = templates_id_user + templates_id_common
    if len(registries) == 0:
        # We retrieve deactivated registries so as not to get their metadata formats
        deactivatedRegistries = [str(x.id) for x in OaiRegistry.objects(isDeactivated=True).order_by('id')]
        metadataFormatsID = OaiMetadataFormat.objects(template__in=templates_id,
                                                      registry__not__in=deactivatedRegistries).distinct(field="id")
    else:
        # We retrieve registries from the refinement
        metadataFormatsID = OaiMetadataFormat.objects(template__in=templates_id, registry__in=registries).distinct(
            field="id")

    return metadataFormatsID


def _get_list_ids_for_refinement(dictionary, refinement):
    ids = []
    try:
        key = "metadata."+refinement.split("==")[0]
        value = refinement.split("==")[1]
        for item in dictionary:
            try:
                _id = str(item['_id'])
                for index in key.split("."):
                    if index in item:
                        item = item[index]
                    else:
                        break

                if isinstance(item, list):
                    for elt in item:
                        if isinstance(elt, dict) and index in elt and elt[index] == value:
                                ids.append(_id)
                        elif elt == value:
                            ids.append(_id)
                # If the item has attributes
                elif isinstance(item, OrderedDict):
                    if "#text" in item and item['#text'] == value:
                        ids.append(_id)
                elif item == value:
                    ids.append(_id)
            except (IndexError, Exception):
                pass
    except Exception:
        pass

    return ids
