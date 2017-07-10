################################################################################
#
# File Name: XSDflattener.py
# 
# Purpose: Flatten an XSD file - gather all dependencies in one file
# 
# V1: 
#    - works with include statement only (not import)
#    - works with API URL in include schemaLocation attribute
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
import urllib2
from urlparse import urlparse


class XSDFlattener(object):
    __metaclass__ = ABCMeta

    def __init__(self, xmlString, download_enabled=True):
        self.xmlString = xmlString
        self.dependencies = []
        self.download_enabled = download_enabled

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


class XSDFlattenerURL(XSDFlattener):
    """
    Download the content of the dependency
    """
    def get_dependency_content(self, uri):
        content = ""

        if self.download_enabled:
            file = urllib2.urlopen(uri)
            content = file.read()

        return content


class XSDFlattenerDatabaseOrURL(XSDFlattener):
    """
    Get the content of the dependency from the database or from the URL
    """

    def get_dependency_content(self, uri):
        content = self._get_dependency_content_database(uri)
        if content == "":
            content = self._get_dependency_content_url(uri)

        return content

    def _get_dependency_content_database(self, uri):
        from mgi.models import Type, Template
        content = ""
        try:
            url = urlparse(uri)
            _id = url.query.split("=")[1]
            try:
                _type = Type.objects.get(pk=str(_id))
                content = _type.content
            except:
                template = Template.objects.get(pk=str(_id))
                content = template.content
        except:
            pass

        return content

    def _get_dependency_content_url(self, uri):
        content = ""

        try:
            if self.download_enabled:
                _file = urllib2.urlopen(uri)
                content = _file.read()
        except:
            pass

        return content
