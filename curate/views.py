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
from lxml.etree import XMLSyntaxError
import json 
import xmltodict
from django.contrib import messages
from mgi.models import Template, TemplateVersion, XML2Download, FormData,\
    XMLdata, FormElement, XMLElement
from curate.forms import NewForm, OpenForm, UploadForm, SaveDataForm
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
@permission_required(content_type=RIGHTS.curate_content_type, permission=RIGHTS.curate_access, login_url='/login')
def index(request):
    template = loader.get_template('curate/curate.html')
    currentTemplateVersions = []
    for tpl_version in TemplateVersion.objects():
        currentTemplateVersions.append(tpl_version.current)

    currentTemplates = dict()
    for tpl_version in currentTemplateVersions:
        tpl = Template.objects.get(pk=tpl_version)
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
@permission_required(content_type=RIGHTS.curate_content_type, permission=RIGHTS.curate_edit_document, login_url='/login')
def curate_edit_data(request):
    try:
        if 'useForm' in request.GET and request.GET['useForm'] == 'true':
            pass
        else:
            xml_data_id = request.GET['id']
            xml_data = XMLdata.get(xml_data_id)
            json_content = xml_data['content']
            xml_content = xmltodict.unparse(json_content)
            request.session['curate_edit_data'] = xml_content
            request.session['curate_edit'] = True
            request.session['currentTemplateID'] = xml_data['schema']
            # remove previously created forms when editing a new one
            previous_forms = FormData.objects(user=str(request.user.id), xml_data_id__exists=True)
            for previous_form in previous_forms:
                # cascade delete references
                for form_element_id in previous_form.elements.values():
                    try:
                        form_element = FormElement.objects().get(pk=form_element_id)
                        if form_element.xml_element is not None:
                            try:
                                xml_element = XMLElement.objects().get(pk=str(form_element.xml_element.id))
                                xml_element.delete()
                            except:
                                # raise an exception when element not found
                                pass
                        form_element.delete()
                    except:
                        # raise an exception when element not found
                        pass
                previous_form.delete()
            form_data = FormData(user=str(request.user.id), template=xml_data['schema'], name=xml_data['title'], xml_data=xml_content, xml_data_id=xml_data_id).save()
            request.session['curateFormData'] = str(form_data.id)
            if 'formString' in request.session:
                del request.session['formString']
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
                
                if 'useForm' in request.GET and request.GET['useForm'] == 'true':
                    pass
                else:
                    if 'formString' in request.session:
                        del request.session['formString']
                    if 'xmlDocTree' in request.session:
                        del request.session['xmlDocTree']
            else:
                raise MDCSError("The selection of template by name can't be used if the MDCS contain more than one template with the same name.")            
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
            context = RequestContext(request, {'edit': True, 'template_name':template.title})
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
        edit =True
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
    if 'currentTemplateID' not in request.session and not 'template' in request.GET:
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
                form_data = FormData(user=str(user), template=template_id, name=new_form.data['document_name'], xml_data=None).save()
            elif selected_option == "open":
                request.session['curate_edit'] = True
                open_form = OpenForm(request.POST)
                form_data = FormData.objects.get(pk=ObjectId(open_form.data['forms']))
                request.session['curate_edit_data'] = form_data.xml_data
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
                form_data = FormData(user=str(user), template=template_id, name=xml_file.name, xml_data=xml_data).save()

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
                        raise MDCSError("The selection of template by name can't be used if the MDCS contain more than one template with the same name.")

                    template = loader.get_template('curate/curate_full_start.html')

                    if 'formString' in request.session:
                        del request.session['formString']
                    if 'xmlDocTree' in request.session:
                        del request.session['xmlDocTree']

                else:
                    ajaxCall = True
                    template = loader.get_template('curate/curate_start.html')

                open_form = OpenForm(forms=FormData.objects(user=str(request.user.id), template=request.session['currentTemplateID'], xml_data_id__exists=False))
                new_form = NewForm()
                upload_form = UploadForm()
                
                context_params['new_form']= new_form
                context_params['open_form']= open_form
                context_params['upload_form']= upload_form
                
                context = RequestContext(request, context_params)#, 'options_form': options_form})

                if ajaxCall:
                    return HttpResponse(json.dumps({'template': template.render(context)}), content_type='application/javascript')
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
    xmlString = request.session['xmlString']
    templateID = request.session['currentTemplateID']

    form = SaveDataForm(request.POST)

    if form.is_valid():
        if xmlString != "":
            try:
                # get form data from the database
                form_data_id = request.session['curateFormData']
                form_data = FormData.objects.get(pk=ObjectId(form_data_id))
                if not form.data['title'].lower().endswith('.xml'):
                    form.data['title'] += ".xml"
                # update data if id is present
                if form_data.xml_data_id is not None:
                    XMLdata.update_content(form_data.xml_data_id, xmlString, title=form.data['title'])
                else:
                    #create new data otherwise
                    newJSONData = XMLdata(schemaID=templateID, xml=xmlString, title=form.data['title'], iduser=str(request.user.id))
                    newJSONData.save()
                # delete form data
                try:
                    form_data = FormData.objects().get(pk=form_data_id)
                    # cascade delete references
                    for form_element_id in form_data.elements.values():
                        try:
                            form_element = FormElement.objects().get(pk=form_element_id)
                            if form_element.xml_element is not None:
                                try:
                                    xml_element = XMLElement.objects().get(pk=str(form_element.xml_element.id))
                                    xml_element.delete()
                                except:
                                    # raise an exception when element not found
                                    pass
                            form_element.delete()
                        except:
                            # raise an exception when element not found
                            pass
                    form_data.delete()
                except Exception, e:
                    return HttpResponseBadRequest('Unable to save data.')
                return HttpResponse('ok')
            except Exception, e:
                message = e.message.replace('"', '\'')
                return HttpResponseBadRequest(message)
        else:
            return HttpResponseBadRequest('No data to save.')
    else:
        return HttpResponseBadRequest('Invalid title.')

    