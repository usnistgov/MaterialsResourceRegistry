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
import os
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
USE_BACKGROUND_TASK = settings.USE_BACKGROUND_TASK


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
        if USE_BACKGROUND_TASK:
            tasks.init_harvest()
