################################################################################
#
# File Name: ajax.py
# Application: user_dashboard
# Purpose:   AJAX methods used for user dashboard purposes
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

from django.http import HttpResponse, HttpResponseBadRequest
from mgi.models import XMLdata, FormData
import json
from bson.objectid import ObjectId
from mgi.common import send_mail_to_managers
import os
from django.utils.importlib import import_module
from django.shortcuts import redirect
from utils.XSDParser.parser import delete_branch_from_db
from django.contrib import messages
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
MDCS_URI = settings.MDCS_URI


################################################################################
#
# Function Name: delete_result(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Delete an XML document from the database
#
################################################################################
def delete_result(request):
    result_id = request.GET['result_id']

    try:
        XMLdata.delete(result_id)
    except:
        # XML can't be found
        pass

    return HttpResponse(json.dumps({}), content_type='application/javascript')

################################################################################
#
# Function Name: update_publish(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Publish and update the publish date of an XMLdata
#
################################################################################
def update_publish(request):
    XMLdata.update_publish(request.GET['result_id'])
    resource = XMLdata.get(request.GET['result_id'])

    # Send mail to the user and the admin
    context = {'URI': MDCS_URI,
               'title': resource['title'],
               'publicationdate': resource['publicationdate'],
               'user': request.user.username}

    send_mail_to_managers(subject='Resource Published',
                                pathToTemplate='dashboard/email/resource_published.html',
                                context=context)
    return HttpResponse(json.dumps({}), content_type='application/javascript')

################################################################################
#
# Function Name: update_unpublish(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Unpublish an XMLdata
#
################################################################################
def update_unpublish(request):
    XMLdata.update_unpublish(request.GET['result_id'])
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: edit_curate_form(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Set data in session before editing form
#
################################################################################
def edit_curate_form(request):
    form_data_id = request.GET['id']
    form_data = FormData.objects.get(pk=ObjectId(form_data_id))
    request.session['currentTemplateID'] = form_data.template
    request.session['form_id'] = str(form_data.schema_element_root.id)
    url='/curate/edit-form?id='+form_data_id
    return redirect(url)


################################################################################
#
# Function Name: update_publish_draft(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Publish a draft
#
################################################################################
def update_publish_draft(request):
    form_id = request.GET['draft_id']
    form_data = FormData.objects.get(pk=form_id)
    xml_string = form_data.xml_data
    title = form_data.name
    if xml_string == "" or xml_string is None:
        return HttpResponseBadRequest('No XML data found')
    try:
        # update form data if id is present
        if form_data.xml_data_id is not None:
            publicationdate = XMLdata.update_publish_draft(form_data.xml_data_id, xml_string, str(request.user.id))
            #Delete the form
            if form_data.schema_element_root is not None:
                delete_branch_from_db(form_data.schema_element_root.pk)
            form_data.delete()

            # Send mail to the managers
            context = {'URI': MDCS_URI,
                       'title': title,
                       'publicationdate': publicationdate,
                       'user': request.user.username}

            send_mail_to_managers(subject='Resource Published',
                                    pathToTemplate='dashboard/email/resource_published.html',
                                    context=context)

            messages.add_message(request, messages.INFO, 'New version published with success.')
            return HttpResponse(json.dumps({}), content_type='application/javascript')
        else:
            return HttpResponseBadRequest('Related record not found. Impossible to publish the draft')

    except Exception, e:
        message = e.message.replace('"', '\'')
        return HttpResponseBadRequest(message)


################################################################################
#
# Function Name: change_status(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   change status of a record
#
################################################################################
def change_status(request):
    ispublished = request.GET['is_published'] == 'True'
    XMLdata.change_status(request.GET['result_id'], request.GET['status'], ispublished)
    return HttpResponse(json.dumps({}), content_type='application/javascript')






