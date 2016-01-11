import importlib
from mgi.models import Module
from django.template import Context, Template


default_app_config = 'modules.apps.ModulesConfig'


def get_module_view(url):
    """

    :param url:
    :return:
    """
    module = Module.objects.get(url=url)
    pkglist = module.view.split('.')

    pkgs = '.'.join(pkglist[:-1])
    func = pkglist[-1:][0]

    imported_pkgs = importlib.import_module(pkgs)
    return getattr(imported_pkgs, func)


def render_module(template, params={}):
    """
        Purpose:
            renders the template with its context
        Input:
            template: path to HTML template to render
            params: parameters to create a context for the template
    """
    with open(template, 'r') as template_file:
        template_content = template_file.read()

        template = Template(template_content)
        context = Context(params)

        return template.render(context)
