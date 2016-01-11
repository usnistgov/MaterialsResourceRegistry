################################################################################
#
# File Name: XSDflattener.py
# 
# Purpose: Flatten an XSD file - gather all dependencies in one file
# 
# V1: 
#    - works with include statement only (not import)
#    - works with API URL in include schemaLocation attribute
#	 - works with local URI
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
from io import BytesIO
from abc import ABCMeta, abstractmethod

class XSDFlattener(object):
	
	__metaclass__ = ABCMeta
	
	def __init__(self, xmlString):
		self.xmlString = xmlString
		self.dependencies = []

	def get_flat(self):
		parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
		etree.set_default_parser(parser=parser)
		
		# parse the XML String removing blanks, comments, processing instructions
		xmlTree = etree.parse(BytesIO(self.xmlString.encode('utf-8')))

		# check if it has includes
		includes = xmlTree.findall("{http://www.w3.org/2001/XMLSchema}include")
		if len(includes) > 0:
			for el_include in includes:
				uri = el_include.attrib['schemaLocation']			
				flatDependency = self.get_flat_dependency(uri)
				if flatDependency is not None:
					# append flatDependency to the tree
					dependencyTree = etree.fromstring(flatDependency)
					dependencyElements = dependencyTree.getchildren()
					for element in dependencyElements:
						xmlTree.getroot().append(element)
				el_include.getparent().remove(el_include)
		return etree.tostring(xmlTree)
		
	def get_flat_dependency(self, uri):
		try:
			if uri not in self.dependencies:
				self.dependencies.append(uri)
				dependencyContent = self.get_dependency_content(uri)
				xmlTree = etree.parse(BytesIO(dependencyContent.encode('utf-8')))
				includes = xmlTree.findall("{http://www.w3.org/2001/XMLSchema}include")
				if len(includes) > 0:
					for el_include in includes:
						uri = el_include.attrib['schemaLocation']	
						flatDependency = self.get_flat_dependency(uri)
						if flatDependency is not None:
							# append flatDependency to the tree
							dependencyTree = etree.fromstring(flatDependency)
							dependencyElements = dependencyTree.getchildren()
							for element in dependencyElements:
								xmlTree.getroot().append(element)
						el_include.getparent().remove(el_include)
				return etree.tostring(xmlTree)
			else:
				return None
		except:
			return None
	
	@abstractmethod	
	def get_dependency_content(self, uri):
		pass


################################################################################
#
# XSDFlattenerURL
#
# future: flattener that could work using URL of distant server requiring authentication
#
################################################################################
class XSDFlattenerURL(XSDFlattener):
			
	def __init__(self, xmlString):
		XSDFlattener.__init__(self, xmlString)
		self.servers = {}
	
	def get_dependency_content(self, uri):
		pass
# 		r = requests.get(uri,auth=(self.user, self.password))
# 		return r.text
	
	def registerServer(self, url, user, password):
		self.servers[url] = {'user':user, 'password':password}

################################################################################
#
# XSDFlattenerLocal
#
# description: flattener that can flatten files on the local file system
#
################################################################################	
class XSDFlattenerLocal(XSDFlattener):
		
	def get_dependency_content(self, uri):
		file = open(uri,'r')
		content = file.read()
		return content


################################################################################
#
# XSDFlattenerFull
#
# future: flattener that could work using URL and local files
#
################################################################################
class XSDFlattenerFull(XSDFlattener):
		
	def get_dependency_content(self, uri):
		pass
	
	