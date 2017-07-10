################################################################################
#
# File Name: views.py
# Application: curate
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

from cStringIO import StringIO
from django.http import HttpResponse
from django.template import RequestContext, loader, Context
from django.shortcuts import redirect
from django.core.servers.basehttp import FileWrapper
from bson.objectid import ObjectId
import lxml.etree as etree
from io import BytesIO
from lxml.etree import XMLSyntaxError
import json
import xmltodict
from django.contrib import messages
from curate.ajax import load_config

from curate.models import SchemaElement
from mgi.models import Template, TemplateVersion, XML2Download, FormData, XMLdata
from curate.forms import NewForm, OpenForm, UploadForm, SaveDataForm, CancelChangesForm
from django.http.response import HttpResponseBadRequest
from admin_mdcs.models import permission_required
import mgi.rights as RIGHTS
from mgi.exceptions import MDCSError



################################################################################
#
# Function Name: index(request)
# Inputs:        request - 
# Outputs:       Main Page of Curate Application
# Exceptions:    None
# Description:   Page that allows to select a template to start curating         
#
################################################################################
from utils.XSDParser.parser import delete_branch_from_db, generate_form
from utils.XSDParser.renderer.xml import XmlRenderer


@permission_required(content_type=RIGHTS.curate_content_type, permission=RIGHTS.curate_access, login_url='/login')
def index(request):
    template = loader.get_template('curate/curate.html')
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
       'templates':currentTemplates,
       'userTemplates': Template.objects(user=str(request.user.id)),
    })

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: curate_select_template(request)
# Inputs:        request -
# Outputs:       Main Page of Curate Application
# Exceptions:    None
# Description:   Page that allows to select a template to start curating data
#
#
################################################################################
@permission_required(content_type=RIGHTS.curate_content_type, permission=RIGHTS.curate_access, login_url='/login')
def curate_select_template(request):
    template = loader.get_template('curate/curate.html')
    context = RequestContext(request, {
        '': '',
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: curate_edit_data(request)
# Inputs:        request -
# Outputs:       Edit Data
# Exceptions:    None
# Description:   Call by curate_enter_data if we want to edit the form
#
#
################################################################################
@permission_required(content_type=RIGHTS.curate_content_type, permission=RIGHTS.curate_edit_document,
                     login_url='/login')
def curate_edit_data(request):
    try:
        if 'useForm' in request.GET and request.GET['useForm'] == 'true':
            pass
        else:
            xml_data_id = request.GET['id']
            request.session['curate_edit'] = True
            # remove previously created forms when editing a new one
            previous_forms = FormData.objects(user=str(request.user.id), xml_data_id__exists=True,
                                              isNewVersionOfRecord=False)
            for previous_form in previous_forms:
                if previous_form.schema_element_root is not None:
                    delete_branch_from_db(previous_form.schema_element_root.pk)
                previous_form.delete()

            #Check if a form_data already exists for this record
            form_data = FormData.objects(xml_data_id=xml_data_id).all().first()
            if not form_data:
                xml_data = XMLdata.get(xml_data_id)
                json_content = xml_data['content']
                xml_content = XMLdata.unparse(json_content)
                form_data = FormData(
                    user=str(request.user.id),
                    template=xml_data['schema'],
                    name=xml_data['title'],
                    xml_data=xml_content,
                    xml_data_id=xml_data_id,
                    isNewVersionOfRecord=xml_data.get('ispublished', False)
                )
                form_data.save()

            request.session['currentTemplateID'] = form_data.template
            request.session['curate_edit_data'] = form_data.xml_data
            request.session['curateFormData'] = str(form_data.pk)

            if 'form_id' in request.session:
                del request.session['form_id']
            if 'xmlDocTree' in request.session:
                del request.session['xmlDocTree']
    except:
        raise MDCSError("The document you are looking for doesn't exist.")


################################################################################
#
# Function Name: curate_from_schema(request)
# Inputs:        request -
# Outputs:       Edit Data
# Exceptions:    None
# Description:   Load Data Entry Form from a template name
#                If many template of the same name:
#                    - take the current one if from the same version
#                    - raise exception otherwise
#                TODO: is used in addition to start_curate, can't be used by itself in magic URL
#
#
################################################################################
@permission_required(content_type=RIGHTS.curate_content_type, permission=RIGHTS.curate_access, login_url='/login')
def curate_from_schema(request):
    try:
        schema_name = request.GET['template']
        templates = Template.objects(title=schema_name)

        if 'curate_edit' in request.session and request.session['curate_edit'] == False:
            # if the schemas are all versions of the same schema
            if len(set(templates.values_list('templateVersion'))) == 1:
                template_id = TemplateVersion.objects().get(pk=templates[0].templateVersion).current
                request.session['currentTemplateID'] = template_id
                #
                # form_data = FormData(user=str(request.user.id), template=template_id, name=schema_name)
                # form_data.save()
                #
                # request.session['curateFormData'] = str(form_data.pk)
                # request.session['curate_edit'] = False

                if 'useForm' in request.GET and request.GET['useForm'] == 'true':
                    pass
                else:
                    if 'formString' in request.session:
                        del request.session['formString']
                    # if 'xmlDocTree' in request.session:
                    #     del request.session['xmlDocTree']
            else:
                error_message = "The selection of template by name can't be used if the MDCS contain more than one "
                error_message += "template with the same name."

                raise MDCSError(error_message)
    except:
        raise MDCSError("The template you are looking for doesn't exist.")


################################################################################
#
# Function Name: curate_enter_data(request)
# Inputs:        request -
# Outputs:       Enter Data Page
# Exceptions:    None
# Description:   Page that allows to fill XML document data using an HTML form
#
#
################################################################################
@permission_required(content_type=RIGHTS.curate_content_type, permission=RIGHTS.curate_access, login_url='/login')
def curate_enter_data(request):
    print "BEGIN curate_enter_data(request)"

    try:
        context = RequestContext(request, {})
        if 'id' in request.GET:
            xml_data_id = request.GET['id']
            xml_data = XMLdata.get(xml_data_id)
            template = Template.objects().get(pk=ObjectId(xml_data['schema']))
            context = RequestContext(request, {'edit': True, 'template_name': template.title})
            curate_edit_data(request)
        elif 'template' in request.GET:
            context = RequestContext(request, {'template_name': request.GET['template']})
            curate_from_schema(request)
        elif 'templateid' in request.GET:
            pass

        template = loader.get_template('curate/curate_enter_data.html')

        return HttpResponse(template.render(context))
    except MDCSError, e:
        template = loader.get_template('curate/errors.html')
        context = RequestContext(request, {
            'errors': e.message,
        })
        return HttpResponse(template.render(context))


################################################################################
#
# Function Name: curate_view_data(request)
# Inputs:        request -
# Outputs:       View Data Page
# Exceptions:    None
# Description:   Page that allows to view XML data to be curated
#
################################################################################
@permission_required(content_type=RIGHTS.curate_content_type, permission=RIGHTS.curate_access, login_url='/login')
def curate_view_data(request):
    template = loader.get_template('curate/curate_view_data.html')

    # get form data from the database
    form_data_id = request.session['curateFormData']
    form_data = FormData.objects.get(pk=ObjectId(form_data_id))
    if not form_data.name.lower().endswith('.xml'):
        form_data.name += ".xml"
    form_name = form_data.name

    # detect if new document, or editing
    if form_data.xml_data_id is not None:
        edit = True
    else:
        edit = False

    context = RequestContext(request, {
        'form_save': SaveDataForm({"title": form_name}),
        'edit': edit,
    })
    if 'currentTemplateID' not in request.session:
        return redirect('/curate/select-template')
    else:
        return HttpResponse(template.render(context))


################################################################################
#
# Function Name: curate_view_data_downloadxsd(request)
# Inputs:        request -
# Outputs:       XSD representation of the current form instance
# Exceptions:    None
# Description:   Returns an XSD representation of the current form instance.
#                Used when user wants to download the form / xml schema.
#
################################################################################
@permission_required(content_type=RIGHTS.curate_content_type, permission=RIGHTS.curate_access, login_url='/login')
def curate_enter_data_downloadxsd(request):
    if 'currentTemplateID' not in request.session:
        return redirect('/curate/select-template')
    else:
        templateID = request.session['currentTemplateID']

        templateObject = Template.objects.get(pk=ObjectId(templateID))
        template_filename = templateObject.filename

        xsdDocData = templateObject.content

        xsdEncoded = xsdDocData.encode('utf-8')
        fileObj = StringIO(xsdEncoded)

        response = HttpResponse(FileWrapper(fileObj), content_type='application/xsd')
        response['Content-Disposition'] = 'attachment; filename=' + template_filename
        return response


################################################################################
#
# Function Name: curate_view_data_downloadxml(request)
# Inputs:        request -
# Outputs:       XML representation of the current data instance
# Exceptions:    None
# Description:   Returns an XML representation of the current data instance.
#                Used when user wants to download the XML file.
#
################################################################################
@permission_required(content_type=RIGHTS.curate_content_type, permission=RIGHTS.curate_access, login_url='/login')
def curate_view_data_downloadxml(request):
    if 'currentTemplateID' not in request.session:
        return redirect('/curate/select-template')
    else:
        xml2downloadID = request.GET.get('id', None)

        if xml2downloadID is not None:
            xmlDataObject = XML2Download.objects.get(pk=xml2downloadID)

            xmlStringEncoded = xmlDataObject.xml.encode('utf-8')
            fileObj = StringIO(xmlStringEncoded)

            xmlDataObject.delete()

            if not xmlDataObject.title.lower().endswith('.xml'):
                xmlDataObject.title += ".xml"

            response = HttpResponse(FileWrapper(fileObj), content_type='application/xml')
            response['Content-Disposition'] = 'attachment; filename=' + xmlDataObject.title
            return response
        else:
            return redirect('/')


################################################################################
#
# Function Name: start_curate(request)
# Inputs:        request -
# Exceptions:    None
# Description:   Load forms to start curation
#
################################################################################
@permission_required(content_type=RIGHTS.curate_content_type, permission=RIGHTS.curate_access, login_url='/login')
def start_curate(request):
    if 'currentTemplateID' not in request.session and 'template' not in request.GET:
        return redirect('/curate/select-template')
    else:
        if request.method == 'POST':
            # parameters to build FormData object in db
            user = request.user.id
            template_id = request.session['currentTemplateID']

            form_data = None

            selected_option = request.POST['curate_form']
            if selected_option == "new":
                request.session['curate_edit'] = False
                new_form = NewForm(request.POST)
                try:
                    form_data = FormData(user=str(user), template=template_id, name=new_form.data['document_name'],
                                         xml_data=None).save()
                except:
                    return HttpResponseBadRequest(
                        'Unable to create the form. A form with the same name may already exists.')
            elif selected_option == "open":
                request.session['curate_edit'] = True
                open_form = OpenForm(request.POST)
                form_data = FormData.objects.get(pk=ObjectId(open_form.data['forms']))
            elif selected_option == "upload":
                request.session['curate_edit'] = True
                upload_form = UploadForm(request.POST, request.FILES)
                xml_file = request.FILES['file']
                # put the cursor at the beginning of the file
                xml_file.seek(0)
                # read the content of the file
                xml_data = xml_file.read()
                # check XML data or not?
                try:
                    etree.fromstring(xml_data)
                except XMLSyntaxError:
                    return HttpResponseBadRequest('Uploaded File is not well formed XML.')
                try:
                    form_data = FormData(user=str(user), template=template_id, name=xml_file.name,
                                         xml_data=xml_data).save()
                except:
                    return HttpResponseBadRequest(
                        'Unable to create the form. A form with the same name may already exist.')

            # parameters that will be used during curation
            request.session['curateFormData'] = str(form_data.id)

            return HttpResponse('ok')
        else:
            try:
                ajaxCall = False
                context_params = dict()
                if 'template' in request.GET:
                    schema_name = request.GET['template']
                    context_params['template_name'] = schema_name
                    try:
                        templates = Template.objects(title=schema_name)
                    except:
                        raise MDCSError("The template you are looking for doesn't exist.")

                    # if the schemas are all versions of the same schema
                    if len(set(templates.values_list('templateVersion'))) == 1:
                        template_id = TemplateVersion.objects().get(pk=templates[0].templateVersion).current
                        request.session['currentTemplateID'] = template_id
                    else:
                        raise MDCSError("The selection of template by name can't be used if the MDCS contain more than "
                                        "one template with the same name.")

                    template = loader.get_template('curate/curate_full_start.html')

                    if 'formString' in request.session:
                        del request.session['formString']

                    if 'xmlDocTree' in request.session:
                        del request.session['xmlDocTree']

                else:
                    ajaxCall = True
                    template = loader.get_template('curate/curate_start.html')

                open_form = OpenForm(forms=FormData.objects(user=str(request.user.id),
                                                            template=request.session['currentTemplateID'],
                                                            xml_data_id__exists=False))
                new_form = NewForm()
                upload_form = UploadForm()

                context_params['new_form'] = new_form
                context_params['open_form'] = open_form
                context_params['upload_form'] = upload_form

                context = RequestContext(request, context_params)  # , 'options_form': options_form})

                if ajaxCall:
                    return HttpResponse(json.dumps({'template': template.render(context)}),
                                        content_type='application/javascript')
                else:
                    return HttpResponse(template.render(context))

            except MDCSError, e:
                template = loader.get_template('curate/errors.html')
                context = RequestContext(request, {
                    'errors': e.message,
                })
                return HttpResponse(template.render(context))


################################################################################
#
# Function Name: save_xml_data_to_db(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Save the current XML document in MongoDB. The document is also
#                converted to RDF format and sent to a Jena triplestore.
#                
#
################################################################################
@permission_required(content_type=RIGHTS.curate_content_type, permission=RIGHTS.curate_access, login_url='/login')
def save_xml_data_to_db(request):
    form_data_id = request.session['curateFormData']
    form_data = FormData.objects.get(pk=form_data_id)
    form_id = request.session['form_id']
    root_element = SchemaElement.objects.get(pk=form_id)
    xml_renderer = XmlRenderer(root_element)
    xml_string = xml_renderer.render()
    template_id = form_data.template

    # Parse data from form
    form = SaveDataForm(request.POST)
    if not form.data['title'].lower().endswith('.xml'):
        form.data['title'] += ".xml"

    if not form.is_valid():
        return HttpResponseBadRequest('Invalid form name')

    if xml_string == "" or xml_string is None:
        return HttpResponseBadRequest('No XML data found')

    try:
        # update form data if id is present
        if form_data.xml_data_id is not None:
            if not form_data.isNewVersionOfRecord:
                #Update the record
                XMLdata.update_content(
                    form_data.xml_data_id,
                    xml_string,
                    title=form.data['title']
                )
                #Delete form_data
                if form_data.schema_element_root is not None:
                    delete_branch_from_db(form_data.schema_element_root.pk)
                form_data.delete()
            else:
                form_data.xml_data = xml_string
                form_data.save()
        else:
            # create new data otherwise
            xml_data = XMLdata(
                schemaID=template_id,
                xml=xml_string,
                title=form.data['title'],
                iduser=str(request.user.id)
            )
            xml_data.save()
            #Delete form_data because we just create an XmlData and we don't need anymore the formdata
            if form_data.schema_element_root is not None:
                delete_branch_from_db(form_data.schema_element_root.pk)
            form_data.delete()

        return HttpResponse('ok')
    except Exception, e:
        message = e.message.replace('"', '\'')
        return HttpResponseBadRequest(message)


################################################################################
#
# Function Name: curate_edit_form(request)
# Inputs:        request -
# Exceptions:    None
# Description:   Load forms to start curation
#
################################################################################
@permission_required(content_type=RIGHTS.curate_content_type, permission=RIGHTS.curate_access, login_url='/login')
def curate_edit_form(request):
    try:
        if request.method == 'GET':
            if 'id' in request.GET:
                form_data_id = request.GET['id']
                try:
                    form_data = FormData.objects.get(pk=ObjectId(form_data_id))
                except:
                    raise MDCSError("The form you are looking for doesn't exist.")
                request.session['curate_edit'] = True
                # parameters that will be used during curation
                request.session['curateFormData'] = str(form_data.id)
                request.session['currentTemplateID'] = form_data.template
                templateObject = Template.objects.get(pk=form_data.template)
                xmlDocData = templateObject.content
                XMLtree = etree.parse(BytesIO(xmlDocData.encode('utf-8')))
                request.session['xmlDocTree'] = etree.tostring(XMLtree)

                if form_data.schema_element_root is not None:
                    delete_branch_from_db(form_data.schema_element_root.pk)
                    form_data.schema_element_root = None

                if form_data.template is not None:
                    template_object = Template.objects.get(pk=form_data.template)
                    xsd_doc_data = template_object.content
                else:
                    raise MDCSError("No schema attached to this file")

                if form_data.xml_data is not None:
                    xml_doc_data = form_data.xml_data
                else:
                    xml_doc_data = None

                root_element_id = generate_form(request, xsd_doc_data, xml_doc_data, config=load_config())
                root_element = SchemaElement.objects.get(pk=root_element_id)

                form_data.update(set__schema_element_root=root_element)
                form_data.reload()

                request.session['form_id'] = str(form_data.schema_element_root.id)

                context = RequestContext(request, {})
                template = loader.get_template('curate/curate_enter_data.html')

                return HttpResponse(template.render(context))
            else:
                raise MDCSError("The form ID is missing.")
    except MDCSError, e:
        template = loader.get_template('curate/errors.html')
        context = RequestContext(request, {
            'errors': e.message,
        })
        return HttpResponse(template.render(context))


def cancel_changes(request):
    if request.method == 'POST':
        form = CancelChangesForm(request.POST)
        if form.is_valid():
            return HttpResponse(request.POST['cancel'])
    else:
        form = CancelChangesForm({'cancel': 'revert'})

    return HttpResponse(json.dumps({'form': str(form)}), content_type='application/javascript')
