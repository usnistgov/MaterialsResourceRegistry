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
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.contrib.auth import authenticate
from django.template import RequestContext, loader
from django.shortcuts import redirect
from mgi.models import FormData, XMLdata, Status
from admin_mdcs.forms import EditProfileForm, UserForm
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
import json
from password_policies.views import PasswordChangeFormView
from django.utils import timezone
from django.core.urlresolvers import reverse
from utils.DateTimeDecoder import DateTimeEncoder

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
    template = loader.get_template('dashboard/my_dashboard_my_records.html')
    query = {}
    context = RequestContext(request, {})
    ispublished = request.GET.get('ispublished', None)
    template_name = request.GET.get('template', None)
    query['iduser'] = str(request.user.id)
    #If ispublished not None, check if we want publish or unpublish records
    if ispublished:
        ispublished = ispublished == 'true'
        query['ispublished'] = ispublished
    if template_name:
        context.update({'template': template_name})
        if template_name == 'datacollection':
            templateNamesQuery = list(chain(Template.objects.filter(title=template_name).values_list('id'),
                                            Template.objects.filter(title='repository').values_list('id'),
                                            Template.objects.filter(title='database').values_list('id'),
                                            Template.objects.filter(title='projectarchive').values_list('id')))
        else :
            templateNamesQuery = Template.objects.filter(title=template_name).values_list('id')
        templateNames = []
        for templateQuery in templateNamesQuery:
            templateNames.append(str(templateQuery))

        query['schema'] = {"$in" : templateNames}

    userXmlData = sorted(XMLdata.find(query), key=lambda data: data['lastmodificationdate'], reverse=True)
    #Add user_form for change owner
    user_form = UserForm(request.user)
    context.update({'XMLdatas': userXmlData, 'ispublished': ispublished, 'user_form': user_form})

    #If the user is an admin, we get records for other users
    if request.user.is_staff:
        #Get user name for admin
        usernames = dict((str(x.id), x.username) for x in User.objects.all())
        query['iduser'] = {"$ne": str(request.user.id)}
        otherUsersXmlData = sorted(XMLdata.find(query), key=lambda data: data['lastmodificationdate'], reverse=True)
        context.update({'OtherUsersXMLdatas': otherUsersXmlData, 'usernames': usernames})

    #Get new version of records
    listIds = [str(x['_id']) for x in userXmlData]
    if request.user.is_staff:
        listIdsOtherUsers = [str(x['_id']) for x in otherUsersXmlData]
        listIds = list(set(listIds).union(set(listIdsOtherUsers)))

    drafts = FormData.objects(xml_data_id__in=listIds, isNewVersionOfRecord=True).all()
    XMLdatasDrafts = dict()
    for draft in drafts:
        XMLdatasDrafts[draft.xml_data_id] = draft.id
    context.update({'XMLdatasDrafts': XMLdatasDrafts})

    #Add Status enum
    context.update({'Status': Status})

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
        xmlString = form_data.xml_data.encode('utf-8')
        title = form_data.name
        schemaId = form_data.template
    elif type=='record':
        xmlString = XMLdata.get(result_id)
        title = xmlString['title']
        schemaId = xmlString['schema']
        xmlString = XMLdata.unparse(xmlString['content']).encode('utf-8')


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
    template = loader.get_template('dashboard/my_dashboard_my_forms.html')
    forms = FormData.objects(user=str(request.user.id), xml_data_id__exists=False,
                             xml_data__exists=True).order_by('template') # xml_data_id False if document not curated
    detailed_forms = []
    for form in forms:
        detailed_forms.append({'form': form, 'template_name': Template.objects().get(pk=form.template).title,
                               'user': form.user})
    user_form = UserForm(request.user)
    context = RequestContext(request, {'forms': detailed_forms,
                                       'user_form': user_form
    })
    #If the user is an admin, we get forms for other users
    if request.user.is_staff:
        #Get user name for admin
        usernames = dict((str(x.id), x.username) for x in User.objects.all())
        other_users_detailed_forms = []
        otherUsersForms = FormData.objects(user__ne=str(request.user.id), xml_data_id__exists=False,
                                                       xml_data__exists=True).order_by('template')
        for form in otherUsersForms:
            other_users_detailed_forms.append({'form': form,
                                               'template_name': Template.objects().get(pk=form.template).title,
                                               'user': form.user})
        context.update({'otherUsersForms': other_users_detailed_forms, 'usernames': usernames})

    return HttpResponse(template.render(context))



################################################################################
#
# Function Name: change_owner_record(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Change the record owner
#
################################################################################
def change_owner_record(request):
    if 'recordID' in request.POST and 'userID' in request.POST:
        xml_data_id = request.POST['recordID']
        user_id = request.POST['userID']
        try:
            XMLdata.update_user(xml_data_id, user=user_id)
            messages.add_message(request, messages.INFO, 'Record Owner changed with success.')
        except Exception, e:
            return HttpResponseServerError({"Something wrong occurred during the change of owner."}, status=500)
    else:
        return HttpResponseBadRequest({"Bad entries. Please check the parameters."})

    return HttpResponse(json.dumps({}), content_type='application/javascript')

class UserDashboardPasswordChangeFormView(PasswordChangeFormView):
    def form_valid(self, form):
        messages.success(self.request, "Password changed with success.")
        return super(UserDashboardPasswordChangeFormView, self).form_valid(form)

    def get_success_url(self):
        """
Returns a query string field with a previous URL if available (Mimicing
the login view. Used on forced password changes, to know which URL the
user was requesting before the password change.)
If not returns the :attr:`~PasswordChangeFormView.success_url` attribute
if set, otherwise the URL to the :class:`PasswordChangeDoneView`.
"""
        checked = '_password_policies_last_checked'
        last = '_password_policies_last_changed'
        required = '_password_policies_change_required'
        now = json.dumps(timezone.now(), cls=DateTimeEncoder)
        self.request.session[checked] = now
        self.request.session[last] = now
        self.request.session[required] = False
        redirect_to = self.request.POST.get(self.redirect_field_name, '')
        if redirect_to:
            url = redirect_to
        elif self.success_url:
            url = self.success_url
        else:
            url = reverse('password_change_done')
        return url
