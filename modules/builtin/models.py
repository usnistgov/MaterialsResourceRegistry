from __future__ import division
from modules.models import Module, ModuleError
from django.conf import settings
import os
from modules import render_module
from math import ceil

RESOURCES_PATH = os.path.join(settings.SITE_ROOT, 'modules/builtin/resources/')
TEMPLATES_PATH = os.path.join(RESOURCES_PATH, 'html')
SCRIPTS_PATH = os.path.join(RESOURCES_PATH, 'js')
STYLES_PATH = os.path.join(RESOURCES_PATH, 'css')

class InputModule(Module):
    def __init__(self, scripts=list(), styles=list(), label=None, default_value=None, disabled=False):
        scripts = [os.path.join(SCRIPTS_PATH, 'input.js')] + scripts
        Module.__init__(self, scripts=scripts, styles=styles)

        self.label = label
        self.default_value = default_value
        self.disabled = disabled

    def get_module(self, request):
        template = os.path.join(TEMPLATES_PATH, 'input.html')
        params = {}

        if self.label is not None:
            params.update({"label": self.label})

        if self.default_value is not None:
            params.update({"default_value": self.default_value})
            
        if self.disabled is not None:
            params.update({"disabled": self.disabled})

        return render_module(template, params)

class OptionsModule(Module):
    def __init__(self, scripts=list(), styles=list(), label=None, options=dict(), disabled=False, selected=None):
        scripts = [os.path.join(SCRIPTS_PATH, 'options.js')] + scripts
        Module.__init__(self, scripts=scripts, styles=styles)

        self.options = options
        self.label = label
        self.disabled = disabled
        self.selected = selected
        

    def get_module(self, request):
        template = os.path.join(TEMPLATES_PATH, 'options.html')
        options_html = ""

        for key, val in self.options.items():
            if self.selected is not None and key == self.selected:
                options_html += "<option value='" + key + "' selected>" + val + "</option>"
            else:
                options_html += "<option value='" + key + "'>" + val + "</option>"

        params = {"options": options_html}

        if self.label is not None:
            params.update({"label": self.label})
            
        if self.disabled is not None:
            params.update({"disabled": self.disabled})

        return render_module(template, params)


class PopupModule(Module):
    def __init__(self, scripts=list(), styles=list(), popup_content=None, button_label='Save'):
        scripts = [os.path.join(SCRIPTS_PATH, 'popup.js')] + scripts
        Module.__init__(self, scripts=scripts, styles=styles)
        if popup_content is None:
            raise ModuleError("'popup_content' and is required. Cannot instantiate an empty popup")

        self.popup_content = popup_content
        self.button_label = button_label

    def get_module(self, request):
        template = os.path.join(TEMPLATES_PATH, 'popup.html')
        params = {
            "popup_content": self.popup_content,
            "button_label": self.button_label
        }

        return render_module(template, params)


class SyncInputModule(Module):
    def __init__(self, scripts=list(), styles=list(), label=None, default_value=None, modclass=None):
        scripts = [os.path.join(SCRIPTS_PATH, 'sync_input.js')] + scripts
        Module.__init__(self, scripts=scripts, styles=styles)

        if modclass is None:
            raise ModuleError("'modclass' is required.")

        self.modclass = modclass
        self.label = label
        self.default_value = default_value

    def get_module(self, request):
        template = os.path.join(TEMPLATES_PATH, 'sync_input.html')
        params = {'class': self.modclass}
        if self.label is not None:
            params.update({"label": self.label})
        if self.default_value is not None:
            params.update({"default_value": self.default_value})
        return render_module(template, params)
    

class InputButtonModule(Module):
    def __init__(self, scripts=list(), styles=list(), button_label='Send', label=None, default_value=None):
        Module.__init__(self, scripts=scripts, styles=styles)
        self.button_label = button_label
        self.label = label
        self.default_value = default_value

    def get_module(self, request):
        template = os.path.join(TEMPLATES_PATH, 'input_button.html')
        params = {"button_label": self.button_label}
        if self.label is not None:
            params.update({"label": self.label})
        if self.default_value is not None:
            params.update({"default_value": self.default_value})
        return render_module(template, params)


class TextAreaModule(Module):
    def __init__(self, scripts=list(), styles=list(), label=None, data=''):
        scripts = [os.path.join(SCRIPTS_PATH, 'textarea.js')] + scripts
        styles = [os.path.join(STYLES_PATH, 'textarea.css')] + styles
        Module.__init__(self, scripts=scripts, styles=styles)

        self.label = label
        self.data = data

    def get_module(self, request):
        template = os.path.join(TEMPLATES_PATH, 'textarea.html')

        params = {"label": self.label,
                  'data': self.data}

        return render_module(template, params)


class AutoCompleteModule(Module):
    def __init__(self, scripts=list(), styles=list(), label=None):
        scripts = [os.path.join(SCRIPTS_PATH, 'autocomplete.js')] + scripts
        Module.__init__(self, scripts=scripts, styles=styles)

        self.label = label

    def get_module(self, request):
        template = os.path.join(TEMPLATES_PATH, 'autocomplete.html')
        params = {}

        if self.label is not None:
            params.update({"label": self.label})

        return render_module(template, params)


class CheckboxesModule(Module):
    def __init__(self, scripts=list(), styles=list(), label=None, name=None, options=None, selected=list()):
        scripts = [os.path.join(SCRIPTS_PATH, 'checkboxes.js')] + scripts
        styles = [os.path.join(STYLES_PATH, 'checkboxes.css')] + styles
        Module.__init__(self, scripts=scripts, styles=styles)
        
        if name is None:
            raise ModuleError("The name can't be empty.")

        self.selected = selected
        self.options = options if options is not None else dict()
        self.label = label

    def get_module(self, request):
        def _create_html_checkbox(input_key, input_value, checked=False):
            input_tag = '<input type="checkbox" '
            if checked:
                input_tag += 'checked '
            input_tag += 'value="' + input_key + '"/> ' + input_value

            return '<span>' + input_tag + '</span>'

        template = os.path.join(TEMPLATES_PATH, 'checkboxes.html')

        # Compute number of items in each columns
        col_nb = 3
        opt_nb = len(self.options)
        max_item_nb = int(ceil(opt_nb / col_nb))

        # Parameters initialization
        params = {
            "column1": "",
            "column2": "",
            "column3": "",
        }
        item_nb = 0
        col_id = 1
        checkboxes_html = ""

        # Filling the parameters
        for key, val in self.options.items():
            if item_nb == max_item_nb:
                params['column' + str(col_id)] = checkboxes_html

                checkboxes_html = ""
                item_nb = 0
                col_id += 1

            checkboxes_html += _create_html_checkbox(key, val, checked=(key in self.selected))
            item_nb += 1

        params['column' + str(col_id)] = checkboxes_html

        # params = {"options": checkboxes_html}

        if self.label is not None:
            params.update({"label": self.label})

        return render_module(template, params)
