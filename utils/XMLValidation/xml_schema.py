################################################################################
#
# File Name: xml_schema.py
# Application: utils
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


from lxml import etree
from cStringIO import StringIO


def validate_xml_schema(xsd_tree):
    """
    Send XML Schema to server to be validated
    :param xsd_tree:
    :return:
    """    
    return _lxml_validate_xsd(xsd_tree)


def validate_xml_data(xsd_tree, xml_tree):
    """
    Send XML Data and XML Schema to server to validate data against the schema
    :param xsd_tree:
    :param xml_tree:
    :return:
    """
    pretty_XML_string = etree.tostring(xml_tree, pretty_print=True)

    return _lxml_validate_xml(xsd_tree, etree.parse(StringIO(pretty_XML_string)))


def _lxml_validate_xsd(xsd_tree):
    """
    Validate schema using LXML
    :param xsd_tree
    :return: errors
    """
    error = None
    try:
        xml_schema = etree.XMLSchema(xsd_tree)
    except Exception, e:
        error = e.message  
    return error


def _lxml_validate_xml(xsd_tree, xml_tree):                          
    """
    Validate document using LXML
    :param xsd_tree
    :return: errors
    """
    error = None
    try:
        xml_schema = etree.XMLSchema(xsd_tree)
        xml_schema.assertValid(xml_tree)
    except Exception, e:
        error = e.message  
    return error
