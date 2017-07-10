################################################################################
#
# File Name: ajax.py
# Application: compose
# Purpose:   AJAX methods used by the Composer
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

import re
from django.http import HttpResponse
import json
from django.conf import settings
from django.http.response import HttpResponseBadRequest
from mongoengine import *
from mgi.common import LXML_SCHEMA_NAMESPACE, SCHEMA_NAMESPACE, get_default_prefix, get_namespaces, get_target_namespace
from mgi.exceptions import MDCSError
from mgi.models import Template, Type, XML2Download, create_template, create_type
import lxml.etree as etree
from io import BytesIO
from utils.XMLValidation.xml_schema import validate_xml_schema
from utils.APIschemaLocator.APIschemaLocator import getSchemaLocation
from urlparse import urlparse
from mgi import common
import os


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
    print 'BEGIN def setCurrentTemplate(request)'

    template_id = request.POST['templateID']

    request.session['currentComposeTemplateID'] = template_id
    request.session.modified = True

    if template_id != "new":
        templateObject = Template.objects.get(pk=template_id)

        xmlDocData = templateObject.content

        request.session['xmlTemplateCompose'] = xmlDocData
        request.session['newXmlTemplateCompose'] = xmlDocData
    else:
        base_template_path = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsd', 'new_base_template.xsd')
        base_template_file = open(base_template_path, 'r')
        base_template_content = base_template_file.read()
        request.session['xmlTemplateCompose'] = base_template_content
        request.session['newXmlTemplateCompose'] = base_template_content

    print 'END def setCurrentTemplate(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: set_current_user_template(request)
# Inputs:        request -
# Outputs:       JSON data with success or failure
# Exceptions:    None
# Description:   Set the current template to input argument.  Template is read
#                into an xsdDocTree for use later.
#
################################################################################
def set_current_user_template(request):
    print 'BEGIN def setCurrentUserTemplate(request)'

    template_id = request.POST['templateID']

    request.session['currentComposeTemplateID'] = template_id
    request.session.modified = True

    templateObject = Template.objects.get(pk=template_id)

    xmlDocData = templateObject.content

    request.session['xmlTemplateCompose'] = xmlDocData
    request.session['newXmlTemplateCompose'] = xmlDocData

    print 'END def setCurrentUserTemplate(request)'
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
    print 'BEGIN def verifyTemplateIsSelected(request)'
    if 'currentComposeTemplateID' in request.session:
        print 'template is selected'
        templateSelected = 'yes'
    else:
        print 'template is not selected'
        templateSelected = 'no'

    response_dict = {'templateSelected': templateSelected}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: is_new_template(request)
# Inputs:        request -
# Outputs:       JSON data with templateSelected
# Exceptions:    None
# Description:   Verifies the current template is new.
#
################################################################################
def is_new_template(request):
    if 'currentComposeTemplateID' in request.session and request.session['currentComposeTemplateID'] == "new":
        newTemplate = 'yes'
    else:
        newTemplate = 'no'

    response_dict = {'newTemplate': newTemplate}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: download_template(request)
# Inputs:        request -
# Outputs:       JSON data with templateSelected
# Exceptions:    None
# Description:   Download the template file
#
################################################################################
def download_template(request):
    xmlString = request.session['newXmlTemplateCompose']

    xml2download = XML2Download(xml=xmlString, title='schema.xsd').save()
    xml2downloadID = str(xml2download.id)

    response_dict = {'xml2downloadID': xml2downloadID}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: load_xml(request)
# Inputs:        request -
# Outputs:       JSON data with templateSelected
# Exceptions:    None
# Description:   Loads the XML data in the compose page. First transforms the data.
#
################################################################################
def load_xml(request):
    # get the original string
    xmlString = request.session['xmlTemplateCompose']
    # reset the string
    request.session['newXmlTemplateCompose'] = xmlString

    request.session['includedTypesCompose'] = []

    xsltPath = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'xsd2html.xsl')
    xslt = etree.parse(xsltPath)
    transform = etree.XSLT(xslt)
    xmlTree = ""
    if xmlString != "":
        request.session['namespacesCompose'] = common.get_namespaces(BytesIO(str(xmlString)))
        for prefix, url in request.session['namespacesCompose'].items():
            if url == SCHEMA_NAMESPACE:
                request.session['defaultPrefixCompose'] = prefix
                break
        dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
        annotations = dom.findall(".//{}annotation".format(LXML_SCHEMA_NAMESPACE))
        for annotation in annotations:
            annotation.getparent().remove(annotation)
        newdom = transform(dom)
        xmlTree = str(newdom)

    # store the current includes/imports
    includes = dom.findall("{}include".format(LXML_SCHEMA_NAMESPACE))
    for el_include in includes:
        if 'schemaLocation' in el_include.attrib:
            request.session['includedTypesCompose'].append(el_include.attrib['schemaLocation'])
    imports = dom.findall("{}import".format(LXML_SCHEMA_NAMESPACE))
    for el_import in imports:
        if 'schemaLocation' in el_import.attrib:
            request.session['includedTypesCompose'].append(el_import.attrib['schemaLocation'])

    response_dict = {'XMLHolder': xmlTree}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: insert_element_sequence(request)
# Inputs:        request - HTTP request
# Outputs:       JSON
# Exceptions:    None
# Description:   insert the type in the original schema
#
################################################################################
def insert_element_sequence(request):
    try:
        type_id = request.POST['typeID']
        client_type_name = request.POST['typeName']
        xpath = request.POST['xpath']

        xml_tree_str = request.session['newXmlTemplateCompose']

        # build the dom tree of the schema being built
        xsd_tree = etree.parse(BytesIO(xml_tree_str.encode('utf-8')))
        # get namespaces information for the schema
        namespaces = get_namespaces(BytesIO(str(xml_tree_str)))
        default_prefix = get_default_prefix(namespaces)
        # get target namespace information
        target_namespace, target_namespace_prefix = get_target_namespace(namespaces, xsd_tree)
        # build xpath to element
        xpath = xpath.replace(default_prefix + ":", LXML_SCHEMA_NAMESPACE)
        if type_id == 'built_in_type':
            type_name = default_prefix + ':' + client_type_name
            xsd_tree.find(xpath).append(etree.Element("{}element".format(LXML_SCHEMA_NAMESPACE),
                                        attrib={'type': type_name,
                                                'name': client_type_name}))
            # validate XML schema
            error = validate_xml_schema(xsd_tree)
            new_xsd_str = etree.tostring(xsd_tree)
        else:
            # get the type being included
            type_object = Type.objects().get(pk=type_id)
            type_xsd_tree = etree.parse(BytesIO(type_object.content.encode('utf-8')))
            # get namespaces information for the type
            type_namespaces = get_namespaces(BytesIO(str(type_object.content)))
            type_target_namespace, type_target_namespace_prefix = get_target_namespace(type_namespaces, type_xsd_tree)

            # get the type from the included/imported file
            # If there is a complex type
            element_type = type_xsd_tree.find("{}complexType".format(LXML_SCHEMA_NAMESPACE))
            if element_type is None:
                # If there is a simple type
                element_type = type_xsd_tree.find("{}simpleType".format(LXML_SCHEMA_NAMESPACE))
            type_name = element_type.attrib["name"]

            if type_target_namespace is not None:
                ns_type_name = "{0}:{1}".format(type_target_namespace_prefix, type_name)
            else:
                if target_namespace is not None:
                    ns_type_name = "{0}:{1}".format(target_namespace_prefix, type_name)
                else:
                    ns_type_name = '{}'.format(type_name)
            nsmap = {type_target_namespace_prefix: type_target_namespace}
            update_nsmap = False

            # get link to the type to include
            include_url = getSchemaLocation(str(type_id))

            # Schema without target namespace
            if target_namespace is None:
                # Type without target namespace
                if type_target_namespace is None:
                    # add include
                    xsd_tree.getroot().insert(0, etree.Element("{}include".format(LXML_SCHEMA_NAMESPACE),
                                              attrib={'schemaLocation': include_url}))
                    # add element
                    xsd_tree.find(xpath).append(etree.Element("{}element".format(LXML_SCHEMA_NAMESPACE),
                                                attrib={'type': type_name,
                                                        'name': client_type_name}))
                # Type with target namespace
                else:
                    # add import
                    xsd_tree.getroot().insert(0, etree.Element("{}import".format(LXML_SCHEMA_NAMESPACE),
                                              attrib={'schemaLocation': include_url,
                                                      'namespace': type_target_namespace}))
                    # create the element to add
                    element = etree.Element("{}element".format(LXML_SCHEMA_NAMESPACE),
                                            attrib={'name': client_type_name,
                                                    'type': ns_type_name},
                                            )
                    # add the element
                    xsd_tree.find(xpath).append(element)

                    update_nsmap = True

            # Schema with target namespace
            else:
                # Type without target namespace
                if type_target_namespace is None:
                    # add include
                    xsd_tree.getroot().insert(0, etree.Element("{}include".format(LXML_SCHEMA_NAMESPACE),
                                              attrib={'schemaLocation': include_url}))
                    # add element
                    xsd_tree.find(xpath).append(etree.Element("{}element".format(LXML_SCHEMA_NAMESPACE),
                                                attrib={'name': client_type_name,
                                                        'type': ns_type_name}))
                # Type with target namespace
                else:
                    # Same target namespace as base template
                    if target_namespace == type_target_namespace:
                        # add include
                        xsd_tree.getroot().insert(0, etree.Element("{}include".format(LXML_SCHEMA_NAMESPACE),
                                                  attrib={'schemaLocation': include_url}))
                        # add element
                        xsd_tree.find(xpath).append(etree.Element("{}element".format(LXML_SCHEMA_NAMESPACE),
                                                    attrib={'name': client_type_name,
                                                            'type': ns_type_name}))
                    # Different target namespace as base template
                    else:
                        # add import
                        xsd_tree.getroot().insert(0, etree.Element("{}import".format(LXML_SCHEMA_NAMESPACE),
                                                  attrib={'schemaLocation': include_url,
                                                          'namespace': type_target_namespace}))
                        # create the element to add
                        element = etree.Element("{}element".format(LXML_SCHEMA_NAMESPACE),
                                                attrib={'name': client_type_name,
                                                        'type': ns_type_name},
                                                )
                        # add the element
                        xsd_tree.find(xpath).append(element)

                        update_nsmap = True

            # add the id of the type if not already present
            if include_url not in request.session['includedTypesCompose']:
                request.session['includedTypesCompose'].append(include_url)

            if update_nsmap:
                root = xsd_tree.getroot()
                root_nsmap = root.nsmap

                if type_target_namespace_prefix in root_nsmap.keys() and\
                                root_nsmap[type_target_namespace_prefix] != type_target_namespace:
                    raise MDCSError('The namespace prefix is already declared for a different namespace.')
                else:
                    root_nsmap[type_target_namespace_prefix] = type_target_namespace
                    new_root = etree.Element(root.tag, nsmap=root_nsmap)
                    new_root[:] = root[:]

                    # validate XML schema
                    error = validate_xml_schema(new_root)
                    new_xsd_str = etree.tostring(new_root)

            else:
                # validate XML schema
                error = validate_xml_schema(xsd_tree)
                new_xsd_str = etree.tostring(xsd_tree)

        if error is not None:
            raise MDCSError(error)

        # save the tree in the session
        request.session['newXmlTemplateCompose'] = new_xsd_str
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')

    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: rename_element(request)
# Inputs:        request - HTTP request
# Outputs:       JSON 
# Exceptions:    None
# Description:   replace the current name of the element by the new name
# 
################################################################################
def rename_element(request):
    new_name = request.POST['newName']
    xpath = request.POST['xpath']
    
    defaultPrefix = request.session['defaultPrefixCompose']
    namespace = LXML_SCHEMA_NAMESPACE
    
    xmlString = request.session['newXmlTemplateCompose']
    dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix + ":", namespace)
    # add the element to the sequence
    dom.find(xpath).attrib['name'] = new_name
    
    # save the tree in the session
    request.session['newXmlTemplateCompose'] = etree.tostring(dom) 
    return HttpResponse(json.dumps({}), content_type='application/javascript')
    

################################################################################
# 
# Function Name: save_template(request)
# Inputs:        request - HTTP request
# Outputs:       JSON 
# Exceptions:    None
# Description:   save the current template in the database
# 
################################################################################
def save_template(request):
    template_name = request.POST['templateName']
    content = request.session['newXmlTemplateCompose']
    
    response_dict = {}

    # Validate XML document
    try:
        xml_tree = etree.parse(BytesIO(content.encode('utf-8')))
    except Exception, e:
        response_dict['errors'] = e.message.replace("'", "")
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

    # validate the schema
    error = validate_xml_schema(xml_tree)

    if error is not None:
        response_dict['errors'] = 'This is not a valid XML schema.' + error.replace("'","")
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

    dependencies = []

    for uri in request.session["includedTypesCompose"]:
        try:
            url = urlparse(uri)
            id = url.query.split("=")[1]
            # add dependency if it matches a type id
            Type.objects().get(pk=id)
            dependencies.append(id)
        except:
            pass

    try:
        create_template(content, template_name, template_name, dependencies, user=str(request.user.id))
    except Exception, e:
        response_dict['errors'] = e.message.replace("'", "")
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: save_type(request)
# Inputs:        request - HTTP request
# Outputs:       JSON 
# Exceptions:    None
# Description:   save the current type in the database
# 
################################################################################
def save_type(request):     
    type_name = request.POST['typeName']
    response_dict = {}
       
    content=request.session['newXmlTemplateCompose']
    
    templateID = request.session['currentComposeTemplateID']
    # can save as type if new type or from existing type
    if templateID != "new":
        if templateID not in Type.objects.all().values_list('id'):
            response_dict['errors'] = "Unable to save an existing template as a type."
            return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    
    # is it a valid XML document ?
    try:            
        xmlTree = etree.parse(BytesIO(content.encode('utf-8')))
        # this is a type: remove the root element to only keep the type
        root = xmlTree.find("{}element".format(LXML_SCHEMA_NAMESPACE))
        root.getparent().remove(root)
        content = etree.tostring(xmlTree)
    except Exception, e:
        response_dict['errors'] = "Not a valid XML document."
        response_dict['message'] = e.message.replace("'","")
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

    # validate the schema
    error = validate_xml_schema(xmlTree)

    if error is not None:
        response_dict['errors'] = "Not a valid XML document."
        response_dict['message'] = error.message.replace("'","")
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

    dependencies = []
    for uri in request.session["includedTypesCompose"]:
        try:
            url = urlparse(uri)
            id = url.query.split("=")[1]
            # add dependency if it matches a type id
            Type.objects().get(pk=id)
            dependencies.append(id)
        except:
            pass

    try:
        create_type(content, type_name, type_name, [], dependencies, user=str(request.user.id))
    except Exception, e:
        response_dict['errors'] = e.message.replace("'", "")
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: get_occurrences(request)
# Inputs:        request - HTTP request
# Outputs:       JSON 
# Exceptions:    None
# Description:   Get the occurrences of the selected element
# 
################################################################################
def get_occurrences(request):
    xpath = request.POST['xpath']
    
    defaultPrefix = request.session['defaultPrefixCompose']
    namespace = LXML_SCHEMA_NAMESPACE
    
    xmlString = request.session['newXmlTemplateCompose']
    dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix + ":", namespace)
    # add the element to the sequence
    element = dom.find(xpath)
    minOccurs = "1"
    maxOccurs = "1"
    if 'minOccurs' in element.attrib:
        minOccurs = element.attrib['minOccurs']
    if 'maxOccurs' in element.attrib:
        maxOccurs = element.attrib['maxOccurs']
    
    response_dict = {'minOccurs':minOccurs, 'maxOccurs':maxOccurs}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: set_occurrences(request)
# Inputs:        request - HTTP request
# Outputs:       JSON 
# Exceptions:    None
# Description:   Set the occurrences of the selected element
# 
################################################################################
def set_occurrences(request):    
    xpath = request.POST['xpath']
    minOccurs = request.POST['minOccurs']
    maxOccurs = request.POST['maxOccurs']
    
    defaultPrefix = request.session['defaultPrefixCompose']
    namespace = LXML_SCHEMA_NAMESPACE
    
    xmlString = request.session['newXmlTemplateCompose']
    dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix + ":", namespace)
    # add the element to the sequence
    element = dom.find(xpath)
    element.attrib['minOccurs'] = minOccurs
    element.attrib['maxOccurs'] = maxOccurs
    
    # save the tree in the session
    request.session['newXmlTemplateCompose'] = etree.tostring(dom) 
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: delete_element(request)
# Inputs:        request - HTTP request
# Outputs:       JSON 
# Exceptions:    None
# Description:   delete the element from the template
# 
################################################################################
def delete_element(request):
    xpath = request.POST['xpath']
    defaultPrefix = request.session['defaultPrefixCompose']
    namespace = LXML_SCHEMA_NAMESPACE
    
    xmlString = request.session['newXmlTemplateCompose']
    dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix + ":", namespace)
    # add the element to the sequence
    toRemove = dom.find(xpath)
    toRemove.getparent().remove(toRemove)
    
    # save the tree in the session
    request.session['newXmlTemplateCompose'] = etree.tostring(dom)     
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: change_root_type_name(request)
# Inputs:        request - HTTP request
# Outputs:       JSON 
# Exceptions:    None
# Description:   Change the name of the root type
# 
################################################################################
def change_root_type_name(request):
    type_name = request.POST['typeName']
    
    defaultPrefix = request.session['defaultPrefixCompose']
    namespace = LXML_SCHEMA_NAMESPACE
    
    xmlString = request.session['newXmlTemplateCompose']
    dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
    
    # root is the only element
    xpathRoot = namespace + "element"
    # root type is the only complex type
    xpathRootType = namespace + "complexType"

    # change the root type name in the dom
    dom.find(xpathRoot).attrib['type'] = type_name
    dom.find(xpathRootType).attrib['name'] = type_name
    
    # save the tree in the session
    request.session['newXmlTemplateCompose'] = etree.tostring(dom) 
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: change_xsd_type(request)
# Inputs:        request - HTTP request
# Outputs:       JSON 
# Exceptions:    None
# Description:   Change the type of the element
# 
################################################################################
def change_xsd_type(request):
    xpath = request.POST['xpath']
    new_type = request.POST['newType']
    
    defaultPrefix = request.session['defaultPrefixCompose']
    namespace = LXML_SCHEMA_NAMESPACE
    
    xmlString = request.session['newXmlTemplateCompose']
    dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix + ":", namespace)
    dom.find(xpath).tag = namespace + new_type
    
    # save the tree in the session
    request.session['newXmlTemplateCompose'] = etree.tostring(dom) 
    return HttpResponse(json.dumps({}), content_type='application/javascript')
