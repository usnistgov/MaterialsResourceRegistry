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
from mgi.models import Type, MetaSchema
from urlparse import urlparse

################################################################################
#
# XSDFlattenerMDCS
#
# description: flattener that works with MDCS model
#
################################################################################
class XSDFlattenerMDCS(XSDFlattener):
			
	def get_dependency_content(self, uri):
		content = ""
		try:
			url = urlparse(uri)
			id = url.query.split("=")[1]
			if id in MetaSchema.objects.all().values_list('schemaId'):
				meta = MetaSchema.objects.get(schemaId=id)
				content = meta.api_content
			else:
				type = Type.objects.get(pk=str(id))
				content = type.content
		except:
			pass
		return content
	
	