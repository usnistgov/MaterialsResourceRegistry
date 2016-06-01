################################################################################
#
# File Name: rdfPublisher.py
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


from lxml import etree
from cStringIO import StringIO
  
def validate_xml_schema(xsd_tree):
    """
    Send XML Schema to server to be validated
    :param xsd_tree:
    :return:
    """
    error = None
    try:
        xml_schema = etree.XMLSchema(xsd_tree)
    except Exception, e:
        error = e.message
    return error


def validate_xml_data(xsd_tree, xml_tree):
    """
    Send XML Data and XML Schema to server to validate data against the schema
    :param xsd_tree:
    :param xml_tree:
    :return:
    """
    error = None
    pretty_XML_string = etree.tostring(xml_tree, pretty_print=True)
    try:
        xml_schema = etree.XMLSchema(xsd_tree)
        xml_schema.assertValid(etree.parse(StringIO(pretty_XML_string)))
    except Exception, e:
        error = e.message
    return error
