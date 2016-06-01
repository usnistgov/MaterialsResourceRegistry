from django.http.request import HttpRequest

import urls
import re
from django.core.urlresolvers import RegexURLResolver, RegexURLPattern
from django.contrib.admindocs.views import simplify_regex
from mgi.models import Module
from mongoengine.errors import ValidationError

from modules import get_module_view
from modules.exceptions import ModuleError


def __assemble_endpoint_data__(pattern, prefix='', filter_path=None):
    """
    Creates a dictionary for matched API urls
    pattern -- the pattern to parse
    prefix -- the API path prefix (used by recursion)
    """
    path = simplify_regex(prefix + pattern.regex.pattern)
    
    if filter_path is not None:
        if re.match('^/?%s(/.*)?$' % re.escape(filter_path), path) is None:
            return None
    
    path = path.replace('<', '{').replace('>', '}')
    
    return {
        'url': path,
        'view': pattern._callback_str,
        'name': pattern.name,        
    }


def __flatten_patterns_tree__(patterns, prefix='', filter_path=None, excluded=[]):
    """
    Uses recursion to flatten url tree.
    patterns -- urlpatterns list
    prefix -- (optional) Prefix for URL pattern
    """
    pattern_list = []
    
    for pattern in patterns:
        if isinstance(pattern, RegexURLPattern):
            if pattern.name is not None and pattern.name in excluded: 
                continue
            
            endpoint_data = __assemble_endpoint_data__(pattern, prefix, filter_path=filter_path)
    
            if endpoint_data is None:
                continue
    
            pattern_list.append(endpoint_data)
        elif isinstance(pattern, RegexURLResolver):
            pref = prefix + pattern.regex.pattern
            pattern_list.extend(__flatten_patterns_tree__(
                pattern.url_patterns,
                pref,
                filter_path=filter_path,
                excluded=excluded,
            ))
    
    return pattern_list


def is_module_managing_occurencies(module):
    request = HttpRequest()
    request.method = 'GET'

    request.GET = {
        'url': module.url,
        'module_id': module.id,
        'managing_occurences': True
    }

    module_view = get_module_view(module.url)

    response = module_view(request).content.decode("utf-8")

    if response == 'false':
        return False
    elif response == 'true':
        return True
    else:
        raise ValueError("Unexpected value (expected 'true'|'false', got {})".format(response))


def discover_modules():
    patterns = __flatten_patterns_tree__(urls.urlpatterns, excluded=urls.excluded)

    # Remove all existing modules
    Module.objects.all().delete()
        
    try:
        for pattern in patterns:
            module = Module(
                url=pattern['url'],
                name=pattern['name'],
                view=pattern['view'],
                multiple=False
            )
            module.save()

            module.update(set__multiple=is_module_managing_occurencies(module))
            module.reload()
    except ValidationError:
        Module.objects.all().delete()

        error_msg = 'A validation error occured during the module discovery. Please provide a name to all modules urls '
        error_msg += 'using the name argument.'
        raise ModuleError(error_msg)
        # something went wrong, delete already added modules
    except Exception, e:
        Module.objects.all().delete()
        raise e
        # something went wrong, delete already added modules
