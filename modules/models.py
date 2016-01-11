import os
from django.conf import settings
from django.http import HttpResponse
import json
from rest_framework.status import HTTP_200_OK
from exceptions import ModuleError
from abc import ABCMeta, abstractmethod
from modules.utils import sanitize
from modules import render_module


class Module(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, scripts=list(), styles=list()):
        self.scripts = scripts
        self.styles = styles

        # Skeleton of the modules
        self.template = os.path.join(settings.SITE_ROOT, 'templates', 'module.html')

    def add_scripts(self, scripts):
        for script in scripts:
            self.scripts.append(script)

    def add_styles(self, styles):
        for style in styles:
            self.styles.append(style)

    def render(self, request):        
        if request.method == 'GET':
            if 'resources' in request.GET:
                return self._get_resources()
            else:
                return self._get(request)
        elif request.method == 'POST':
            return self._post(request)
        else:
            raise ModuleError('Only GET and POST methods can be used to communicate with a module.')

    def _get(self, request):
        template_data = {
            'module': '',
            'display': '',
            'result': '',
            'url': request.GET['url']
        }

        try:
            template_data['module'] = self._get_module(request)
            template_data['display'] = self._get_display(request)
            template_data['result'] = sanitize(self._get_result(request))
        except Exception, e:
            raise ModuleError('Something went wrong during module initialization: ' + e.message)

        # TODO Add additional checks
        for key, val in template_data.items():
            if val is None:
                raise ModuleError('Variable '+key+' cannot be None. Module initialization cannot be completed.')

        # Apply tags to the template
        html_code = render_module(self.template, template_data)
        return HttpResponse(html_code, status=HTTP_200_OK)

    def _post(self, request):
        template_data = {
            'display': '',
            'result': '',
            'url': ''
        }

        try:
            template_data['display'] = self._post_display(request)
            template_data['result'] = sanitize(self._post_result(request))
        except Exception, e:
            raise ModuleError('Something went wrong during module update: ' + e.message)

        html_code = render_module(self.template, template_data)
        
        response_dict = dict()
        response_dict['html'] = html_code

        if hasattr(self, "get_XpathAccessor"):
            response_dict.update(self.get_XpathAccessor())

        return HttpResponse(json.dumps(response_dict))
    
    def _get_resources(self):
        """
        """
        response = {
            'scripts': self.scripts,
            'styles': self.styles
        }
    
        return HttpResponse(json.dumps(response), status=HTTP_200_OK)

    @abstractmethod
    def _get_module(self, request):
        """
            Method:
                Get the default value to be stored in the form.
            Outputs:
                default result value
        """
        raise NotImplementedError("This method is not implemented.")

    @abstractmethod
    def _get_display(self, request):
        """
            Method:
                Get the default value to be stored in the form.
            Outputs:
                default result value
        """
        raise NotImplementedError("This method is not implemented.")

    @abstractmethod
    def _get_result(self, request):
        """
            Method:
                Get the default value to be stored in the form.
            Outputs:
                default result value
        """
        raise NotImplementedError("This method is not implemented.")

    @abstractmethod
    def _post_display(self, request):
        """
            Method:
                Get the value to be displayed in the form.
            Outputs:
                default displayed value
        """
        raise NotImplementedError("This method is not implemented.")

    @abstractmethod
    def _post_result(self, request):
        """
            Method:
                Get the value to be stored in the form.
            Outputs:
                default result value
        """
        raise NotImplementedError("This method is not implemented.")
