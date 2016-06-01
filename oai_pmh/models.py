################################################################################
#
# File Name: models.py
# Application: oai_pmh
# Purpose:
#
# Author: Pierre Francois RIGODIAT
#         pierre-francois.rigodiat@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from django.db import models
import oai_pmh.rights as RIGHTS

class OAIPMH(models.Model):
    class Meta:
        default_permissions = ()
        permissions = (
            (RIGHTS.oai_pmh_access, RIGHTS.get_description(RIGHTS.oai_pmh_access)),
        )
