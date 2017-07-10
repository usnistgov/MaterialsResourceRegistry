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

from cStringIO import StringIO
import os
from django.utils.importlib import import_module
from lxml import etree
import json

settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
XERCES_VALIDATION = settings.XERCES_VALIDATION

if XERCES_VALIDATION:
    from xerces_client import send_message

def validate_xml_schema(xsd_tree):
    """
    Send XML Schema to server to be validated
    :param xsd_tree:
    :return:
    """
    error = None

    if XERCES_VALIDATION and _xerces_exists():
        try:
            xsd_string = etree.tostring(xsd_tree)
            message = {'xsd_string': xsd_string}
            message = json.dumps(message)
            send_message(message)
        except Exception, e:
            print e.message
            error = _lxml_validate_xsd(xsd_tree)
    else:
        error = _lxml_validate_xsd(xsd_tree)

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

    if XERCES_VALIDATION and _xerces_exists():
        try:
            xsd_string = etree.tostring(xsd_tree)
            message = {'xsd_string': xsd_string, 'xml_string': pretty_XML_string}
            message = json.dumps(message)
            send_message(message)
        except Exception, e:
            print e.message
            error = _lxml_validate_xml(xsd_tree, etree.parse(StringIO(pretty_XML_string)))
    else:
        error = _lxml_validate_xml(xsd_tree, etree.parse(StringIO(pretty_XML_string)))

    return error


def _xerces_exists():
    """
    Check if xerces wrapper is installed
    :return:
    """
    try:
        __import__('xerces_wrapper')
    except ImportError:
        print "XERCES DOES NOT EXIST"
        return False
    else:
        print "XERCES EXISTS"
        return True


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

