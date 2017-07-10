################################################################################
#
# File Name: views.py
# Application: compose
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

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import redirect
from django.core.servers.basehttp import FileWrapper
from cStringIO import StringIO
from mgi.models import Template, TemplateVersion, XML2Download, Type, TypeVersion, Bucket
from admin_mdcs.models import permission_required
import mgi.rights as RIGHTS
from mgi.common import getXSDTypes


################################################################################
#
# Function Name: index(request)
# Inputs:        request - 
# Outputs:       Main Page of Composer Application
# Exceptions:    None
# Description:   Page that allows to select a template to start composing         
#
################################################################################
@permission_required(content_type=RIGHTS.compose_content_type, permission=RIGHTS.compose_access, login_url='/login')
def index(request):
    template = loader.get_template('compose/compose.html')
    currentTemplateVersions = []
    for tpl_version in TemplateVersion.objects():
        currentTemplateVersions.append(tpl_version.current)

    currentTemplates = dict()
    for tpl_version in currentTemplateVersions:
        tpl = Template.objects.get(pk=tpl_version)
        templateVersions = TemplateVersion.objects.get(pk=tpl.templateVersion)
        currentTemplates[tpl] = templateVersions.isDeleted

    context = RequestContext(request, {
       'templates': currentTemplates,
       'userTemplates': Template.objects(user=str(request.user.id)),
    })

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: compose_build_template(request)
# Inputs:        request -
# Outputs:       Build Template Page
# Exceptions:    None
# Description:   Page that allows to Compose the Template
#
################################################################################
@permission_required(content_type=RIGHTS.compose_content_type, permission=RIGHTS.compose_access, login_url='/login')
def compose_build_template(request):
    template = loader.get_template('compose/compose_build_template.html')
    # 1) user types: list of ids
    user_types = []
    for user_type in Type.objects(user=str(request.user.id)):
        user_types.append(user_type)
    # 2) buckets: label -> list of type that are not deleted
    # 3) nobuckets: list of types that are not assigned to a specific bucket
    buckets_types = dict()
    no_buckets_types = []

    buckets = Bucket.objects
    for type_version in TypeVersion.objects():
        if not type_version.isDeleted:
            has_bucket = False
            for bucket in buckets:
                if str(type_version.id) in bucket.types:
                    if bucket not in buckets_types.keys():
                        buckets_types[bucket] = []
                    buckets_types[bucket].append(Type.objects.get(pk=type_version.current))
                    has_bucket = True
            if not has_bucket:
                no_buckets_types.append(Type.objects.get(pk=type_version.current))

    built_in_types = []
    for built_in_type in getXSDTypes(""):
        built_in_types.append({'id': 'built_in_type', 'title': built_in_type})

    context = RequestContext(request, {
       'bucketsTypes': buckets_types,
       'builtinTypes': built_in_types,
       'nobucketsTypes': no_buckets_types,
       'userTypes': user_types,
    })

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: compose_downloadxsd(request)
# Inputs:        request -
# Outputs:       XSD representation of the current data instance
# Exceptions:    None
# Description:   Returns an XSD representation of the current data instance.
#                Used when user wants to download the XML file.
#
################################################################################
@permission_required(content_type=RIGHTS.compose_content_type, permission=RIGHTS.compose_access, login_url='/login')
def compose_downloadxsd(request):
    xml2downloadID = request.GET.get('id', None)
    if xml2downloadID is not None:
        xmlDataObject = XML2Download.objects.get(pk=xml2downloadID)
        xmlStringEncoded = xmlDataObject.xml.encode('utf-8')
        fileObj = StringIO(xmlStringEncoded)
        xmlDataObject.delete()
        response = HttpResponse(FileWrapper(fileObj), content_type='application/xsd')
        response['Content-Disposition'] = 'attachment; filename=' + "new_template.xsd"
        return response
    else:
        return redirect('/')
