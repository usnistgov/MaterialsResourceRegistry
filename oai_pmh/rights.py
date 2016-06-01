################################################################################
#
# File Name: models.py
# Application: mgi
# Description:
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
#         Pierre Francois RIGODIAT
#         pierre-francois.rigodiat@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

### Anonymous group ###
anonymous_group = "anonymous"
#######################

### Default group ###
default_group = "default"
#######################

### API Rights ###
api_content_type = "api_oai_pmh"
api_access = "api_oai_pmh_access"
### End API Rights ###

### OAI PMH Rights ###
oai_pmh_content_type = "oaipmh"
oai_pmh_access = "oaipmh_access"
### End OAI PMH Rights ###


def get_description(right):
    return "Can " + right.replace("_", " ")