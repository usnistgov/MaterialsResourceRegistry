################################################################################
#
# File Name: XSDhash.py
# 
# Purpose: Hash an XSD file
# 
# Author: Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
#		  Sharief Youssef
#         sharief.youssef@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

import lxml.etree as etree
import hashlib
import xmltodict
from io import BytesIO
import copy


def get_hash(xml_string):
    """
    Get the has of an XML String
    :param xml_string: XML String to hash
    :return:
    """
    hash_parser = etree.XMLParser(remove_blank_text=True,remove_comments=True,remove_pis=True)
    etree.set_default_parser(parser=hash_parser)

    # parse the XML String removing blanks, comments, processing instructions
    xml_tree = etree.parse(BytesIO(xml_string.encode('utf-8')))
    # remove all annotations
    annotations = xml_tree.findall(".//{http://www.w3.org/2001/XMLSchema}annotation")
    for annotation in annotations:
        annotation.getparent().remove(annotation)
    clean_xml_string = etree.tostring(xml_tree)

    # transform into dict and order it
    xml_dict = xmltodict.parse(clean_xml_string, dict_constructor=dict)
    clean_ordered_xml_string = str(sort_dict(xml_dict))

    # compute the hash
    hash = hashlib.sha1(clean_ordered_xml_string)

    return hash.hexdigest()


def sort_dict(o):
    """
    Return a sorted dictionary
    inspired by: http://stackoverflow.com/questions/5884066/hashing-a-python-dictionary
    :param o:
    :return:
    """
    if isinstance(o, (set, tuple, list)):
        return tuple([sort_dict(e) for e in sorted(o)])
    elif not isinstance(o, dict):
        return o

    new_o = copy.deepcopy(o)
    for k, v in new_o.items():
        new_o[k] = sort_dict(v)

    return tuple(frozenset(sorted(new_o.items())))
