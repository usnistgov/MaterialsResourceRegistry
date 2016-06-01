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

# Responses
from django.core.servers.basehttp import FileWrapper
from rest_framework import status
from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect
# Requests
import requests
from oai_pmh.forms import RequestForm
import json
import os
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
OAI_HOST_URI = settings.OAI_HOST_URI
OAI_USER = settings.OAI_USER
OAI_PASS = settings.OAI_PASS
from django.template import RequestContext, loader
from mgi.models import XML2Download
import datetime
from mgi.models import OaiSet, OaiMetadataFormat
from django.contrib.auth.decorators import login_required
from django.conf import settings
import lxml.etree as etree
import os
from StringIO import StringIO
from django.core.urlresolvers import reverse
from oai_pmh.api.messages import APIMessage
import urllib

################################################################################
#
# Function Name: download_xml_build_req(request)
# Inputs:        request -
# Outputs:       XML representation of the current build request
# Exceptions:    None
# Description:   Returns an XML representation of the current build request.
#                Used when user wants to download the OAI-PMH XML file.
#
################################################################################
@login_required(login_url='/login')
def download_xml_build_req(request):
    #POST request
    if request.method == 'POST':
        if 'xmlStringOAIPMH' in request.session:
            #We retrieve the XML file in session
            xmlDataObject = request.session['xmlStringOAIPMH']
            try:
                # Load a parser able to clean the XML from blanks, comments and processing instructions
                clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
                # set the parser
                etree.set_default_parser(parser=clean_parser)
                # load the XML tree from the text
                xmlDoc = etree.XML(str(xmlDataObject.encode('utf-8')))
                xmlStringEncoded = etree.tostring(xmlDoc, pretty_print=True)
            except:
                xmlStringEncoded = xmlDataObject

            #Get the date to append it to the file title
            i = datetime.datetime.now()
            title = "OAI_PMH_BUILD_REQ_%s_.xml" % i.isoformat()
            #Use the XML2Download collection to save the XML to download. We can't directly return the XML
            #because this method is called via Ajax. We need to save the XML and call the GET request of this function
            #in the success part of the Ajax call
            xml2download = XML2Download(title=title, xml=xmlStringEncoded).save()
            xml2downloadID = str(xml2download.id)
            #Return the ID to call the GET request with it
            response_dict = {"xml2downloadID": xml2downloadID}
            return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
        else:
            return HttpResponseBadRequest('An error occured. Please reload the page and try again.')
    else:
        #Get the XML2Download ID
        xml2downloadID = request.GET.get('id', None)
        if xml2downloadID is not None:
            #Get the XML
            xmlDataObject = XML2Download.objects.get(pk=xml2downloadID)
            #Encode the XML
            xmlStringEncoded = xmlDataObject.xml.encode('utf-8')
            fileObj = StringIO(xmlStringEncoded)
            #Delete the record
            xmlDataObject.delete()
            #Check that the file is ending by .xml
            if not xmlDataObject.title.lower().endswith('.xml'):
                xmlDataObject.title += ".xml"
            #Return the XML file
            response = HttpResponse(FileWrapper(fileObj), content_type='application/xml')
            response['Content-Disposition'] = 'attachment; filename=' + xmlDataObject.title
            request.session['xmlStringOAIPMH'] = xmlStringEncoded

            return response
        else:
            return redirect('/')


################################################################################
#
# Function Name: all_sets(request)
# Inputs:        request -
# Outputs:       List of set's name
# Exceptions:    None
# Description:   Returns all the sets of a registry.
#
################################################################################
@login_required(login_url='/login')
def all_sets(request, registry):
    sets = []
    #Get all sets information
    registrySets = OaiSet.objects(registry=registry).order_by("setName")
    for set in registrySets:
        sets.append({'key': set.setName, 'value': set.setSpec})
    return HttpResponse(json.dumps(sets), content_type="application/javascript")

################################################################################
#
# Function Name: all_metadataprefix(request)
# Inputs:        request -
# Outputs:       List of metadataprefix's name
# Exceptions:    None
# Description:   Returns all the sets of a registry.
#
################################################################################
@login_required(login_url='/login')
def all_metadataprefix(request, registry):
    prefix = []
    #Get all metadataprefix information
    metadataformats = OaiMetadataFormat.objects(registry=registry).order_by("metadataPrefix")
    for format in metadataformats:
        prefix.append(format.metadataPrefix)
    return HttpResponse(json.dumps(prefix), content_type="application/javascript")

################################################################################
#
# Function Name: getData(request)
# Inputs:        request -
# Outputs:       XML representation of the build request response
# Exceptions:    None
# Description:   Returns OAI PMH response
#
################################################################################
@login_required(login_url='/login')
def getData(request):
    url = request.POST['url']
    args_url = json.loads(request.POST['args_url'])
    #Encode args for the Get request
    encoded_args = urllib.urlencode(args_url)
    #Build the url
    url = url + "?" + encoded_args
    uri= OAI_HOST_URI + reverse("api_get_data")
    req = requests.post(uri, {"url":url}, auth=(OAI_USER, OAI_PASS))
    if req.status_code == status.HTTP_200_OK:
        data = json.load(StringIO(req.content))

        xsltPath = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'xml2html.xsl')
        xslt = etree.parse(xsltPath)
        transform = etree.XSLT(xslt)

        XMLParser = etree.XMLParser(remove_blank_text=True, recover=True)
        dom = etree.XML(str(data.encode("utf8")),  parser=XMLParser)
        request.session['xmlStringOAIPMH'] = str(data.encode("utf8"))
        newdom = transform(dom)
        xmlTree = str(newdom)

        content = {'message' : xmlTree}
        return HttpResponse(json.dumps(content), content_type="application/javascript")
    else:
        data = json.load(StringIO(req.content))
        return HttpResponseBadRequest(data[APIMessage.label], content_type="application/javascript")


################################################################################
#
# Function Name: oai_pmh_build_request(request)
# Inputs:        request -
# Outputs:       OAI-PMH Page
# Exceptions:    None
# Description:   Page that allows to manage OAI-PMH
#
################################################################################
@login_required(login_url='/login')
def oai_pmh_build_request(request):
    #Get the template
    template = loader.get_template('oai_pmh/oai_pmh_build_request.html')
    #Build the form
    requestForm = RequestForm();
    context = RequestContext(request, {'request_form': requestForm})
    return HttpResponse(template.render(context))
