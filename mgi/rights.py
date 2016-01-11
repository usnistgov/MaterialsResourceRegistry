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
api_content_type = "api"
api_access = "api_access"
### End API Rights ###

### Compose Rights ###
compose_content_type = "compose"
compose_access = "compose_access"
compose_save_template = "compose_save_template"
compose_save_type = "compose_save_type"
### End Compose Rights ###


### Curate Rights ###
curate_content_type = "curate"
curate_access = "curate_access"
curate_view_data_save_repo = "curate_view_data_save_repo"
curate_edit_document="curate_edit_document"
curate_delete_document="curate_delete_document"
### End Curate Rights ###


### Explore Rights ###
explore_content_type = "explore"
explore_access = "explore_access"
explore_save_query="explore_save_query"
explore_delete_query="explore_delete_query"
### End Explore Rights ###


def get_description(right):
    return "Can " + right.replace("_", " ")