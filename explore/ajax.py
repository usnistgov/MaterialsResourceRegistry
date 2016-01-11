################################################################################
#
# File Name: ajax.py
# Application: explore
# Purpose:   AJAX methods used for Explore purposes
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume Sousa Amaral
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

import re
from django.http import HttpResponse
from django.conf import settings
from io import BytesIO
from lxml import html
from collections import OrderedDict
import xmltodict
import requests
import os
import json
import copy
import lxml.etree as etree
from mgi.models import Template, QueryResults, SavedQuery, XMLdata, Instance, MetaSchema, TemplateVersion
from mgi import common
from django.template import loader, Context, RequestContext
from django.contrib.auth.models import Group
from django.db.models import Q
import mgi.rights as RIGHTS
import random
#Class definition

################################################################################
# 
# Class Name: ElementInfo
#
# Description: Store information about element from the XML schema
#
################################################################################
class ElementInfo:    
    def __init__(self, type="", path=""):
        self.type = type
        self.path = path
    
    def __to_json__(self):
        return json.dumps(self, default=lambda o:o.__dict__)

################################################################################
# 
# Class Name: CriteriaInfo
#
# Description: Store information about a criteria from the query builder
#
################################################################################
class CriteriaInfo:
    def __init__(self, elementInfo=None, queryInfo=None):
        self.elementInfo = elementInfo
        self.queryInfo = queryInfo
    
    def __to_json__(self):
        jsonDict = dict()
        if self.elementInfo == None:
            jsonDict['elementInfo'] = None
        else:
            jsonDict['elementInfo'] = self.elementInfo.__to_json__()
        if self.queryInfo == None:
            jsonDict['queryInfo'] = None
        else:
            jsonDict['queryInfo'] = self.queryInfo.__to_json__()
        return str(jsonDict)

################################################################################
# 
# Class Name: QueryInfo
#
# Description: Store information about a query
#
################################################################################
class QueryInfo:
    def __init__(self, query="", displayedQuery=""):
        self.query = query
        self.displayedQuery = displayedQuery

    def __to_json__(self):        
        return json.dumps(self, default=lambda o:o.__dict__)
 
################################################################################
# 
# Class Name: BranchInfo
#
# Description: Store information about a branch from the xml schema while it is
# being processed for customization
#
################################################################################   
class BranchInfo:
    def __init__(self, keepTheBranch, selectedLeave):
        self.keepTheBranch = keepTheBranch
        self.selectedLeave = selectedLeave


################################################################################
# 
# Function Name: set_current_template(request):
# Inputs:        request - 
# Outputs:       JSON data with success or failure
# Exceptions:    None
# Description:   Set the current template to input argument.  Template is read into
#                an xsdDocTree for use later.
#
################################################################################
def set_current_template(request):
    print 'BEGIN def setCurrentTemplate(request)'    

    template_id = request.POST['templateID']

    setCurrentTemplate(request, template_id)

    print 'END def setCurrentTemplate(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: setCurrentTemplate(request):
# Inputs:        request - 
#                template_filename - name of the template
#                template_id - id of the template
# Outputs:       
# Exceptions:    None
# Description:   Set the current template to input argument.  Template is read into
#                an xsdDocTree for use later.
#
################################################################################
def setCurrentTemplate(request, template_id):
    print 'BEGIN def setCurrentTemplate(request)'    

    # reset global variables
    request.session['formStringExplore'] = ""
    request.session['customFormStringExplore'] = ""

    request.session['exploreCurrentTemplateID'] = template_id
    request.session.modified = True

    if template_id in MetaSchema.objects.all().values_list('schemaId'):
        meta = MetaSchema.objects.get(schemaId=template_id)
        xmlDocData = meta.flat_content
    else:
        templateObject = Template.objects.get(pk=template_id)
        xmlDocData = templateObject.content

    XMLtree = etree.parse(BytesIO(xmlDocData.encode('utf-8')))
    request.session['xmlDocTreeExplore'] = etree.tostring(XMLtree)

    print 'END def setCurrentTemplate(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')

################################################################################
# 
# Function Name: set_current_user_template(request,):
# Inputs:        request - 
# Outputs:       JSON data with success or failure
# Exceptions:    None
# Description:   Set the current template to input argument.  Template is read into
#                an xsdDocTree for use later.
#
################################################################################
def set_current_user_template(request):
    print 'BEGIN def setCurrentTemplate(request)'    

    template_id = request.POST['templateID']
    
    # reset global variables
    request.session['formStringExplore'] = ""
    request.session['customFormStringExplore'] = ""
        
    request.session['exploreCurrentTemplateID'] = template_id
    request.session.modified = True

    templateObject = Template.objects.get(pk=template_id)
    
    if template_id in MetaSchema.objects.all().values_list('schemaId'):
        meta = MetaSchema.objects.get(schemaId=template_id)
        xmlDocData = meta.flat_content
    else:
        xmlDocData = templateObject.content


    XMLtree = etree.parse(BytesIO(xmlDocData.encode('utf-8')))
    request.session['xmlDocTreeExplore'] = etree.tostring(XMLtree)

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
    print 'BEGIN def verifyTemplateIsSelected(request)'
    if 'exploreCurrentTemplateID' in request.session:
        templateSelected = 'yes'
    else:
        templateSelected = 'no'

    print 'END def verifyTemplateIsSelected(request)'
    
    response_dict = {'templateSelected': templateSelected}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: removeAnnotations(element, namespace)
# Inputs:        element - XML element 
#                namespace - namespace
# Outputs:       None
# Exceptions:    None
# Description:   Remove annotations of an element if present
# 
################################################################################
def removeAnnotations(element, namespace):
    "Remove annotations of the current element"
    
    #check if the first child is an annotation and delete it
    if(len(list(element)) != 0):
        if (element[0].tag == "{0}annotation".format(namespace)):
            element.remove(element[0])


################################################################################
# 
# Function Name: generateSequence(request, element, fullPath, xmlTree)
# Inputs:        request - 
#                element - XML element
#                fullPath - full Xpath to the current element
#                xmlTree - XML Tree
# Outputs:       HTML string representing a sequence
# Exceptions:    None
# Description:   Generates a section of the form that represents an XML sequence
# 
################################################################################
def generateSequence(request, element, fullPath, xmlTree, choiceInfo=None):
    #(annotation?,(element|group|choice|sequence|any)*)
    defaultNamespace = request.session['defaultNamespaceExplore']
    
    formString = ""
    
    # remove the annotations
    removeAnnotations(element, defaultNamespace)
    
    if choiceInfo:
        if (choiceInfo.counter > 0):
            formString += "<ul id=\"" + choiceInfo.chooseIDStr + "-" + str(choiceInfo.counter) + "\" class=\"notchosen\">"
        else:
            formString += "<ul id=\"" + choiceInfo.chooseIDStr + "-" + str(choiceInfo.counter) + "\" >"
    else:
        formString += "<ul>"
    
    # generates the sequence
    if(len(list(element)) != 0):
        for child in element:
            if (child.tag == "{0}element".format(defaultNamespace)):            
                formString += generateElement(request, child, fullPath, xmlTree, choiceInfo)
            elif (child.tag == "{0}sequence".format(defaultNamespace)):
                formString += generateSequence(request, child, fullPath, xmlTree, choiceInfo)
            elif (child.tag == "{0}choice".format(defaultNamespace)):
                formString += generateChoice(request, child, fullPath, xmlTree, choiceInfo)
            elif (child.tag == "{0}any".format(defaultNamespace)):
                pass
            elif (child.tag == "{0}group".format(defaultNamespace)):
                pass
    
    formString += "</ul>"
    
    return formString

################################################################################
# 
# Function Name: generateChoice(request, element, fullPath, xmlTree)
# Inputs:        request - 
#                element - XML element
#                fullPath - full Xpath to the current element
#                xmlTree - XML Tree
#                choiceInfo - 
# Outputs:       HTML string representing a sequence
# Exceptions:    None
# Description:   Generates a section of the form that represents an XML choice
# 
################################################################################
def generateChoice(request, element, fullPath, xmlTree, choiceInfo=None):
    #(annotation?,(element|group|choice|sequence|any)*)
    nbChoicesID = int(request.session['nbChoicesIDExplore'])
    
    defaultNamespace = request.session['defaultNamespaceExplore']    
    
    formString = ""
    
    #remove the annotations
    removeAnnotations(element, defaultNamespace) 
    
    if choiceInfo:
        if (choiceInfo.counter > 0):
            formString += "<ul id=\"" + choiceInfo.chooseIDStr + "-" + str(choiceInfo.counter) + "\" class=\"notchosen\">"
        else:
            formString += "<ul id=\"" + choiceInfo.chooseIDStr + "-" + str(choiceInfo.counter) + "\" >"
    else:
        formString += "<ul>"
    
    chooseID = nbChoicesID
    chooseIDStr = 'choice' + str(chooseID)
    nbChoicesID += 1
    request.session['nbChoicesIDExplore'] = str(nbChoicesID)
    formString += "<li>Choose <select id='"+ chooseIDStr +"' onchange=\"changeChoice(this);\">"
    
    nbSequence = 1
    # generates the choice
    if(len(list(element)) != 0):
        for child in element:
            if (child.tag == "{0}element".format(defaultNamespace)):            
                name = child.attrib.get('name')
                if name is None:
                    name = child.attrib.get('ref')
                formString += "<option value='" + name + "'>" + name + "</option></b><br>"
            elif (child.tag == "{0}group".format(defaultNamespace)):
                pass
            elif (child.tag == "{0}choice".format(defaultNamespace)):
                pass
            elif (child.tag == "{0}sequence".format(defaultNamespace)):
                formString += "<option value='sequence" + str(nbSequence) + "'>Sequence " + str(nbSequence) + "</option></b><br>"
                nbSequence += 1
            elif (child.tag == "{0}any".format(defaultNamespace)):
                pass

    formString += "</select>"
    
    for (counter, choiceChild) in enumerate(list(element)):
        if choiceChild.tag == "{0}element".format(defaultNamespace):
            formString += generateElement(request, choiceChild, fullPath, xmlTree, common.ChoiceInfo(chooseIDStr,counter))
        elif (choiceChild.tag == "{0}group".format(defaultNamespace)):
            pass
        elif (choiceChild.tag == "{0}choice".format(defaultNamespace)):
            pass
        elif (choiceChild.tag == "{0}sequence".format(defaultNamespace)):
            formString += generateSequence(request, choiceChild, fullPath, xmlTree, common.ChoiceInfo(chooseIDStr,counter))
        elif (choiceChild.tag == "{0}any".format(defaultNamespace)):
            pass
                                  
    
    formString += "</li>"
    formString += "</ul>"
    
    return formString

################################################################################
# 
# Function Name: generateSimpleType(request, element, elementName, elementType, fullPath, xmlTree)
# Inputs:        request - 
#                element - XML element
#                elementName - name of the XML element
#                elementType - type of the XML element
#                xmlTree - XML Tree
#                namespace - namespace
# Outputs:       HTML string representing a sequence
# Exceptions:    None
# Description:   Generates a section of the form that represents an XML choice
# 
################################################################################
def generateSimpleType(request, element, elementName, elementType, fullPath, xmlTree):
    #(annotation?,(restriction|list|union))
    
    defaultNamespace = request.session['defaultNamespaceExplore']  
    
    # build the path to element to be used in the query
    fullPath += "." + elementName
    
    formString = ""

    # remove the annotations
    removeAnnotations(elementType, defaultNamespace)    
    
    if(len(list(elementType)) != 0):
        child = elementType[0] 
        if child.tag == "{0}restriction".format(defaultNamespace):
            formString += generateRestriction(request, child, fullPath, elementName, xmlTree)
        elif child.tag == "{0}list".format(defaultNamespace):
            formString += "<li>" + elementName + "</li>"
        elif child.tag == "{0}union".format(defaultNamespace):
            pass
    
    return formString 

################################################################################
# 
# Function Name: generateRestriction(request, element, fullPath, elementName)
# Inputs:        request - 
#                element - XML element
#                fullPath - full XPath
#                elementName - name of the XML element
# Outputs:       HTML string representing a sequence
# Exceptions:    None
# Description:   Generates a section of the form that represents an XML restriction
# 
################################################################################
def generateRestriction(request, element, fullPath, elementName, xmlTree):
    defaultNamespace = request.session['defaultNamespaceExplore']  
    mapTagIDElementInfo = request.session['mapTagIDElementInfoExplore']
    
    elementID = len(mapTagIDElementInfo.keys()) 
    
    formString = ""
    
    enumChildren = element.findall("{0}enumeration".format(defaultNamespace))
    if len(enumChildren) > 0:
        formString += "<li id='" + str(elementID) + "'>" + elementName + " <input type='checkbox'>" + "</li>"
        elementInfo = ElementInfo("enum",fullPath[1:])
        mapTagIDElementInfo[elementID] = elementInfo.__to_json__()
        request.session['mapTagIDElementInfoExplore'] = mapTagIDElementInfo
        listChoices = []
        for enumChild in enumChildren:
            listChoices.append(enumChild.attrib['value'])
        request.session['mapEnumIDChoicesExplore'][elementID] = listChoices
    else:
        simpleType = element.find('{0}simpleType'.format(defaultNamespace))
        if simpleType is not None:
            formString += generateSimpleType(request, element, elementName, simpleType, fullPath, xmlTree)
        else:
            if 'base' in element.attrib and element.attrib['base'] in common.getXSDTypes(request.session['defaultPrefixExplore']):
                formString += "<li id='" + str(elementID) + "'>" + elementName + " <input type='checkbox'>"    
                elementInfo = ElementInfo(element.attrib['base'], fullPath[1:])
                mapTagIDElementInfo[elementID] = elementInfo.__to_json__()
                request.session['mapTagIDElementInfoExplore'] = mapTagIDElementInfo
            
    return formString

################################################################################
# 
# Function Name: generateExtension(request, element, fullPath, elementName)
# Inputs:        request - 
#                element - XML element
#                fullPath - full XPath
#                elementName - name of the XML element
# Outputs:       HTML string representing a sequence
# Exceptions:    None
# Description:   Generates a section of the form that represents an XML extension
# 
################################################################################
def generateExtension(request, element, fullPath, elementName):
    mapTagIDElementInfo = request.session['mapTagIDElementInfoExplore']
    
    elementID = len(mapTagIDElementInfo.keys()) 
    
    formString = ""
    
    if element.attrib['base'] in common.getXSDTypes(request.session['defaultPrefixExplore']):
        formString += "<li id='" + str(elementID) + "'>" + elementName + " <input type='checkbox'/>"    
        elementInfo = ElementInfo(element.attrib['base'], fullPath[1:])
        mapTagIDElementInfo[elementID] = elementInfo.__to_json__()
        request.session['mapTagIDElementInfoExplore'] = mapTagIDElementInfo
        formString += "</li>"
            
    return formString

################################################################################
# 
# Function Name: generateComplexType(request, elementType, elementName, fullPath, xmlTree)
# Inputs:        request - 
#                elementType - XML elementType
#                elementName - name of the XML element
#                fullPath - full XPath
#                xmlTree - XML Tree
# Outputs:       HTML string representing a sequence
# Exceptions:    None
# Description:   Generates a section of the form that represents an XML complexType
# 
################################################################################
def generateComplexType(request, elementType, elementName, fullPath, xmlTree):
    defaultNamespace = request.session['defaultNamespaceExplore']    
    
    # build the path to element to be used in the query
    fullPath += "." + elementName
    
    formString = ""
    
    # remove the annotations
    removeAnnotations(elementType, defaultNamespace)
    
    # TODO: does it contain attributes ?
    
    # does it contain sequence or all?
    complexTypeChild = elementType.find('{0}sequence'.format(defaultNamespace))
    if complexTypeChild is not None:
        formString += "<li>" + elementName
        formString += generateSequence(request, complexTypeChild, fullPath, xmlTree)
        formString += "</li>"
    else:
        complexTypeChild = elementType.find('{0}all'.format(defaultNamespace))
        if complexTypeChild is not None:
            formString += "<li>" + elementName
            formString += generateSequence(request, complexTypeChild, fullPath, xmlTree)
            formString += "</li>"
        else:
            # does it contain choice ?
            complexTypeChild = elementType.find('{0}choice'.format(defaultNamespace))
            if complexTypeChild is not None:
                formString += "<li>" + elementName
                formString += generateChoice(request, complexTypeChild, fullPath, xmlTree)
                formString += "</li>"
            else:
                # does it contain a simple content ?
                complexTypeChild = elementType.find('{0}simpleContent'.format(defaultNamespace))
                if complexTypeChild is not None:
                    return generateSimpleContent(request, complexTypeChild, fullPath, elementName)
                else:
                    return formString
    
    return formString 


################################################################################
# 
# Function Name: generateSimpleContent(request, element, fullPath, xmlTree)
# Inputs:        request - 
#                complexTypeChild - element
#                fullPath - full XPath
#                xmlTree - XML Tree
# Outputs:       HTML string representing a sequence
# Exceptions:    None
# Description:   Generates a section of the form that represents an XML simple content
# 
################################################################################
def generateSimpleContent(request, element, fullPath, elementName):
    #(annotation?,(restriction|extension))
    
    defaultNamespace = request.session['defaultNamespaceExplore']
    
    formString = ""
    
    # remove the annotations
    removeAnnotations(element, defaultNamespace)
    
    # generates the sequence
    if(len(list(element)) != 0):
        child = element[0]    
        if (child.tag == "{0}restriction".format(defaultNamespace)):            
            formString += generateRestriction(request, child, fullPath, elementName)
        elif (child.tag == "{0}extension".format(defaultNamespace)):
            formString += generateExtension(request, child, fullPath, elementName)
    
    return formString

################################################################################
# 
# Function Name: generateElement(request, element, fullPath, xmlTree)
# Inputs:        request -
#                element - XML element
#                fullPath - full Xpath to the current element
#                xmlTree - XML Tree
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Generate an HTML string that represents an XML element.
#
################################################################################
def generateElement(request, element, fullPath, xmlTree, choiceInfo=None):
    # get the variables in session
    defaultNamespace = request.session['defaultNamespaceExplore']    
    defaultPrefix = request.session['defaultPrefixExplore']
    
    formString = ""

    # remove the annotations
    removeAnnotations(element, defaultNamespace)

    # type is a reference included in the document
    if 'ref' in element.attrib: 
        ref = element.attrib['ref']
        refElement = None
        if ':' in ref:
            refSplit = ref.split(":")
            refNamespacePrefix = refSplit[0]
            refName = refSplit[1]
            namespaces = request.session['namespaces']
            # refNamespace = namespaces[refNamespacePrefix]
            # TODO: manage namespaces/targetNamespaces, composed schema with different target namespaces
            # element = xmlTree.findall("./{0}element[@name='"+refName+"']".format(refNamespace))
            refElement = xmlTree.find("./{0}element[@name='{1}']".format(defaultNamespace, refName))
        else:
            refElement = xmlTree.find("./{0}element[@name='{1}']".format(defaultNamespace, ref))
                
        if refElement is not None:
            textCapitalized = refElement.attrib.get('name')            
            element = refElement
            # remove the annotations
            removeAnnotations(element, defaultNamespace)
    else:
        textCapitalized = element.attrib.get('name')
        
    if choiceInfo:
        if (choiceInfo.counter > 0):
            formString += "<ul id=\"" + choiceInfo.chooseIDStr + "-" + str(choiceInfo.counter) + "\" class=\"notchosen\">"
        else:
            formString += "<ul id=\"" + choiceInfo.chooseIDStr + "-" + str(choiceInfo.counter) + "\" >"
    else:
        formString += "<ul>"

    # type declared below
    if 'type' not in element.attrib:           
        # if tag not closed:  <element/>
        if len(list(element)) > 0 :
            if (element[0].tag == "{0}complexType".format(defaultNamespace)):
                formString += generateComplexType(request, element[0], textCapitalized, fullPath, xmlTree)
            else:                     
                formString += generateSimpleType(request, element, textCapitalized, element[0], fullPath, xmlTree)
                   
    # if element is one of the declared type
    elif element.attrib.get('type') in common.getXSDTypes(defaultPrefix):                                                                   
        mapTagIDElementInfo = request.session['mapTagIDElementInfoExplore']                  
        elementID = len(mapTagIDElementInfo.keys())
        formString += "<li id='" + str(elementID) + "'>" + textCapitalized + " <input type='checkbox'>"                         
        formString += "</li>"                    
        elementInfo = ElementInfo(element.attrib.get('type'),fullPath[1:] + "." + textCapitalized)
        mapTagIDElementInfo[elementID] = elementInfo.__to_json__()
        request.session['mapTagIDElementInfoExplore'] = mapTagIDElementInfo                
    else:                        
        # TODO: manage namespaces
        # type of the element is complex
        typeName = element.attrib.get('type')
        if ':' in typeName:
            typeName = typeName.split(":")[1]
        xpath = "./{0}complexType[@name='{1}']".format(defaultNamespace,typeName)
        elementType = xmlTree.find(xpath)
        if elementType is None:
            # type of the element is simple
            xpath = "./{0}simpleType[@name='{1}']".format(defaultNamespace,typeName)
            elementType = xmlTree.find(xpath)                        
        if elementType is not None:
            if elementType.tag == "{0}complexType".format(defaultNamespace):
                formString += generateComplexType(request, elementType, textCapitalized, fullPath, xmlTree) 
            elif elementType.tag == "{0}simpleType".format(defaultNamespace):                
                formString += generateSimpleType(request, element, textCapitalized, elementType, fullPath, xmlTree)

    formString += "</ul>"
    return formString

################################################################################
# 
# Function Name: generateForm(request)
# Inputs:        request -
# Outputs:       rendered HTMl form
# Exceptions:    None
# Description:   Renders HTMl form for display.
#
################################################################################
def generateForm(request):
    print 'BEGIN def generateForm(request)'    
    

    xmlDocTreeStr = request.session['xmlDocTreeExplore']
    xmlDocTree = etree.fromstring(xmlDocTreeStr)
    
    if 'mapTagIDElementInfoExplore' in request.session:
        del request.session['mapTagIDElementInfoExplore']    
    if 'mapEnumIDChoicesExplore' in request.session:
        del request.session['mapEnumIDChoicesExplore']
    request.session['mapTagIDElementInfoExplore'] = dict()
    request.session['mapEnumIDChoicesExplore'] = dict()
    request.session['nbChoicesIDExplore'] = '0'
    
    formString = ""   
        
    defaultNamespace = request.session['defaultNamespaceExplore'] 
    elements = xmlDocTree.findall("./{0}element".format(defaultNamespace))

    try:
        if len(elements) == 1:
            formString += generateElement(request, elements[0], "", xmlDocTree)    
        elif len(elements) > 1:
            formString += generateChoice(request, elements, "", xmlDocTree)
    except Exception, e:
        formString = "UNSUPPORTED ELEMENT FOUND (" + e.message + ")" 
        
    print 'END def generateForm(request)'

    return formString

################################################################################
# 
# Function Name: generate_xsd_tree_for_querying_data(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Generate an HTML tree from the XSD to select the fields being used in the query
#
################################################################################
def generate_xsd_tree_for_querying_data(request): 
    print 'BEGIN def generateXSDTreeForQueryingData(request)'
    
    if 'formStringExplore' in request.session:
        formString = request.session['formStringExplore']  
    else:
        formString = ''
    
    if 'xmlDocTreeExplore' in request.session:
        xmlDocTreeStr = request.session['xmlDocTreeExplore'] 
    else:
        xmlDocTreeStr = ""
    
    templateID = request.session['exploreCurrentTemplateID']
    
    # get the namespaces of the schema and the default prefix
    xmlDocTree = etree.fromstring(xmlDocTreeStr)
    defaultNamespace = "http://www.w3.org/2001/XMLSchema"
    for prefix, url in xmlDocTree.nsmap.iteritems():
        if (url == defaultNamespace):            
            request.session['defaultPrefixExplore'] = prefix
            break
    defaultNamespace = "{" + defaultNamespace + "}"
    request.session['defaultNamespaceExplore'] = defaultNamespace
    
    if xmlDocTreeStr == "":
        setCurrentTemplate(request, templateID)        
    if (formString == ""):
        formString = "<form id=\"dataQueryForm\" name=\"xsdForm\">"
        formString += generateForm(request)        
        formString += "</form>"        
 
    print 'END def generateXSDTreeForQueryingData(request)'
    response_dict = {'xsdForm': formString}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: execute_query(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   execute a query in Mongo db
#
################################################################################
def execute_query(request):
    print 'BEGIN def executeQuery(request)'        
    
    query_form = request.POST['queryForm']
    fed_of_queries = request.POST['fedOfQueries']
    
    request.session['savedQueryFormExplore'] = query_form    
    
    response_dict = {}
    queryFormTree = html.fromstring(query_form)
    errors = checkQueryForm(request, queryFormTree)
    if(len(errors)== 0):
        instances = getInstances(request, fed_of_queries)
        if (len(instances)==0):
            response_dict = {'errors': 'zero'}
        else:
            htmlTree = html.fromstring(query_form)
            query = fieldsToQuery(request, htmlTree)            
            request.session['queryExplore'] = query
            json_instances = []
            for instance in instances:
                json_instances.append(instance.to_json()) 
            request.session['instancesExplore'] = json_instances
    else:
        errorsString = ""
        for error in errors:
            errorsString += "<p>" + error + "</p>"    
        response_dict = {'listErrors': errorsString}        

    print 'END def executeQuery(request, queryForm, queryBuilder, fedOfQueries)'
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

################################################################################
# 
# Function Name: getInstances(request, fedOfQueries)
# Inputs:        request -
#                fedOfQueries - html list of repositories
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Get the selected instances from the the repositories section
#
################################################################################
def getInstances(request, fedOfQueries):
    
    instances = []
    fedOfQueriesTree = html.fromstring(fedOfQueries)    
    instancesCheckboxes = fedOfQueriesTree.findall(".//input[@type='checkbox']")
    
    for checkbox in instancesCheckboxes:
        if 'checked' in checkbox.attrib:
            if checkbox.attrib['value'] == "Local":
                if 'HTTPS' in request.META['SERVER_PROTOCOL']:
                    protocol = "https"
                else:
                    protocol = "http"
                instances.append(Instance(name="Local", protocol=protocol, address=request.META['REMOTE_ADDR'], port=request.META['SERVER_PORT'], access_token="token", refresh_token="token"))
            else:
                instances.append(Instance.objects.get(name=checkbox.attrib['value']))
    
    return instances  

################################################################################
# 
# Function Name: get_results(request)
# Inputs:        request -
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Get the results of a query
#
################################################################################
def get_results(request):
    instances = request.session['instancesExplore']    
    response_dict = {'numInstance': str(len(instances))}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

################################################################################
# 
# Function Name: getResults(query)
# Inputs:        query -
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Transform the query to get rid of Regex object 
#
################################################################################
def manageRegexBeforeExe(query):
    for key, value in query.iteritems():
        if key == "$and" or key == "$or":
            for subValue in value:
                manageRegexBeforeExe(subValue)
        elif isinstance(value, unicode):
            if (len(value) >= 2 and value[0] == "/" and value[-1] == "/"):
                query[key] = re.compile(value[1:-1])
        elif isinstance(value, dict):
            manageRegexBeforeExe(value)

# ################################################################################
# # 
# # Function Name: getResultsByInstance(request, numInstance)
# # Inputs:        request -  
# # Outputs:       
# # Exceptions:    None
# # Description:   Get results of a query
# #
# ################################################################################
# @dajaxice_register
# def getResultsByInstance(request, numInstance):
#     print 'BEGIN def getResults(request)'
#     dajax = Dajax()
#     
#     query = copy.deepcopy(request.session['queryExplore'])
#     
#     instances = request.session['instancesExplore']
#         
#     resultString = ""
#     results = []    
#     
#     instance = eval(instances[int(numInstance)])
#     sessionName = "resultsExplore" + instance['name']
#     resultString += "<b>From " + instance['name'] + ":</b> <br/>"
#     if instance['name'] == "Local":
#         manageRegexBeforeExe(query)
#         instanceResults = XMLdata.executeQuery(query)
#         if len(instanceResults) > 0:
#             for instanceResult in instanceResults:
#                 results.append(xmltodict.unparse(instanceResult))
# #                 resultString += "<textarea class='xmlResult' readonly='true'>"
#                 resultString += "<div class='xmlResult' readonly='true'>"
#                 xsltPath = os.path.join(settings.SITE_ROOT, 'static/resources/xsl/xml2html.xsl')
#                 xslt = etree.parse(xsltPath)
#                 transform = etree.XSLT(xslt)
#                 dom = etree.fromstring(str(xmltodict.unparse(instanceResult).replace('<?xml version="1.0" encoding="utf-8"?>\n',"")))
#                 newdom = transform(dom)
#                 resultString += str(newdom)
# #                 resultString += str(xmltodict.unparse(instanceResult, pretty=True))
# #                 resultString += "</textarea> <br/>"
#                 resultString += "</div> <br/>"
#             resultString += "<br/>"
#         else:
#             resultString += "<span style='font-style:italic; color:red;'> No Results found... </span><br/><br/>"
#     else:
#         url = instance['protocol'] + "://" + instance['address'] + ":" + str(instance['port']) + "/rest/explore/query-by-example"
# #         queryStr = str(query)
# #         queryStr = manageRegexBeforeAPI(query, queryStr)
# #         queryToSend = eval(queryStr)
#         data = {"query":str(query)}
#         r = requests.post(url, data, auth=(instance['user'], instance['password']))   
#         result = r.text
#         instanceResults = json.loads(result,object_pairs_hook=OrderedDict)
#         if len(instanceResults) > 0:
#             for instanceResult in instanceResults:
#                 results.append(xmltodict.unparse(instanceResult['content']))
# #                 resultString += "<textarea class='xmlResult' readonly='true'>"  
# #                 resultString += str(xmltodict.unparse(instanceResult['content'], pretty=True))
# #                 resultString += "</textarea> <br/>"
#                 resultString += "<div class='xmlResult' readonly='true'>"
#                 xsltPath = os.path.join(settings.SITE_ROOT, 'static/resources/xsl/xml2html.xsl')
#                 xslt = etree.parse(xsltPath)
#                 transform = etree.XSLT(xslt)
#                 dom = etree.fromstring(str(xmltodict.unparse(instanceResult['content']).replace('<?xml version="1.0" encoding="utf-8"?>\n',"")))
#                 newdom = transform(dom)
#                 resultString += str(newdom)
#                 resultString += "</div> <br/>"
#             resultString += "<br/>"
#         else:
#             resultString += "<span style='font-style:italic; color:red;'> No Results found... </span><br/><br/>"
#         
#     request.session[sessionName] = results
#     dajax.append("#results", "innerHTML", resultString)
#     
#     print 'END def getResults(request)'
#     return dajax.json()


################################################################################
#
# Function Name: get_results_by_instance_keyword(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Get results of a query for a specific keyword
#
################################################################################
def get_results_by_instance_keyword(request):
    print 'BEGIN def getResultsKeyword(request)'
    resultsByKeyword = []
    results = []
    resultString = ""
    sessionName = "resultsExploreLocal"

    if settings.EXPLORE_BY_KEYWORD:
        try:
            keyword = request.GET['keyword']
            schemas = request.GET.getlist('schemas[]')
            refinements = refinements_to_mongo(request.GET.getlist('refinements[]'))
            onlySuggestions = json.loads(request.GET['onlySuggestions'])
        except:
            keyword = ''
            schemas = []
            refinements = {}
            onlySuggestions = True

        #We get all template versions for the given schemas
        templatesVersions = Template.objects(title__in=schemas).distinct(field="templateVersion")
        #We get all templates ID, for all versions
        templatesID = TemplateVersion.objects(pk__in=templatesVersions).distinct(field="versions")
        
        instanceResults = XMLdata.executeFullTextQuery(keyword, templatesID, refinements)
        if len(instanceResults) > 0:
            if not onlySuggestions:
                xsltPath = os.path.join(settings.SITE_ROOT, 'static/resources/xsl/xml2html.xsl')
                xslt = etree.parse(xsltPath)
                transform = etree.XSLT(xslt)
                template = loader.get_template('explore/explore_result_keyword.html')

            for instanceResult in instanceResults:
                if not onlySuggestions:
                    custom_xslt = False
                    results.append({'title':instanceResult['title'], 'content':xmltodict.unparse(instanceResult['content']),'id':str(instanceResult['_id'])})
                    dom = etree.XML(str(xmltodict.unparse(instanceResult['content']).encode('utf-8')))
                    #Check if a custom list result XSLT has to be used
                    try:
                        schema = Template.objects.get(pk=instanceResult['schema'])
                        if schema.ResultXsltList:
                            listXslt = etree.parse(BytesIO(schema.ResultXsltList.content.encode('utf-8')))
                            listTransform = etree.XSLT(listXslt)
                            newdom = listTransform(dom)
                            custom_xslt = True
                        else:
                            newdom = transform(dom)
                    except Exception, e:
                        #We use the default one
                        newdom = transform(dom)
                        custom_xslt = False

                    context = RequestContext(request, {'id':str(instanceResult['_id']),
                                       'xml': str(newdom),
                                       'title': instanceResult['title'],
                                       'custom_xslt': custom_xslt})

                    resultString+= template.render(context)
                else:
                    wordList = re.sub("[^\w]", " ",  keyword).split()
                    wordList = [x + "|" + x +"\w+" for x in wordList]
                    wordList = '|'.join(wordList)
                    listWholeKeywords = re.findall("\\b("+ wordList +")\\b", xmltodict.unparse(instanceResult['content']).encode('utf-8'), flags=re.IGNORECASE)
                    labels = list(set(listWholeKeywords))

                    for label in labels:
                        label = label.lower()
                        result_json = {}
                        result_json['label'] = label
                        result_json['value'] = label
                        if not result_json in resultsByKeyword:
                            resultsByKeyword.append(result_json)

            result_json = {}
            result_json['resultString'] = resultString

    request.session[sessionName] = results
    print 'END def getResultsKeyword(request)'

    return HttpResponse(json.dumps({'resultsByKeyword' : resultsByKeyword, 'resultString' : resultString, 'count' : len(instanceResults)}), content_type='application/javascript')



################################################################################
# 
# Function Name: get_results_by_instance(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Get results of a query for a specific instance (Local or others)
#
################################################################################
def get_results_by_instance(request):
    print 'BEGIN def getResults(request)'
    num_instance = request.GET['numInstance']
    instances = request.session['instancesExplore']
    resultString = ""

    for i in range(int(num_instance)):
        results = []
        instance = eval(instances[int(i)])
        sessionName = "resultsExplore" + instance['name']
        resultString += "<p style='font-weight:bold; color:#369;'>From " + instance['name'] + ":</p>"
        if instance['name'] == "Local":
            query = copy.deepcopy(request.session['queryExplore'])
            manageRegexBeforeExe(query)
            instanceResults = XMLdata.executeQueryFullResult(query)

            if len(instanceResults) > 0:
                template = loader.get_template('explore/explore_result.html')
                xsltPath = os.path.join(settings.SITE_ROOT, 'static/resources/xsl/xml2html.xsl')
                xslt = etree.parse(xsltPath)
                transform = etree.XSLT(xslt)
                for instanceResult in instanceResults:
                    custom_xslt = False
                    results.append({'title':instanceResult['title'], 'content':xmltodict.unparse(instanceResult['content']),'id':str(instanceResult['_id'])})
                    #dom = etree.fromstring(str(xmltodict.unparse(instanceResult['content']).replace('<?xml version="1.0" encoding="utf-8"?>\n',"")))
                    dom = etree.XML(str(xmltodict.unparse(instanceResult['content']).encode('utf-8')))
                    #Check if a custom list result XSLT has to be used
                    try:
                        schema = Template.objects.get(pk=instanceResult['schema'])
                        if schema.ResultXsltList:
                            listXslt = etree.parse(BytesIO(schema.ResultXsltList.content.encode('utf-8')))
                            listTransform = etree.XSLT(listXslt)
                            newdom = listTransform(dom)
                            custom_xslt = True
                        else:
                            newdom = transform(dom)
                    except Exception, e:
                        #We use the default one
                        newdom = transform(dom)
                        custom_xslt = False

                    context = RequestContext(request, {'id':str(instanceResult['_id']),
                                               'xml': str(newdom),
                                               'title': instanceResult['title'],
                                               'custom_xslt': custom_xslt})

                    resultString+= template.render(context)

                resultString += "<br/>"
            else:
                resultString += "<span style='font-style:italic; color:red;'> No Results found... </span><br/><br/>"

        else:
            url = instance['protocol'] + "://" + instance['address'] + ":" + str(instance['port']) + "/rest/explore/query-by-example"
            query = copy.deepcopy(request.session['queryExplore'])
            data = {"query":str(query)}
            headers = {'Authorization': 'Bearer ' + instance['access_token']}
            r = requests.post(url, data=data, headers=headers)   
            result = r.text
            instanceResults = json.loads(result,object_pairs_hook=OrderedDict)
            if len(instanceResults) > 0:
                template = loader.get_template('explore_result.html')
                xsltPath = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'xml2html.xsl')
                xslt = etree.parse(xsltPath)
                transform = etree.XSLT(xslt)
                for instanceResult in instanceResults:
                    custom_xslt = False
                    results.append({'title':instanceResult['title'], 'content':instanceResult['content'],'id':str(instanceResult['_id'])})
                    dom = etree.XML(str(xmltodict.unparse(instanceResult['content']).encode('utf-8')))
                    #Check if a custom list result XSLT has to be used
                    try:
                        schema = Template.objects.get(pk=instanceResult['schema'])
                        if schema.ResultXsltList:
                            listXslt = etree.parse(BytesIO(schema.ResultXsltList.content.encode('utf-8')))
                            listTransform = etree.XSLT(listXslt)
                            newdom = listTransform(dom)
                            custom_xslt = True
                        else:
                            newdom = transform(dom)
                    except Exception, e:
                        #We use the default one
                        newdom = transform(dom)
                        custom_xslt = False

                    context = Context({'id':str(instanceResult['_id']),
                                       'xml': str(newdom),
                                       'title': instanceResult['title'],
                                       'custom_xslt': custom_xslt})

                    resultString+= template.render(context)
                resultString += "<br/>"
            else:
                resultString += "<span style='font-style:italic; color:red;'> No Results found... </span><br/><br/>"
            
        request.session[sessionName] = results
    
    print 'END def getResults(request)'
    response_dict = {'results': resultString}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
 
 
################################################################################
# 
# Function Name: manageRegexBeforeAPI(query, queryStr)
# Inputs:        query - 
#                queryStr -
# Outputs:       
# Exceptions:    None
# Description:   Can't do a deep copy of a dictionary containing pattern objects (deepcopy bug).
#                This function is no longer in use
#
################################################################################
def manageRegexBeforeAPI(query, queryStr):
    for key, value in query.iteritems():
        if key == "$and" or key == "$or":
            for subValue in value:
                queryStr = manageRegexBeforeAPI(subValue, queryStr)
        elif isinstance(value, re._pattern_type):
#             query[key] = "/" + str(value.pattern) + "/"
            queryStr = queryStr.replace(str(value),"'/" + str(value.pattern) + "/'")
        elif isinstance(value, dict):
            queryStr = manageRegexBeforeAPI(value, queryStr)
    return queryStr

################################################################################
# 
# Function Name: intCriteria(path, comparison, value, isNot=False)
# Inputs:        path - 
#                comparison -
#                value -
#                isNot -
# Outputs:       a criteria
# Exceptions:    None
# Description:   Build a criteria for mongo db for the type integer
#
################################################################################
def intCriteria(path, comparison, value, isNot=False):
    print 'BEGIN def intCriteria(path, comparison, value, isNot=False)'
    criteria = dict()

    if(comparison == "="):
        if(isNot):
            criteria[path] = eval('{"$ne":' + value + '}')
        else:
            criteria[path] = int(value)
    else:
        if(isNot):
            criteria[path] = eval('{"$not":{"$' +comparison+ '":'+ value +'}}')
        else:
            criteria[path] = eval('{"$'+comparison+'":'+ value +'}')

    print 'END def intCriteria(path, comparison, value, isNot=False)'
    return criteria


################################################################################
# 
# Function Name: floatCriteria(path, comparison, value, isNot=False)
# Inputs:        path - 
#                comparison -
#                value -
#                isNot -
# Outputs:       a criteria
# Exceptions:    None
# Description:   Build a criteria for mongo db for the type float
#
################################################################################
def floatCriteria(path, comparison, value, isNot=False):
    criteria = dict()

    if(comparison == "="):
        if(isNot):
            criteria[path] = eval('{"$ne":' + value + '}')
        else:
            criteria[path] = float(value)
    else:
        if(isNot):
            criteria[path] = eval('{"$not":{"$' +comparison+ '":'+ value +'}}')
        else:
            criteria[path] = eval('{"$'+comparison+'":'+ value +'}')

    return criteria

################################################################################
# 
# Function Name: stringCriteria(path, comparison, value, isNot=False)
# Inputs:        path - 
#                comparison -
#                value -
#                isNot -
# Outputs:       a criteria
# Exceptions:    None
# Description:   Build a criteria for mongo db for the type string
#
################################################################################
def stringCriteria(path, comparison, value, isNot=False):
    criteria = dict()
    
    if (comparison == "is"):
        if(isNot):
            criteria[path] = eval('{"$ne":' + repr(value) + '}')
        else:
            criteria[path] = str(value)
    elif (comparison == "like"):
        if(isNot):
            criteria[path] = dict()
            criteria[path]["$not"] = "/" + value + "/"
        else:
            criteria[path] = "/" + value + "/"
    
    return criteria

################################################################################
# 
# Function Name: queryToCriteria(query, isNot=False)
# Inputs:        query - 
#                isNot -
# Outputs:       a criteria
# Exceptions:    None
# Description:   Build a criteria for mongo db for a query
#
################################################################################
def queryToCriteria(query, isNot=False):
    if(isNot):
        return invertQuery(query.copy())
    else:
        return query

################################################################################
# 
# Function Name: invertQuery(query)
# Inputs:        query - 
# Outputs:       
# Exceptions:    None
# Description:   Invert each field of the query to build NOT(query)
#
################################################################################
def invertQuery(query):
    for key, value in query.iteritems():
        if key == "$and" or key == "$or":
            for subValue in value:
                invertQuery(subValue)
        else:            
            #lt, lte, =, gte, gt, not, ne
            if isinstance(value,dict):                
                if value.keys()[0] == "$not" or value.keys()[0] == "$ne":
                    query[key] = (value[value.keys()[0]])                    
                else:
                    savedValue = value
                    query[key] = dict()
                    query[key]["$not"] = savedValue
            else:
                savedValue = value
                if isinstance(value, re._pattern_type):
                    query[key] = dict()
                    query[key]["$not"] = savedValue
                else:
                    query[key] = dict()
                    query[key]["$ne"] = savedValue
    return query

################################################################################
# 
# Function Name: enumCriteria(path, value, isNot=False)
# Inputs:        path -
#                value -
#                isNot -
# Outputs:       criteria
# Exceptions:    None
# Description:   Build a criteria for mongo db for an enumeration
#
################################################################################
def enumCriteria(path, value, isNot=False):
    criteria = dict()
    
    if(isNot):
        criteria[path] = eval('{"$ne":' + repr(value) + '}')
    else:
        criteria[path] = str(value)
            
    return criteria

################################################################################
# 
# Function Name: ANDCriteria(criteria1, criteria2)
# Inputs:        criteria1 -
#                criteria2 -
# Outputs:       criteria
# Exceptions:    None
# Description:   Build a criteria that is the result of criteria1 and criteria2
#
################################################################################
def ANDCriteria(criteria1, criteria2):
    ANDcriteria = dict()
    ANDcriteria["$and"] = []
    ANDcriteria["$and"].append(criteria1)
    ANDcriteria["$and"].append(criteria2)
    return ANDcriteria

################################################################################
# 
# Function Name: ORCriteria(criteria1, criteria2)
# Inputs:        criteria1 -
#                criteria2 -
# Outputs:       criteria
# Exceptions:    None
# Description:   Build a criteria that is the result of criteria1 or criteria2
#
################################################################################
def ORCriteria(criteria1, criteria2):
    ORcriteria = dict()
    ORcriteria["$or"] = []
    ORcriteria["$or"].append(criteria1)
    ORcriteria["$or"].append(criteria2)
    return ORcriteria

################################################################################
# 
# Function Name: buildCriteria(elemPath, comparison, value, elemType, isNot=False)
# Inputs:        elemPath -
#                comparison -
#                value -
#                elemType - 
#                isNot - 
# Outputs:       criteria
# Exceptions:    None
# Description:   Look at element type and route to the right function to build the criteria
#
################################################################################
def buildCriteria(request, elemPath, comparison, value, elemType, isNot=False):
    defaultPrefix = request.session['defaultPrefixExplore']
    
    if (elemType in ['{0}:byte'.format(defaultPrefix),
                     '{0}:int'.format(defaultPrefix),
                     '{0}:integer'.format(defaultPrefix),
                     '{0}:long'.format(defaultPrefix),
                     '{0}:negativeInteger'.format(defaultPrefix),
                     '{0}:nonNegativeInteger'.format(defaultPrefix),
                     '{0}:nonPositiveInteger'.format(defaultPrefix),
                     '{0}:positiveInteger'.format(defaultPrefix),
                     '{0}:short'.format(defaultPrefix),
                     '{0}:unsignedLong'.format(defaultPrefix),
                     '{0}:unsignedInt'.format(defaultPrefix),
                     '{0}:unsignedShort'.format(defaultPrefix),
                     '{0}:unsignedByte'.format(defaultPrefix),]):
        return intCriteria(elemPath, comparison, value, isNot)
    elif (elemType in ['{0}:float'.format(defaultPrefix), 
                       '{0}:double'.format(defaultPrefix),
                       '{0}:decimal'.format(defaultPrefix)]):
        return floatCriteria(elemPath, comparison, value, isNot)
    elif (elemType == '{0}:string'.format(defaultPrefix)):
        return stringCriteria(elemPath, comparison, value, isNot)
    else:
        return stringCriteria(elemPath, comparison, value, isNot)

################################################################################
# 
# Function Name: fieldsToQuery(htmlTree)
# Inputs:        htmlTree -
# Outputs:       query
# Exceptions:    None
# Description:   Take values from the html tree and create a query with them
#
################################################################################
def fieldsToQuery(request, htmlTree):
    
    mapCriterias = request.session['mapCriteriasExplore']
    
    fields = htmlTree.findall("./p")
    
    query = dict()
    for field in fields:        
        boolComp = field[0].value
        if (boolComp == 'NOT'):
            isNot = True
        else:
            isNot = False
            
        criteriaInfo = eval(mapCriterias[field.attrib['id']])
        if criteriaInfo['elementInfo'] is None:
            elementInfo = None
        else:
            elementInfo = eval(criteriaInfo['elementInfo'])
        if criteriaInfo['queryInfo'] is None:
            queryInfo = None
        else:
            queryInfo = eval(criteriaInfo['queryInfo'])
        elemType = elementInfo['type']
        if (elemType == "query"):
            queryValue = queryInfo['query']
            criteria = queryToCriteria(queryValue, isNot)
        elif (elemType == "enum"):
            element = "content." + elementInfo['path']
            value = field[2][0].value            
            criteria = enumCriteria(element, value, isNot)
        else:                
            element = "content." + elementInfo['path']
            comparison = field[2][0].value
            value = field[2][1].value
            criteria = buildCriteria(request, element, comparison, value, elemType , isNot)
        
        if(boolComp == 'OR'):        
            query = ORCriteria(query, criteria)
        elif(boolComp == 'AND'):
            query = ANDCriteria(query, criteria)
        else:
            if(fields.index(field) == 0):
                query.update(criteria)
            else:
                query = ANDCriteria(query, criteria)
        
    return query

################################################################################
# 
# Function Name: checkQueryForm(htmlTree)
# Inputs:        htmlTree -
# Outputs:       query
# Exceptions:    None
# Description:   Check that values entered by the user match each element type
#
################################################################################
def checkQueryForm(request, htmlTree):
    
    mapCriterias = request.session['mapCriteriasExplore']
    
    # get the prefix/namespace used in the schema
    if 'defaultPrefixExplore' in request.session:
        defaultPrefix = request.session['defaultPrefixExplore']
    else:
        xmlDocTreeStr = request.session['xmlDocTreeExplore']
        xmlDocTree = etree.fromstring(xmlDocTreeStr)
        
        defaultNamespace = "http://www.w3.org/2001/XMLSchema"
        for prefix, url in xmlDocTree.nsmap.iteritems():
            if (url == defaultNamespace):            
                request.session['defaultPrefixExplore'] = prefix
                defaultPrefix = prefix
                break
        
    
    # check if there are no errors in the query
    errors = []
    fields = htmlTree.findall("./p")
    if (len(mapCriterias) != len(fields)):
        errors.append("Some fields are empty !")
    else:
        for field in fields:
            criteriaInfo = eval(mapCriterias[field.attrib['id']])
            elementInfo = eval(criteriaInfo['elementInfo']) 
            elemType = elementInfo['type']
            
            if (elemType in ['{0}:float'.format(defaultPrefix), 
                       '{0}:double'.format(defaultPrefix),
                       '{0}:decimal'.format(defaultPrefix)]):
                value = field[2][1].value
                try:
                    float(value)
                except ValueError:
                    elementPath = elementInfo['path']
                    element = elementPath.split('.')[-1]
                    errors.append(element + " must be a number !")
                        
            elif (elemType in ['{0}:byte'.format(defaultPrefix),
                     '{0}:int'.format(defaultPrefix),
                     '{0}:integer'.format(defaultPrefix),
                     '{0}:long'.format(defaultPrefix),
                     '{0}:negativeInteger'.format(defaultPrefix),
                     '{0}:nonNegativeInteger'.format(defaultPrefix),
                     '{0}:nonPositiveInteger'.format(defaultPrefix),
                     '{0}:positiveInteger'.format(defaultPrefix),
                     '{0}:short'.format(defaultPrefix),
                     '{0}:unsignedLong'.format(defaultPrefix),
                     '{0}:unsignedInt'.format(defaultPrefix),
                     '{0}:unsignedShort'.format(defaultPrefix),
                     '{0}:unsignedByte'.format(defaultPrefix)]):
                value = field[2][1].value
                try:
                    int(value)
                except ValueError:
                    elementPath = elementInfo['path']
                    element = elementPath.split('.')[-1]
                    errors.append(element + " must be an integer !")
                    
            elif (elemType == "{0}:string".format(defaultPrefix)):
                comparison = field[2][0].value
                value = field[2][1].value
                elementPath = elementInfo['path']
                element = elementPath.split('.')[-1]
                if (comparison == "like"):
                    try:
                        re.compile(value)
                    except Exception, e:
                        errors.append(element + " must be a valid regular expression ! (" + str(e) + ")")
                    
    return errors
                
    
################################################################################
# 
# Function Name: add_field(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Add an empty field to the query builder
#
################################################################################
def add_field(request):
    
    html_form = request.POST['htmlForm']
    htmlTree = html.fromstring(html_form)
    
    fields = htmlTree.findall("./p")    
    fields[-1].remove(fields[-1].find("./span[@class='icon add']"))      
    if (len(fields) == 1):
        criteriaID = fields[0].attrib['id']
        minusButton = html.fragment_fromstring("""<span class="icon remove" onclick="removeField('""" + str(criteriaID) +"""')"></span>""")
        fields[0].append(minusButton)
    
    # get the id of the last field (get the value of the increment, remove crit)
    lastID = fields[-1].attrib['id'][4:]
    tagID = int(lastID) + 1
    element = html.fragment_fromstring("""
        <p id='crit""" + str(tagID) + """'>
        """
        +
            renderANDORNOT() 
        +
        """
            <input onclick="showCustomTree('crit""" + str(tagID) + """')" readonly="readonly" type="text" class="elementInput">     
            <span id='ui"""+ str(tagID) +"""'>
            </span>  
            <span class="icon remove" onclick="removeField('crit""" + str(tagID) + """')"></span>
            <span class="icon add" onclick="addField()"></span>
        </p>
    """)
    
    #insert before the 3 buttons (save, clear, execute)
    htmlTree.insert(-3,element)   
    
    response_dict = {'queryForm': html.tostring(htmlTree)}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: remove_field(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Remove a field from the query builder
#
################################################################################
def remove_field(request):
    criteria_id = request.POST['criteriaID']
    query_form = request.POST['queryForm']
    
    htmlTree = html.fromstring(query_form)
    
    currentElement = htmlTree.get_element_by_id(criteria_id)
    fields = htmlTree.findall("./p")
    
    
    # suppress last element => give the + to the previous
    if(fields[-1].attrib['id'] == criteria_id):
        plusButton = html.fragment_fromstring("""<span class="icon add" onclick="addField()"></span>""")
        fields[-2].append(plusButton)
    # only one element left => remove the -
    if(len(fields) == 2):
        fields[-1].remove(fields[-1].find("./span[@class='icon remove']"))
        fields[-2].remove(fields[-2].find("./span[@class='icon remove']"))
        
    htmlTree.remove(currentElement)
    
    # replace the bool of the first element by the 2 choices input (YES/NOT) if it was an element with 3 inputs (AND/OR/NOT)
    fields = htmlTree.findall("./p")
    if(len(fields[0][0].value_options) is not 2):
        if (fields[0][0].value == 'NOT'):
            fields[0][0] = html.fragment_fromstring(renderYESORNOT())
            fields[0][0].value = 'NOT'
        else:
            fields[0][0] = html.fragment_fromstring(renderYESORNOT())
        
    try:
        mapCriterias = request.session['mapCriteriasExplore']
        del mapCriterias[criteria_id]
        request.session['mapCriteriasExplore'] = mapCriterias
    except:
        pass

    response_dict = {'queryForm': html.tostring(htmlTree)}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

################################################################################
# 
# Function Name: renderYESORNOT()
# Inputs:        
# Outputs:       Yes or Not select string
# Exceptions:    None
# Description:   Returns a string that represents an html select with yes or not options
#
################################################################################
def renderYESORNOT():
    return """
    <select>
      <option value=""></option>
      <option value="NOT">NOT</option>
    </select> 
    """

################################################################################
# 
# Function Name: renderANDORNOT()
# Inputs:        
# Outputs:       AND OR NOT select string
# Exceptions:    None
# Description:   Returns a string that represents an html select with AND, OR, NOT options
#
################################################################################
def renderANDORNOT():
    return """
    <select>
      <option value="AND">AND</option>
      <option value="OR">OR</option>
      <option value="NOT">NOT</option>
    </select> 
    """

################################################################################
# 
# Function Name: renderNumericSelect()
# Inputs:        
# Outputs:       numeric select string
# Exceptions:    None
# Description:   Returns a string that represents an html select with numeric comparisons
#
################################################################################
def renderNumericSelect():
    return """
    <select style="width:70px">
      <option value="lt">&lt;</option>
      <option value="lte">&le;</option>
      <option value="=">=</option>
      <option value="gte">&ge;</option>
      <option value="gt">&gt;</option>
    </select> 
    """

################################################################################
# 
# Function Name: renderValueInput()
# Inputs:        
# Outputs:       input for a value
# Exceptions:    None
# Description:   Returns an input to type a value
#
################################################################################
def renderValueInput():
    return """
    <input style="margin-left:4px;" type="text" class="valueInput"/>
    """

################################################################################
# 
# Function Name: renderValueInput()
# Inputs:        
# Outputs:       input for a value
# Exceptions:    None
# Description:   Returns an input to type a value
#
################################################################################
def renderStringSelect():
    return """
    <select>
      <option value="is">is</option>
      <option value="like">like</option>                      
    </select> 
    """

################################################################################
# 
# Function Name: renderEnum()
# Inputs:        
# Outputs:       render an html select from an enumeration
# Exceptions:    None
# Description:   Returns html select from an enumeration
#
################################################################################
def renderEnum(request, fromElementID):
    enum = "<select class='selectInput'>"
    listOptions = request.session['mapEnumIDChoicesExplore'][str(fromElementID)]
    for option in listOptions:
        enum += "<option value='" + option + "'>" + option + "</option>"    
    enum += "</select>"
    return enum


################################################################################
# 
# Function Name: buildPrettyCriteria(elementName, comparison, value, isNot=False)
# Inputs:        elementName - 
#                comparison - 
#                value -
#                isNot - 
# Outputs:       render a criteria in a pretty form
# Exceptions:    None
# Description:   Returns a pretty representation of the criteria
#
################################################################################
def buildPrettyCriteria(elementName, comparison, value, isNot=False):
    prettyCriteria = ""
    
    if (isNot):
        prettyCriteria += "NOT("
        
    prettyCriteria += elementName
    if(comparison == "lt"):
        prettyCriteria += " &lt; "
    elif (comparison == "lte"):
        prettyCriteria += " &le; "
    elif (comparison == "="):
        prettyCriteria += "="
    elif (comparison == "gte"):
        prettyCriteria += " &ge; "
    elif (comparison == "gt"):
        prettyCriteria += " &gt; "
    elif (comparison == "is"):
        prettyCriteria += " is "
    elif (comparison == "like"):
        prettyCriteria += " like "
    
    if value == "":
        prettyCriteria += ' &ldquo;  &ldquo;'
    else:
        prettyCriteria += str(value)        
    
    if(isNot):
        prettyCriteria += ")"
    
    return prettyCriteria

################################################################################
# 
# Function Name: queryToPrettyCriteria(queryValue, isNot)
# Inputs:        queryValue - 
#                isNot - 
# Outputs:       render a query in a pretty form
# Exceptions:    None
# Description:   Returns a pretty representation of the query
#
################################################################################
def queryToPrettyCriteria(queryValue, isNot):
    if(isNot):
        return "NOT(" + queryValue + ")"
    else:
        return queryValue

################################################################################
# 
# Function Name: enumToPrettyCriteria(element, value, isNot=False)
# Inputs:        element - 
#                value - 
#                isNot - 
# Outputs:       render an enumeration value in a pretty form
# Exceptions:    None
# Description:   Returns a pretty representation of the enumeration value
#
################################################################################
def enumToPrettyCriteria(element, value, isNot=False):
    if(isNot):
        return "NOT(" + str(element) + " is " + str(value) + ")"
    else:
        return str(element) + " is " + str(value)

################################################################################
# 
# Function Name: ORPrettyCriteria(query, criteria)
# Inputs:        query - 
#                criteria - 
# Outputs:       render a OR in a pretty form
# Exceptions:    None
# Description:   Returns a pretty representation of the OR
#
################################################################################
def ORPrettyCriteria(query, criteria):
    return "(" + query + " OR " + criteria + ")"

################################################################################
# 
# Function Name: ANDPrettyCriteria(query, criteria)
# Inputs:        query - 
#                criteria - 
# Outputs:       render a AND in a pretty form
# Exceptions:    None
# Description:   Returns a pretty representation of the AND
#
################################################################################
def ANDPrettyCriteria(query, criteria):
    return "(" + query + " AND " + criteria + ")"

################################################################################
# 
# Function Name: fieldsToPrettyQuery(request, queryFormTree)
# Inputs:        request - 
#                queryFormTree - 
# Outputs:       
# Exceptions:    None
# Description:   Tranforms fields from the HTML form into pretty representation
#
################################################################################
def fieldsToPrettyQuery(request, queryFormTree):
    
    mapCriterias = request.session['mapCriteriasExplore']
    
    fields = queryFormTree.findall("./p")
    query = ""

    for field in fields:        
        boolComp = field[0].value
        if (boolComp == 'NOT'):
            isNot = True
        else:
            isNot = False
                
        criteriaInfo = eval(mapCriterias[field.attrib['id']])
        if criteriaInfo['elementInfo'] is None:
            elementInfo = None
        else:
            elementInfo = eval(criteriaInfo['elementInfo'])
        if criteriaInfo['queryInfo'] is None:
            queryInfo = None
        else:
            queryInfo = eval(criteriaInfo['queryInfo']) 
        elemType = elementInfo['type']
        if (elemType == "query"):
            queryValue = queryInfo['displayedQuery']
            criteria = queryToPrettyCriteria(queryValue, isNot)
        elif (elemType == "enum"):
            elementPath = elementInfo['path']
            element = elementPath.split('.')[-1]
            value = field[2][0].value            
            criteria = enumToPrettyCriteria(element, value, isNot)
        else:                 
            elementPath = elementInfo['path']
            element = elementPath.split('.')[-1]
            comparison = field[2][0].value
            value = field[2][1].value
            criteria = buildPrettyCriteria(element, comparison, value, isNot)
        
        if(boolComp == 'OR'):        
            query = ORPrettyCriteria(query, criteria)
        elif(boolComp == 'AND'):
            query = ANDPrettyCriteria(query, criteria)
        else:
            if(fields.index(field) == 0):
                query += criteria
            else:
                query = ANDPrettyCriteria(query, criteria)
        
    return query    

################################################################################
# 
# Function Name: save_query(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   save a query into mongo db and update the html display
#
################################################################################
def save_query(request):
    query_form = request.POST['queryForm']
    
    mapQueryInfo = request.session['mapQueryInfoExplore']
    queryFormTree = html.fromstring(query_form)

    # Check that the user can save a query
    errors = []
    if '_auth_user_id' in request.session:
        userID = request.session['_auth_user_id']
        if 'exploreCurrentTemplateID' in request.session:
            templateID = request.session['exploreCurrentTemplateID'] 
        else:
            errors = ['You have to select a template before you can save queries (Step 1 : Select Template).']
    else:
        errors = ['You have to login to save a query.']
    
    response_dict = {}
    if(len(errors)== 0): 
        # Check that the query is valid      
        errors = checkQueryForm(request, queryFormTree)
        if(len(errors)== 0):
            query = fieldsToQuery(request, queryFormTree)    
            displayedQuery = fieldsToPrettyQuery(request, queryFormTree) 
        
            #save the query in the data base
#             manageRegexBeforeSave(query)
            savedQuery = SavedQuery(str(userID),str(templateID), str(query),displayedQuery)
            savedQuery.save()
            
            queryInfo = QueryInfo(query, displayedQuery)
            mapQueryInfo[str(savedQuery.id)] = queryInfo.__to_json__()
            request.session['mapQueryInfoExplore'] = mapQueryInfo
        else:
            errorsString = ""
            for error in errors:
                errorsString += "<p>" + error + "</p>"  
            response_dict = {'listErrors': errorsString}
    else:
        errorsString = ""
        for error in errors:
            errorsString += "<p>" + error + "</p>"            
        response_dict = {'listErrors': errorsString}

    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: manageRegexBeforeSave(query)
# Inputs:        query
# Outputs:       
# Exceptions:    None
# Description:   Replaces the Regex objects before saving into mongo db
#
################################################################################
def manageRegexBeforeSave(query):
#     for key, value in query.iteritems():
#         if isinstance(value, dict):
#             manageRegexBeforeSave(value)
#         else:
#             if isinstance(value, re._pattern_type):
#                 query[key] = "re.compile(" + value.pattern + ")"
    for key, value in query.iteritems():
        if key == "$and" or key == "$or":
            for subValue in value:
                manageRegexBeforeSave(subValue)
        elif isinstance(value, re._pattern_type):
            query[key] = "/" + str(value.pattern) + "/"
        elif isinstance(value, dict):
            manageRegexBeforeSave(value)
#                 DictRegex[str(value).replace(".", "")] = value.pattern


################################################################################
# 
# Function Name: delete_query(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Deletes a query and update the HTML display
#
################################################################################
def delete_query(request):
    saved_query_id = request.POST['savedQueryID']
    SavedQuery(id=saved_query_id[5:]).delete()
    
    mapQueryInfo = request.session['mapQueryInfoExplore']
    del mapQueryInfo[saved_query_id[5:]]
    request.session['mapQueryInfoExplore'] = mapQueryInfo
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: update_user_inputs(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Update the user input of the query builder according to the type of the selected element
#
################################################################################  
def update_user_inputs(request):   
    html_form = request.POST['html'] 
    from_element_id = request.POST['fromElementID']
    criteria_id = request.POST['criteriaID']
    
    mapTagIDElementInfo = request.session['mapTagIDElementInfoExplore']
    mapCriterias = request.session['mapCriteriasExplore']
    defaultPrefix = request.session['defaultPrefixExplore']
    
    toCriteriaID = "crit" + str(criteria_id)
    
    criteriaInfo = CriteriaInfo()
    criteriaInfo.elementInfo = ElementInfo(path=eval(mapTagIDElementInfo[str(from_element_id)])['path'], type=eval(mapTagIDElementInfo[str(from_element_id)])['type'])
    mapCriterias[toCriteriaID] = criteriaInfo.__to_json__()
    request.session['mapCriteriasExplore'] = mapCriterias
    
    htmlTree = html.fromstring(html_form)
    currentCriteria = htmlTree.get_element_by_id(toCriteriaID)  
    
    try:
        currentCriteria[1].attrib['class'] = currentCriteria[1].attrib['class'].replace('queryInput','elementInput') 
    except:
        pass
    
    # criteria id = crit%d  
    criteriaIDIncr = toCriteriaID[4:]
    userInputs = currentCriteria.find("./span/[@id='ui"+ str(criteriaIDIncr) +"']")
    
    for element in userInputs.findall("*"):
        userInputs.remove(element) 
    
    if (criteriaInfo.elementInfo.type in ["{0}:byte".format(defaultPrefix),
                                            "{0}:decimal".format(defaultPrefix),
                                            "{0}:int".format(defaultPrefix),
                                            "{0}:integer".format(defaultPrefix),
                                            "{0}:long".format(defaultPrefix),
                                            "{0}:negativeInteger".format(defaultPrefix),
                                            "{0}:nonNegativeInteger".format(defaultPrefix),
                                            "{0}:nonPositiveInteger".format(defaultPrefix),
                                            "{0}:positiveInteger".format(defaultPrefix), 
                                            "{0}:short".format(defaultPrefix), 
                                            "{0}:unsignedLong".format(defaultPrefix), 
                                            "{0}:unsignedInt".format(defaultPrefix), 
                                            "{0}:unsignedShort".format(defaultPrefix), 
                                            "{0}:unsignedByte".format(defaultPrefix),
                                            "{0}:double".format(defaultPrefix),
                                            "{0}:float".format(defaultPrefix)]):
        form = html.fragment_fromstring(renderNumericSelect())
        inputs = html.fragment_fromstring(renderValueInput()) 
        userInputs.append(form)
        userInputs.append(inputs) 
    elif (criteriaInfo.elementInfo.type == "enum"):
        form = html.fragment_fromstring(renderEnum(request, from_element_id))
        userInputs.append(form)
    else:
        form = html.fragment_fromstring(renderStringSelect())
        inputs = html.fragment_fromstring(renderValueInput())
        userInputs.append(form)
        userInputs.append(inputs)
        
    response_dict = {'queryForm': html.tostring(htmlTree)}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    
    
################################################################################
# 
# Function Name: add_saved_query_to_form(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Adds the selected query to query builder
#
################################################################################ 
def add_saved_query_to_form(request):
    query_form = request.POST['queryForm']
    saved_query_id = request.POST['savedQueryID']
    
    
    mapQueryInfo = request.session['mapQueryInfoExplore']
    queryTree = html.fromstring(query_form)
    
    fields = queryTree.findall("./p")
    fields[-1].remove(fields[-1].find("./span[@class='icon add']"))      
    if (len(fields) == 1):
        criteriaID = fields[0].attrib['id']
        minusButton = html.fragment_fromstring("""<span class="icon remove" onclick="removeField('""" + str(criteriaID) +"""')"></span>""")
        fields[0].append(minusButton)
        
    lastID = fields[-1].attrib['id'][4:]
    queryInfo = eval(mapQueryInfo[saved_query_id[5:]])
    query = queryInfo['displayedQuery']
    if (len(fields)== 1 and fields[0][1].value == ""):
        queryTree.remove(fields[0])
        tagID = int(lastID)
        element = html.fragment_fromstring("""
        <p id='crit""" + str(tagID) + """'>
        """
        +
            renderYESORNOT() 
        +
        """
            <input onclick="showCustomTree('crit""" + str(tagID) + """')" readonly="readonly" type="text" class="queryInput" value=" """+ str(query) +""" ">     
            <span id="ui"""+ str(tagID) +"""">
            </span>              
            <span class="icon add" onclick=addField()> </span>
        </p>
        """)
    else:
        tagID = int(lastID) + 1
        element = html.fragment_fromstring("""
            <p id='crit""" + str(tagID) + """'>
            """
            +
                renderANDORNOT() 
            +
            """
                <input onclick="showCustomTree('crit""" + str(tagID) + """')" readonly="readonly" type="text" class="queryInput" value=" """+ str(query) +""" ">     
                <span id="ui"""+ str(tagID) +"""">
                </span>  
                <span class="icon remove" onclick="removeField('crit"""+ str(tagID) +"""')"></span>
                <span class="icon add" onclick="addField()"> </span>
            </p>
        """)  

    #insert before the 3 buttons (save, clear, execute)
    queryTree.insert(-3,element)
    
    mapCriterias = request.session['mapCriteriasExplore']
    criteriaInfo = CriteriaInfo()
    criteriaInfo.queryInfo = QueryInfo(query=eval(mapQueryInfo[saved_query_id[5:]])['query'], displayedQuery=eval(mapQueryInfo[saved_query_id[5:]])['displayedQuery'])
    criteriaInfo.elementInfo = ElementInfo("query")
    mapCriterias['crit'+ str(tagID)] = criteriaInfo.__to_json__() 
    request.session['mapCriteriasExplore'] = mapCriterias

    response_dict = {'queryForm': html.tostring(queryTree)}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    
    
################################################################################
# 
# Function Name: renderInitialForm()
# Inputs:        
# Outputs:       
# Exceptions:    None
# Description:   Renders the initial Query Builder
#
################################################################################ 
def renderInitialForm():
    return """
    <p id="crit0">
        <select>
          <option value=""></option>
          <option value="NOT">NOT</option>
        </select> 
        <input onclick="showCustomTree('crit0')" readonly="readonly" type="text" class="elementInput"/>
        <span id="ui0">
        </span>                        
        <span class="icon add" onclick="addField()"></span>                                
    </p>
    """

################################################################################
# 
# Function Name: clear_criterias(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Clears the Query Builder
#
################################################################################ 
def clear_criterias(request):
    """ Reset Saved Criterias """
    
    query_form = request.POST['queryForm']
    
    # Load the criterias tree     
    queryTree = html.fromstring(query_form)
    
    fields = queryTree.findall("./p")
    for field in fields:
        queryTree.remove(field)
    
    initialForm = html.fragment_fromstring(renderInitialForm())
    queryTree.insert(0,initialForm)  
    
    request.session['mapCriteriasExplore'] = dict()

    response_dict = {'queryForm': html.tostring(queryTree)}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: clear_queries(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Delete all saved queries
#
################################################################################ 
def clear_queries(request):
    """ Reset Saved Queries """
    
    mapQueryInfo = request.session['mapQueryInfoExplore']
       
    for queryID in mapQueryInfo.keys():
        SavedQuery(id=queryID).delete()
            
    request.session['mapQueryInfoExplore'] = dict()
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: manageRegexFromDB(query)
# Inputs:        query - 
# Outputs:       
# Exceptions:    None
# Description:   Restore Regex from Mongo db
#
################################################################################ 
def manageRegexFromDB(query):
    for key, value in query.iteritems():
        if key == "$and" or key == "$or":
            for subValue in value:
                manageRegexFromDB(subValue)
        elif isinstance(value, str):
            if (len(value) >= 2 and value[0] == "/" and value[-1] == "/"):
                query[key] = re.compile(value[1:-1])
        elif isinstance(value, dict):
            manageRegexFromDB(value)


################################################################################
# 
# Function Name: get_custom_form(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Get the form customized by the user to select the fields
#
################################################################################ 
def get_custom_form(request):
    if 'savedQueryFormExplore' in request.session:
        savedQueryForm = request.session['savedQueryFormExplore']
    else:
        savedQueryForm = ""
    customFormString = request.session['customFormStringExplore']
    
    response_dict = {}
    #delete criterias if user comes from another page than results
    if 'keepCriterias' in request.session:
        del request.session['keepCriterias']
        if savedQueryForm != "" :
            response_dict['queryForm'] = savedQueryForm
            request.session['savedQueryFormExplore'] = ""
    else:
        request.session['mapCriteriasExplore'] = dict()
    
    #Get saved queries of an user
    mapQueryInfo = dict()
    request.session['mapQueryInfoExplore'] = dict()
    if '_auth_user_id' in request.session and 'exploreCurrentTemplateID' in request.session:
        userID = request.session['_auth_user_id']
        templateID = request.session['exploreCurrentTemplateID']
        userQueries = SavedQuery.objects(user=str(userID),template=str(templateID))
        for savedQuery in userQueries:
            query = eval(savedQuery.query)
#            manageRegexFromDB(query)     
            queryInfo = QueryInfo(query, savedQuery.displayedQuery)
            mapQueryInfo[str(savedQuery.id)] = queryInfo.__to_json__()
            request.session['mapQueryInfoExplore'] = mapQueryInfo
            
        
    if (customFormString != ""):
        if 'currentExploreTab' in request.session and request.session['currentExploreTab'] == "tab-1":
            customForm = customFormString
        elif 'currentExploreTab' in request.session and request.session['currentExploreTab'] == "tab-2":
            customForm = ""
    else:
        customFormErrorMsg = "<p style='color:red;'>You should customize the template first. <a href='/explore/customize-template' style='color:red;font-weight:bold;'>Go back to Step 2 </a> and select the elements that you want to use in your queries.</p>"
        customForm = customFormErrorMsg
    
    response_dict['customForm'] = customForm

    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: save_custom_data(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Saves the custom template with fields selected by the user
#                
#
################################################################################
def save_custom_data(request):
    print '>>>>  BEGIN def saveCustomData(request)'
    
    form_content = request.POST['formContent']
    request.session['formStringExplore']  = form_content

    # modify the form string to only keep the selected elements
    htmlTree = html.fromstring(form_content)
    createCustomTreeForQuery(request, htmlTree)
    anyChecked = request.session['anyCheckedExplore']
    if (anyChecked):
        request.session['customFormStringExplore'] = html.tostring(htmlTree)
    else:
        request.session['customFormStringExplore'] = ""
    
    request.session['anyCheckedExplore'] = False 

    print '>>>> END def saveCustomData(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')

################################################################################
#
# Function Name: createCustomTreeForQuery(request,htmlTree)
# Inputs:        request - 
#                htmlTree - 
# Outputs:       
# Exceptions:    None
# Description:   Creates a custom HTML tree from fields chosen by the user
#                
#
################################################################################
def createCustomTreeForQuery(request, htmlTree):
    request.session['anyCheckedExplore'] = False
    for li in htmlTree.findall("./ul/li"):
        manageLiForQuery(request, li)

################################################################################
#
# Function Name: manageUlForQuery(request, ul)
# Inputs:        request - 
#                ul - 
# Outputs:       
# Exceptions:    None
# Description:   Process the ul element of an HTML list
#                
################################################################################
def manageUlForQuery(request, ul):
    branchInfo = BranchInfo(keepTheBranch = False, selectedLeave = None)

    selectedLeaves = []
    for li in ul.findall("./li"):
        liBranchInfo = manageLiForQuery(request, li)
        if(liBranchInfo.keepTheBranch == True):
            branchInfo.keepTheBranch = True
        if (liBranchInfo.selectedLeave is not None):
            selectedLeaves.append(liBranchInfo.selectedLeave)
            branchInfo.selectedLeave = liBranchInfo.selectedLeave
    
    # ul can contain ul, because XSD allows recursive sequence or sequence with choices
    for ul in ul.findall("./ul"):
        ulBranchInfo = manageUlForQuery(request, ul)
        if(ulBranchInfo.keepTheBranch == True):
            branchInfo.keepTheBranch = True
        if (ulBranchInfo.selectedLeave is not None):
            if branchInfo.selectedLeave is None:
                branchInfo.selectedLeave = []
            branchInfo.selectedLeave.append(ulBranchInfo.selectedLeave)
                
    if(not branchInfo.keepTheBranch):
        ul.attrib['style'] = "display:none;"
        
    return branchInfo


################################################################################
#
# Function Name: manageLiForQuery(request, li)
# Inputs:        request - 
#                li - 
# Outputs:       
# Exceptions:    None
# Description:   Process the li element of an HTML list
#                
################################################################################
def manageLiForQuery(request, li):
    listUl = li.findall("./ul")
    branchInfo = BranchInfo(keepTheBranch = False, selectedLeave = None)
    if (len(listUl) != 0):
        selectedLeaves = []
        for ul in listUl:
            ulBranchInfo = manageUlForQuery(request, ul)
            if(ulBranchInfo.keepTheBranch == True):
                branchInfo.keepTheBranch = True
            if(ulBranchInfo.selectedLeave is not None):
                selectedLeaves.extend(ulBranchInfo.selectedLeave)
        # subelement queries
        if len(selectedLeaves) > 1: # starting at 2 because 1 is the regular case
            li.attrib['style'] = "color:purple;font-weight:bold;cursor:pointer;"
            leavesID = ""
            for leave in selectedLeaves[:-1]:
                leavesID += leave + " "
            leavesID += selectedLeaves[-1]
    #         parent.attrib['onclick'] = "selectParent('"+ leavesID +"')"
            li.insert(0, html.fragment_fromstring("""<span onclick="selectParent('"""+ leavesID +"""')">"""+ li.text +"""</span>"""))
            li.text = ""
        if(not branchInfo.keepTheBranch):
            li.attrib['style'] = "display:none;"
        return branchInfo
    else:
        try:
            checkbox = li.find("./input[@type='checkbox']")
            if(checkbox.attrib['value'] == 'false'):
                li.attrib['style'] = "display:none;"
                return branchInfo
            else:
                request.session['anyCheckedExplore'] = True
                # remove the checkbox and make the element clickable
                li.attrib['style'] = "color:orange;font-weight:bold;cursor:pointer;"
                li.attrib['onclick'] = "selectElement("+ li.attrib['id'] +")"
                checkbox.attrib['style'] = "display:none;"   
                # tells to keep this branch until this leave
                branchInfo.keepTheBranch = True
                branchInfo.selectedLeave = li.attrib['id']          
                return branchInfo
        except:
            return branchInfo
  

################################################################################
#
# Function Name: back_to_query(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Allows to come back to the query definition keeping the criterias
#                
################################################################################
def back_to_query(request):         
    request.session['keepCriterias'] = True
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: redirect_explore(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Switch tab
#                
################################################################################
def redirect_explore(request):
    request.session['currentExploreTab'] = "tab-2"


################################################################################
#
# Function Name: redirectExploreTabs(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Switch tab
#                
################################################################################
def redirect_explore_tabs(request):
    if 'currentExploreTab' in request.session and request.session['currentExploreTab'] == "tab-2":
        response_dict = {'tab':'tab-2'}
    else:
        response_dict = {'tab':'tab-1'}
     
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: redirectExploreTabs(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Switch tab and clears/sets custom forms
#                
################################################################################
def switch_explore_tab(request):    
    request.session["currentExploreTab"] = request.POST['tab']
    customForm = ""
    
    if 'customFormStringExplore' in request.session:   
        customFormString = request.session['customFormStringExplore']
    else:
        customFormString = ""
    
    if (customFormString != ""):
        if 'currentExploreTab' in request.session and request.session['currentExploreTab'] == "tab-1":
            customForm = customFormString
        elif 'currentExploreTab' in request.session and request.session['currentExploreTab'] == "tab-2":
            customForm = ""
    
    response_dict = {"customForm": customForm}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: set_current_criteria(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Set the id of the criteria that is currently set
#                
################################################################################
def set_current_criteria(request):
    
    request.session['criteriaIDExplore'] = request.POST['currentCriteriaID']
    return HttpResponse(json.dumps({}), content_type='application/javascript')
    

################################################################################
#
# Function Name: select_element(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Select an element from the Get Element feature of the SPARQL endpoint
#                
################################################################################
def select_element(request):
    
    element_id = request.POST['elementID']
    element_name = request.POST['elementName']
    
    if 'currentExploreTab' in request.session and request.session['currentExploreTab'] == "tab-1":
        criteria_id = request.session['criteriaIDExplore']  
        response_dict = {"tab": "tab-1", 
                         "criteriaTagID": criteria_id,
                         "criteriaID": str(criteria_id[4:])}  
        
        request.session['criteriaIDExplore'] = ""
    elif 'currentExploreTab' in request.session and request.session['currentExploreTab'] == "tab-2":
        mapTagIDElementInfo = request.session['mapTagIDElementInfoExplore']
        elementPath = eval(mapTagIDElementInfo[str(element_id)])['path']
        response_dict = {"tab": "tab-2", 
                         "elementPath": elementPath} 

    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: prepare_sub_element_query(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Build the form for queries on a same subelement 
#                
################################################################################
def prepare_sub_element_query(request):
    print '>>>>  BEGIN def prepareSubElementQuery(request)'

    leaves_id = request.GET['leavesID']    
    mapTagIDElementInfo =  request.session['mapTagIDElementInfoExplore']
    
    defaultPrefix = request.session['defaultPrefixExplore']
    
    listLeavesId = leaves_id.split(" ")
    firstElementPath = eval(mapTagIDElementInfo[str(listLeavesId[0])])['path']
    parentPath = ".".join(firstElementPath.split(".")[:-1])
    parentName = parentPath.split(".")[-1]
    
    subElementQueryBuilderStr = "<p><b>" +parentName+ "</b></p>"
    subElementQueryBuilderStr += "<ul>"
    for leaveID in listLeavesId:
        elementInfo = ElementInfo(path=eval(mapTagIDElementInfo[str(leaveID)])['path'], type=eval(mapTagIDElementInfo[str(leaveID)])['type'])
        elementName = elementInfo.path.split(".")[-1]
        subElementQueryBuilderStr += "<li><input type='checkbox' style='margin-right:4px;margin-left:2px;' checked/>"
        subElementQueryBuilderStr += renderYESORNOT()
        subElementQueryBuilderStr += elementName + ": "
        if (elementInfo.type in ["{0}:byte".format(defaultPrefix),
                                            "{0}:decimal".format(defaultPrefix),
                                            "{0}:int".format(defaultPrefix),
                                            "{0}:integer".format(defaultPrefix),
                                            "{0}:long".format(defaultPrefix),
                                            "{0}:negativeInteger".format(defaultPrefix),
                                            "{0}:nonNegativeInteger".format(defaultPrefix),
                                            "{0}:nonPositiveInteger".format(defaultPrefix),
                                            "{0}:positiveInteger".format(defaultPrefix), 
                                            "{0}:short".format(defaultPrefix), 
                                            "{0}:unsignedLong".format(defaultPrefix), 
                                            "{0}:unsignedInt".format(defaultPrefix), 
                                            "{0}:unsignedShort".format(defaultPrefix), 
                                            "{0}:unsignedByte".format(defaultPrefix),
                                            "{0}:double".format(defaultPrefix),
                                            "{0}:float".format(defaultPrefix)]):
            subElementQueryBuilderStr += renderNumericSelect()
            subElementQueryBuilderStr += renderValueInput()
        elif (elementInfo.type == "enum"):
            subElementQueryBuilderStr += renderEnum(request, leaveID)
        else:
            subElementQueryBuilderStr += renderStringSelect()
            subElementQueryBuilderStr += renderValueInput()
        subElementQueryBuilderStr += "</li><br/>"
    subElementQueryBuilderStr += "</ul>"
    
    print '>>>>  END def prepareSubElementQuery(request)'
    response_dict = {'subElementQueryBuilder': subElementQueryBuilderStr}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: insert_sub_element_query(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Inserts a query for a sub element in the query builder  
#                
################################################################################
def insert_sub_element_query(request):
    print '>>>>  BEGIN def insertSubElementQuery(request)'
    
    form = request.POST['form']
    leaves_id = request.POST['leavesID']
    
    mapTagIDElementInfo = request.session['mapTagIDElementInfoExplore'] 
    
    mapCriterias = request.session['mapCriteriasExplore']
    criteriaID = request.session['criteriaIDExplore']
    
    htmlTree = html.fromstring(form)
    listLi = htmlTree.findall("ul/li")
    listLeavesId = leaves_id.split(" ")
    
    i = 0
    nbSelected = 0
    errors = []
    for li in listLi:
        if (li[0].attrib['value'] == 'true'):
            nbSelected += 1            
            elementInfo = ElementInfo(path=eval(mapTagIDElementInfo[str(listLeavesId[i])])['path'], type=eval(mapTagIDElementInfo[str(listLeavesId[i])])['type'])
            elementName = elementInfo.path.split(".")[-1]
            elementType = elementInfo.type
            error = checkSubElementField(request, li, elementName, elementType)
            if (error != ""):
                errors.append(error)
        i += 1
    
    if (nbSelected < 2):
        errors = ["Please select at least two elements."]
    
    if(len(errors) == 0):
        query = subElementfieldsToQuery(request, listLi, listLeavesId)
        prettyQuery = subElementfieldsToPrettyQuery(request, listLi, listLeavesId)
        criteriaInfo = CriteriaInfo()
        criteriaInfo.queryInfo = QueryInfo(query, prettyQuery)
        criteriaInfo.elementInfo = ElementInfo("query")
        mapCriterias[criteriaID] = criteriaInfo.__to_json__()
        request.session['mapCriteriasExplore'] = mapCriterias
        uiID = "ui" + criteriaID[4:]
        response_dict = {'criteriaID': criteriaID,
                         'prettyQuery': prettyQuery,
                         'uiID': uiID}    
    else:
        errorsString = ""
        for error in errors:
            errorsString += "<p>" + error + "</p>"
        response_dict = {'listErrors': errorsString}            
            
    
    print '>>>>  END def insertSubElementQuery(request)'
    
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

################################################################################
#
# Function Name: checkSubElementField(request, liElement, elementName, elementType)
# Inputs:        request -
#                liElement -
#                elementName - 
#                elementType - 
# Outputs:       
# Exceptions:    None
# Description:   Checks that the fields of the subelement query are of the good type
#                
################################################################################
def checkSubElementField(request, liElement, elementName, elementType):   
    error = ""
    defaultPrefix = request.session['defaultPrefixExplore']
    
    if (elementType in ['{0}:float'.format(defaultPrefix), 
                       '{0}:double'.format(defaultPrefix),
                       '{0}:decimal'.format(defaultPrefix)]):
        value = liElement[3].value
        try:
            float(value)
        except ValueError:
            error = elementName + " must be a number !"
                
    elif (elementType in ['{0}:byte'.format(defaultPrefix),
                     '{0}:int'.format(defaultPrefix),
                     '{0}:integer'.format(defaultPrefix),
                     '{0}:long'.format(defaultPrefix),
                     '{0}:negativeInteger'.format(defaultPrefix),
                     '{0}:nonNegativeInteger'.format(defaultPrefix),
                     '{0}:nonPositiveInteger'.format(defaultPrefix),
                     '{0}:positiveInteger'.format(defaultPrefix),
                     '{0}:short'.format(defaultPrefix),
                     '{0}:unsignedLong'.format(defaultPrefix),
                     '{0}:unsignedInt'.format(defaultPrefix),
                     '{0}:unsignedShort'.format(defaultPrefix),
                     '{0}:unsignedByte'.format(defaultPrefix)]):
        value = liElement[3].value
        try:
            int(value)
        except ValueError:
            error = elementName + " must be an integer !"
            
    elif (elementType == "{0}:string".format(defaultPrefix)):
        comparison = liElement[2].value
        value = liElement[3].value
        if (comparison == "like"):
            try:
                re.compile(value)
            except Exception, e:
                error = elementName + " must be a valid regular expression ! (" + str(e) + ")"    

    return error

################################################################################
#
# Function Name: subElementfieldsToQuery(request, liElement, listLeavesId)
# Inputs:        request -
#                liElement -
#                listLeavesId - 
# Outputs:       
# Exceptions:    None
# Description:   Tranforms HTML fields in a subelement query for mongo db
#                
################################################################################
def subElementfieldsToQuery(request, liElements, listLeavesId):
    
    mapTagIDElementInfo = request.session['mapTagIDElementInfoExplore'] 
    elemMatch = dict()
    i = 0
    
    firstElementPath = eval(mapTagIDElementInfo[str(listLeavesId[i])])['path']
    parentPath = "content." + ".".join(firstElementPath.split(".")[:-1])
    
    for li in liElements:        
        if (li[0].attrib['value'] == 'true'):
            boolComp = li[1].value
            if (boolComp == 'NOT'):
                isNot = True
            else:
                isNot = False
                
            elementInfo = ElementInfo(path=eval(mapTagIDElementInfo[str(listLeavesId[i])])['path'], type=eval(mapTagIDElementInfo[str(listLeavesId[i])])['type'])
            elementType = elementInfo.type
            elementName = elementInfo.path.split(".")[-1]
            if (elementType == "enum"):
                value = li[2].value            
                criteria = enumCriteria(elementName, value, isNot)
            else:                
                comparison = li[2].value
                value = li[3].value
                criteria = buildCriteria(request, elementName, comparison, value, elementType , isNot)
             
        
            elemMatch.update(criteria)
                
        i += 1
         
    query = dict()
    query[parentPath] = dict()
    query[parentPath]["$elemMatch"] = elemMatch
    
    
    return query

################################################################################
#
# Function Name: subElementfieldsToQuery(request, liElement, listLeavesId)
# Inputs:        request -
#                liElement -
#                listLeavesId - 
# Outputs:       
# Exceptions:    None
# Description:   Tranforms HTML fields in a pretty subelement query
#                
################################################################################
def subElementfieldsToPrettyQuery(request, liElements, listLeavesId):
    mapTagIDElementInfo = request.session['mapTagIDElementInfoExplore'] 
    
    query = ""
    
    elemMatch = "("
    i = 0
    
    for li in liElements:        
        if (li[0].attrib['value'] == 'true'):
            boolComp = li[1].value
            if (boolComp == 'NOT'):
                isNot = True
            else:
                isNot = False
                
            elementInfo = ElementInfo(path=eval(mapTagIDElementInfo[str(listLeavesId[i])])['path'], type=eval(mapTagIDElementInfo[str(listLeavesId[i])])['type'])
            elementType = elementInfo.type
            elementName = elementInfo.path.split(".")[-1]
            if (elementType == "enum"):
                value = li[2].value
                criteria = enumToPrettyCriteria(elementName, value, isNot)
            else:                 
                comparison = li[2].value
                value = li[3].value
                criteria = buildPrettyCriteria(elementName, comparison, value, isNot)
            
            if (elemMatch != "("):
                elemMatch += ", "
            elemMatch += criteria       
        i += 1
        
    elemMatch += ")"
    firstElementPath = eval(mapTagIDElementInfo[str(listLeavesId[0])])['path']
    parentName = firstElementPath.split(".")[-2]
    
    query =  parentName + elemMatch
        
    return query 


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
        if request.user.is_superuser:
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
# Function Name: update_publish(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Publish and update the publish date of an XMLdata
#
################################################################################
def update_publish(request):
    XMLdata.update_publish(request.GET['result_id'])
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
# Function Name: load_refinements(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Load refinements criterias from selected schemas
#                
################################################################################
def load_refinements(request):
    schema_name = request.GET['schema']    
    schemas = Template.objects(title=schema_name)
    schema_id = TemplateVersion.objects().get(pk=schemas[0].templateVersion).current
    
    schema = Template.objects().get(pk=schema_id)
    
    xmlDocTree = etree.parse(BytesIO(schema.content.encode('utf-8')))
    
    # find the namespaces
    namespaces = common.get_namespaces(BytesIO(schema.content.encode('utf-8')))
    default_namespace = "{http://www.w3.org/2001/XMLSchema}"
    for prefix, url in namespaces.items():
        if (url == default_namespace):            
            defaultPrefix = prefix
            break
    
    # building refinement options based on the schema
    refinement_options = "<a onclick='clearRefinements();' style='cursor:pointer;'>Clear Refinements</a> <br/><br/>"
    
    # TODO: change enumeration look up by something more generic (using annotations in the schema)
    # looking for enumerations
    simple_types = xmlDocTree.findall("./{0}simpleType".format(default_namespace))
    for simple_type in simple_types:
        try:
            enums = simple_type.findall("./{0}restriction/{0}enumeration".format(default_namespace))
            refinement = ""
            if len(enums) > 0:
                # build dot notation query
                # find the element using the enumeration            
                element = xmlDocTree.findall(".//{0}element[@type='{1}']".format(default_namespace, simple_type.attrib['name']))
                if len(element) > 1:
                    print "error: more than one element using the enumeration (" +str(len(element)) +")"
                else:
                    element = element[0]
                    
                    # get the label of refinements
                    app_info = common.getAppInfo(element, default_namespace)
                    label = app_info['label'] if 'label' in app_info else element.attrib['name']
                    label = label if label is not None else ''
                    query = []
                    while element is not None:
                        if element.tag == "{0}element".format(default_namespace):
                            query.insert(0,element.attrib['name'])
                        elif element.tag == "{0}simpleType".format(default_namespace):
                            element = xmlDocTree.findall(".//{0}element[@type='{1}']".format(default_namespace, element.attrib['name']))
                            if len(element) > 1:
                                print "error: more than one element using the enumeration (" +str(len(element)) +")"
                            else:
                                element = element[0]
                                query.insert(0,element.attrib['name'])
                        elif element.tag == "{0}complexType".format(default_namespace):
                            element = xmlDocTree.findall(".//{0}element[@type='{1}']".format(default_namespace, element.attrib['name']))
                            if len(element) > 1:
                                print "error: more than one element using the enumeration (" +str(len(element)) +")"
                            else:
                                element = element[0]
                                query.insert(0,element.attrib['name'])
                        element = element.getparent()            
                
                dot_query = ".".join(query)
                dot_query = "content." + dot_query
                
                # get the name of the enumeration
                refinement += "<div class='refine_criteria' query='" + dot_query + "'>" + label + ": <br/>"
                for enum in sorted(enums, key=lambda x: x.attrib['value']):
                    refinement += "<input type='checkbox' value='" + enum.attrib['value'] + "' onchange='get_results_keyword_refined();'> " + enum.attrib['value'].title() + "<br/>"
                refinement += "<br/>"
                refinement += "</div>"
        except:
            print "ERROR AUTO GENERATION OF REFINEMENTS."
        refinement_options += refinement
    
    return HttpResponse(json.dumps({'refinements': refinement_options}), content_type='application/javascript')
    
################################################################################
#
# Function Name: refinements_to_mongo(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Build a refined mongo query (AND between types + OR between values of the same type) 
#                
################################################################################
def refinements_to_mongo(refinements):
    try:
        # transform the refinement in mongo query
        mongo_queries = dict()
        mongo_in = {}
        for refinement in refinements:
            splited_refinement = refinement.split(':')
            dot_notation = splited_refinement[0]
            value = splited_refinement[1]
            if dot_notation in mongo_queries:
                mongo_queries[dot_notation].append(value)
            else:
                mongo_queries[dot_notation] = [value]

        for query in mongo_queries:
            key = query
            values = ({ '$in' : mongo_queries[query]})
            mongo_in[key] = values

        mongo_or = {'$and' : [mongo_in]}
        return mongo_or
    except:
        return []
        


################################################################################
#
# Function Name: custom_view(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Build Custom View
#                
################################################################################
def custom_view(request):
    schema_name = request.GET['schema']
    
    schema = Template.objects().get(title=schema_name)
    
    xmlDocTree = etree.parse(BytesIO(schema.content.encode('utf-8')))
    
    # find the namespaces
    namespaces = common.get_namespaces(BytesIO(schema.content.encode('utf-8')))
    default_namespace = "{http://www.w3.org/2001/XMLSchema}"
    for prefix, url in namespaces.items():
        if (url == default_namespace):            
            defaultPrefix = prefix
            break
    
    # building custom fields based on the schema
    custom_fields = ""
        
    # look for elements
    elements = xmlDocTree.findall(".//{0}element".format(default_namespace))
    added_element_names = []
    for element in elements:
        if element.attrib['name'] not in added_element_names:
            added_element_names.append(element.attrib['name'])
            if is_field(element, xmlDocTree, default_namespace, defaultPrefix):   
                app_info = common.getAppInfo(element, default_namespace)
                label = app_info['label'] if 'label' in app_info else element.attrib['name']
                label = label if label is not None else ''
                value = 'line_' + element.attrib['name']
                custom_fields += "<input type='checkbox' value='" + value + "'> " + label + "<br/>"
    
    # look for attributes
    attributes = xmlDocTree.findall(".//{0}attribute".format(default_namespace))
    added_attribute_names = []
    for attribute in attributes:
        if attribute.attrib['name'] not in added_attribute_names:
            added_attribute_names.append(attribute.attrib['name'])
            if is_field(attribute, xmlDocTree, default_namespace, defaultPrefix):   
                app_info = common.getAppInfo(attribute, default_namespace)
                label = app_info['label'] if 'label' in app_info else attribute.attrib['name']
                label = label if label is not None else ''
                value = 'line_' + attribute.attrib['name']
                custom_fields += "<input type='checkbox' value='" + value + "'> " + label + "<br/>"
    
    return HttpResponse(json.dumps({'custom_fields': custom_fields}), content_type='application/javascript')


################################################################################
#
# Function Name: is_field(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Look if the element is a field, and not a node
#                
################################################################################
def is_field(element, xmlDocTree, default_namespace, defaultPrefix):
    # the element has a type
    if 'type' in element.attrib:
        # the element's type i
        if element.attrib['type'] in common.getXSDTypes(defaultPrefix):
            return True
        else:
            simple_type = xmlDocTree.find(".//{0}simpleType[@name='{1}']".format(default_namespace, element.attrib['type']))
            if simple_type is not None:
                return True
            else:
                complex_type = xmlDocTree.find(".//{0}complexType[@name='{1}']".format(default_namespace, element.attrib['type']))
                if complex_type is not None:
                    simple_content = complex_type.find("./{0}simpleContent".format(default_namespace))
                    if simple_content is not None:
                        return True
    else:
        simple_type = xmlDocTree.find("./{0}simpleType".format(default_namespace))
        if simple_type is not None:
            return True
        else:
            complex_type = xmlDocTree.find(".//{0}complexType".format(default_namespace))
            if complex_type is not None:
                simple_content = complex_type.find("./{0}simpleContent".format(default_namespace))
                if simple_content is not None:
                    return True
    return False
    