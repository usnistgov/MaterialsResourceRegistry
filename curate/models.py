################################################################################
#
# File Name: models.py
# Application: curate
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
# from mongoengine.document import Document
from django_mongoengine import Document
from django_mongoengine import fields
# from mongoengine.fields import StringField, ListField, ReferenceField, DictField

import mgi.rights as RIGHTS

class Curate(models.Model):
    # model stuff here
    class Meta:
        default_permissions = ()
        permissions = (
            (RIGHTS.curate_access, RIGHTS.get_description(RIGHTS.curate_access)),
            (RIGHTS.curate_view_data_save_repo, RIGHTS.get_description(RIGHTS.curate_view_data_save_repo)),
            (RIGHTS.curate_edit_document, RIGHTS.get_description(RIGHTS.curate_edit_document)),
            (RIGHTS.curate_delete_document, RIGHTS.get_description(RIGHTS.curate_delete_document)),
        )


class SchemaElement(Document):
    tag = fields.StringField()
    value = fields.StringField(default=None, blank=True)

    options = fields.DictField(blank=True)

    children = fields.ListField(fields.ReferenceField('SchemaElement'), blank=True)
