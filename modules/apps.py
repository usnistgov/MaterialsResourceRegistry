from django.apps import AppConfig
from modules import discover


# FIXME: loaded two times (not a problem and may not happen in production)
# see http://stackoverflow.com/a/16111968 
class ModulesConfig(AppConfig):
    name = 'modules'
    verbose_name = "Modules"

    def ready(self):
        discover.discover_modules()
