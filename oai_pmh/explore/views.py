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

# Responses
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from oai_pmh.explore.forms import KeywordForm, MetadataFormatsForm
from mgi.models import OaiMetadataFormat, OaiRegistry, OaiRecord, XMLdata
import json
import os
from mgi import settings
from lxml import etree
from io import BytesIO
from collections import OrderedDict

################################################################################
#
# Function Name: index(request)
# Inputs:        request -
# Outputs:       Data Exploration by keyword homepage
# Exceptions:    None
# Description:   renders the data exploration by keyword home page from template
#                (index.html)
#
################################################################################
@login_required(login_url='/login')
def index_keyword(request):
    template = loader.get_template('oai_pmh/explore/explore_keyword.html')
    search_form = KeywordForm(request.user.id)
    context = RequestContext(request, {
        'search_Form':search_form,
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: get_metadata_formats(request)
# Inputs:        request -
# Outputs:       Metadata Formats
# Exceptions:    None
# Description:   Return a form with common metadata formats for registries given in parameter
#
################################################################################
@login_required(login_url='/login')
def get_metadata_formats(request):
    template = loader.get_template('oai_pmh/explore/explore_metadata_formats.html')
    #Get registries
    listRegistriesId = request.GET.getlist('registries[]')
    #Create the form
    metadata_formats_Form = MetadataFormatsForm(listRegistriesId)
    context = RequestContext(request, {
        'metadata_formats_Form':metadata_formats_Form,
    })

    return HttpResponse(json.dumps({'form': template.render(context)}), content_type='application/javascript')


################################################################################
#
# Function Name: get_metadata_formats_detail(request)
# Inputs:        request -
# Outputs:       Metadata formats information
# Exceptions:    None
# Description:   Return information about metadata format given in parameter
#
################################################################################
@login_required(login_url='/login')
def get_metadata_formats_detail(request):
    template = loader.get_template('oai_pmh/explore/explore_metadata_formats_detail.html')
    try:
        #Get metadata formats
        infos = json.loads(request.GET['metadataFormats'])
        metadataFormats = infos['oai-pmh']
        if 'local' in infos:
            localTemplate = infos['local']
        else:
            localTemplate = None
    except:
        metadataFormats = []
        localTemplate = None

    list_metadata_formats = OaiMetadataFormat.objects(pk__in=metadataFormats).all()
    list_metadata_formats_info = []
    for metadataFormat in list_metadata_formats:
        item = {
            'registry' : OaiRegistry.objects(isDeactivated=False).only('name').get(pk=metadataFormat.registry).name,
            'metadataPrefix' : metadataFormat.metadataPrefix,
            'schema' : metadataFormat.schema,
        }
        list_metadata_formats_info.append(item)

    context = RequestContext(request, {
        'list_metadata_formats_info': list_metadata_formats_info,
        'local' : localTemplate
    })

    return HttpResponse(json.dumps(template.render(context)), content_type='application/javascript')


################################################################################
#
# Function Name: explore_detail_result_process
# Inputs:        request -
# Outputs:       Detail of result
# Exceptions:    None
# Description:   Page that allows to see detail result from a selected result
#
################################################################################
def explore_detail_result_keyword(request) :
    template = loader.get_template('oai_pmh/explore/explore_detail_results_keyword.html')
    result_id = request.GET['id']
    record = OaiRecord.objects.get(pk=result_id)
    # schemaId = xmlString['schema']
    if 'title' in request.GET:
        title = request.GET['title']
    else:
        title = record.identifier
    xmlString = XMLdata.unparse(record.getMetadataOrdered()).encode('utf-8')
    xsltPath = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'xml2html.xsl')
    xslt = etree.parse(xsltPath)
    transform = etree.XSLT(xslt)
    dom = etree.fromstring(str(xmlString))

    #Check if a custom list result XSLT has to be used
    try:
        metadataFormat = record.metadataformat
        if metadataFormat.template.ResultXsltDetailed:
            listXslt = etree.parse(BytesIO(metadataFormat.template.ResultXsltDetailed.content.encode('utf-8')))
            transform = etree.XSLT(listXslt)
            newdom = transform(dom)
        else:
            newdom = transform(dom)
    except Exception, e:
        #We use the default one
        newdom = transform(dom)

    registry_name = OaiRegistry.objects.get(pk=record.registry).name
    if len(registry_name) > 30:
        registry_name = "{0}...".format(registry_name[:30])

    result = str(newdom)
    context = RequestContext(request, {
        'XMLHolder': result,
        'title': title,
        'oai_pmh': True,
        'registry_name': registry_name,
        "template_name": record.metadataformat.template.title if record.metadataformat.template else '',
    })

    return HttpResponse(template.render(context))
