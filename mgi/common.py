
import lxml.etree as etree
from mgi.models import MetaSchema, Template
from cStringIO import StringIO

################################################################################
# 
# Function Name: checkValidForMDCS(xmlTree, type)
# Inputs:        request - 
#                xmlTree - 
#                type - 
# Outputs:       errors
# Exceptions:    None
# Description:   Check that the format of the the schema is supported by the current version of the MDCS
# 
################################################################################
def getValidityErrorsForMDCS(xmlTree, type):
    errors = []
    
    # General Tests
    
    # get the imports
    imports = xmlTree.findall("{http://www.w3.org/2001/XMLSchema}import")
    # get the includes
    includes = xmlTree.findall("{http://www.w3.org/2001/XMLSchema}include")
    # get the elements
    elements = xmlTree.findall("{http://www.w3.org/2001/XMLSchema}element")
    
    if len(imports) != 0 or len(includes) != 0:
        # V1: Only includes        
        if len(imports) != 0:
            errors.append("Import statements are not supported.")
        else:
            for el_include in includes:
                if 'schemaLocation' not in el_include.attrib:
                    errors.append("The attribute schemaLocation of include is required but missing.")
                elif ' ' in el_include.attrib['schemaLocation']:
                    errors.append("The use of namespace in include elements is not supported.")

    # Templates Tests

    if type == "Template":
        # Tests for templates
        if len(elements) < 1 :
            errors.append("Only templates with at least one root element are supported.")

    # Types Tests
    
    elif type == "Type":        
        elements = xmlTree.findall("*")
        # only simpleType, complexType or include
        for element in elements:
            if 'complexType' not in element.tag and 'simpleType' not in element.tag and 'include' not in element.tag:
                errors.append("A type should be a valid XML schema containing only one type definition (Allowed tags are: simpleType or complexType and include).")
                break
        # only one type
        for element in elements:
            cptType = 0 
            if 'complexType' in element.tag or 'simpleType' in element.tag:
                cptType += 1
                if cptType > 1:
                    errors.append("A type should be a valid XML schema containing only one type definition (only one simpleType or complexType).")
                    break

    return errors


################################################################################
#
# Function Name: validateXMLDocument(templateID, xmlString)
# Inputs:        request - 
#                templateID - 
#                xmlString - 
# Outputs:       
# Exceptions:    None
# Description:   Check that the XML document is validated by the template
#                
#
################################################################################
def validateXMLDocument(templateID, xmlString):
    
    if str(templateID) in MetaSchema.objects.all().values_list('schemaId'):
        meta = MetaSchema.objects.get(schemaId=str(templateID))
        xmlDocData = meta.flat_content
    else:
        templateObject = Template.objects.get(pk=templateID)
        xmlDocData = templateObject.content
    
    xmlTree = etree.parse(StringIO(xmlDocData.encode('utf-8')))
    
    xmlSchema = etree.XMLSchema(xmlTree)    
    xmlDoc = etree.XML(str(xmlString.encode('utf-8')))
    prettyXMLString = etree.tostring(xmlDoc, pretty_print=True)  
    xmlSchema.assertValid(etree.parse(StringIO(prettyXMLString)))
    

################################################################################
#
# Function Name: manageNamespace(templateID, xmlString)
# Inputs:        request - 
#                templateID - 
#                xmlString - 
# Outputs:       
# Exceptions:    None
# Description:   - manage global targetNamespace
#                
#
################################################################################
def manageNamespace(templateID, xmlString):    
    # the schema has no dependencies
    if str(templateID) not in MetaSchema.objects.all().values_list('schemaId'):
        templateObject = Template.objects.get(pk=templateID)
        templateData = templateObject.content    
        templateTree = etree.parse(StringIO(templateData.encode('utf-8')))
        templateTreeRoot = templateTree.getroot()
        # The schema is using a target namespace
        if 'targetNamespace' in templateTreeRoot.attrib:    
            xmlTree = etree.parse(StringIO(xmlString.encode('utf-8')))
            xmlRoot = xmlTree.getroot()
            xmlRoot.attrib['xmlns'] = templateTreeRoot.attrib['targetNamespace']
            xmlString = etree.tostring(xmlTree)

    return xmlString


################################################################################
#
# Function Name: getXSDTypes(prefix)
# Inputs:        request - 
#                prefix - Namespace prefix 
# Outputs:       
# Exceptions:    None
# Description:   Returns the list of all supported XSD types
#
################################################################################
def getXSDTypes(prefix):
    return ["{0}:string".format(prefix), 
            "{0}:normalizedString".format(prefix),
            "{0}:token".format(prefix),
            "{0}:date".format(prefix),
            "{0}:dateTime".format(prefix),
            "{0}:duration".format(prefix),
            "{0}:gDay".format(prefix),
            "{0}:gMonth".format(prefix),
            "{0}:gMonthDay".format(prefix),
            "{0}:gYear".format(prefix),
            "{0}:gYearMonth".format(prefix),
            "{0}:gYearMonth".format(prefix),
            "{0}:time".format(prefix), 
            "{0}:byte".format(prefix),
            "{0}:decimal".format(prefix),
            "{0}:int".format(prefix),
            "{0}:integer".format(prefix),
            "{0}:long".format(prefix),
            "{0}:negativeInteger".format(prefix),
            "{0}:nonNegativeInteger".format(prefix),
            "{0}:nonPositiveInteger".format(prefix),
            "{0}:positiveInteger".format(prefix), 
            "{0}:short".format(prefix), 
            "{0}:unsignedLong".format(prefix), 
            "{0}:unsignedInt".format(prefix), 
            "{0}:unsignedShort".format(prefix), 
            "{0}:unsignedByte".format(prefix), 
            "{0}:anyURI".format(prefix), 
            "{0}:base64Binary".format(prefix), 
            "{0}:boolean".format(prefix), 
            "{0}:double".format(prefix),  
            "{0}:float".format(prefix),
            "{0}:hexBinary".format(prefix),
            "{0}:QName".format(prefix),
            "{0}:anyType".format(prefix)]
    
    
################################################################################
# 
# Class Name: ChoiceInfo
#
# Description: Store information about a choice being rendered
#
################################################################################
class ChoiceInfo:
    "Class that stores information about a choice being rendered"
        
    def __init__(self, chooseIDStr, counter):
        self.chooseIDStr = chooseIDStr
        self.counter = counter        
        
        
################################################################################
# 
# Function Name: get_namespaces(file)
# Inputs:        file -
# Outputs:       namespaces
# Exceptions:    None
# Description:   Get the namespaces used in the document
#
################################################################################
def get_namespaces(file):
    "Reads and returns the namespaces in the schema tag"
    events = "start", "start-ns"
    ns = {}
    for event, elem in etree.iterparse(file, events):
        if event == "start-ns":
            if elem[0] in ns and ns[elem[0]] != elem[1]:
                raise Exception("Duplicate prefix with different URI found.")
            ns[elem[0]] = "{%s}" % elem[1]
        elif event == "start":
            break
    return ns


################################################################################
# 
# Function Name: getAppInfo(element, namespace)
# Inputs:        element -
#                namespace - 
# Outputs:       app info
# Exceptions:    None
# Description:   Get app info if present
#
################################################################################
def getAppInfo(element, namespace):
    app_info = {}
    
    app_info_elements = element.findall("./{0}annotation/{0}appinfo".format(namespace))
    for app_info_element in app_info_elements:
        for app_info_child in app_info_element.getchildren():
            if app_info_child.tag in ['label', 'placeholder', 'tooltip', 'use']:
                app_info[app_info_child.tag] = app_info_child.text
    
    return app_info
