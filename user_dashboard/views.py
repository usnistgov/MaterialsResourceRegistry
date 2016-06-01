################################################################################
#
# File Name: views.py
# Application: user_dashboard
# Purpose:
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################


from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.template import RequestContext, loader
from django.shortcuts import redirect
from mgi.models import FormData, XMLdata
from admin_mdcs.forms import EditProfileForm, ChangePasswordForm, UserForm
from django.contrib.auth.decorators import login_required
from itertools import chain
from mgi.models import Template
from django.contrib.auth.models import User
from django.contrib import messages
import lxml.etree as etree
from io import BytesIO
import os
import xmltodict
from django.conf import settings
from bson.objectid import ObjectId

################################################################################
#
# Function Name: my_profile(request)
# Inputs:        request -
# Outputs:       My Profile Page
# Exceptions:    None
# Description:   Page that allows to look at user's profile information
#
################################################################################
@login_required(login_url='/login')
def my_profile(request):
    template = loader.get_template('dashboard/my_profile.html')
    context = RequestContext(request, {
        '': '',
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: my_profile_edit(request)
# Inputs:        request -
# Outputs:       Edit My Profile Page
# Exceptions:    None
# Description:   Page that allows to edit a profile
#
################################################################################
@login_required(login_url='/login')
def my_profile_edit(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=request.user.id)
            if request.POST['username'] != user.username:
                try:
                    user = User.objects.get(username=request.POST['username'])
                    message = "A user with the same username already exists."
                    return render(request, 'dashboard/my_profile_edit.html', {'form':form, 'action_result':message})
                except:
                    user.username = request.POST['username']

            user.first_name = request.POST['firstname']
            user.last_name = request.POST['lastname']
            user.email = request.POST['email']
            user.save()
            messages.add_message(request, messages.INFO, 'Profile information edited with success.')
            return redirect('/dashboard/my-profile')
    else:
        user = User.objects.get(id=request.user.id)
        data = {'firstname':user.first_name,
                'lastname':user.last_name,
                'username':user.username,
                'email':user.email}
        form = EditProfileForm(data)

    return render(request, 'dashboard/my_profile_edit.html', {'form':form})




################################################################################
#
# Function Name: my_profile_change_password(request)
# Inputs:        request -
# Outputs:       Change Password Page
# Exceptions:    None
# Description:   Page that allows to change a password
#
################################################################################
@login_required(login_url='/login')
def my_profile_change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=request.user.id)
            auth_user = authenticate(username=user.username, password=request.POST['old'])
            if auth_user is None:
                message = "The old password is incorrect."
                return render(request, 'dashboard/my_profile_change_password.html', {'form':form, 'action_result':message})
            else:
                user.set_password(request.POST['new1'])
                user.save()
                messages.add_message(request, messages.INFO, 'Password changed with success.')
                return redirect('/dashboard/my-profile')
    else:
        form = ChangePasswordForm()

    return render(request, 'dashboard/my_profile_change_password.html', {'form':form})


################################################################################
# Function Name: dashboard(request)
# Inputs:        request -
# Outputs:       My Profile Page
# Exceptions:    None
# Description:   Page that allows to look at user's profile information
#
################################################################################
@login_required(login_url='/login')
def dashboard(request):
    template = loader.get_template('dashboard.html')
    context = RequestContext(request, {
        '': '',
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: my_profile_favorites(request)
# Inputs:        request -
# Outputs:       My Favorites Page
# Exceptions:    None
# Description:
#
################################################################################
@login_required(login_url='/login')
def my_profile_favorites(request):
    template = loader.get_template('profile/my_profile_favorites.html')
    context = RequestContext(request, {
        '': '',
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: my_profile_resources(request)
# Inputs:        request -
# Outputs:       My Resources Page
# Exceptions:    None
# Description:
#
################################################################################
@login_required(login_url='/login')
def dashboard_resources(request):
    template = loader.get_template('dashboard/my_dashboard_my_resources.html')
    if 'template' in request.GET:
        template_name = request.GET['template']

        if template_name == 'datacollection':
            templateNamesQuery = list(chain(Template.objects.filter(title=template_name).values_list('id'), Template.objects.filter(title='repository').values_list('id'), Template.objects.filter(title='database').values_list('id'), Template.objects.filter(title='projectarchive').values_list('id')))
        else :
            templateNamesQuery = Template.objects.filter(title=template_name).values_list('id')
        templateNames = []
        for templateQuery in templateNamesQuery:
            templateNames.append(str(templateQuery))


        if 'ispublished' in request.GET:
            ispublished = request.GET['ispublished']
            context = RequestContext(request, {
                'XMLdatas': sorted(XMLdata.find({'iduser' : str(request.user.id), 'schema':{"$in" : templateNames}, 'ispublished': ispublished=='true'}), key=lambda data: data['lastmodificationdate'], reverse=True),
                'template': template_name,
                'ispublished': ispublished,
             })
        else:
            context = RequestContext(request, {
                'XMLdatas': sorted(XMLdata.find({'iduser' : str(request.user.id), 'schema':{"$in" : templateNames}}), key=lambda data: data['lastmodificationdate'], reverse=True),
                'template': template_name,
            })
    else:
        if 'ispublished' in request.GET:
            ispublished = request.GET['ispublished']
            context = RequestContext(request, {
                    'XMLdatas': sorted(XMLdata.find({'iduser' : str(request.user.id), 'ispublished': ispublished=='true'}), key=lambda data: data['lastmodificationdate'], reverse=True),
                    'ispublished': ispublished,
            })
        else:
            context = RequestContext(request, {
                    'XMLdatas': sorted(XMLdata.find({'iduser' : str(request.user.id)}), key=lambda data: data['lastmodificationdate'], reverse=True),
            })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: dashboard_detail_resource
# Inputs:        request -
# Outputs:       Detail of a resource
# Exceptions:    None
# Description:   Page that allows to see detail resource from a selected resource
#
################################################################################
@login_required(login_url='/login')
def dashboard_detail_resource(request) :
    template = loader.get_template('dashboard/my_dashboard_detail_resource.html')
    result_id = request.GET['id']
    type = request.GET['type']

    if type=='form':
        form_data = FormData.objects.get(pk=ObjectId(result_id))
        xmlString = form_data.xml_data
        title = form_data.name
        schemaId = form_data.template
    elif type=='record':
        xmlString = XMLdata.get(result_id)
        title = xmlString['title']
        schemaId = xmlString['schema']
        xmlString = xmltodict.unparse(xmlString['content']).encode('utf-8')


    xsltPath = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'xml2html.xsl')
    xslt = etree.parse(xsltPath)
    transform = etree.XSLT(xslt)

    #Check if a custom detailed result XSLT has to be used
    try:
        if (xmlString != ""):
            dom = etree.fromstring(str(xmlString))
            schema = Template.objects.get(pk=schemaId)
            if schema.ResultXsltDetailed:
                shortXslt = etree.parse(BytesIO(schema.ResultXsltDetailed.content.encode('utf-8')))
                shortTransform = etree.XSLT(shortXslt)
                newdom = shortTransform(dom)
            else:
                newdom = transform(dom)
        else:
            newdom = "No data to display"
    except Exception, e:
        #We use the default one
        newdom = transform(dom)

    result = str(newdom)
    context = RequestContext(request, {
        'XMLHolder': result,
        'title': title,
        'type': type
    })

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: dashboard_my_drafts(request)
# Inputs:        request -
# Outputs:       Review forms page
# Exceptions:    None
# Description:   Page that allows to review user forms (draft)
#
################################################################################
@login_required(login_url='/login')
def dashboard_my_drafts(request):
    forms = FormData.objects(user=str(request.user.id), xml_data_id__exists=False, xml_data__exists=True).order_by('template') # xml_data_id False if document not curated
    detailed_forms = []
    for form in forms:
        detailed_forms.append({'form': form, 'template_name': Template.objects().get(pk=form.template).title})
    user_form = UserForm(request.user)

    return render(request, 'dashboard/my_dashboard_my_forms.html', {'forms':detailed_forms, 'user_form': user_form})
