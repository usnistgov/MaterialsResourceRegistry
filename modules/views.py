import json
from rest_framework import status
from modules.utils import sanitize
# from mgi.models import Module
from modules import get_module_view
# from models import ModuleManager
from django.http import HttpResponse

def load_resources_view(request):
    """ Load resources for a given list of modules

    :param request:
    :return:
    """
    if not request.method == 'GET':
        return HttpResponse({}, status=status.HTTP_400_BAD_REQUEST)

    if 'urlsToLoad' not in request.GET or 'urlsLoaded' not in request.GET:
        return HttpResponse({}, status=status.HTTP_403_FORBIDDEN)

    # URLs of the modules to load
    mod_urls_qs = sanitize(request.GET['urlsToLoad'])
    mod_urls = json.loads(mod_urls_qs)

    # URLs of the loaded modules
    mod_urls_loaded_qs = sanitize(request.GET['urlsLoaded'])
    mod_urls_loaded = json.loads(mod_urls_loaded_qs)

    # Request hack to get module resources
    request.GET = {
        'resources': True
    }

    # List of resources
    resources = {
        'scripts': [],
        'styles': []
    }

    # loaded_resources = {
    #     'scripts': [],
    #     'styles': []
    # }

    # Add all resources from requested modules
    for url in mod_urls:
        module_view = get_module_view(url)
        mod_resources = module_view(request).content

        mod_resources = sanitize(mod_resources)
        mod_resources = json.loads(mod_resources)

        # Append resource to the list
        for key in resources.keys():
            if mod_resources[key] is None:
                continue

            for resource in mod_resources[key]:
                if resource not in resources[key]:
                    resources[key].append(resource)

    # Remove possible dependencies form already loaded modules
    for url in mod_urls_loaded:
        module_view = get_module_view(url)
        mod_resources = module_view(request).content

        mod_resources = sanitize(mod_resources)
        mod_resources = json.loads(mod_resources)

        # Remove resources already loaded
        for key in resources.keys():
            if mod_resources[key] is None:
                continue

            for resource in mod_resources[key]:
                if resource in resources[key]:
                    i = resources[key].index(resource)
                    del resources[key][i]


    # Build response content
    response = {
        'scripts': "",
        'styles': ""
    }

    # Aggregate scripts
    for script in resources['scripts']:
        if script.startswith('http://') or script.startswith('https://'):
            script_tag = '<script src="' + script + '"></script>'
        else:
            with open(script, 'r') as script_file:
                script_tag = '<script>' + script_file.read() + '</script>'

        response['scripts'] += script_tag

    # Aggregate styles
    for style in resources['styles']:
        if style.startswith('http://') or style.startswith('https://'):
            script_tag = '<link rel="stylesheet" type="text/css" href="' + style + '"></link>'
        else:
            with open(style, 'r') as script_file:
                script_tag = '<style>' + script_file.read() + '</style>'

        response['styles'] += script_tag

    # Send response
    return HttpResponse(json.dumps(response), status=status.HTTP_200_OK)

