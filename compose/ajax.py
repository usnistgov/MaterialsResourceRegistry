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
from mongoengine import *
from mgi.models import Template, Type, XML2Download, MetaSchema, Exporter
import lxml.etree as etree
from io import BytesIO
from utils.XSDhash import XSDhash
from utils.XSDflattenerMDCS.XSDflattenerMDCS import XSDFlattenerMDCS
from utils.APIschemaLocator.APIschemaLocator import getSchemaLocation
from urlparse import urlparse
from mgi import common

# XSL file loading
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
        if template_id in MetaSchema.objects.all().values_list('schemaId'):
            meta = MetaSchema.objects.get(schemaId=template_id)
            xmlDocData = meta.api_content
        else:
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
    if template_id in MetaSchema.objects.all().values_list('schemaId'):
        meta = MetaSchema.objects.get(schemaId=template_id)
        xmlDocData = meta.api_content
    else:
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
    if (xmlString != ""):
        request.session['namespacesCompose'] = common.get_namespaces(BytesIO(str(xmlString)))
        for prefix, url in request.session['namespacesCompose'].items():
            if (url == "{http://www.w3.org/2001/XMLSchema}"):            
                request.session['defaultPrefixCompose'] = prefix
                break
        dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
        annotations = dom.findall(".//{http://www.w3.org/2001/XMLSchema}annotation")
        for annotation in annotations:
            annotation.getparent().remove(annotation)
        newdom = transform(dom)
        xmlTree = str(newdom)
    
    # store the current includes
    includes = dom.findall("{http://www.w3.org/2001/XMLSchema}include")
    for el_include in includes:
        if 'schemaLocation' in el_include.attrib:
            request.session['includedTypesCompose'].append(el_include.attrib['schemaLocation'])
            
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
    type_id = request.POST['typeID']
    type_name = request.POST['typeName']
    xpath = request.POST['xpath']
    
    defaultPrefix = request.session['defaultPrefixCompose']
    namespace = request.session['namespacesCompose'][defaultPrefix]
    
    xmlString = request.session['newXmlTemplateCompose']
    dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
    
    # get the type to add
    includedType = Type.objects.get(pk=type_id)
    typeTree = etree.XML(str(includedType.content))
    elementType = typeTree.find("{http://www.w3.org/2001/XMLSchema}complexType")
    if elementType is None:
        elementType = typeTree.find("{http://www.w3.org/2001/XMLSchema}simpleType")
    type = elementType.attrib["name"]
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix +":", namespace)
    # add the element to the sequence
    dom.find(xpath).append(etree.Element(namespace+"element", attrib={'type': type, 'name':type_name}))
    
    includeURL = getSchemaLocation(request, str(type_id))
    # add the id of the type if not already present
    if includeURL not in request.session['includedTypesCompose']:
        request.session['includedTypesCompose'].append(includeURL)        
        dom.getroot().insert(0,etree.Element(namespace+"include", attrib={'schemaLocation':includeURL}))
    
    # save the tree in the session
    request.session['newXmlTemplateCompose'] = etree.tostring(dom) 
    print etree.tostring(dom)
    
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
    namespace = request.session['namespacesCompose'][defaultPrefix]
    
    xmlString = request.session['newXmlTemplateCompose']
    dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix +":", namespace)
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
    content=request.session['newXmlTemplateCompose']
    
    response_dict = {}
    # is it a valid XML document ?
    try:            
        xmlTree = etree.parse(BytesIO(content.encode('utf-8')))
    except Exception, e:
        response_dict['errors'] = e.message.replace("'","")
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    
    flattener = XSDFlattenerMDCS(etree.tostring(xmlTree))
    flatStr = flattener.get_flat()
    flatTree = etree.fromstring(flatStr)
    
    try:
        # is it a valid XML schema ?
        xmlSchema = etree.XMLSchema(flatTree)
    except Exception, e:
        response_dict['errors'] = e.message.replace("'","")
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    
    hash = XSDhash.get_hash(content) 
    dependencies = []
    for uri in request.session["includedTypesCompose"]:
        url = urlparse(uri)
        id = url.query.split("=")[1]
        dependencies.append(id)
    template = Template(title=template_name, filename=template_name, content=content, hash=hash, user=str(request.user.id), dependencies=dependencies)
    #We add default exporters
    try:
        exporters = Exporter.objects.filter(available_for_all=True)
        template.exporters = exporters
    except:
        pass

    template.save()
    
    MetaSchema(schemaId=str(template.id), flat_content=flatStr, api_content=content).save()
    
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
        root = xmlTree.find("{http://www.w3.org/2001/XMLSchema}element")
        root.getparent().remove(root)
        content = etree.tostring(xmlTree)
    except Exception, e:
        response_dict['errors'] = "Not a valid XML document."
        response_dict['message'] = e.message.replace("'","")
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    
    flattener = XSDFlattenerMDCS(content)
    flatStr = flattener.get_flat()
    flatTree = etree.fromstring(flatStr)
    
    try:
        # is it a valid XML schema ?
        xmlSchema = etree.XMLSchema(flatTree)
    except Exception, e:
        response_dict['errors'] = "Not a valid XML document."
        response_dict['message'] = e.message.replace("'","")
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    
    
    hash = XSDhash.get_hash(content)
    dependencies = []
    for uri in request.session["includedTypesCompose"]:
        url = urlparse(uri)
        id = url.query.split("=")[1]
        dependencies.append(id)
    type = Type(title=type_name, filename=type_name, content=content, user=str(request.user.id), hash=hash, dependencies=dependencies)
    type.save()
    MetaSchema(schemaId=str(type.id), flat_content=flatStr, api_content=content).save()
    
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
    namespace = request.session['namespacesCompose'][defaultPrefix]
    
    xmlString = request.session['newXmlTemplateCompose']
    dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix +":", namespace)
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
    namespace = request.session['namespacesCompose'][defaultPrefix]
    
    xmlString = request.session['newXmlTemplateCompose']
    dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix +":", namespace)
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
    namespace = request.session['namespacesCompose'][defaultPrefix]
    
    xmlString = request.session['newXmlTemplateCompose']
    dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix +":", namespace)
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
    namespace = request.session['namespacesCompose'][defaultPrefix]
    
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
    namespace = request.session['namespacesCompose'][defaultPrefix]
    
    xmlString = request.session['newXmlTemplateCompose']
    dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix +":", namespace)
    dom.find(xpath).tag = namespace + new_type
    
    # save the tree in the session
    request.session['newXmlTemplateCompose'] = etree.tostring(dom) 
    return HttpResponse(json.dumps({}), content_type='application/javascript')
    
