"""
"""
import types
from types import NoneType
from django.http.request import HttpRequest
from django.template.base import Template
from django.template.context import RequestContext
from django.template import loader
from os.path import join
from curate.models import SchemaElement


class BaseRenderer(object):
    """ Base renderer containing base functions for any renderer
    """

    def __init__(self, template_list=None):
        """ Default renderer for the HTML form

        Parameters:
            - xsd_data:
            - template_list:
        """
        # Data initialization
        self.templates = {}

        if template_list is not None:
            self.templates.update(template_list)

    def _load_template(self, tpl_key, tpl_data=None):
        """ Instantiate a preloaded template

        Parameters:
            tpl_key:
            tpl_data:

        Returns:
        """
        add_context = {}
        context = RequestContext(HttpRequest())

        if tpl_data is not None:
            add_context.update(tpl_data)
            context.update(add_context)

        return self.templates[tpl_key].render(context)


class HtmlRenderer(BaseRenderer):
    """ Renderer for HTML forms
    """

    def __init__(self, template_list=None):
        """ Init function

        Parameters:
            template_list:
        """
        # Parameters test
        # if template_list is not None:
        #     if type(template_list) != dict:
        #         raise TypeError("template_list type is wrong (" + str(type(template_list)) + " received, dict needed")
        #
        #     for template in template_list.values():
        #         if not isinstance(template, Template):
        #             template_type = str(type(template_list))
        #             raise TypeError("template value type is wrong (" + template_type + " received, dict needed")

        # Data initialization
        html_renderer_templates_path = join('renderer', 'default')
        html_templates = {
            'form_error': loader.get_template(join(html_renderer_templates_path, 'form-error.html')),
            'warning': loader.get_template(join(html_renderer_templates_path, 'warning.html')),

            'input': loader.get_template(join(html_renderer_templates_path, 'inputs', 'input.html')),
            'select': loader.get_template(join(html_renderer_templates_path, 'inputs', 'select.html')),

            'btn_add': loader.get_template(join(html_renderer_templates_path, 'buttons', 'add.html')),
            'btn_del': loader.get_template(join(html_renderer_templates_path, 'buttons', 'delete.html')),
            'btn_collapse': loader.get_template(join(html_renderer_templates_path, 'buttons', 'collapse.html'))
        }

        if template_list is not None:
            html_templates.update(template_list)

        super(HtmlRenderer, self).__init__(html_templates)

    def _render_form_error(self, err_message):
        context = RequestContext(HttpRequest())
        data = {
            'message': err_message
        }

        context.update(data)
        return self.templates['form_error'].render(context)

    def _render_warnings(self, warnings):
        html_content = ''

        for warning in warnings:
            data = {
                'message': warning
            }

            html_content += self._load_template('warning', data)

        return html_content

    # def _render_input(self, input_id, value, placeholder, title):
    def _render_input(self, element):
        """

        :param element
        :return:
        """
        if not isinstance(element, SchemaElement):
            raise TypeError('element should be SchemaElement (' + str(type(element)) + ' given)')

        placeholder = ''
        tooltip = ''
        use = ''

        if 'placeholder' in element.options:
            placeholder = element.options['placeholder']

        if 'tooltip' in element.options:
            tooltip = element.options['tooltip']

        if 'use' in element.options:
            use = element.options['use']

        data = {
            'id': element.pk,
            'value': element.value,
            'placeholder': placeholder,
            'tooltip': tooltip,
            'use': use,
        }

        return self._load_template('input', data)

    def _render_select(self, select_id, select_class, option_list):
        # if type(select_id) not in [str, unicode, NoneType]:
        #     raise TypeError('First param (select_id) should be a str or None (' + str(type(select_id)) + ' given)')
        #
        # if not isinstance(option_list, types.ListType):
        #     raise TypeError('First param (option_list) should be a list (' + str(type(option_list)) + ' given)')
        #
        # for option in option_list:
        #     if not isinstance(option, types.TupleType):
        #         raise TypeError('Malformed param (option_list): type of item not good')
        #
        #     if len(option) != 3:
        #         raise TypeError('Malformed param (option_list): Length of item not good')
        #
        #     if type(option[0]) not in [str, unicode]:
        #         raise TypeError('Malformed param (option_list): item[0] should be a str')
        #
        #     if type(option[1]) not in [str, unicode]:
        #         raise TypeError('Malformed param (option_list): item[1] should be a str')
        #
        #     if type(option[2]) != bool:
        #         raise TypeError('Malformed param (option_list): item[2] should be a bool')

        data = {
            'select_id': select_id,
            'select_class': select_class,
            'option_list': option_list
        }

        return self._load_template('select', data)

    # def _render_buttons(self, min_occurs, max_occurs, occurence_count):
    def _render_buttons(self, add_button, delete_button):
        """

        :param min_occurs:
        :param max_occurs:
        :param occurence_count:
        :return:
        """
        # add_button = False
        # del_button = False
        #
        # if occurence_count < max_occurs or max_occurs == -1:
        #     add_button = True
        #
        # if occurence_count > min_occurs:
        #     del_button = True
        #
        # if occurence_count < min_occurs:
        #     pass
        #
        # add_button_type = type(add_button)
        # del_button_type = type(del_button)
        #
        # if add_button_type is not bool:
        #     raise TypeError('add_button type is wrong (' + str(add_button_type) + 'received, bool needed')
        #
        # if del_button_type is not bool:
        #     raise TypeError('add_button type is wrong (' + str(del_button_type) + 'received, bool needed')
        #
        # form_string = ""
        #
        # # Fixed number of occurences, don't need buttons
        # if add_button or del_button:
        #     if add_button:
        #         form_string += self._load_template('btn_add', {'is_hidden': False})
        #     else:
        #         form_string += self._load_template('btn_add', {'is_hidden': True})
        #
        #     if del_button:
        #         form_string += self._load_template('btn_del', {'is_hidden': False})
        #     else:
        #         form_string += self._load_template('btn_del', {'is_hidden': True})
        #
        # return form_string
        # FIXME Remove type checking
        add_button_type = type(add_button)
        del_button_type = type(delete_button)

        if add_button_type is not bool:
            raise TypeError('add_button type is wrong (' + str(add_button_type) + 'received, bool needed')

        if del_button_type is not bool:
            raise TypeError('add_button type is wrong (' + str(del_button_type) + 'received, bool needed')

        form_string = ""

        # Fixed number of occurences, don't need buttons
        if not (add_button or delete_button):
            pass
        else:
            if add_button:
                form_string += self._load_template('btn_add', {'is_hidden': False})
            else:
                form_string += self._load_template('btn_add', {'is_hidden': True})

            if delete_button:
                form_string += self._load_template('btn_del', {'is_hidden': False})
            else:
                form_string += self._load_template('btn_del', {'is_hidden': True})

        return form_string

    def _render_collapse_button(self):
        return self._load_template('btn_collapse')


class DefaultRenderer(object):

    def __init__(self, xsd_data, template_list=None):
        """ Default renderer for the HTML form

        Parameters:
            - xsd_data:
            - template_list:
        """

        if not isinstance(xsd_data, SchemaElement):
            raise TypeError("xsd_data type should be a SchemaElement")

        if template_list is not None:
            if type(template_list) != dict:
                raise TypeError("template_list type is wrong (" + str(type(template_list)) + " received, dict needed")

            for template in template_list.values():
                if not isinstance(template, Template):
                    template_type = str(type(template_list))
                    raise TypeError("template value type is wrong (" + template_type + " received, dict needed")

        self.data = xsd_data
        self.warnings = []

        default_renderer_path = join('renderer', 'default')
        self.templates = {
            'form_error': loader.get_template(join(default_renderer_path, 'form-error.html')),
            'warning': loader.get_template(join(default_renderer_path, 'warning.html')),

            'input': loader.get_template(join(default_renderer_path, 'inputs', 'input.html')),
            'select': loader.get_template(join(default_renderer_path, 'inputs', 'select.html')),
            'checkbox': loader.get_template(join(default_renderer_path, 'inputs', 'checkbox.html')),

            'btn_add': loader.get_template(join(default_renderer_path, 'buttons', 'add.html')),
            'btn_del': loader.get_template(join(default_renderer_path, 'buttons', 'delete.html')),
            'btn_collapse': loader.get_template(join(default_renderer_path, 'buttons', 'collapse.html'))
        }

        if template_list is not None:
            self.templates.update(template_list)

    def _load_template(self, tpl_key, tpl_data=None):
        context = RequestContext(HttpRequest())

        if tpl_key not in self.templates.keys():
            raise IndexError('Template "' + tpl_key + '" not found in registered templates ' +
                             str(self.templates.keys()))

        if tpl_data is not None and type(tpl_data) != dict:
            raise TypeError('Data parameter should be a dict (' + str(type(tpl_data)) + ' given)')

        if tpl_data is not None:
            context.update(tpl_data)

        return self.templates[tpl_key].render(context)

    def _render_form_error(self, err_message):
        if type(err_message) not in [str, unicode]:
            raise TypeError('Error message should be string or unicode (' + str(type(err_message)) + ' given)')

        context = RequestContext(HttpRequest())
        data = {
            'message': err_message
        }

        context.update(data)
        return self.templates['form_error'].render(context)

    def _render_warnings(self):
        html_content = ''

        for warning in self.warnings:
            data = {
                'message': warning
            }

            html_content += self._load_template('warning', data)

        return html_content

    def _render_input(self, element):
        """

        :param element
        :return:
        """
        placeholder = ''
        tooltip = ''
        use = ''

        if 'placeholder' in element.options:
            placeholder = element.options['placeholder']

        if 'tooltip' in element.options:
            tooltip = element.options['tooltip']

        if 'use' in element.options:
            use = element.options['use']

        data = {
            'id': element.pk,
            'value': element.value,
            'placeholder': placeholder,
            'tooltip': tooltip,
            'use': use,
        }

        return self._load_template('input', data)

    def _render_select(self, select_id, select_class, option_list):
        if type(select_id) not in [str, unicode, NoneType]:
            raise TypeError('First param (select_id) should be a str or None (' + str(type(select_id)) + ' given)')

        if not isinstance(option_list, types.ListType):
            raise TypeError('First param (option_list) should be a list (' + str(type(option_list)) + ' given)')

        for option in option_list:
            if not isinstance(option, types.TupleType):
                raise TypeError('Malformed param (option_list): type of item not good')

            if len(option) != 3:
                raise TypeError('Malformed param (option_list): Length of item not good')

            if type(option[0]) not in [str, unicode]:
                raise TypeError('Malformed param (option_list): item[0] should be a str')

            if type(option[1]) not in [str, unicode]:
                raise TypeError('Malformed param (option_list): item[1] should be a str')

            if type(option[2]) != bool:
                raise TypeError('Malformed param (option_list): item[2] should be a bool')

        data = {
            'select_id': select_id,
            'select_class': select_class,
            'option_list': option_list
        }

        return self._load_template('select', data)

    # def _render_buttons(self, min_occurs, max_occurs, occurence_count):
    def _render_buttons(self, add_button, delete_button):
        """Displays buttons for a duplicable/removable element

        Parameters:
            add_button: boolean
            delete_button: boolean

        Returns:
            JSON data
        """
        add_button_type = type(add_button)
        del_button_type = type(delete_button)

        if add_button_type is not bool:
            raise TypeError('add_button type is wrong (' + str(add_button_type) + 'received, bool needed')

        if del_button_type is not bool:
            raise TypeError('add_button type is wrong (' + str(del_button_type) + 'received, bool needed')

        form_string = ""

        # Fixed number of occurences, don't need buttons
        if not add_button and not delete_button:
            pass
        else:
            if add_button:
                form_string += self._load_template('btn_add', {'is_hidden': False})
            else:
                form_string += self._load_template('btn_add', {'is_hidden': True})

            if delete_button:
                form_string += self._load_template('btn_del', {'is_hidden': False})
            else:
                form_string += self._load_template('btn_del', {'is_hidden': True})

        return form_string

    def _render_collapse_button(self):
        return self._load_template('btn_collapse')
