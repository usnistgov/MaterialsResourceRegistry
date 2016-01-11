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

def get_hash(xmlString):
	hash_parser = etree.XMLParser(remove_blank_text=True,remove_comments=True,remove_pis=True)
	etree.set_default_parser(parser=hash_parser)
	
	# parse the XML String removing blanks, comments, processing instructions
	xmlTree = etree.parse(BytesIO(xmlString.encode('utf-8')))
	# remove all annotations
	annotations = xmlTree.findall(".//{http://www.w3.org/2001/XMLSchema}annotation")
	for annotation in annotations:
		annotation.getparent().remove(annotation)
	cleanXmlString = etree.tostring(xmlTree)
	
	# transform into dict and order it
	xmlDict = xmltodict.parse(cleanXmlString, dict_constructor=dict)
	cleanOrderedXmlString = str(sort_dict(xmlDict))
	
	# compute the hash
	hash = hashlib.sha1(cleanOrderedXmlString)
	
	return hash.hexdigest()
	

# inspired by: http://stackoverflow.com/questions/5884066/hashing-a-python-dictionary
def sort_dict(o):
	if isinstance(o, (set, tuple, list)):
		return tuple([sort_dict(e) for e in sorted(o)]) 
	elif not isinstance(o, dict):
		return o

	new_o = copy.deepcopy(o)
	for k, v in new_o.items():
		new_o[k] = sort_dict(v)

	return tuple(frozenset(sorted(new_o.items())))