################################################################################
#
# File Name: models.py
# Application: explore
# Purpose:   
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume Sousa Amaral
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from django.db import models
import mgi.rights as RIGHTS

class Explore(models.Model):
    # model stuff here
    class Meta:
        default_permissions = ()
        permissions = (
            (RIGHTS.explore_access, RIGHTS.get_description(RIGHTS.explore_access)),
            (RIGHTS.explore_save_query, RIGHTS.get_description(RIGHTS.explore_save_query)),
            (RIGHTS.explore_delete_query, RIGHTS.get_description(RIGHTS.explore_delete_query)),
        )