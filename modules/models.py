import os
from django.conf import settings
from django.http import HttpResponse
import json
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from curate.models import SchemaElement
from exceptions import ModuleError
from abc import ABCMeta, abstractmethod
from modules.utils import sanitize
from modules import render_module


class Module(object):
    __metaclass__ = ABCMeta

    def __init__(self, scripts=list(), styles=list()):
        self.scripts = scripts
        self.styles = styles

        # Is the module managing occurences by its own? (False by default)
        self.is_managing_occurences = False

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
            elif 'managing_occurences' in request.GET:
                return HttpResponse(json.dumps(self.is_managing_occurences), HTTP_200_OK)
            else:
                return self._get(request)
        elif request.method == 'POST':
            return self._post(request)
        else:
            raise ModuleError('Only GET and POST methods can be used to communicate with a module.')

    def _get(self, request):
        module_id = request.GET['module_id']
        url = request.GET['url'] if 'url' in request.GET else SchemaElement.objects().get(pk=module_id).options['url']
        template_data = {
            'module_id': module_id,
            'module': '',
            'display': '',
            'result': '',
            'url': url
        }

        try:
            template_data['module'] = self._get_module(request)
            template_data['display'] = self._get_display(request)

            result = self._get_result(request)
            template_data['result'] = result

            module_element = SchemaElement.objects.get(pk=request.GET['module_id'])
            options = module_element.options

            options['data'] = result
            module_element.update(set__options=options)

            module_element.reload()
        except Exception, e:
            raise ModuleError('Something went wrong during module initialization: ' + e.message)

        # TODO Add additional checks
        for key, val in template_data.items():
            if val is None:
                raise ModuleError('Variable ' + key + ' cannot be None. Module initialization cannot be completed.')

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
            if 'module_id' not in request.POST:
                return HttpResponse({'error': 'No "module_id" parameter provided'}, status=HTTP_400_BAD_REQUEST)

            module_element = SchemaElement.objects.get(pk=request.POST['module_id'])
            template_data['display'] = self._post_display(request)
            options = module_element.options

            # FIXME temporary solution
            post_result = self._post_result(request)

            if type(post_result) == dict:
                options['data'] = self._post_result(request)['data']
                options['attributes'] = self._post_result(request)['attributes']
            else:
                options['data'] = post_result

            # TODO Implement this system instead
            # options['content'] = self._get_content(request)
            # options['attributes'] = self._get_attributes(request)

            module_element.update(set__options=options)
            module_element.reload()
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
        raise NotImplementedError("_get_module method is not implemented.")

    @abstractmethod
    def _get_display(self, request):
        """
            Method:
                Get the default value to be stored in the form.
            Outputs:
                default result value
        """
        raise NotImplementedError("_get_display method is not implemented.")

    @abstractmethod
    def _get_result(self, request):
        """
            Method:
                Get the default value to be stored in the form.
            Outputs:
                default result value
        """
        raise NotImplementedError("_get_result method is not implemented.")

    @abstractmethod
    def _post_display(self, request):
        """
            Method:
                Get the value to be displayed in the form.
            Outputs:
                default displayed value
        """
        raise NotImplementedError("_post_display method is not implemented.")

    @abstractmethod
    def _post_result(self, request):
        """
            Method:
                Get the value to be stored in the form.
            Outputs:
                default result value
        """
        raise NotImplementedError("_post_result method is not implemented.")
