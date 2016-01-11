################################################################################
#
# File Name: models.py
# Application: api
# Purpose:   
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from django.db import models
import mgi.rights as RIGHTS

class API(models.Model):
    # model stuff here
    class Meta:
        default_permissions = ()
        permissions = (
            (RIGHTS.api_access, RIGHTS.get_description(RIGHTS.api_access)),
        )
