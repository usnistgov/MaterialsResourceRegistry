from modules.builtin.models import InputModule, OptionsModule, SyncInputModule, AutoCompleteModule,\
    CheckboxesModule
from modules.exceptions import ModuleError
from django.conf import settings
import os
from modules.xpathaccessor import XPathAccessor
from modules.models import Module


RESOURCES_PATH = os.path.join(settings.SITE_ROOT, 'modules', 'examples', 'resources')
TEMPLATES_PATH = os.path.join(RESOURCES_PATH, 'html')
SCRIPTS_PATH = os.path.join(RESOURCES_PATH, 'js')
STYLES_PATH = os.path.join(RESOURCES_PATH, 'css')


class PositiveIntegerInputModule(InputModule):
    def __init__(self):
        InputModule.__init__(self, label='Enter positive integer', default_value=1)

    def _get_module(self, request):
        if 'data' in request.GET:
            self.default_value = request.GET['data']

        return InputModule.get_module(self, request)

    def is_data_valid(self, data):
        try:
            value = int(data)
            if value >= 0:
                return True
            else:
                return False
        except ValueError:
            return False

    def _get_display(self, request):
        if 'data' in request.GET:
            data = str(request.GET['data'])
            return data + " is a positive integer" if self.is_data_valid(data) else "<div style='color:red;'>This is not a positive integer</div>"
        return str(self.default_value) + ' is a positive integer'

    def _get_result(self, request):
        if 'data' in request.GET:
            return str(request.GET['data'])
        return str(self.default_value)

    def _post_display(self, request):
        data = str(request.POST['data'])
        return data + " is a positive integer" if self.is_data_valid(data) \
            else "<div style='color:red;'>This is not a positive integer</div>"

    def _post_result(self, request):
        return str(request.POST['data'])


class ChemicalElementMappingModule(OptionsModule):
    
    def __init__(self):
        self.options = {
            'Ac': 'Actinium',
            'Al': 'Aluminum',
            'Ag': 'Silver',
            'Am': 'Americium',
            'Ar': 'Argon',
            'As': 'Arsenic',
            'At': 'Astatine',
            'Au': 'Gold'
        }
                
        OptionsModule.__init__(self, options=self.options, label='Select an element')

    def _get_module(self, request):
        return OptionsModule.get_module(self, request)

    def _get_display(self, request):
        return self.options.values()[0] + ' is selected'

    def _get_result(self, request):
        return self.options.keys()[0]

    def _post_display(self, request):
        data = str(request.POST['data'])
        return self.options[data] + ' is selected'

    def _post_result(self, request):
        return str(request.POST['data'])


class ListToGraphInputModule(SyncInputModule):
    
    def __init__(self):
        SyncInputModule.__init__(self, label='Enter a list of numbers', modclass='list_to_graph',
                                  styles=[os.path.join(STYLES_PATH, 'list_to_graph.css')],
                                  scripts=["https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js",
                                           os.path.join(SCRIPTS_PATH, 'list_to_graph.js')])

    def _get_module(self, request):
        return SyncInputModule.get_module(self, request)

    def _get_display(self, request):
        return ''

    def _get_result(self, request):
        return ''

    def _is_data_valid(self, data):
        values = data.split(' ')

        for value in values:
            try:
                int(value)
            except ValueError:
                return False

        return True

    def _post_display(self, request):
        if 'data' not in request.POST:
            raise ModuleError('No data sent to server.')

        display = "<div class='chart'></div>"

        if not self._is_data_valid(request.POST['data']):
            display = "<b style='color:red;'>Expecting a list of integer values separated by spaces.</b>"

        return display

    def _post_result(self, request):
        return request.POST['data']


class ExampleAutoCompleteModule(AutoCompleteModule):

    def __init__(self):
        self.data = [
            'Plastic',
            'Concrete',
            'Cement',
            'Material1',
            'Material2',
            'Material3',
            'Others'
        ]

        AutoCompleteModule.__init__(self, label='Material Name', scripts=[os.path.join(SCRIPTS_PATH,
                                                                                       'example_autocomplete.js')])

    def _get_module(self, request):
        return AutoCompleteModule.get_module(self, request)

    def _get_display(self, request):
        return ''

    def _get_result(self, request):
        return ''

    def _post_display(self, request):
        if 'list' in request.POST:
            response_list = []

            for term in self.data:
                if request.POST['list'].lower() in term.lower():
                    response_list.append(term)

            return response_list

        if 'data' in request.POST:
            return request.POST['data']

    def _post_result(self, request):
        if 'data' in request.POST:
            return request.POST['data']

        return ''


class CountriesModule(OptionsModule, XPathAccessor):
    country_codes = {
                     'None': '',
                     'FRANCE': 'FR',
                     'UNITED STATES OF AMERICA': 'USA',
                     }
    
    capitals = {
                'None': '',
                'FRANCE': 'PARIS',
                'UNITED STATES OF AMERICA': 'WASHINGTON DC',
                }
    
    anthems = {
               'None': '',
               'FRANCE': 'La Marseillaise',
               'UNITED STATES OF AMERICA': 'The Star-Sprangled Banner',
               }
    
    flags = {
             'None': 'None',
             'FRANCE': 'Tricolour',
             'UNITED STATES OF AMERICA': 'The Stars and Stripes',
             }
    
    languages = {
             'None': '',
             'FRANCE': 'FRENCH',
             'UNITED STATES OF AMERICA': 'ENGLISH',
             }
    
    def __init__(self):
        self.options = {
            'None': '--------',
            'FRANCE': 'France',
            'UNITED STATES OF AMERICA': 'USA',
        }
                
        OptionsModule.__init__(self, options=self.options, label='Select a Country',
                               scripts=[os.path.join(SCRIPTS_PATH, 'countries.js')])

    def _get_module(self, request):
        return OptionsModule.get_module(self, request)

    def _get_display(self, request):
        return ''

    def _get_result(self, request):     
        if 'data' in request.GET:
            return str(request.GET['data'])
        return ''

    def _post_display(self, request):
        return ''

    def _post_result(self, request):
        # get the selected value
        value = str(request.POST['data'])
        
        # create the XPathAccessor
        XPathAccessor.__init__(self, request)
        
        return value
        
    def set_XpathAccessor(self, request):
        # get the selected value
        if 'data' not in request.POST:
            return

        value = str(request.POST['data'])

        if value not in self.country_codes.keys():  # FIXME loose test, fix datastrcture
            return
        
        # get values to return for siblings
        country_code = self.country_codes[value]
        capital = self.capitals[value]
        anthem = self.anthems[value]
        language = self.languages[value]
        flag = self.flags[value]
         
        # get xpath of current node (for dynamic xpath building)
        module_xpath = self.get_xpath()
        parent_xpath = "/".join(module_xpath.split("/")[:-1])
        parent_xpath_idx = parent_xpath[parent_xpath.rfind("[")+1:-1]
        idx = "[" + str(parent_xpath_idx) + "]"
         
        # set nodes with values
        form_id = request.session['form_id']

        self.set_xpath_value(form_id, '/Countries[1]/country' + idx + '/country_code', country_code)
        self.set_xpath_value(form_id, '/Countries[1]/country' + idx + '/details[1]/capital', capital)
        self.set_xpath_value(form_id, '/Countries[1]/country' + idx + '/details[1]/anthem', anthem)
        self.set_xpath_value(form_id, '/Countries[1]/country' + idx + '/details[1]/language', language)
        self.set_xpath_value(form_id, '/Countries[1]/country' + idx + '/details[1]/flag', {'data': flag})


class FlagModule(Module):
    
    images = {
        'The Stars and Stripes': "<img src='https://upload.wikimedia.org/wikipedia/en/a/a4/Flag_of_the_United_States.svg' height='42' width='42'/>",
        'Tricolour': "<img src='https://upload.wikimedia.org/wikipedia/commons/c/c3/Flag_of_France.svg' height='42' width='42'/>"
    }
    
    def __init__(self):                
        Module.__init__(self)

    def _get_module(self, request):
        return ''

    def _get_display(self, request):
        if 'data' in request.GET:
            image_id = str(request.GET['data'])

            if image_id in self.images.keys():
                return self.images[image_id]

        return ''

    def _get_result(self, request):
        if 'data' in request.GET:
            return str(request.GET['data'])
        return ''

    def _post_display(self, request):
        if 'data' in request.POST:
            image_id = str(request.POST['data'])

            if image_id in self.images.keys():
                return self.images[image_id]

        return ''

    def _post_result(self, request):
        return str(request.POST['data'])


class ChemicalElementCheckboxesModule(CheckboxesModule):
    
    def __init__(self):
        self.options = {
            'Ac': 'Actinium',
            'Al': 'Aluminum',
            'Ag': 'Silver',
            'Am': 'Americium',
            'Ar': 'Argon',
            'As': 'Arsenic',
            'At': 'Astatine',
            'Au': 'Gold'
        }
                
        CheckboxesModule.__init__(self, options=self.options, label='Select elements', name='chemical')

    def _get_module(self, request):
        return CheckboxesModule.get_module(self, request)

    def _get_display(self, request):
        return ''

    def _get_result(self, request):
        return ''

    def _post_display(self, request):
        return ''

    def _post_result(self, request):
        if 'data[]' in request.POST:
            return str(request.POST['data[]'])
