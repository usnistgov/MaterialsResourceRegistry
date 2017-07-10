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

from utils.XSDflattener.XSDflattener import XSDFlattener
from mgi.models import Type, Template
from urlparse import urlparse


class XSDFlattenerMDCS(XSDFlattener):
    """
    Download the content of the dependency from MongoDB
    """
    def get_dependency_content(self, uri):
        content = ""
        try:
            url = urlparse(uri)
            id = url.query.split("=")[1]
            try:
                type = Type.objects.get(pk=str(id))
                content = type.content
            except:
                template = Template.objects.get(pk=str(id))
                content = template.content
        except:
            pass
        return content
