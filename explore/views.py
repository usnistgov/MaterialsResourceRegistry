################################################################################
#
# File Name: views.py
# Application: explore
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

from django.http import HttpResponse
from django.template import RequestContext, loader, Context
from django.shortcuts import redirect
from django.conf import settings
from mgi.models import Instance, SavedQuery, XMLdata, ExporterXslt
import mgi.rights as RIGHTS
from cStringIO import StringIO
import zipfile
import lxml.etree as etree
import os
import json
from explore.forms import *
from exporter import get_exporter
from io import BytesIO
from exporter.builtin.models import XSLTExporter
from admin_mdcs.models import permission_required


################################################################################
#
# Function Name: index(request)
# Inputs:        request - 
# Outputs:       Data Exploration homepage
# Exceptions:    None
# Description:   renders the main data exploration home page from template 
#                (index.html)
#
################################################################################
@permission_required(content_type=RIGHTS.explore_content_type, permission=RIGHTS.explore_access, login_url='/login')
def index(request):
    currentTemplateVersions = []
    for tpl_version in TemplateVersion.objects():
        currentTemplateVersions.append(tpl_version.current)

    currentTemplates = dict()
    for tpl_version in currentTemplateVersions:
        tpl = Template.objects.get(pk=tpl_version)
        templateVersions = TemplateVersion.objects.get(pk=tpl.templateVersion)
        currentTemplates[tpl] = templateVersions.isDeleted

    template = loader.get_template('explore/explore.html')
    context = RequestContext(request, {
    'templates':currentTemplates,
    'userTemplates': Template.objects(user=str(request.user.id)),
    })

    return HttpResponse(template.render(context))


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
@permission_required(content_type=RIGHTS.explore_content_type, permission=RIGHTS.explore_access, login_url='/login')
def index_keyword(request):
    template = loader.get_template('explore/explore_keyword.html')
    search_form = KeywordForm(request.user.id)
    context = RequestContext(request, {
        'search_Form':search_form,
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: explore_select_template(request)
# Inputs:        request -
# Outputs:       Main Page of Explore Application
# Exceptions:    None
# Description:   Page that allows to select a template to start Exploring
#
################################################################################
@permission_required(content_type=RIGHTS.explore_content_type, permission=RIGHTS.explore_access, login_url='/login')
def explore_select_template(request):
    template = loader.get_template('explore/explore.html')
    context = RequestContext(request, {
        '': '',
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: explore_customize_template(request)
# Inputs:        request -
# Outputs:       Customize Template Page
# Exceptions:    None
# Description:   Page that allows to select fields being used during Exploration
#
################################################################################
@permission_required(content_type=RIGHTS.explore_content_type, permission=RIGHTS.explore_access, login_url='/login')
def explore_customize_template(request):
    template = loader.get_template('explore/explore_customize_template.html')
    context = RequestContext(request, {
    })
    if 'exploreCurrentTemplateID' not in request.session:
        return redirect('/explore/select-template')
    else:
        return HttpResponse(template.render(context))


################################################################################
#
# Function Name: explore_perform_search(request)
# Inputs:        request -
# Outputs:       Perform Search Page
# Exceptions:    None
# Description:   Page that allows to submit queries
#
################################################################################
@permission_required(content_type=RIGHTS.explore_content_type, permission=RIGHTS.explore_access, login_url='/login')
def explore_perform_search(request):
    try:
        template = loader.get_template('explore/explore_perform_search.html')
        instances = Instance.objects()
        if 'HTTPS' in request.META['SERVER_PROTOCOL']:
            protocol = "https"
        else:
            protocol = "http"
        local = Instance(name="Local", protocol=protocol, address=request.META['REMOTE_ADDR'], port=request.META['SERVER_PORT'])
        listInstances = [local]
        for instance in instances:
            listInstances.append(instance)

        template_hash = Template.objects.get(pk=request.session['exploreCurrentTemplateID']).hash

        queries = SavedQuery.objects(user=str(request.user.id), template=str(request.session['exploreCurrentTemplateID']))
        context = RequestContext(request, {
            'instances': listInstances,
            'template_hash': template_hash,
            'queries':queries,
            'template_id': request.session['exploreCurrentTemplateID']
        })
        if 'exploreCurrentTemplateID' not in request.session:
            return redirect('/explore/select-template')
        else:
            return HttpResponse(template.render(context))
    except:
        return redirect("/explore")


################################################################################
#
# Function Name: explore_results(request)
# Inputs:        request -
# Outputs:       Query results page
# Exceptions:    None
# Description:   Page that allows to see results from a query
#
################################################################################
@permission_required(content_type=RIGHTS.explore_content_type, permission=RIGHTS.explore_access, login_url='/login')
def explore_results(request):
    template = loader.get_template('explore/explore_results.html')
    context = RequestContext(request, {
        '': '',
    })
    if 'exploreCurrentTemplateID' not in request.session:
        return redirect('/explore/select-template')
    else:
        return HttpResponse(template.render(context))


################################################################################
#
# Function Name: explore_all_results(request)
# Inputs:        request -
# Outputs:       Query results page
# Exceptions:    None
# Description:   Page that allows to see all results from a template
#
################################################################################
@permission_required(content_type=RIGHTS.explore_content_type, permission=RIGHTS.explore_access, login_url='/login')
def explore_all_results(request):
    template_id = request.GET['id']

    if 'HTTPS' in request.META['SERVER_PROTOCOL']:
        protocol = "https"
    else:
        protocol = "http"

    request.session['queryExplore'] = {"schema": template_id}
    json_instances = [Instance(name="Local", protocol=protocol, address=request.META['REMOTE_ADDR'], port=request.META['SERVER_PORT'], access_token="token", refresh_token="token").to_json()]
    request.session['instancesExplore'] = json_instances

    template = loader.get_template('explore/explore_results.html')

    context = RequestContext(request, {
        '': '',
    })
    if 'exploreCurrentTemplateID' not in request.session:
        return redirect('/explore/select-template')
    else:
        return HttpResponse(template.render(context))


################################################################################
#
# Function Name: explore_all_versions_results(request)
# Inputs:        request -
# Outputs:       Query results page
# Exceptions:    None
# Description:   Page that allows to see all results from all versions of a template
#
################################################################################
@permission_required(content_type=RIGHTS.explore_content_type, permission=RIGHTS.explore_access, login_url='/login')
def explore_all_versions_results(request):
    template_id = request.GET['id']
    template = Template.objects().get(pk=template_id)
    version_id = template.templateVersion
    template_version = TemplateVersion.objects().get(pk=version_id)

    if len(template_version.versions) == 1:
            query = {"schema": template_id}
    else:
        list_query = []
        for version in template_version.versions:
            list_query.append({'schema': version})
        query = {"$or": list_query}

    request.session['queryExplore'] = query

    if 'HTTPS' in request.META['SERVER_PROTOCOL']:
        protocol = "https"
    else:
        protocol = "http"
    json_instances = [Instance(name="Local", protocol=protocol, address=request.META['REMOTE_ADDR'], port=request.META['SERVER_PORT'], access_token="token", refresh_token="token").to_json()]
    request.session['instancesExplore'] = json_instances

    template = loader.get_template('explore/explore_results.html')

    context = RequestContext(request, {
        '': '',
    })
    if 'exploreCurrentTemplateID' not in request.session:
        return redirect('/explore/select-template')
    else:
        return HttpResponse(template.render(context))


################################################################################
#
# Function Name: explore_detail_result
# Inputs:        request -
# Outputs:       Detail of result
# Exceptions:    None
# Description:   Page that allows to see all selected detail result from a template
#
################################################################################
@permission_required(content_type=RIGHTS.explore_content_type, permission=RIGHTS.explore_access, login_url='/login')
def explore_detail_result(request) :
    template = loader.get_template('explore/explore_detail_results.html')
    context = explore_detail_result_process(request)

    if 'exploreCurrentTemplateID' not in request.session:
        return redirect('/explore/select-template')
    else:
        return HttpResponse(template.render(context))


################################################################################
#
# Function Name: explore_detail_result_keyword
# Inputs:        request -
# Outputs:       Detail of result keyword
# Exceptions:    None
# Description:   Page that allows to see detail result from a selected result
#
################################################################################
@permission_required(content_type=RIGHTS.explore_content_type, permission=RIGHTS.explore_access, login_url='/login')
def explore_detail_result_keyword(request) :
    template = loader.get_template('explore/explore_detail_results_keyword.html')
    context = explore_detail_result_process(request)

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: explore_detail_result_process
# Inputs:        request -
# Outputs:       Detail of result
# Exceptions:    None
# Description:   Page that allows to see detail result from a selected result
#
################################################################################
@permission_required(content_type=RIGHTS.explore_content_type, permission=RIGHTS.explore_access, login_url='/login')
def explore_detail_result_process(request):
    result_id = request.GET['id']
    xmlString = XMLdata.get(result_id)
    schemaId = xmlString['schema']
    if 'title' in request.GET:
        title = request.GET['title']
    else:
        title = xmlString['title']
    xmlString = XMLdata.unparse(xmlString['content']).encode('utf-8')
    xsltPath = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'xml2html.xsl')
    xslt = etree.parse(xsltPath)
    transform = etree.XSLT(xslt)

    #Check if a custom detailed result XSLT has to be used
    schema = Template.objects.get(pk=schemaId)
    try:
        if (xmlString != ""):
            dom = etree.fromstring(str(xmlString))
            if schema.ResultXsltDetailed:
                shortXslt = etree.parse(BytesIO(schema.ResultXsltDetailed.content.encode('utf-8')))
                shortTransform = etree.XSLT(shortXslt)
                newdom = shortTransform(dom)
            else:
                newdom = transform(dom)
    except Exception, e:
        #We use the default one
        newdom = transform(dom)

    result = str(newdom)
    context = RequestContext(request, {
        'XMLHolder': result,
        'title': title,
        "template_name": schema.title
    })

    return context


################################################################################
#
# Function Name: start_export
# Inputs:        request - All ids
# Outputs:       Detail of results
# Exceptions:    None
# Description:   Page that allows to see all selected detail results from a template
#
################################################################################
@permission_required(content_type=RIGHTS.explore_content_type, permission=RIGHTS.explore_access, login_url='/login')
def start_export(request):
    if request.method == 'POST':
        #We retrieve all selected exporters
        listExporter = request.POST.getlist('my_exporters')
        instances = request.session['instancesExplore']
        listId = request.session['listIdToExport']
        xmlResults = []
        #Creation of ZIP file
        in_memory = StringIO()
        zip = zipfile.ZipFile(in_memory, "a")
        is_many_inst = len(instances) > 1
        for instance in instances:
            #Retrieve data
            sessionName = "resultsExplore" + json.loads(instance)['name']
            results = request.session[sessionName]
            if (len(results) > 0):
                for result in results:
                    if result['id'] in listId:
                        xmlResults.append(result)

            #For each data, we convert
            if len(xmlResults) > 0:
                #Init the folder name
                folder_name = None
                if is_many_inst:
                    folder_name = json.loads(instance)['name']
                #Check if the XSLT converter is asked. If yes, we start with this one because there is a specific treatment
                listXslt = request.POST.getlist('my_xslts')
                #Get the content of the file
                if len(listXslt) > 0:
                    exporter = XSLTExporter()
                    for xslt in listXslt:
                        xslt = ExporterXslt.objects.get(pk=xslt)
                        exporter._setXslt(xslt.content)
                        if folder_name == None:
                            exporter._transformAndZip(xslt.name, xmlResults, zip)
                        else:
                            exporter._transformAndZip(folder_name+"/"+xslt.name, xmlResults, zip)

                #We export for others exporters
                for exporter in listExporter:
                    exporter = get_exporter(exporter)
                    exporter._transformAndZip(folder_name, xmlResults, zip)

        zip.close()

        #ZIP file to be downloaded
        in_memory.seek(0)
        response = HttpResponse(in_memory.read())
        response["Content-Disposition"] = "attachment; filename=Results.zip"
        response['Content-Type'] = 'application/x-zip'
        request.session['listIdToExport'] = ''

        return response
    else:
        # We retrieve the result_id for each file the user wants to export
        listId = request.GET.getlist('listId[]')
        request.session['listIdToExport'] = listId

        # Get all schemaId from the listId
        listSchemas = XMLdata.getByIDsAndDistinctBy(listId, "schema")

        export_form = ExportForm(listSchemas)

        upload_xslt_Form = UploadXSLTForm(listSchemas)
        template = loader.get_template('explore/export_start.html')
        context = Context({'export_form': export_form,
                           'upload_xslt_Form': upload_xslt_Form,
                           'nb_elts_exp': len(export_form.EXPORT_OPTIONS),
                           'nb_elts_xslt': len(upload_xslt_Form.EXPORT_OPTIONS)})

        return HttpResponse(json.dumps({'template': template.render(context)}), content_type='application/javascript')
