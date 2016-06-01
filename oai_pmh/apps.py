################################################################################
#
# File Name: apps.py
# Application: Informatics Core
# Description:
#
# Author: Pierre Francois RIGODIAT
#         pierre-francois.rigodiat@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from django.apps import AppConfig
from oai_pmh import discover, tasks
from mgi.models import OaiRecord



# TODO: loaded two times (not a problem and may not happen in production) 
# see http://stackoverflow.com/a/16111968 
class OAIPMHConfig(AppConfig):
    name = 'oai_pmh'
    verbose_name = "oai_pmh"

    def ready(self):
        #Settings Initialization
        discover.init_settings()
        #Add indexes for the keyword research
        OaiRecord.initIndexes()
        #Load metadata prefixes
        discover.load_metadata_prefixes()
        #Load sets
        discover.load_sets()
        #Load xslt
        discover.load_xslt()
        #Check registries state
        discover.init_registries_status()
        #Launch background tasks
        tasks.init_harvest()
