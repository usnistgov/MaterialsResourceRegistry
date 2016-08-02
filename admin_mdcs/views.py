################################################################################
#
# File Name: views.py
# Application: admin_mdcs
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

from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http.response import HttpResponseBadRequest
from django.template import RequestContext, loader
from django.shortcuts import redirect
from requests import status_codes

from mgi.common import LXML_SCHEMA_NAMESPACE, SCHEMA_NAMESPACE
from mgi.models import Request, Message, PrivacyPolicy, TermsOfUse, Help, Template, TemplateVersion, Type, \
    TypeVersion, Module, Bucket, Instance, Exporter, ExporterXslt, ResultXslt, create_template, create_type, \
    create_template_version, create_type_version, OaiXslt, template_list_current, type_list_current
from forms import UploadResultXSLTForm, PrivacyPolicyForm, TermsOfUseForm, HelpForm, RepositoryForm, \
    RefreshRepositoryForm, UploadXSLTForm, UploadResultXSLTForm, UploadTemplateForm, UploadTypeForm, \
    UploadVersionForm
from django.contrib import messages
import os
from django.conf import settings
import requests
from datetime import datetime
from datetime import timedelta
from bson.objectid import ObjectId
from dateutil import tz
from collections import OrderedDict
import lxml.etree as etree
from lxml.etree import XMLSyntaxError
from io import BytesIO
from mgi import common
import json
from mongoengine import NotUniqueError, OperationError
from django.contrib.admin.views.decorators import staff_member_required
import xmltodict
#TODO Move to OAI-PMH
from oai_pmh.admin.forms import UploadOaiPmhXSLTForm
from django import utils
from utils.XMLValidation.xml_schema import validate_xml_schema
import xmltodict
#TODO Move to OAI-PMH
from oai_pmh.admin.forms import UploadOaiPmhXSLTForm


################################################################################
#
# Function Name: user_requests(request)
# Inputs:        request -
# Outputs:       User Request Page
# Exceptions:    None
# Description:   Page that allows to accept or deny user requests
#
################################################################################
@staff_member_required
def user_requests(request):
    template = loader.get_template('admin/user_requests.html')

    context = RequestContext(request, {
        'requests': Request.objects
    })

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: contact_messages(request)
# Inputs:        request -
# Outputs:       User Request Page
# Exceptions:    None
# Description:   Page that allows to read messages from the contact page
#
################################################################################
@staff_member_required
def contact_messages(request):
    template = loader.get_template('admin/contact_messages.html')

    context = RequestContext(request, {
        'contacts': Message.objects
    })

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: website(request)
# Inputs:        request -
# Outputs:       User Request Page
# Exceptions:    None
# Description:   Page that allows to edit website pages
#
################################################################################
def website(request):
    template = loader.get_template('admin/website.html')

    context = RequestContext(request, {
    })

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: privacy_policy_admin(request)
# Inputs:        request -
# Outputs:       User Request Page
# Exceptions:    None
# Description:   Page that allows to edit Privacy Policy
#
################################################################################
@staff_member_required
def privacy_policy_admin(request):
    if request.method == 'POST':
        form = PrivacyPolicyForm(request.POST)
        if form.is_valid():
            for privacy in PrivacyPolicy.objects:
                privacy.delete()

            if (request.POST['content'] != ""):
                newPrivacy = PrivacyPolicy(content = request.POST['content'])
                newPrivacy.save()
            messages.add_message(request, messages.INFO, 'Privacy Policy saved with success.')
            return redirect('/admin/website')
    else:
        if len(PrivacyPolicy.objects) != 0:
            policy = PrivacyPolicy.objects[0]
            data = {'content':policy.content}
            form = PrivacyPolicyForm(data)
        else:
            form = PrivacyPolicyForm()

    return render(request, 'admin/privacy_policy.html', {'form':form})


################################################################################
#
# Function Name: terms_of_use_admin(request)
# Inputs:        request -
# Outputs:       User Request Page
# Exceptions:    None
# Description:   Page that allows to edit Terms of Use
#
################################################################################
@staff_member_required
def terms_of_use_admin(request):
    if request.method == 'POST':
        form = TermsOfUseForm(request.POST)
        if form.is_valid():
            for terms in TermsOfUse.objects:
                terms.delete()

            if request.POST['content'] != "":
                newTerms = TermsOfUse(content=request.POST['content'])
                newTerms.save()
            messages.add_message(request, messages.INFO, 'Terms of Use saved with success.')
            return redirect('/admin/website')
    else:
        if len(TermsOfUse.objects) != 0:
            terms = TermsOfUse.objects[0]
            data = {'content':terms.content}
            form = TermsOfUseForm(data)
        else:
            form = TermsOfUseForm()

    return render(request, 'admin/terms_of_use.html', {'form':form})


################################################################################
#
# Function Name: help_admin(request)
# Inputs:        request -
# Outputs:       User Request Page
# Exceptions:    None
# Description:   Page that allows to edit Help
#
################################################################################
@staff_member_required
def help_admin(request):
    if request.method == 'POST':
        form = HelpForm(request.POST)
        if form.is_valid():
            for help in Help.objects:
                help.delete()

            if (request.POST['content'] != ""):
                newHelp = Help(content = request.POST['content'])
                newHelp.save()
            messages.add_message(request, messages.INFO, 'Help saved with success.')
            return redirect('/admin/website')
    else:
        if len(Help.objects) != 0:
            help = Help.objects[0]
            data = {'content':help.content}
            form = HelpForm(data)
        else:
            form = HelpForm()

    return render(request, 'admin/help.html', {'form':form})


################################################################################
#
# Function Name: manage_schemas(request)
# Inputs:        request -
# Outputs:       Manage Templates Page
# Exceptions:    None
# Description:   Page that allows to upload new schemas and manage the existing ones
#
################################################################################
@staff_member_required
def manage_schemas(request):
        template = loader.get_template('admin/manage_uploads.html')

        currentTemplateVersions = []
        for tpl_version in TemplateVersion.objects():
            currentTemplateVersions.append(tpl_version.current)

        currentTemplates = dict()
        for tpl_version in currentTemplateVersions:
            tpl = Template.objects.get(pk=tpl_version)
            if tpl.user is None:
                templateVersions = TemplateVersion.objects.get(pk=tpl.templateVersion)
                currentTemplates[tpl] = templateVersions.isDeleted

        context = RequestContext(request, {
            'objects':currentTemplates,
            'objectType': "Template",
        })
        return HttpResponse(template.render(context))


################################################################################
#
# Function Name: manage_types(request)
# Inputs:        request -
# Outputs:       Manage Types Page
# Exceptions:    None
# Description:   Page that allows to upload new types and manage the existing ones
#
################################################################################
@staff_member_required
def manage_types(request):
    template = loader.get_template('admin/manage_uploads.html')

    currentTypeVersions = []
    for type_version in TypeVersion.objects():
        currentTypeVersions.append(type_version.current)

    currentTypes = dict()
    for type_version in currentTypeVersions:
        type = Type.objects.get(pk=type_version)
        if type.user is None:
            typeVersions = TypeVersion.objects.get(pk=type.typeVersion)
            currentTypes[type] = typeVersions.isDeleted

    context = RequestContext(request, {
        'objects':currentTypes,
        'objectType': "Type",
        'buckets': Bucket.objects,
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: check_unique_name(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Check that the name of the template is unique
#
################################################################################
def check_unique_name(name):
    # check that the name is unique
    names = Template.objects.all().values_list('title')
    if name in names:
        return False
    return True


################################################################################
#
# Function Name: upload_xsd(request)
# Inputs:        request -
# Outputs:       View to upload XSD (template or type)
# Exceptions:    None
# Description:   Form that allows to upload new XSD templates and types
#
################################################################################
@staff_member_required
def upload_xsd(request):
    # get the type of object in param: Template or Type
    object_type = request.GET['type'] if 'type' in request.GET else None

    request.session['uploadObjectContent'] = None
    request.session['uploadObjectName'] = None
    request.session['uploadObjectFilename'] = None
    request.session['uploadObjectType'] = None
    request.session['uploadVersion'] = None

    # check if object type is set
    if object_type is not None:
        # load the html template to upload xsd
        template = loader.get_template('admin/upload_xsd.html')
        # check the parameters are correct
        if object_type in ['Template', 'Type']:
            # method is POST
            if request.method == 'POST':
                if object_type == 'Template':
                    form = UploadTemplateForm(request.POST,  request.FILES)
                elif object_type == 'Type':
                    form = UploadTypeForm(request.POST, request.FILES)

                if form.is_valid():
                    # check that the name is unique
                    if object_type == 'Template':
                        names = Template.objects.all().values_list('title')
                    elif object_type == 'Type':
                        names = Type.objects.all().values_list('title')
                    name = request.POST['name']
                    if name in names:
                        context = RequestContext(request, {
                            'upload_form': form,
                            'object_type':  object_type,
                            'errors': 'A {} with the same name already exists.'.format(object_type),
                        })
                        return HttpResponse(template.render(context))

                    # get the file from the form
                    xsd_file = request.FILES['xsd_file']
                    # put the cursor at the beginning of the file
                    xsd_file.seek(0)
                    # read the content of the file
                    xsd_data = xsd_file.read()

                    # is it a valid XML document ?
                    try:
                        xsd_tree = etree.parse(BytesIO(xsd_data.encode('utf-8')))
                    except Exception, e:
                        context = RequestContext(request, {
                            'upload_form': form,
                            'object_type':  object_type,
                            'errors': 'Uploaded file is not well formatted XML.',
                        })
                        return HttpResponse(template.render(context))

                    # is it supported by the MDCS ?
                    errors = common.getValidityErrorsForMDCS(xsd_tree, object_type)
                    if len(errors) > 0:
                        errors_str = ", ".join(errors)
                        context = RequestContext(request, {
                            'upload_form': form,
                            'object_type':  object_type,
                            'errors': errors_str,
                        })
                        return HttpResponse(template.render(context))

                    # is it a valid XML schema?

                    error = validate_xml_schema(xsd_tree)

                    if error is not None:
                        # a problem with includes/imports has been detected
                        # get the imports
                        imports = xsd_tree.findall("{}import".format(LXML_SCHEMA_NAMESPACE))
                        # get the includes
                        includes = xsd_tree.findall("{}include".format(LXML_SCHEMA_NAMESPACE))
                        if len(includes) > 0 or len(imports) > 0:
                            # build the list of dependencies
                            list_dependencies_template = loader.get_template('admin/list_dependencies.html')
                            context = RequestContext(request, {
                                'templates': template_list_current(),
                                'types':  type_list_current(),
                            })
                            list_dependencies_html = list_dependencies_template.render(context)

                            imports = xsd_tree.findall("{}import".format(LXML_SCHEMA_NAMESPACE))
                            includes = xsd_tree.findall("{}include".format(LXML_SCHEMA_NAMESPACE))

                            # build the dependency resolver form
                            dependency_resolver_template = loader.get_template('admin/dependency_resolver.html')
                            context = RequestContext(request, {
                                'imports': imports,
                                'includes': includes,
                                'xsd_content': utils.html.escape(xsd_data),
                                'dependencies': list_dependencies_html,
                            })
                            dependency_resolver_html = dependency_resolver_template.render(context)

                            context = RequestContext(request, {
                                'upload_form': form,
                                'object_type':  object_type,
                                'dependency_resolver': dependency_resolver_html,
                            })

                            # TODO: use a better method to store schema information
                            # TODO: can create an entry in db
                            request.session['uploadObjectName'] = name
                            request.session['uploadObjectFilename'] = xsd_file.name
                            request.session['uploadObjectContent'] = xsd_data
                            request.session['uploadObjectType'] = object_type
                            if object_type == 'Type':
                                request.session['uploadBuckets'] = request.POST.getlist('buckets')
                            return HttpResponse(template.render(context))
                        else:
                            context = RequestContext(request, {
                                'upload_form': form,
                                'object_type':  object_type,
                                'errors': utils.html.escape(error),
                            })
                            return HttpResponse(template.render(context))
                    else:
                        # XML schema loaded with success
                        messages.add_message(request, messages.INFO, '{} uploaded with success.'.format(object_type))
                        if object_type == 'Template':
                            create_template(xsd_data, name, xsd_file.name)
                            return redirect('/admin/xml-schemas/manage-schemas')
                        elif object_type == 'Type':
                            buckets = request.POST.getlist('buckets')
                            create_type(xsd_data, name, xsd_file.name, buckets)
                            return redirect('/admin/xml-schemas/manage-types')
                else:
                    context = RequestContext(request, {
                        'upload_form': form,
                        'object_type':  object_type,
                    })
                    return HttpResponse(template.render(context))
            # method is GET
            else:
                # if the param is Template
                if object_type == 'Template':
                    # render the form to upload a template
                    context = RequestContext(request, {
                        'upload_form': UploadTemplateForm(),
                        'object_type':  object_type,
                    })
                    return HttpResponse(template.render(context))
                # if the param is Type
                elif object_type == 'Type':
                    # render the form to upload a type
                    context = RequestContext(request, {
                        'upload_form': UploadTypeForm(),
                        'object_type':  object_type,
                    })
                    return HttpResponse(template.render(context))
        else:
            return HttpResponse(status=400, reason='Expected type parameter: Template, Type.')

    else:
        return HttpResponse(status=400, reason='Expecting get parameter: type.')


################################################################################
#
# Function Name: upload_xsd(request)
# Inputs:        request -
# Outputs:       View to upload XSD (template or type)
# Exceptions:    None
# Description:   Form that allows to upload new XSD templates and types
#
################################################################################
@staff_member_required
def manage_versions(request):
    # get the type of object in param: Template or Type
    object_type = request.GET['type'] if 'type' in request.GET else None
    object_id = request.GET['id'] if 'id' in request.GET else None

    request.session['uploadObjectContent'] = None
    request.session['uploadObjectName'] = None
    request.session['uploadObjectFilename'] = None
    request.session['uploadObjectType'] = None
    request.session['uploadVersion'] = None

    # check if object type is set
    if object_type is not None and object_id is not None:
        # load the html template to upload xsd
        template = loader.get_template('admin/manage_versions.html')
        # check the parameters are correct
        if object_type in ['Template', 'Type']:
            # method is POST
            if request.method == 'POST':
                # get the form
                if object_type == 'Template':
                    form = UploadVersionForm(request.POST,  request.FILES)
                elif object_type == 'Type':
                    form = UploadVersionForm(request.POST, request.FILES)

                # build the versions to render again in case of an error
                if object_type == "Template":
                    object = Template.objects.get(pk=object_id)
                    object_versions = TemplateVersion.objects.get(pk=object.templateVersion)
                else:
                    object = Type.objects.get(pk=object_id)
                    object_versions = TypeVersion.objects.get(pk=object.typeVersion)

                versions = get_versions(object_versions, object_type)

                if form.is_valid():
                    # get the file from the form
                    xsd_file = request.FILES['xsd_file']
                    # put the cursor at the beginning of the file
                    xsd_file.seek(0)
                    # read the content of the file
                    xsd_data = xsd_file.read()

                    # is it a valid XML document ?
                    try:
                        xsd_tree = etree.parse(BytesIO(xsd_data.encode('utf-8')))
                    except Exception, e:
                        context = RequestContext(request, {
                            'upload_form': form,
                            'versions': versions,
                            'object_versions': object_versions,
                            'object_type': object_type,
                            'object_id': object_id,
                            'errors': 'Uploaded file is not well formatted XML.',
                        })
                        return HttpResponse(template.render(context))

                    # is it supported by the MDCS ?
                    errors = common.getValidityErrorsForMDCS(xsd_tree, object_type)
                    if len(errors) > 0:
                        errors_str = ", ".join(errors)

                        context = RequestContext(request, {
                            'upload_form': form,
                            'versions': versions,
                            'object_versions': object_versions,
                            'object_type': object_type,
                            'object_id': object_id,
                            'errors': errors_str,
                        })
                        return HttpResponse(template.render(context))

                    # is it a valid XML schema?

                    error = validate_xml_schema(xsd_tree)

                    if error is not None:
                        # a problem with includes/imports has been detected
                        # get the imports
                        imports = xsd_tree.findall("{}import".format(LXML_SCHEMA_NAMESPACE))
                        # get the includes
                        includes = xsd_tree.findall("{}include".format(LXML_SCHEMA_NAMESPACE))
                        if len(includes) > 0 or len(imports) > 0:
                            # build the list of dependencies
                            list_dependencies_template = loader.get_template('admin/list_dependencies.html')
                            context = RequestContext(request, {
                                'templates': template_list_current(),
                                'types':  type_list_current(),
                            })
                            list_dependencies_html = list_dependencies_template.render(context)

                            imports = xsd_tree.findall("{}import".format(LXML_SCHEMA_NAMESPACE))
                            includes = xsd_tree.findall("{}include".format(LXML_SCHEMA_NAMESPACE))

                            # build the dependency resolver form
                            dependency_resolver_template = loader.get_template('admin/dependency_resolver.html')
                            context = RequestContext(request, {
                                'imports': imports,
                                'includes': includes,
                                'xsd_content': utils.html.escape(xsd_data),
                                'dependencies': list_dependencies_html,
                            })
                            dependency_resolver_html = dependency_resolver_template.render(context)

                            context = RequestContext(request, {
                                'upload_form': form,
                                'versions': versions,
                                'object_versions': object_versions,
                                'object_type': object_type,
                                'object_id': object_id,
                                'dependency_resolver': dependency_resolver_html,
                            })

                            # TODO: use a better method to store schema information
                            # TODO: can create an entry in db
                            request.session['uploadObjectFilename'] = xsd_file.name
                            request.session['uploadObjectName'] = xsd_file.name
                            request.session['uploadObjectContent'] = xsd_data
                            request.session['uploadObjectType'] = object_type
                            request.session['uploadVersion'] = str(object_versions.id)
                            if object_type == 'Type':
                                request.session['uploadBuckets'] = request.POST.getlist('buckets')
                            return HttpResponse(template.render(context))
                        else:
                            context = RequestContext(request, {
                                'upload_form': form,
                                'versions': versions,
                                'object_versions': object_versions,
                                'object_type':  object_type,
                                'object_id': str(object_id),
                                'errors': utils.html.escape(error),
                            })
                            return HttpResponse(template.render(context))
                    else:
                        # XML schema loaded with success
                        messages.add_message(request, messages.INFO, '{} uploaded with success.'.format(object_type))
                        if object_type == 'Template':
                            new_object = create_template_version(xsd_data, xsd_file.name, object_versions.id)
                            object_versions = TemplateVersion.objects.get(pk=new_object.templateVersion)
                            versions = get_versions(object_versions, object_type)
                        elif object_type == 'Type':
                            new_object = create_type_version(xsd_data, xsd_file.name, object_versions.id)
                            object_versions = TypeVersion.objects.get(pk=new_object.typeVersion)
                            versions = get_versions(object_versions, object_type)

                        context = RequestContext(request, {
                            'upload_form': form,
                            'versions': versions,
                            'object_versions': object_versions,
                            'object_type': object_type,
                            'object_id': str(new_object.id),
                        })
                        return HttpResponse(template.render(context))
                else:
                    context = RequestContext(request, {
                        'upload_form': form,
                        'versions': versions,
                        'object_versions': object_versions,
                        'object_type': object_type,
                        'object_id': object_id,
                    })
                    return HttpResponse(template.render(context))
            # method is GET
            else:
                if object_type == "Template":
                    object = Template.objects.get(pk=object_id)
                    object_versions = TemplateVersion.objects.get(pk=object.templateVersion)
                else:
                    object = Type.objects.get(pk=object_id)
                    object_versions = TypeVersion.objects.get(pk=object.typeVersion)

                versions = get_versions(object_versions, object_type)

                context = RequestContext(request, {
                    'upload_form': UploadVersionForm(),
                    'versions': versions,
                    'object_versions': object_versions,
                    'object_type': object_type,
                    'object_id': object_id,
                })
                return HttpResponse(template.render(context))
        else:
            return HttpResponse(status=400, reason='Expected type parameter: Template, Type.')

    else:
        return HttpResponse(status=400, reason='Expecting get parameters: type, id.')


def get_versions(object_versions, object_type):
    versions = OrderedDict()
    reversed_versions = list(reversed(object_versions.versions))
    for version_id in reversed_versions:
        if object_type == "Template":
            version = Template.objects.get(pk=version_id)
        else:
            version = Type.objects.get(pk=version_id)
        object_id = ObjectId(version.id)
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        datetimeUTC = object_id.generation_time
        datetimeUTC = datetimeUTC.replace(tzinfo=from_zone)
        datetimeLocal = datetimeUTC.astimezone(to_zone)
        datetime = datetimeLocal.strftime('%m/%d/%Y %H&#58;%M&#58;%S')
        versions[version] = datetime

    return versions


################################################################################
#
# Function Name: federation_of_queries(request)
# Inputs:        request -
# Outputs:       Repositories Management Page
# Exceptions:    None
# Description:   Page that allows to add instance of repositories and manage existing ones
#
#
################################################################################
@staff_member_required
def federation_of_queries(request):
    template = loader.get_template('admin/federation_of_queries.html')

    context = RequestContext(request, {
        'instances': Instance.objects.order_by('-id')
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: add_repository(request)
# Inputs:        request -
# Outputs:       Page that allows to add a repository
# Exceptions:    None
# Description:   Page that allows to add instance of a repository
#
#
################################################################################
@staff_member_required
def add_repository(request):
    if request.method == 'POST':
        form = RepositoryForm(request.POST)
        if form.is_valid():
            if request.POST["action"] == "Register":
                errors = ""

                # test if the name is "Local"
                if (request.POST["name"].upper() == "LOCAL"):
                    errors += "By default, the instance named Local is the instance currently running."
                else:
                    # test if an instance with the same name exists
                    instance = Instance.objects(name=request.POST["name"])
                    if len(instance) != 0:
                        errors += "An instance with the same name already exists.<br/>"

                # test if new instance is not the same as the local instance
                if request.POST["ip_address"] == request.META['REMOTE_ADDR'] and request.POST["port"] == request.META['SERVER_PORT']:
                    errors += "The address and port you entered refer to the instance currently running."
                else:
                    # test if an instance with the same address/port exists
                    instance = Instance.objects(address=request.POST["ip_address"], port=request.POST["port"])
                    if len(instance) != 0:
                        errors += "An instance with the address/port already exists.<br/>"

                # If some errors display them, otherwise insert the instance
                if(errors == ""):
                    try:
                        url = request.POST["protocol"] + "://" + request.POST["ip_address"] + ":" + request.POST["port"] + "/o/token/"
#                             data="grant_type=password&username=" + request.POST["username"] + "&password=" + request.POST["password"]
                        headers = {'content-type': 'application/x-www-form-urlencoded'}
                        data={
                            'grant_type': 'password',
                            'username': request.POST["username"],
                            'password': request.POST["password"],
                            'client_id': request.POST["client_id"],
                            'client_secret': request.POST["client_secret"]
                        }
                        r = requests.post(url=url, data=data, headers=headers, timeout=int(request.POST["timeout"]))
                        if r.status_code == 200:
                            create_instance(r.content, request.POST)
                            messages.add_message(request, messages.INFO, 'Repository registered with success.')
                            return redirect('/admin/repositories')
                        else:
                            message = "Unable to get access to the remote instance using these parameters."
                            return render(request, 'admin/add_repository.html', {'form':form, 'action_result':message})
                    except Exception, e:
                        message = "Unable to get access to the remote instance using these parameters."
                        return render(request, 'admin/add_repository.html', {'form':form, 'action_result':message})

                else:
                    return render(request, 'admin/add_repository.html', {'form':form, 'action_result':errors})

            elif request.POST["action"] == "Ping":
                try:
                    url = request.POST["protocol"] + "://" + request.POST["ip_address"] + ":" + request.POST["port"] + "/rest/ping"
                    r = requests.get(url, auth=(request.POST["username"], request.POST["password"]), timeout=int(request.POST["timeout"]))
                    if r.status_code == 200:
                        message = "Remote API reached with success."
                    else:
                        if 'detail' in json.loads(r.content):
                            message = "Error: " + json.loads(r.content)['detail']
                        else:
                            message = "Error: Unable to reach the remote API."
                except Exception, e:
                    message = "Error: Unable to reach the remote API."

                return render(request, 'admin/add_repository.html', {'form':form, 'action_result':message})
    else:
        form = RepositoryForm()

    return render(request, 'admin/add_repository.html', {'form':form})


def create_instance(content, request):
    now = datetime.now()
    delta = timedelta(seconds=int(json.loads(content)["expires_in"]))
    expires = now + delta
    Instance(name=request["name"], protocol=request["protocol"], address=request["ip_address"],
             port=request["port"], access_token=json.loads(content)["access_token"],
             refresh_token=json.loads(content)["refresh_token"], expires=expires).save()


################################################################################
#
# Function Name: refresh_repository(request)
# Inputs:        request -
# Outputs:       Page that allows to refresh a repository token
# Exceptions:    None
# Description:   Page that allows to refresh a repository token
#
#
################################################################################
@staff_member_required
def refresh_repository(request):
    if request.method == 'POST':

        form = RefreshRepositoryForm(request.POST)

        if form.is_valid():
            try:
                id = request.session['refreshInstanceID']
                instance = Instance.objects.get(pk=ObjectId(id))
            except:
                message = "Error: Unable to access the registered instance."
                return render(request, 'admin/refresh_repository.html', {'form':form, 'action_result':message})

            try:
                url = instance.protocol + "://" + instance.address + ":" + str(instance.port) + "/o/token/"
                data="&grant_type=refresh_token&refresh_token=" + instance.refresh_token
                headers = {'content-type': 'application/x-www-form-urlencoded'}
                r = requests.post(url=url, data=data, headers=headers, auth=(request.POST["client_id"], request.POST["client_secret"]), timeout=int(request.POST["timeout"]))
                if r.status_code == 200:
                    update_instance(instance, r.content)
                    return HttpResponseRedirect('/admin/repositories')
                else:
                    message = "Unable to get access to the remote instance using these parameters."
                    return render(request, 'admin/refresh_repository.html', {'form':form, 'action_result':message})
            except Exception, e:
                message = "Unable to get access to the remote instance using these parameters."
                return render(request, 'admin/refresh_repository.html', {'form':form, 'action_result':message})
    else:
        form = RefreshRepositoryForm()
        request.session['refreshInstanceID'] = request.GET['id']

    return render(request, 'admin/refresh_repository.html', {'form':form})


def update_instance(instance, content):
    now = datetime.now()
    delta = timedelta(seconds=int(json.loads(content)["expires_in"]))
    expires = now + delta
    instance.access_token = json.loads(content)["access_token"]
    instance.refresh_token = json.loads(content)["refresh_token"]
    instance.expires = expires
    instance.save()


################################################################################
#
# Function Name: modules(request)
# Inputs:        request -
# Outputs:       User Request Page
# Exceptions:    None
# Description:   Page that allows to add modules to a template
#
################################################################################
@staff_member_required
def modules(request):
    template = loader.get_template('admin/modules.html')

    object_id = request.GET.get('id', None)
    object_type = request.GET.get('type', None)

    if object_id is not None:
        try:
            if object_type == 'Template':
                db_object = Template.objects.get(pk=object_id)
            elif object_type == 'Type':
                db_object = Type.objects.get(pk=object_id)
            else:
                raise AttributeError('Type parameter unrecognized')

            xslt_path = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'xsd2html4modules.xsl')
            xslt = etree.parse(xslt_path)
            transform = etree.XSLT(xslt)

            dom = etree.parse(BytesIO(db_object.content.encode('utf-8')))
            annotations = dom.findall(".//{}annotation".format(LXML_SCHEMA_NAMESPACE))
            for annotation in annotations:
                annotation.getparent().remove(annotation)
            newdom = transform(dom)
            xsd_tree = str(newdom)

            request.session['moduleTemplateID'] = object_id
            request.session['moduleTemplateContent'] = db_object.content

            namespaces = common.get_namespaces(BytesIO(str(db_object.content)))
            for prefix, url in namespaces.iteritems():
                if url == SCHEMA_NAMESPACE:
                    request.session['moduleDefaultPrefix'] = prefix
                    break

            context = RequestContext(request, {
                'xsdTree': xsd_tree,
                'modules': Module.objects,
                'object_type': object_type
            })

            return HttpResponse(template.render(context))
        except:
            return redirect('/')
    else:
        return redirect('/')

################################################################################
#
# Function Name: exporters(request)
# Inputs:        request -
# Outputs:       User Request Page
# Exceptions:    None
# Description:   Page that allows to add exporters to a template
#
################################################################################
@staff_member_required
def exporters(request):
    #Get the HTML template
    template = loader.get_template('admin/exporters.html')
    id = request.GET.get('id', None)
    if id is not None:
        try:
            object = Template.objects.get(pk=id)
            request.session['moduleTemplateID'] = id
            #Get all exporters
            allExporters = list(Exporter.objects.all())
            #Get exporters already bind with the template
            templateExporters = Template.objects.get(pk=id).exporters
            #Get all XSLT
            allXsltFiles = ExporterXslt.objects.all()
            #Get XSLT already bind with the template
            templateXsltExporters = Template.objects.get(pk=id).XSLTFiles

            useExporter = dict()
            useXsltFiles = dict()

            #We initialise all exporters like if there are not used by the template
            for exporter in allExporters:
                useExporter[exporter.id] = False
            #We set all exporters already used by the template
            for exporter in templateExporters:
                useExporter[exporter.id] = True
            #We initialise all exporters like if there are not used by the template
            for xmlFile in allXsltFiles:
                useXsltFiles[xmlFile.id] = False
            #We set all XSLT already used by the template
            for xmlFile in templateXsltExporters:
                useXsltFiles[xmlFile.id] = True

            context = RequestContext(request, {
                'exporters': allExporters,
                'xsltFiles': allXsltFiles,
                'useExporter': useExporter,
                'useXsltFiles': useXsltFiles
            })

            return HttpResponse(template.render(context))
        except:
            return redirect('/')
    else:
        return redirect('/')


################################################################################
#
# Function Name: manage_xslt(request)
# Inputs:        request -
# Outputs:       Manage XSLT Page
# Exceptions:    None
# Description:   Page that allows to upload new XSLT and manage the existing ones
#
################################################################################
@staff_member_required
def manage_xslt(request, id=None):
    if request.method == 'POST':
        upload_form = UploadXSLTForm(request.POST, request.FILES)
        name = upload_form['name'].value()
        name = name.strip(' \t\n\r')
        available = upload_form['available_for_all'].value()
        xml_file = upload_form['xslt_file'].value()
        # put the cursor at the beginning of the file
        xml_file.seek(0)
        # read the content of the file
        xml_data = xml_file.read()
        # check XML data or not?
        try:
            etree.fromstring(xml_data)
        except XMLSyntaxError:
            return HttpResponseBadRequest('Uploaded File is not well formed XML.')
        #No exceptions, we can add it in DB
        try:
            xslt = ExporterXslt(name=name, filename=xml_file.name, content=xml_data, available_for_all=available).save()
            #IF it's available for all templates, we add the reference for all templates using the XSLT exporter
            if available:
                xslt_exporter = None
                try:
                    xslt_exporter = Exporter.objects.get(name='XSLT')
                except:
                    None

                if xslt_exporter != None:
                    Template.objects(exporters__all=[xslt_exporter]).update(push__XSLTFiles=xslt)
        except NotUniqueError, e:
            return HttpResponseBadRequest('This XSLT name already exists. Please enter an other name.')

        messages.add_message(request, messages.INFO, 'XSLT saved with success.')
        return HttpResponse('ok')
    else:
        template = loader.get_template('admin/manage_xslt.html')
        upload_xslt_Form = UploadXSLTForm()
        upload_result_xslt_Form = UploadResultXSLTForm()
        #TODO Move to OAI-PMH
        upload_oai_pmh_xslt_Form = UploadOaiPmhXSLTForm()
        xslt_files = ExporterXslt.objects.all()
        result_xslt_files = ResultXslt.objects.all()
        #TODO Move to OAI-PMH
        oai_pmh_xslt = OaiXslt.objects.all()
        context = RequestContext(request, {
            'upload_xslt_Form': upload_xslt_Form,
            'upload_result_xslt_Form': upload_result_xslt_Form,
            'upload_oai_pmh_xslt_Form': upload_oai_pmh_xslt_Form,
            'xslt_files': xslt_files,
            'result_xslt_files': result_xslt_files,
            #TODO Move to OAI-PMH
            'oai_pmh_xslt': oai_pmh_xslt,
        })

        return HttpResponse(template.render(context))

################################################################################
#
# Function Name: delete_xslt(request)
# Inputs:        request -
# Outputs:       Delete XSLT document
# Exceptions:    None
# Description:   Page that allows to delete an XSLT
#
################################################################################
@staff_member_required
def delete_xslt(request):
        if request.method == 'POST':
            try:
                xslt_id = request.POST['xslt_id']
                ExporterXslt.objects(pk=xslt_id).delete()
            except Exception:
                return HttpResponseBadRequest('Something went wrong during the deletion')

            messages.add_message(request, messages.INFO, 'XSLT deleted with success.')
            return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: edit_xslt(request)
# Inputs:        request -
# Outputs:       Edit XSLT
# Exceptions:    None
# Description:   Page that allows to edit an existing XSLT
#
################################################################################
@staff_member_required
def edit_xslt(request, id=None):
    if request.method == 'POST':
        object_id = request.POST['object_id']
        new_name = request.POST['new_name']
        new_name = new_name.strip(' \t\n\r')
        try:
            exporter = ExporterXslt.objects.get(pk=object_id)
            if exporter.name == new_name:
                return HttpResponseBadRequest('Please enter a different name.')
            else:
                exporter.update(set__name=str(new_name))
        except OperationError, e:
            return HttpResponseBadRequest('This XSLT name already exists. Please enter an other name.')

        messages.add_message(request, messages.INFO, 'XSLT edited with success.')
        return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: manage_result_xslt(request)
# Inputs:        request -
# Outputs:       Manage Result XSLT Page
# Exceptions:    None
# Description:   Page that allows to upload new Result XSLT and manage the existing ones
#
################################################################################
@staff_member_required
def manage_result_xslt(request, id=None):
    if request.method == 'POST':
        upload_form = UploadResultXSLTForm(request.POST, request.FILES)
        name = upload_form['result_name'].value()
        name = name.strip(' \t\n\r')
        xml_file = upload_form['result_xslt_file'].value()
        # put the cursor at the beginning of the file
        xml_file.seek(0)
        # read the content of the file
        xml_data = xml_file.read()
        # check XML data or not?
        try:
            etree.fromstring(xml_data)
        except XMLSyntaxError:
            return HttpResponseBadRequest('Uploaded File is not well formed XML.')
        #No exceptions, we can add it in DB
        try:
            ResultXslt(name=name, filename=xml_file.name, content=xml_data).save()
        except NotUniqueError, e:
            return HttpResponseBadRequest('This XSLT name already exists. Please enter an other name.')

        messages.add_message(request, messages.INFO, 'XSLT saved with success.')
        return HttpResponse('ok')

    else:
        return HttpResponseBadRequest('This method should not be called on GET.')

################################################################################
#
# Function Name: delete_result_xslt(request)
# Inputs:        request -
# Outputs:       Delete Result XSLT document
# Exceptions:    None
# Description:   Page that allows to delete an XSLT
#
################################################################################
@staff_member_required
def delete_result_xslt(request):
    if request.method == 'POST':
        try:
            xslt_id = request.POST['xslt_id']
            ResultXslt.objects(pk=xslt_id).delete()
        except Exception:
            return HttpResponseBadRequest('Something went wrong during the deletion')

        messages.add_message(request, messages.INFO, 'XSLT deleted with success.')
        return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: edit_result_xslt(request)
# Inputs:        request -
# Outputs:       Edit XSLT
# Exceptions:    None
# Description:   Page that allows to edit an existing XSLT
#
################################################################################
@staff_member_required
def edit_result_xslt(request, id=None):
    if request.method == 'POST':
        object_id = request.POST['object_id']
        new_name = request.POST['new_name']
        new_name = new_name.strip(' \t\n\r')
        try:
            xslt = ResultXslt.objects.get(pk=object_id)
            if xslt.name == new_name:
                return HttpResponseBadRequest('Please enter a different name.')
            else:
                xslt.update(set__name=str(new_name))
        except OperationError, e:
            return HttpResponseBadRequest('This XSLT name already exists. Please enter an other name.')

        messages.add_message(request, messages.INFO, 'XSLT edited with success.')
        return HttpResponse(json.dumps({}), content_type='application/javascript')

################################################################################
#
# Function Name: result_xslt(request)
# Inputs:        request -
# Outputs:       User Request Page
# Exceptions:    None
# Description:   Page that allows to add result xslt to a template
#
################################################################################
@staff_member_required
def result_xslt(request):
    #Get the HTML template
    template = loader.get_template('admin/result_xslt.html')
    id = request.GET.get('id', None)
    if id is not None:
        try:
            object = Template.objects.get(pk=id)
            request.session['moduleTemplateID'] = id
            #Get exporters already bind with the template
            templateShort = Template.objects.get(pk=id).ResultXsltList
            #Get exporters already bind with the template
            templateDetailed = Template.objects.get(pk=id).ResultXsltDetailed
            #Get all XSLT
            allXsltFiles = ResultXslt.objects.all()

            context = RequestContext(request, {
                'templateShort': templateShort,
                'templateDetailed': templateDetailed,
                'xsltFiles': allXsltFiles,
            })

            return HttpResponse(template.render(context))
        except:
            return redirect('/')
    else:
        return redirect('/')
