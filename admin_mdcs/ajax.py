################################################################################
#
# File Name: ajax.py
# Application: admin_mdcs
# Purpose:    AJAX methods used for administration purposes
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
import lxml.etree as etree
import json
from io import BytesIO
from mgi.common import LXML_SCHEMA_NAMESPACE, update_dependencies
from mgi.models import create_template, create_type, create_template_version, create_type_version
from rest_framework.status import HTTP_404_NOT_FOUND
from mgi.models import Template, TemplateVersion, Instance, Request, Module, Type, TypeVersion, Message, Bucket, \
    Exporter, ExporterXslt, ResultXslt
from django.contrib.auth.models import User
from utils.XMLValidation.xml_schema import validate_xml_schema
import random
from django.contrib import messages
from mgi.common import send_mail
from django.utils.importlib import import_module
import os
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
MDCS_URI = settings.MDCS_URI


################################################################################
# 
# Function Name: resolve_dependencies(request)
# Inputs:        request - 
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Save an object (template or type) in mongodb
# 
################################################################################
def resolve_dependencies(request):
    print 'BEGIN def resolveDependencies(request)'
    schema_locations = request.POST.getlist('schemaLocations[]')
    dependencies = request.POST.getlist('dependencies[]')

    if ('uploadObjectName' in request.session and request.session['uploadObjectName'] is not None and
        'uploadObjectFilename' in request.session and request.session['uploadObjectFilename'] is not None and
        'uploadObjectContent' in request.session and request.session['uploadObjectContent'] is not None and
        'uploadObjectType' in request.session and request.session['uploadObjectType'] is not None):
        object_content = request.session['uploadObjectContent']
        name = request.session['uploadObjectName']
        filename = request.session['uploadObjectFilename']
        object_type = request.session['uploadObjectType']

    # Load a parser able to clean the XML from blanks, comments and processing instructions
    clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    # set the parser
    etree.set_default_parser(parser=clean_parser)

    xsd_tree = etree.XML(str(object_content.encode('utf-8')))

    # replace includes/imports by API calls (get dependencies starting by the imports)
    update_dependencies(xsd_tree, dict(zip(schema_locations, dependencies)))

    # validate the schema
    error = validate_xml_schema(xsd_tree)

    if error is None:
        object_content = etree.tostring(xsd_tree)
        # create a new version
        if 'uploadVersion' in request.session and request.session['uploadVersion'] is not None:
            object_versions_id = request.session['uploadVersion']
            if object_type == 'Template':
                new_template = create_template_version(object_content, filename, object_versions_id, dependencies)
                redirect = '/admin/manage_versions?type={0}&id={1}'.format(object_type, str(new_template.id))
            elif object_type == 'Type':
                new_type = create_type_version(object_content, filename, object_versions_id, dependencies)
                redirect = '/admin/manage_versions?type={0}&id={1}'.format(object_type, str(new_type.id))
        # create new object
        else:
            # save the object
            if object_type == "Template":
                create_template(object_content, name, filename, dependencies)
                redirect = '/admin/xml-schemas/manage-schemas'
            elif object_type == "Type":
                if 'uploadBuckets' in request.session and request.session['uploadBuckets'] is not None:
                    buckets = request.session['uploadBuckets']
                create_type(object_content, name, filename, buckets, dependencies)
                redirect = '/admin/xml-schemas/manage-types'

        response_dict = {'redirect': redirect}
        messages.add_message(request, messages.INFO, '{} uploaded with success.'.format(object_type))
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    else:
        response_dict = {'errorDependencies': error.replace("'", "")}
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: delete_object(request)
# Inputs:        request - 
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Delete an object (template or type).
# 
################################################################################
def delete_object(request):
    print 'BEGIN def delete_object(request)'
    object_id = request.POST['objectID']
    object_type = request.POST['objectType']

    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)

    objectVersions.deletedVersions.append(str(object.id))    
    objectVersions.isDeleted = True
    objectVersions.save()

    print 'END def delete_object(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: set_type_version_content(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Save the name and content of uploaded type before save
#
################################################################################
def set_type_version_content(request):
    version_content = request.POST['versionContent']
    version_filename = request.POST['versionFilename']
    
    request.session['uploadVersionContent'] = version_content
    request.session['uploadVersionFilename'] = version_filename
    request.session['uploadVersionValid'] = False
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: set_current_version(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Set the current version of the object (template or type)
#
################################################################################
def set_current_version(request):
    object_id = request.GET['objectid']
    object_type = request.GET['objectType']
    
    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)
    
    objectVersions.current = str(object.id)
    objectVersions.save()
     
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: delete_version(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Delete a version of the object (template or type) by adding it to the list of deleted
#
################################################################################
def delete_version(request):
    object_id = request.POST['objectid']
    object_type = request.POST['objectType']
    new_current = request.POST['newCurrent']
    
    response_dict = {}
    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)
      

    if len(objectVersions.versions) == 1 or len(objectVersions.versions) == len(objectVersions.deletedVersions) + 1:
        objectVersions.deletedVersions.append(str(object.id))    
        objectVersions.isDeleted = True
        objectVersions.save()
        response_dict = {'deleted': 'object'}
    
    else:
        if new_current != "": 
            objectVersions.current = new_current
        objectVersions.deletedVersions.append(str(object.id))   
        objectVersions.save()        
        response_dict = {'deleted': 'version'}
    
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: assign_delete_custom_message(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Assign a message to the dialog box regarding the situation of the version that is about to be deleted
#
################################################################################
def assign_delete_custom_message(request):
    object_id = request.GET['objectid']
    object_type = request.GET['objectType']
    
    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)  
    
    message = ""

    if len(objectVersions.versions) == 1:
        message = "<span style='color:red'>You are about to delete the only version of this " + object_type + ". The " + object_type + " will be deleted from the "+ object_type + " manager.</span>"
    elif objectVersions.current == str(object.id) and len(objectVersions.versions) == len(objectVersions.deletedVersions) + 1:
        message = "<span style='color:red'>You are about to delete the last version of this " + object_type + ". The " + object_type + " will be deleted from the "+ object_type + " manager.</span>"
    elif objectVersions.current == str(object.id):
        message = "<span>You are about to delete the current version. If you want to continue, please select a new current version: <select id='selectCurrentVersion'>"
        for version in objectVersions.versions:
            if version != objectVersions.current and version not in objectVersions.deletedVersions:
                if object_type == "Template":
                    obj = Template.objects.get(pk=version)
                else:
                    obj = Type.objects.get(pk=version)
                message += "<option value='"+version+"'>Version " + str(obj.version) + "</option>"
        message += "</select></span>"

    response_dict = {'message': message}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: edit_information(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Edit information of an object (template or type)
#
################################################################################
def edit_information(request):
    object_id = request.POST['objectID']
    object_type = request.POST['objectType']
    new_name = request.POST['newName']
    new_filename = request.POST['newFilename']

    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:        
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)
        # check if a type with the same name already exists
        testFilenameObjects = Type.objects(filename=new_filename)    
        if len(testFilenameObjects) == 1: # 0 is ok, more than 1 can't happen
            #check that the type with the same filename is the current one
            if testFilenameObjects[0].id != object.id:
                response_dict = {'errors': 'True'}
                return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    
    # change the name of every version but only the filename of the current
    for version in objectVersions.versions:
        if object_type == "Template":
            obj = Template.objects.get(pk=version)
        else:
            obj = Type.objects.get(pk=version)
        obj.title = new_name
        if version == object_id:
            obj.filename = new_filename
        obj.save()
    
    if object_type == "Type":
        new_buckets = request.POST.getlist('newBuckets[]')
        # update the buckets
        allBuckets = Bucket.objects
        for bucket in allBuckets:
            if str(bucket.id) in new_buckets:
                if str(objectVersions.id) not in bucket.types:
                    bucket.types.append(str(objectVersions.id))
            
            else:   
                if str(objectVersions.id) in bucket.types:
                    bucket.types.remove(str(objectVersions.id))
            
            bucket.save()
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: restore_object(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Restore an object previously deleted (template or type)
#
################################################################################
def restore_object(request):
    object_id = request.POST['objectID']
    object_type = request.POST['objectType']
    
    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)
        
    objectVersions.isDeleted = False
    del objectVersions.deletedVersions[objectVersions.deletedVersions.index(objectVersions.current)]
    objectVersions.save()
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: restore_version(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Restore a version of an object previously deleted (template or type)
#
################################################################################
def restore_version(request):
    object_id = request.POST['objectID']
    object_type = request.POST['objectType']
    
    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)
        
    del objectVersions.deletedVersions[objectVersions.deletedVersions.index(object_id)]
    objectVersions.save()
       
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: edit_instance(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Edit the instance information
#
################################################################################
def edit_instance(request):
    instance_id = request.POST['instanceid']
    name = request.POST['name']
    
    errors = ""
    response_dict = {}
    
    # test if the name is "Local"
    if name.upper() == "LOCAL":
        errors += "By default, the instance named Local is the instance currently running."
    else:   
        # test if an instance with the same name exists
        instance = Instance.objects(name=name)
        if len(instance) != 0 and str(instance[0].id) != instance_id:
            errors += "An instance with the same name already exists.<br/>"
    
    # If some errors display them, otherwise insert the instance
    if errors == "":
        instance = Instance.objects.get(pk=instance_id)
        instance.name = name
        instance.save()
    else:
        response_dict = {'errors': errors}
    
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: delete_instance(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Delete an instance
#
################################################################################
def delete_instance(request):
    instance_id = request.POST['instanceid']
    
    instance = Instance.objects.get(pk=instance_id)
    instance.delete()
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: accept_request(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Accepts a request and creates the user account
# 
################################################################################
def accept_request(request):
    request_id = request.POST['requestid']
    
    response_dict = {}
    
    userRequest = Request.objects.get(pk=request_id)
    try:
        existingUser = User.objects.get(username=userRequest.username)
        response_dict = {'errors': 'User already exists.'} 
    except:
        user = User.objects.create_user(username=userRequest.username, password=userRequest.password, first_name=userRequest.first_name, last_name=userRequest.last_name, email=userRequest.email)
        user.save()
        userRequest.delete()
        # Send mail to the user
        context = {'lastname': userRequest.last_name,
                   'firstname': userRequest.first_name,
                   'URI': MDCS_URI}
        send_mail(subject='Account approved', pathToTemplate='admin/email/request_account_approved.html',
                  context=context, recipient_list=[userRequest.email])
        
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: deny_request(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Denies a request
# 
################################################################################
def deny_request(request):
    request_id = request.POST['requestid']
    
    userRequest = Request.objects.get(pk=request_id)
    userRequest.delete()
    # Send mail to the user
    context = {'lastname': userRequest.last_name,
               'firstname': userRequest.first_name,
               'URI': MDCS_URI}
    send_mail(subject='Account denied', pathToTemplate='admin/email/request_account_denied.html',
              context=context, recipient_list=[userRequest.email])
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: remove_message(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Remove a message from Contact form
#
################################################################################
def remove_message(request):
    message_id = request.POST['messageid']
    
    message = Message.objects.get(pk=message_id)
    message.delete()
            
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: add_bucket(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Add a new bucket
#
################################################################################
def add_bucket(request):
    label = request.POST['label']
    
    # check that the label is unique
    labels = Bucket.objects.all().values_list('label') 
    if label in labels:
        response_dict = {"errors": "True"}
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    # get an unique color
    colors = Bucket.objects.all().values_list('color') 
    color = rdm_hex_color()
    while color in colors:
        color = rdm_hex_color()
        
    Bucket(label=label, color=color).save()
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: delete_bucket(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Delete a bucket
#
################################################################################
def delete_bucket(request):
    bucket_id = request.POST['bucket_id']
    
    bucket = Bucket.objects.get(pk=bucket_id)
    bucket.delete()
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: rdm_hex_color()
# Inputs:        None
# Outputs:       hex color
# Exceptions:    None
# Description:   Generates a random color code
#
################################################################################
def rdm_hex_color():
    return '#' + ''.join([random.choice('0123456789ABCDEF') for x in range(6)])


################################################################################
# 
# Function Name: insert_module(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Insert a module in the template by adding an attribute.
#
################################################################################
def insert_module(request):
    module_id = request.POST['moduleID']
    xpath = request.POST['xpath']
    
    defaultPrefix = request.session['moduleDefaultPrefix']
    namespace = LXML_SCHEMA_NAMESPACE
    template_content = request.session['moduleTemplateContent']
    
    dom = etree.parse(BytesIO(template_content.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix + ":", namespace)
    # add the element to the sequence
    element = dom.find(xpath)
    
    module = Module.objects.get(pk=module_id)
        
    element.attrib['{http://mdcs.ns}_mod_mdcs_'] = module.url
        
    # save the tree in the session
    request.session['moduleTemplateContent'] = etree.tostring(dom)
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: remove_module(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Remove a module from the template by removing an attribute and the automatic namespace.
#
################################################################################
def remove_module(request):
    xpath = request.POST['xpath']
    
    defaultPrefix = request.session['moduleDefaultPrefix']
    namespace = LXML_SCHEMA_NAMESPACE
    template_content = request.session['moduleTemplateContent']
    
    dom = etree.parse(BytesIO(template_content.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix +":", namespace)
    # add the element to the sequence
    element = dom.find(xpath)
    
    if '{http://mdcs.ns}_mod_mdcs_' in element.attrib:
        del element.attrib['{http://mdcs.ns}_mod_mdcs_']
    
    # remove prefix from namespaces
    nsmap = element.nsmap
    for prefix, ns in nsmap.iteritems():
        if ns == 'http://mdcs.ns':
            del nsmap[prefix]
            break
    
    # create a new element to replace the previous one (can't replace directly the nsmap using lxml)
    element = etree.Element(element.tag, nsmap = nsmap)
    
    # save the tree in the session
    request.session['moduleTemplateContent'] = etree.tostring(dom)
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')
    

################################################################################
#
# Function Name: save_modules(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Save the template with its modules.
#
################################################################################
def save_modules(request):
    object_content = request.session['moduleTemplateContent']
    object_id = request.session['moduleTemplateID']
    object_type = request.POST['type'] if 'type' in request.POST else None

    if object_type == 'Template':
        db_object = Template.objects.get(pk=object_id)
    elif object_type == 'Type':
        db_object = Type.objects.get(pk=object_id)
    else:
        return HttpResponse(status=HTTP_404_NOT_FOUND)

    db_object.content = object_content
    db_object.save()

    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: save_exporters(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Save exporters and XSLT for a template.
#
################################################################################
def save_exporters(request):
    template_id = request.session['moduleTemplateID']
    listIdOn = request.POST.getlist('listIdOn[]')
    listIdOnXslt = request.POST.getlist('listIdOnXslt[]')
    #We retrieve the exporter
    template = Template.objects.get(pk=template_id)
    #We reinitialise exporters and XSLT
    template.exporters = None
    template.XSLTFiles = None
    template.save()
    #We add exporters
    for exp in listIdOn:
        exp = Exporter.objects.get(pk=exp)
        Template.objects(id=template_id).update_one(push__exporters=exp)
    #We add XSLT files
    for xslt in listIdOnXslt:
        xslt = ExporterXslt.objects.get(pk=xslt)
        Template.objects(id=template_id).update_one(push__XSLTFiles=xslt)
    template.save()

    return HttpResponse(json.dumps({}), content_type='application/javascript')

################################################################################
#
# Function Name: save_result_xslt(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Save result XSLT for a template.
#
################################################################################
def save_result_xslt(request):
    template_id = request.session['moduleTemplateID']
    idXsltShort = request.POST.get('idXsltShort')
    idXsltDetailed = request.POST.get('idXsltDetailed')
    #We retrieve the exporter
    template = Template.objects.get(pk=template_id)
    #We reinitialise exporters and XSLT
    template.ResultXsltList = None
    template.ResultXsltDetailed = None
    template.save()
    #We add short XSLT
    if idXsltShort:
        shortXslt = ResultXslt.objects.get(pk=idXsltShort)
        template.ResultXsltList = shortXslt
    #We add detailed XSLT
    if idXsltDetailed:
        detailedXSLT = ResultXslt.objects.get(pk=idXsltDetailed)
        template.ResultXsltDetailed = detailedXSLT

    if idXsltShort or idXsltDetailed:
        template.save()

    return HttpResponse(json.dumps({}), content_type='application/javascript')
