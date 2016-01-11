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
from mgi.models import Request, Message, PrivacyPolicy, TermsOfUse, Help, Template, TemplateVersion, Type, \
    TypeVersion, Module, Bucket, Instance, Exporter, ExporterXslt, ResultXslt
from forms import UploadResultXSLTForm, PrivacyPolicyForm, TermsOfUseForm, HelpForm, RepositoryForm, RefreshRepositoryForm, UploadXSLTForm, UploadResultXSLTForm
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

            if (request.POST['content'] != ""):
                newTerms = TermsOfUse(content = request.POST['content'])
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
            templateVersions = TemplateVersion.objects.get(pk=tpl.templateVersion)
            currentTemplates[tpl] = templateVersions.isDeleted

        context = RequestContext(request, {
            'objects':currentTemplates,
            'objectType': "Template"
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
        typeVersions = TypeVersion.objects.get(pk=type.typeVersion)
        currentTypes[type] = typeVersions.isDeleted

    context = RequestContext(request, {
        'objects':currentTypes,
        'objectType': "Type",
        'buckets': Bucket.objects

    })
    return HttpResponse(template.render(context))


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
                            now = datetime.now()
                            delta = timedelta(seconds=int(eval(r.content)["expires_in"]))
                            expires = now + delta
                            Instance(name=request.POST["name"], protocol=request.POST["protocol"], address=request.POST["ip_address"], port=request.POST["port"], access_token=eval(r.content)["access_token"], refresh_token=eval(r.content)["refresh_token"], expires=expires).save()
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
                        if 'detail' in eval(r.content):
                            message = "Error: " + eval(r.content)['detail']
                        else:
                            message = "Error: Unable to reach the remote API."
                except Exception, e:
                    message = "Error: Unable to reach the remote API."

                return render(request, 'admin/add_repository.html', {'form':form, 'action_result':message})
    else:
        form = RepositoryForm()

    return render(request, 'admin/add_repository.html', {'form':form})


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
                    now = datetime.now()
                    delta = timedelta(seconds=int(eval(r.content)["expires_in"]))
                    expires = now + delta
                    instance.access_token=eval(r.content)["access_token"]
                    instance.refresh_token=eval(r.content)["refresh_token"]
                    instance.expires=expires
                    instance.save()
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

################################################################################
#
# Function Name: manage_versions(request)
# Inputs:        request -
# Outputs:       Manage Version Page
# Exceptions:    None
# Description:   Redirects to the version manager of a given object
#
################################################################################
@staff_member_required
def manage_versions(request):
    template = loader.get_template('admin/manage_versions.html')

    id = request.GET.get('id', None)
    objectType = request.GET.get('type', None)

    if id is not None and objectType is not None:
        try:
            if objectType == "Template":
                object = Template.objects.get(pk=id)
                objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
            else:
                object = Type.objects.get(pk=id)
                objectVersions = TypeVersion.objects.get(pk=object.typeVersion)

            versions = OrderedDict()
            reversedVersions = list(reversed(objectVersions.versions))
            for version_id in reversedVersions:
                if objectType == "Template":
                    version = Template.objects.get(pk=version_id)
                else:
                    version = Type.objects.get(pk=version_id)
                objectid = ObjectId(version.id)
                from_zone = tz.tzutc()
                to_zone = tz.tzlocal()
                datetimeUTC = objectid.generation_time
                datetimeUTC = datetimeUTC.replace(tzinfo=from_zone)
                datetimeLocal = datetimeUTC.astimezone(to_zone)
                datetime = datetimeLocal.strftime('%m/%d/%Y %H&#58;%M&#58;%S')
                versions[version] = datetime


            context = RequestContext(request, {
                'versions': versions,
                'objectVersions': objectVersions,
                'objectType': objectType,
            })
            return HttpResponse(template.render(context))
        except:
            return redirect('/')
    else:
        return redirect('/')


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
    id = request.GET.get('id', None)
    if id is not None:
        try:
            object = Template.objects.get(pk=id)
            xsltPath = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'xsd2html4modules.xsl')
            xslt = etree.parse(xsltPath)
            transform = etree.XSLT(xslt)

            dom = etree.parse(BytesIO(object.content.encode('utf-8')))
            annotations = dom.findall(".//{http://www.w3.org/2001/XMLSchema}annotation")
            for annotation in annotations:
                annotation.getparent().remove(annotation)
            newdom = transform(dom)
            xsdTree = str(newdom)

            request.session['moduleTemplateID'] = id
            request.session['moduleTemplateContent'] = object.content

            request.session['moduleNamespaces'] = common.get_namespaces(BytesIO(str(object.content)))
            for prefix, url in request.session['moduleNamespaces'].items():
                if (url == "{http://www.w3.org/2001/XMLSchema}"):
                    request.session['moduleDefaultPrefix'] = prefix
                    break

            context = RequestContext(request, {
                'xsdTree': xsdTree,
                'modules': Module.objects
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
        xslt_files = ExporterXslt.objects.all()
        result_xslt_files = ResultXslt.objects.all()
        context = RequestContext(request, {
            'upload_xslt_Form': upload_xslt_Form,
            'upload_result_xslt_Form': upload_result_xslt_Form,
            'xslt_files': xslt_files,
            'result_xslt_files': result_xslt_files,
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
