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

from django.http import HttpResponseNotFound, HttpResponseBadRequest
from django.conf import settings
from django.views.generic import TemplateView
from mgi.models import XMLdata, OaiSettings, OaiMyMetadataFormat, OaiTemplMfXslt, Template, TemplateVersion, OaiMySet,\
    Status
from oai_pmh.server.exceptions import *
from bson.objectid import ObjectId
import lxml.etree as etree
import re
from oai_pmh import datestamp
import datetime
from exporter.builtin.models import XSLTExporter
from django.shortcuts import HttpResponse
from StringIO import StringIO
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from utils.XSDflattener.XSDflattener import XSDFlattenerDatabaseOrURL


class OAIProvider(TemplateView):
    content_type = 'text/xml'

################################################################################
#
# Function Name: render_to_response(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Render the XML file
#
################################################################################
    def render_to_response(self, context, **response_kwargs):
        # all OAI responses should be XML
        if 'content_type' not in response_kwargs:
            response_kwargs['content_type'] = self.content_type

        # add common context data needed for all responses
        context.update({
            'now': datestamp.datetime_to_datestamp(datetime.datetime.now()),
            'verb': self.oai_verb,
            'identifier': self.identifier if hasattr(self, 'identifier') else None,
            'metadataPrefix': self.metadataPrefix if hasattr(self, 'metadataPrefix') else None,
            'url': self.request.build_absolute_uri(self.request.path),
            'from': self.From if hasattr(self, 'From') else None,
            'until': self.until if hasattr(self, 'until') else None,
            'set': self.set if hasattr(self, 'set') else None,
        })
        #Render the template with the context information
        return super(TemplateView, self) \
            .render_to_response(context, **response_kwargs)

################################################################################
#
# Function Name: get_earliest_date(request)
# Inputs:        request -
# Outputs:       A datetime date
# Exceptions:    None
# Description:   Get the earliest date of publication
#
################################################################################
    def get_earliest_date(self):
        try:
            #Get the earliest publication date for the identify request response
            data = XMLdata.getMinValue('oai_datestamp')
            #If we have a date
            if data != None:
                return datestamp.datetime_to_datestamp(data)
            else:
                return ''
        except Exception:
            return ''

################################################################################
#
# Function Name: identify(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Response to identify request
#
################################################################################
    def identify(self):
        #Template name
        self.template_name = 'oai_pmh/xml/identify.xml'
        #Get settings information from database
        information = OaiSettings.objects.get()
        #If we have information
        if information:
            name = information.repositoryName
            repoIdentifier = information.repositoryIdentifier
        #If not, we use information from the settings file
        else:
            name = settings.OAI_NAME
            repoIdentifier = settings.OAI_REPO_IDENTIFIER
        #Fill the identify response
        identify_data = {
            'name': name,
            'protocole_version': settings.OAI_PROTOCOLE_VERSION,
            'admins': (email for name, email in settings.OAI_ADMINS),
            'earliest_date': self.get_earliest_date(),   # placeholder
            'deleted': settings.OAI_DELETED_RECORD,  # no, transient, persistent
            'granularity': settings.OAI_GRANULARITY,  # or YYYY-MM-DD
            'identifier_scheme': settings.OAI_SCHEME,
            'repository_identifier': repoIdentifier,
            'identifier_delimiter': settings.OAI_DELIMITER,
            'sample_identifier': settings.OAI_SAMPLE_IDENTIFIER
        }
        return self.render_to_response(identify_data)

################################################################################
#
# Function Name: list_sets(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Response to ListSets request
#
################################################################################
    def list_sets(self):
        self.template_name = 'oai_pmh/xml/list_sets.xml'
        items = []
        #For the moment, we don't support sets
        try:
            #Retrieve sets
            sets = OaiMySet.objects().all()
            #If there is no sets, we raise noSetHierarchy
            if len(sets) == 0:
                raise noSetHierarchy
            else:
                #Fill the response
                for set in sets:
                    item_info = {
                        'setSpec': set.setSpec,
                        'setName':  set.setName,
                        'description':  set.description
                    }
                    items.append(item_info)
            return self.render_to_response({'items': items})
        except OAIExceptions, e:
            return self.errors(e.errors)
        except OAIException, e:
            return self.error(e)
        except Exception, e:
            return HttpResponse({'content':e.message}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        except badResumptionToken, e:
            return self.error(badResumptionToken.code, badResumptionToken.message)

################################################################################
#
# Function Name: list_metadata_formats(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Response to ListMetadataFormats request
#
################################################################################
    def list_metadata_formats(self):
        try:
            #Template name
            self.template_name = 'oai_pmh/xml/list_metadata_formats.xml'
            items = []
            # If an identifier is provided, with look for its metadataformats
            if self.identifier != None:
                id = self.check_identifier()
                #We retrieve the template id for this record
                listId = []
                listId.append(id)
                listSchemaIds = XMLdata.getByIDsAndDistinctBy(listId, 'schema')
                if len(listSchemaIds) == 0:
                    raise idDoesNotExist(self.identifier)
                #Get metadata formats information for this template. The metadata formats must be activated
                metadataFormats = OaiTemplMfXslt.objects(template__in=listSchemaIds, activated=True).distinct(field='myMetadataFormat')
                #Get the template metadata format if existing
                metadataFormatsTemplate = OaiMyMetadataFormat.objects(template__in=listSchemaIds, isTemplate=True).all()
                if len(metadataFormatsTemplate) != 0:
                    metadataFormats.extend(metadataFormatsTemplate)
            else:
                #No identifier provided. We return all metadata formats available
                metadataFormats = OaiMyMetadataFormat.objects().all()
            #If there is no metadata formats, we raise noMetadataFormat
            if len(metadataFormats) == 0:
                raise noMetadataFormat
            else:
                #Fill the response
                for metadataFormat in metadataFormats:
                    item_info = {
                        'metadataNamespace': metadataFormat.metadataNamespace,
                        'metadataPrefix':  metadataFormat.metadataPrefix,
                        'schema':  metadataFormat.schema
                    }
                    items.append(item_info)

            return self.render_to_response({'items': items})
        except OAIExceptions, e:
            return self.errors(e.errors)
        except OAIException, e:
            return self.error(e)
        except Exception, e:
            return HttpResponse({'content':e.message}, status=HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################
#
# Function Name: list_identifiers(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Response to ListIdentifiers request
#
################################################################################
    def list_identifiers(self):
        try:
            #Template name
            self.template_name = 'oai_pmh/xml/list_identifiers.xml'
            query = dict()
            items=[]
            #Handle FROM and UNTIL
            query = self.check_dates()
            try:
                #Get the metadata format thanks to the prefix
                myMetadataFormat = OaiMyMetadataFormat.objects.get(metadataPrefix=self.metadataPrefix)
                #Get all template using it (activated True)
                templates = OaiTemplMfXslt.objects(myMetadataFormat=myMetadataFormat, activated=True).distinct(field="template")
                #Ids
                templatesID = [str(x.id) for x in templates]
                #If myMetadataFormat is linked to a template, we add the template id
                if myMetadataFormat.isTemplate:
                    templatesID.append(str(myMetadataFormat.template.id))
            except:
                #The metadata format doesn't exist
                raise cannotDisseminateFormat(self.metadataPrefix)
            if self.set:
                try:
                    setsTemplates = OaiMySet.objects(setSpec=self.set).only('templates').get()
                    templatesID = set(templatesID).intersection([str(x.id) for x in setsTemplates.templates])
                except Exception, e:
                    raise noRecordsMatch
            for template in templatesID:
                #Retrieve sets for this template
                sets = OaiMySet.objects(templates=template).all()
                query['schema'] = template
                #The record has to be published
                query['ispublished'] = True
                #Get all records for this template
                data = XMLdata.executeQueryFullResult(query)
                #IF no records, go to the next template
                if len(data) == 0:
                    continue
                for i in data:
                    #Fill the response
                    identifier = '%s:%s:id/%s' % (settings.OAI_SCHEME, settings.OAI_REPO_IDENTIFIER, str(i['_id']))
                    item_info = {
                        'identifier': identifier,
                        'last_modified': self.get_last_modified_date(i),
                        'sets': sets,
                        'deleted': i.get('status', '') == Status.DELETED
                    }
                    items.append(item_info)
            #If there is no records
            if len(items) == 0:
                raise noRecordsMatch

            return self.render_to_response({'items': items})
        except OAIExceptions, e:
            return self.errors(e.errors)
        except OAIException, e:
            return self.error(e)
        except Exception, e:
            return HttpResponse({'content':e.message}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        except badResumptionToken, e:
            return self.error(badResumptionToken.code, badResumptionToken.message)

################################################################################
#
# Function Name: get_record(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Response to GetRecord request
#
################################################################################
    def get_record(self):
        try:
            #Bool if we need to transform the XML via XSLT
            hasToBeTransformed = False
            #Check if the identifier pattern is OK
            id = self.check_identifier()
            #Template name
            self.template_name = 'oai_pmh/xml/get_record.xml'
            query = dict()
            #Convert id to ObjectId
            try:
                query['_id'] = ObjectId(id)
                #The record has to be published
                query['ispublished'] = True
            except Exception:
                raise idDoesNotExist(self.identifier)
            data = XMLdata.executeQueryFullResult(query)
            #This id doesn't exist
            if len(data) == 0:
                raise idDoesNotExist(self.identifier)
            data = data[0]
            #Get the template for the identifier
            template = data['schema']
            #Retrieve sets for this template
            sets = OaiMySet.objects(templates=template).all()
            #Retrieve the XSLT for the transformation
            try:
                #Get the metadataformat for the provided prefix
                myMetadataFormat = OaiMyMetadataFormat.objects.get(metadataPrefix=self.metadataPrefix)
                #If this metadata prefix is not associated to a template, we need to retrieve the XSLT to do the transformation
                if not myMetadataFormat.isTemplate:
                    hasToBeTransformed = True
                    #Get information about the XSLT for the MF and the template
                    objTempMfXslt = OaiTemplMfXslt.objects(myMetadataFormat=myMetadataFormat, template=template, activated=True).get()
                    #If no information or desactivated
                    if not objTempMfXslt.xslt:
                        raise cannotDisseminateFormat(self.metadataPrefix)
                    else:
                        #Get the XSLT for the transformation
                        xslt = objTempMfXslt.xslt
            except:
                raise cannotDisseminateFormat(self.metadataPrefix)

            #Transform XML data
            dataToTransform = [{'title': data['_id'], 'content': self.cleanXML(XMLdata.unparse(data['content']))}]
            if hasToBeTransformed:
                dataXML = self.getXMLTranformXSLT(dataToTransform, xslt)
            else:
                dataXML = dataToTransform

            #Fill the response
            record_info = {
                'identifier': self.identifier,
                'last_modified': self.get_last_modified_date(data),
                'sets': sets,
                'XML': dataXML[0]['content'],
                'deleted': data.get('status', '') == Status.DELETED
            }
            return self.render_to_response(record_info)
        except OAIExceptions, e:
            return self.errors(e.errors)
        except OAIException, e:
            return self.error(e)
        except Exception, e:
            return HttpResponse({'content':e.message}, status=HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: list_records(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Response to ListRecords request
#
################################################################################
    def list_records(self):
        try:
            items = []
            #Template name
            self.template_name = 'oai_pmh/xml/list_records.xml'
            query = dict()
            #Handle FROM and UNTIL
            query = self.check_dates()
            #Get the metadataformat for the provided prefix
            try:
                myMetadataFormat = OaiMyMetadataFormat.objects.get(metadataPrefix=self.metadataPrefix)
            except Exception, e:
                raise cannotDisseminateFormat(self.metadataPrefix)
            if myMetadataFormat.isTemplate:
                #GEt the corresponding template
                templatesID = [str(myMetadataFormat.template.id)]
            else:
                #Get information about templates using this MF
                objTempMfXslt = OaiTemplMfXslt.objects(myMetadataFormat=myMetadataFormat, activated=True).all()
                 #Ids
                templatesID = [str(x.template.id) for x in objTempMfXslt]
            #if a set was provided, we filter the templates
            if self.set:
                try:
                    setsTemplates = OaiMySet.objects(setSpec=self.set).only('templates').get()
                    templatesID = set(templatesID).intersection([str(x.id) for x in setsTemplates.templates])
                except Exception, e:
                    raise noRecordsMatch
            #For each template found
            for template in templatesID:
                #Retrieve sets for this template
                sets = OaiMySet.objects(templates=template).all()
                query['schema'] = template
                #The record has to be published
                query['ispublished'] = True
                #Get all records for this template
                data = XMLdata.executeQueryFullResult(query)
                #IF no records, go to the next template
                if len(data) == 0:
                    continue
                dataToTransform = [{'title': x['_id'], 'content': self.cleanXML(XMLdata.unparse(x['content']))} for x in data]
                if myMetadataFormat.isTemplate:
                    #No transformation needed
                    dataXML = dataToTransform
                else:
                    #Get the XSLT file
                    xslt = objTempMfXslt(template=template).get().xslt
                    #Transform all XML data (1 call)
                    dataXML = self.getXMLTranformXSLT(dataToTransform, xslt)
                #Add each record
                for elt in data:
                    identifier = '%s:%s:id/%s' % (settings.OAI_SCHEME, settings.OAI_REPO_IDENTIFIER,
                          elt['_id'])
                    xmlStr = filter(lambda xml: xml['title'] == elt['_id'], dataXML)[0]
                    record_info = {
                        'identifier': identifier,
                        'last_modified': self.get_last_modified_date(elt),
                        'sets': sets,
                        'XML': xmlStr['content'],
                        'deleted': elt.get('status', '') == Status.DELETED
                    }
                    items.append(record_info)

            #If there is no records
            if len(items) == 0:
                raise noRecordsMatch

            return self.render_to_response({'items': items})
        except OAIExceptions, e:
            return self.errors(e.errors)
        except OAIException, e:
            return self.error(e)
        except Exception, e:
            return HttpResponse({'content':e.message}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        except badResumptionToken, e:
            return self.error(badResumptionToken.code, badResumptionToken.message)


################################################################################
#
# Function Name: get_last_modified_date(request)
# Inputs:        element -
# Outputs:       Date
# Exceptions:    None
# Description:  Get last modified date
#
################################################################################
    def get_last_modified_date(self, element):
        try:
            date = datestamp.datetime_to_datestamp(element['oai_datestamp'])
        except:
            date = datestamp.datetime_to_datestamp(datetime.datetime.min)

        return date

################################################################################
#
# Function Name: error(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Error response. Just one error
#
################################################################################
    def error(self, error):
        return self.errors([error])

################################################################################
#
# Function Name: errors(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Errors response. Several errors
#
################################################################################
    def errors(self, errors):
        self.template_name = 'oai_pmh/xml/error.xml'
        return self.render_to_response({
            'errors': errors,
        })


################################################################################
#
# Function Name: check_illegal_and_required(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Check OAI Error and Exception - Illegal and required arguments
#
################################################################################
    def check_illegal_and_required(self, legal, required, data):
        errors = []
        #Check if a parameter doesn't have to be in the request
        illegal = [arg for arg in data if arg not in legal]
        #If yes, add error
        if len(illegal) > 0:
            for arg in illegal:
                error = 'Arguments ("%s") was passed that was not valid for ' \
                            'this verb' % arg
                errors.append(badArgument(error))
        #Check if a parameter is missing for the request
        missing = [arg for arg in required if arg not in data]
        if len(missing) > 0:
            for arg in missing:
                error = 'Missing required argument - %s' % arg
                errors.append(badArgument(error))
        #Raise exception.
        if len(errors) > 0:
            raise OAIExceptions(errors)

################################################################################
#
# Function Name: check_identifier(request)
# Inputs:        request -
# Outputs:       The record ID
# Exceptions:    None
# Description:   Check if the identifier is legal for the server
#
################################################################################
    def check_identifier(self):
        #Check if the identifier pattern is OK
        p = re.compile("%s:%s:id/(.*)" % (settings.OAI_SCHEME, settings.OAI_REPO_IDENTIFIER))
        idMatch = p.search(self.identifier)
        if idMatch:
            #If yes, we retrieve the record ID
            id = idMatch.group(1)
        else:
            raise idDoesNotExist(self.identifier)
        return id


################################################################################
#
# Function Name: check_dates(request)
# Inputs:        request -
# Outputs:       The Query filled with dates
# Exceptions:    None
# Description:   Check the dates' input
#
################################################################################
    def check_dates(self):
        query = dict()
        query_until = dict()
        query_from = dict()
        #To store errors
        date_errors = []
        #Handle FROM and UNTIL
        if self.until:
            try:
                endDate = datestamp.datestamp_to_datetime(self.until)
                query_until['oai_datestamp'] = {"$lte" : endDate}
            except:
                error = 'Illegal date/time for "until" (%s)' % self.until
                date_errors.append(badArgument(error))
        if self.From:
            try:
                startDate = datestamp.datestamp_to_datetime(self.From)
                query_from['oai_datestamp'] = {"$gte" : startDate}
            except:
                error = 'Illegal date/time for "from" (%s)' % self.From
                date_errors.append(badArgument(error))

        if self.until and self.From:
            query['$and'] = [query_until, query_from]
        elif self.until:
            query = query_until
        elif self.From:
            query = query_from

        #Return possible errors
        if len(date_errors) > 0:
            raise OAIExceptions(date_errors)

        return query

################################################################################
#
# Function Name: check_bad_argument(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Check OAI Error and Exception - Bad Argument in request
#
################################################################################
    def check_bad_argument(self, data):
        #Check if we have duplicate arguments
        duplicates = [arg for arg in data if len(data.getlist(arg)) > 1]
        if len(duplicates) > 0:
            error_msg = 'An argument ("multiple occurances of %s") was passed that was not valid for ' \
                        'this verb' % ', '.join(duplicates)
            raise badArgument(error_msg)

        #Build the illegal and required arguments depending of the verb
        if self.oai_verb == 'Identify':
            legal = ['verb']
            required = ['verb']
        elif self.oai_verb== 'ListIdentifiers':
            if 'resumptionToken' in data:
                legal = ['verb', 'resumptionToken']
                required = ['verb']
            else:
                legal = ['verb', 'metadataPrefix', 'from', 'until', 'set']
                required = ['verb', 'metadataPrefix']
        elif self.oai_verb == 'ListSets':
            legal = ['verb', 'resumptionToken']
            required = ['verb']
        elif self.oai_verb == 'ListMetadataFormats':
            legal = ['verb', 'identifier']
            required = ['verb']
        elif self.oai_verb == 'GetRecord':
            legal = ['verb', 'identifier', 'metadataPrefix']
            required = ['verb', 'identifier', 'metadataPrefix']
        elif self.oai_verb == 'ListRecords':
            if 'resumptionToken' in data:
                legal = ['verb', 'resumptionToken']
                required = ['verb']
            else:
                legal = ['verb', 'metadataPrefix', 'from', 'until', 'set']
                required = ['verb', 'metadataPrefix']
        else:
            error_msg = 'The verb "%s" is illegal' % self.oai_verb
            raise badVerb(error_msg)

        #Check
        self.check_illegal_and_required(legal, required, data)


################################################################################
#
# Function Name: get(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Determine OAI verb and hand off to appropriate
#
################################################################################
    def get(self, request, *args, **kwargs):
        try:
            #Check if the server is enabled for providing information
            information = OaiSettings.objects.get()
            if information and not information.enableHarvesting:
                return HttpResponseNotFound('<h1>OAI-PMH not available for harvesting</h1>')
            #Get the verb
            self.oai_verb = request.GET.get('verb', None)
            if self.oai_verb is None:
                error_msg = 'The request did not provide any verb.'
                raise badVerb(error_msg)
            #Init
            self.request = request
            self.identifier = None
            self.metadataPrefix = None
            self.From = None
            self.until = None
            self.set = None
            self.resumptionToken = None

            #Verb processing. Get informations depending of the verb
            if self.oai_verb == 'Identify':
                #Check entry
                self.check_bad_argument(request.GET)
                return self.identify()
            elif self.oai_verb == 'ListIdentifiers':
                self.From = request.GET.get('from', None)
                self.until = request.GET.get('until', None)
                self.set = request.GET.get('set', None)
                self.resumptionToken = request.GET.get('resumptionToken', None)
                self.metadataPrefix = request.GET.get('metadataPrefix', None)
                #Check entry
                self.check_bad_argument(request.GET)
                #TODO Support resumptionToken
                if self.resumptionToken != None:
                    raise badResumptionToken(self.resumptionToken)
                else:
                    return self.list_identifiers()
            elif self.oai_verb == 'ListSets':
                #Check entry
                self.check_bad_argument(request.GET)
                return self.list_sets()
            elif self.oai_verb == 'ListMetadataFormats':
                self.resumptionToken = request.GET.get('resumptionToken', None)
                self.identifier = request.GET.get('identifier', None)
                #Check entry
                self.check_bad_argument(request.GET)
                #TODO Support resumptionToken
                if self.resumptionToken != None:
                    raise badResumptionToken(self.resumptionToken)
                else:
                    return self.list_metadata_formats()
            elif self.oai_verb == 'GetRecord':
                self.identifier = request.GET.get('identifier', None)
                self.metadataPrefix = request.GET.get('metadataPrefix', None)
                #Check entry
                self.check_bad_argument(request.GET)
                return self.get_record()
            elif self.oai_verb == 'ListRecords':
                self.From = request.GET.get('from', None)
                self.until = request.GET.get('until', None)
                self.set = request.GET.get('set', None)
                self.resumptionToken = request.GET.get('resumptionToken', None)
                self.metadataPrefix = request.GET.get('metadataPrefix', None)
                #Check entry
                self.check_bad_argument(request.GET)
                #TODO Support resumptionToken
                if self.resumptionToken != None:
                    raise badResumptionToken(self.resumptionToken)
                else:
                    return self.list_records()
            else:
                error_msg = 'The verb "%s" is illegal' % self.oai_verb
                raise badVerb(error_msg)

        except OAIExceptions, e:
            return self.errors(e.errors)
        except OAIException, e:
            return self.error(e)
        except Exception, e:
            return HttpResponse({'content':e.message}, status=HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################
#
# Function Name: getTranformXSLT(request)
# Inputs:        request -
# Outputs:       A list of dict
# Exceptions:    None
# Description:   Transform XSLT
#
################################################################################
    def getXMLTranformXSLT(self, dataXML, xslt):
        #Use the exporter to transform record thanks to an XSLT
        #Declare XSLTExporter.
        exporter = XSLTExporter()
        exporter._setXslt(xslt.content)
        #Transformation
        contentRes = exporter._transform(dataXML)
        #Return the transformed XMLs
        return contentRes

################################################################################
#
# Function Name: cleanXML(request)
# Inputs:        request -
# Outputs:       XML
# Exceptions:    None
# Description:   Clean XML
#
################################################################################
    def cleanXML(self, xml):
        clean_parser = etree.XMLParser(remove_blank_text=True,remove_comments=True,remove_pis=True)
        # set the parser
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        xmlEncoding = etree.XML(str(xml.encode('utf-8')))
        xmlStr = etree.tostring(xmlEncoding)
        return xmlStr


################################################################################
#
# Function Name: get_xsd(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Page that allows to retrieve an XML Schema by its name
#
################################################################################
def get_xsd(request, schema):
    # TODO Available if publication ok and no user template
    # We retrieve the schema filename in the schema attribute
    # Get the templateVersion ID
    try:
        templatesVersionID = Template.objects(filename=schema).distinct(field="templateVersion")
        templateID = TemplateVersion.objects(pk__in=templatesVersionID, isDeleted=False).distinct(field="current")
        template = Template.objects.get(pk=templateID[0])
        flattener = XSDFlattenerDatabaseOrURL(template.content.encode('utf-8'))
        content_encoded = flattener.get_flat()
        file_obj = StringIO(content_encoded)

        return HttpResponse(file_obj, content_type='text/xml')
    except Exception, e:
        return HttpResponseBadRequest('Impossible to retrieve the schema with the given name.')
