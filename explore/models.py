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
from mongoengine import *

from curate.models import SchemaElement
from mgi.models import Template


class Explore(models.Model):
    # model stuff here
    class Meta:
        default_permissions = ()
        permissions = (
            (RIGHTS.explore_access, RIGHTS.get_description(RIGHTS.explore_access)),
            (RIGHTS.explore_save_query, RIGHTS.get_description(RIGHTS.explore_save_query)),
            (RIGHTS.explore_delete_query, RIGHTS.get_description(RIGHTS.explore_delete_query)),
        )


class CustomTemplate(Document):
    user = StringField(required=True)
    template = ReferenceField(Template, required=True, unique_with=['user'])
    root = ReferenceField(SchemaElement)
