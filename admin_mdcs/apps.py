from django.apps import AppConfig
from admin_mdcs import discover


# TODO: loaded two times (not a problem and may not happen in production) 
# see http://stackoverflow.com/a/16111968 
class AdminMdcsConfig(AppConfig):
    name = 'admin_mdcs'
    verbose_name = "admin_mdcs"

    def ready(self):
        discover.init_rules()
        discover.load_templates()
