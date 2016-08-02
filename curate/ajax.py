################################################################################
#
# File Name: ajax.py
# Application: curate
# Purpose:   AJAX methods used by the Curator
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

from bson.objectid import ObjectId
from django.http import HttpResponse
from io import BytesIO
from django.core.servers.basehttp import FileWrapper
from cStringIO import StringIO
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_501_NOT_IMPLEMENTED
from curate.models import SchemaElement
from mgi.exceptions import MDCSError
from mgi.models import Template, FormData
import json
from mgi import common, settings
import lxml.etree as etree
from django.contrib import messages
import os
from utils.XSDParser.parser import generate_form, generate_element_absent, generate_choice_absent, \
    update_branch_xpath, delete_branch_from_db
from utils.XSDParser.renderer import DefaultRenderer
from utils.XSDParser.renderer.list import ListRenderer
from utils.XSDParser.renderer.xml import XmlRenderer


################################################################################
#
# Function Name: change_owner_form(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Change the form owner
#
################################################################################
def change_owner_form(request):
    if 'formId' and 'userID' in request.POST:
        form_data_id = request.POST['formID']
        user_id = request.POST['userID']
        try:
            form_data = FormData.objects().get(pk=form_data_id)
            form_data.user = user_id
            form_data.save()
            messages.add_message(request, messages.INFO, 'Form Owner changed with success !')
        except Exception, e:
            return HttpResponse({}, status=400)
    return HttpResponse({})


################################################################################
#
# Function Name: cancel_form(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Cancel a form being entered
#
################################################################################
def cancel_form(request):
    try:
        form_data_id = request.session['curateFormData']
        form_data = FormData.objects().get(pk=form_data_id)
        # TODO: check if need to delete all schema elements

        if form_data.schema_element_root is not None:
            delete_branch_from_db(form_data.schema_element_root.pk)

        form_data.delete()
        messages.add_message(request, messages.INFO, 'Form deleted with success.')
        return HttpResponse({},status=204)
    except Exception, e:
        return HttpResponse({},status=400)


################################################################################
#
# Function Name: delete_form(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Deletes a saved form
#
################################################################################
def delete_form(request):
    if 'id' in request.GET:
        form_data_id = request.GET['id']
        try:
            form_data = FormData.objects().get(pk=form_data_id)
            # TODO: check if need to delete all SchemaElements
            if form_data.schema_element_root is not None:
                delete_branch_from_db(form_data.schema_element_root.pk)

            form_data.delete()

            messages.add_message(request, messages.INFO, 'Form deleted with success.')
        except Exception, e:
            return HttpResponse({}, status=400)
    return HttpResponse({})


################################################################################
#
# Function Name: load_xml(request)
# Inputs:        request -
# Outputs:       JSON data with templateSelected
# Exceptions:    None
# Description:   Loads the XML data in the view data page. First transforms the data.
#
################################################################################
def load_xml(request):
    if 'form_id' not in request.session:
        return HttpResponse(status=HTTP_404_NOT_FOUND)

    xml_form_id = SchemaElement.objects.get(pk=request.session['form_id'])

    xml_renderer = XmlRenderer(xml_form_id)
    xml_string = xml_renderer.render()

    xslt_path = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'nmrr-detail.xsl')
    xslt = etree.parse(xslt_path)
    transform = etree.XSLT(xslt)

    xml_tree = ""
    if xml_string != "":
        dom = etree.fromstring(xml_string)
        newdom = transform(dom)
        xml_tree = str(newdom)

    response_dict = {"XMLHolder": xml_tree}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: clear_fields(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Clears fields of the HTML form. Also restore the occurrences.
#
################################################################################
def clear_fields(request):
    # form = generate_form(request)
    # response_dict = {'xsdForm': form}
    # return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    if 'form_id' in request.session:
        del request.session['form_id']

    return generate_xsd_form(request)


################################################################################
#
# Function Name: download_xml(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Make the current XML document available for download.
#
################################################################################
def download_xml(request):
    form_data_id = request.session['curateFormData']
    form_data = FormData.objects.get(pk=ObjectId(form_data_id))

    form_id = request.session['form_id']
    xml_root_element = SchemaElement.objects.get(pk=form_id)
    xml_renderer = XmlRenderer(xml_root_element)
    xml_data = StringIO(xml_renderer.render().encode("utf-8"))

    response = HttpResponse(FileWrapper(xml_data), content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename=' + form_data.name + '.xml'
    return response


################################################################################
#
# Function Name: download_xml(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Make the current XML document available for download.
#
################################################################################
def download_current_xml(request):
    form_data_id = request.session['curateFormData']
    form_data = FormData.objects.get(pk=ObjectId(form_data_id))

    form_id = request.session['form_id']
    xml_root_element = SchemaElement.objects.get(pk=form_id)
    xml_renderer = XmlRenderer(xml_root_element)
    xml_data = StringIO(xml_renderer.render().encode("utf-8"))

    response = HttpResponse(FileWrapper(xml_data), content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename=' + form_data.name + '.xml'
    return response


################################################################################
#
# Function Name: init_curate(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Reinitialize data structures
#
################################################################################
def init_curate(request):
    if 'form_id' in request.session:
        del request.session['form_id']

    if 'form_name' in request.session:
        del request.session['form_name']

    if 'xmlDocTree' in request.session:
        del request.session['xmlDocTree']

    return HttpResponse(json.dumps({}), content_type='application/javascript')


def load_config():
    """
    Load configuration for the parser
    :return:
    """
    return {
        'PARSER_APPLICATION': 'CURATE',
        'PARSER_MIN_TREE': settings.PARSER_MIN_TREE if hasattr(settings, 'PARSER_MIN_TREE') else True,
        'PARSER_IGNORE_MODULES': settings.PARSER_IGNORE_MODULES if hasattr(settings, 'PARSER_IGNORE_MODULES') else False,
        'PARSER_COLLAPSE': settings.PARSER_COLLAPSE if hasattr(settings, 'PARSER_COLLAPSE') else True,
        'PARSER_AUTO_KEY_KEYREF': settings.PARSER_AUTO_KEY_KEYREF if
        hasattr(settings, 'PARSER_AUTO_KEY_KEYREF') else False,
        'PARSER_IMPLICIT_EXTENSION_BASE': settings.PARSER_IMPLICIT_EXTENSION_BASE if
        hasattr(settings, 'PARSER_IMPLICIT_EXTENSION_BASE') else False,
    }


def generate_xsd_form(request):
    """ Renders HTMl form for display.

    Parameters:
        request:

    Returns:
        str: HTML form
    """
    try:
        if 'form_id' in request.session:
            root_element_id = request.session['form_id']
            form_data = None
            request.session['curate_edit'] = False
        else:  # If this is a new form, generate it and store the root ID
            # get the xsd tree when going back and forth with review step
            if 'xmlDocTree' in request.session:
                xsd_doc_data = request.session['xmlDocTree']
            else:
                template_id = request.session['currentTemplateID']
                template_object = Template.objects.get(pk=template_id)
                xsd_doc_data = template_object.content

            # get form data from the database (empty one or existing one)
            form_data_id = request.session['curateFormData']
            form_data = FormData.objects.get(pk=ObjectId(form_data_id))

            if form_data.xml_data is not None:
                xml_doc_data = form_data.xml_data
            else:
                xml_doc_data = None

            root_element_id = generate_form(request, xsd_doc_data, xml_doc_data, config=load_config())
            request.session['form_id'] = str(root_element_id)

        root_element = SchemaElement.objects.get(pk=root_element_id)

        if form_data is not None:
            if form_data.schema_element_root is not None:
                delete_branch_from_db(form_data.schema_element_root.pk)

            form_data.update(set__schema_element_root=root_element)
            form_data.reload()

        renderer = ListRenderer(root_element, request)
        html_form = renderer.render()
    except Exception as e:
        renderer = DefaultRenderer(SchemaElement(), {})

        if e.message is not None:
            err_message = e.message
        else:
            err_message = "An unknown error raised " + e.__class__.__name__

        html_form = renderer._render_form_error(err_message)

    return HttpResponse(json.dumps({'xsdForm': html_form}), content_type='application/javascript')


def get_element_value(request):
    """ Returns the value of an element

    :param request:
    :return:
    """
    if 'id' not in request.POST:
        return HttpResponse(status=HTTP_400_BAD_REQUEST)

    element = SchemaElement.objects.get(pk=request.POST['id'])
    element_value = element.value

    if element.tag == 'module':
        element_value = {
            'data': element.options['data'],
            'attributes': element.options['attributes']
        }

    return HttpResponse(json.dumps({'value': element_value}), content_type='application/json')


def save_element(request):
    """

    :param request:
    :return:
    """
    if 'id' not in request.POST or 'value' not in request.POST:
        return HttpResponse(status=HTTP_400_BAD_REQUEST)

    # print request.POST['inputs']

    input_element = SchemaElement.objects.get(pk=request.POST['id'])

    input_previous_value = input_element.value
    input_element.value = request.POST['value']
    input_element.save()

    return HttpResponse(json.dumps({'replaced': input_previous_value}), content_type='application/json')


def save_module(request):
    """

    :param request:
    :return:
    """
    if 'id' not in request.POST or 'value' not in request.POST:
        return HttpResponse(status=HTTP_400_BAD_REQUEST)

    input_element = SchemaElement.objects.get(pk=request.POST['id'])

    input_previous_value = input_element.value
    input_element.value = request.POST['value']
    input_element.save()

    return HttpResponse(json.dumps({'replaced': input_previous_value}), content_type='application/json')


def save_form(request):
    """Save the current form in MongoDB. Convert it to XML format first.

    :param request:
    :return:
    """
    form_id = request.session['form_id']
    root_element = SchemaElement.objects.get(pk=form_id)

    xml_renderer = XmlRenderer(root_element)
    xml_data = xml_renderer.render()

    form_data_id = request.session['curateFormData']
    form_data = FormData.objects.get(pk=form_data_id)
    form_data.xml_data = xml_data
    form_data.save()

    return HttpResponse(json.dumps({}), content_type='application/json')


################################################################################
#
# Function Name: validate_xml_data(request)
# Inputs:        request -
#                xmlString - XML string generated from the form
#                xsdForm -  Current form
# Outputs:
# Exceptions:    None
# Description:   Check if the current XML document is valid according to the template
#
#
################################################################################
def validate_xml_data(request):
    # template_id = request.session['currentTemplateID']
    try:
        xsd_tree_str = str(request.session['xmlDocTree'])

        form_id = request.session['form_id']
        root_element = SchemaElement.objects.get(pk=form_id)

        xml_renderer = XmlRenderer(root_element)
        xml_data = xml_renderer.render()

        # validate XML document
        common.validateXMLDocument(xml_data, xsd_tree_str)
    except etree.XMLSyntaxError as xse:
        # xmlParseEntityRef exception: use of & < > forbidden
        message = "Validation Failed. </br> May be caused by : </br> - Syntax problem </br> - Use of forbidden symbols : '&' or '<' or '>'"
        response_dict = {'errors': message}
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    except Exception as e:
        message = e.message.replace('"', '\'')
        response_dict = {'errors': message}
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: view_data(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Save the content of the current form in session before redirection to view data
#
################################################################################
def view_data(request):
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: set_current_template(request)
# Inputs:        request -
# Outputs:       JSON data with success or failure
# Exceptions:    None
# Description:   Set the current template to input argument.  Template is read
#                into an xsdDocTree for use later.
#
################################################################################
def set_current_template(request):
    print 'BEGIN def set_current_template(request)'

    template_id = request.POST['templateID']

    # reset global variables

    request.session['currentTemplateID'] = template_id
    request.session.modified = True

    templateObject = Template.objects.get(pk=template_id)
    xmlDocData = templateObject.content

    XMLtree = etree.parse(BytesIO(xmlDocData.encode('utf-8')))
    request.session['xmlDocTree'] = etree.tostring(XMLtree)

    print 'END def set_current_template(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: set_current_user_template(request)
# Inputs:        request -
# Outputs:       JSON data with success or failure
# Exceptions:    None
# Description:   Set the current template to input argument.  Template is read
#                into an xsdDocTree for use later. This case is for templates
#                defined using the composer.
#
################################################################################
def set_current_user_template(request):
    print 'BEGIN def setCurrentTemplate(request)'

    template_id = request.POST['templateID']

    # reset global variables
    request.session['currentTemplateID'] = template_id
    request.session.modified = True

    templateObject = Template.objects.get(pk=template_id)

    xmlDocData = templateObject.content

    XMLtree = etree.parse(BytesIO(xmlDocData.encode('utf-8')))
    request.session['xmlDocTree'] = etree.tostring(XMLtree)

    print 'END def setCurrentTemplate(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: verify_template_is_selected(request)
# Inputs:        request -
# Outputs:       JSON data with templateSelected
# Exceptions:    None
# Description:   Verifies the current template is selected.
#
################################################################################
def verify_template_is_selected(request):
    print 'BEGIN def verify_template_is_selected(request)'
    if 'currentTemplateID' in request.session:
        templateSelected = 'yes'
    else:
        templateSelected = 'no'

    print 'END def verify_template_is_selected(request)'

    response_dict = {'templateSelected': templateSelected}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


def generate_absent(request):
    """

    :param request:
    :return:
    """
    element_id = request.POST['id']
    html_form = generate_element_absent(request, element_id, config=load_config())
    return HttpResponse(html_form)


def generate_choice_branch(request):
    element_id = request.POST['id']

    try:
        html_form = generate_choice_absent(request, element_id, config=load_config())
    except MDCSError:
        return HttpResponse(status=HTTP_501_NOT_IMPLEMENTED)

    return HttpResponse(html_form)


def remove_element(request):
    element_id = request.POST['id']
    # sub_element = SchemaElement.objects.get(pk=element_id)
    element_list = SchemaElement.objects(children=element_id)

    if len(element_list) == 0:
        raise ValueError("No SchemaElement found")
    elif len(element_list) > 1:
        raise ValueError("More than one SchemaElement found")

    # Removing the element from the data structure
    schema_element = element_list[0]
    schema_element.update(pull__children=element_id)

    schema_element.reload()
    update_branch_xpath(schema_element)

    # Deleting the branch from the database
    delete_branch_from_db(element_id)

    children_number = len(schema_element.children)

    # TODO Move it to parser function
    # FIXME Sequence elem it might not work
    if len(schema_element.children) == 0:
        elem_iter = SchemaElement()

        if schema_element.tag == 'element':
            elem_iter.tag = 'elem-iter'
        elif schema_element.tag == 'choice':
            elem_iter.tag = 'choice-iter'
        elif schema_element.tag == 'sequence':
            elem_iter.tag = 'sequence-iter'

        elem_iter.save()
        schema_element.update(add_to_set__children=[elem_iter])
        schema_element.reload()

    response = {
        'code': 0,
        'html': ""
    }

    if children_number > schema_element.options['min']:
        return HttpResponse(json.dumps(response), status=HTTP_200_OK)
    else:  # len(schema_element.children) == schema_element.options['min']
        if schema_element.options['min'] != 0:
            response['code'] = 1
        else:  # schema_element.options['min'] == 0
            renderer = ListRenderer(schema_element, request)
            html_form = renderer.render(True)

            response['code'] = 2
            response['html'] = html_form

        return HttpResponse(json.dumps(response))


def reload_form(request):
    """
    Reload the form string from latest version saved
    :param request:
    :return:
    """
    try:
        form_data_id = request.session['curateFormData']
        form_data = FormData.objects().get(pk=form_data_id)
        xml_data = form_data.xml_data

        template_id = request.session['currentTemplateID']
        template_object = Template.objects.get(pk=template_id)
        xsd_doc_data = template_object.content

        # the form has been saved already
        if xml_data is not None and xml_data != '':
            request.session['curate_edit'] = True
            root_element_id = generate_form(request, xsd_doc_data, xml_data, config=load_config())
        # the form has never been saved
        else:
            root_element_id = generate_form(request, xsd_doc_data, config=load_config())

        root_element = SchemaElement.objects.get(pk=root_element_id)
        renderer = ListRenderer(root_element, request)
        html_form = renderer.render()
        request.session['form_id'] = str(root_element_id)
        return HttpResponse(json.dumps({'xsdForm': html_form}), content_type='application/javascript')
    except Exception, e:
        return HttpResponse({}, status=400)
