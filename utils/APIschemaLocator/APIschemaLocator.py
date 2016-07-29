################################################################################
#
# File Name: APIschemaLocator.py
# 
# Purpose: Centralized way to provide a an unique URI to get the schema on the server
# 
# Author: Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
#          Sharief Youssef
#         sharief.youssef@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################



# For now:
# - just provide the URL to the API call that returns the schema
#
# Next:
# - add some version management
# - get the schema using the ID and use the hash in the API call
import os
from django.utils.importlib import import_module

settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)


def getSchemaLocation(schemaID):
    return str(settings.MDCS_URI)+'/rest/types/get-dependency?id=' + str(schemaID)
