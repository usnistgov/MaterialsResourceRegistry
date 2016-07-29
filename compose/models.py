################################################################################
#
# File Name: models.py
# Application: compose
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


class Compose(models.Model):
    # model stuff here
    class Meta:
        default_permissions = ()
        permissions = (
            (RIGHTS.compose_access, RIGHTS.get_description(RIGHTS.compose_access)),
            (RIGHTS.compose_save_template, RIGHTS.get_description(RIGHTS.compose_save_template)),
            (RIGHTS.compose_save_type, RIGHTS.get_description(RIGHTS.compose_save_type)),
        )
