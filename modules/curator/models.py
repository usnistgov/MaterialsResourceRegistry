from HTMLParser import HTMLParser
from curate.models import SchemaElement
from modules.builtin.models import PopupModule, TextAreaModule, InputModule, AutoCompleteModule, OptionsModule
from modules.exceptions import ModuleError
from modules.curator.forms import BLOBHosterForm, URLForm
from django.template import Context, Template
import os
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
MONGODB_URI = settings.MONGODB_URI
MGI_DB = settings.MGI_DB
BLOB_HOSTER = settings.BLOB_HOSTER
BLOB_HOSTER_URI = settings.BLOB_HOSTER_URI
BLOB_HOSTER_USER = settings.BLOB_HOSTER_USER
BLOB_HOSTER_PSWD = settings.BLOB_HOSTER_PSWD
MDCS_URI = settings.MDCS_URI
HANDLE_SERVER_URL = settings.HANDLE_SERVER_URL
HANDLE_SERVER_SCHEMA = settings.HANDLE_SERVER_SCHEMA
HANDLE_SERVER_USER = settings.HANDLE_SERVER_USER
HANDLE_SERVER_PSWD = settings.HANDLE_SERVER_PSWD
from utils.BLOBHoster.BLOBHosterFactory import BLOBHosterFactory
from lxml import etree
from lxml.etree import XMLSyntaxError
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import requests
import json

RESOURCES_PATH = os.path.join(settings.SITE_ROOT, 'modules', 'curator', 'resources')
TEMPLATES_PATH = os.path.join(RESOURCES_PATH, 'html')
SCRIPTS_PATH = os.path.join(RESOURCES_PATH, 'js')
STYLES_PATH = os.path.join(RESOURCES_PATH, 'css')


class BlobHosterModule(PopupModule):

    def __init__(self):
        self.handle = None

        with open(os.path.join(TEMPLATES_PATH, 'BLOBHoster.html'), 'r') as blobhoster_file:        
            blobhoster = blobhoster_file.read()            
            template = Template(blobhoster)
            context = Context({'form': BLOBHosterForm()})
            popup_content = template.render(context)
        
        PopupModule.__init__(self, popup_content=popup_content, button_label='Upload File',
                             scripts=[os.path.join(SCRIPTS_PATH, 'blobhoster.js')])

    def _get_module(self, request):
        return PopupModule.get_module(self, request)

    def _get_display(self, request):
        if 'data' in request.GET:
            if len(request.GET['data']) > 0:
                return '<b>Handle: </b> <a href="' + request.GET['data'] + '">' + request.GET['data'] + '</a>' 
        return 'No files selected'

    def _get_result(self, request):
        if 'data' in request.GET:
            if len(request.GET['data']) > 0:
                return request.GET['data']
        return ''

    def _post_display(self, request):
        form = BLOBHosterForm(request.POST, request.FILES)
        if not form.is_valid():
            raise ModuleError('Data not properly sent to server. Please "file" in POST data.')

        uploaded_file = request.FILES['file']
        bh_factory = BLOBHosterFactory(BLOB_HOSTER, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD, MDCS_URI)
        blob_hoster = bh_factory.createBLOBHoster()
        self.handle = blob_hoster.save(blob=uploaded_file, filename=uploaded_file.name, userid=str(request.user.id))

        with open(os.path.join(TEMPLATES_PATH, 'BLOBHosterDisplay.html'), 'r') as display_file:
            display = display_file.read()
            template = Template(display)
            context = Context({'filename': uploaded_file.name, 'handle': self.handle})

        return template.render(context)

    def _post_result(self, request):
        return self.handle if self.handle is not None else ''
        

class RemoteBlobHosterModule(InputModule):
   
    
    def __init__(self):
        self.handle = None
        
        InputModule.__init__(self, label='Enter the URL of a file :')


    def _get_module(self, request):
        return InputModule.get_module(self, request)

 
    def _get_display(self, request):
        if 'data' in request.GET:
            if len(request.GET['data']) > 0:
                return '<b>Handle: </b> <a href="' + request.GET['data'] + '">' + request.GET['data'] + '</a>' 
        return 'No files selected'

    
    def _get_result(self, request):
        if 'data' in request.GET:
            if len(request.GET['data']) > 0:
                return request.GET['data']
        return ''


    def _post_display(self, request):
        url = ''
        if 'data' in request.POST:
            url = request.POST['data']
        
        url_validator = URLValidator()
        self.handle = ''
        try:
            url_validator(url)
            self.handle = url
            with open(os.path.join(TEMPLATES_PATH, 'RemoteBLOBHosterDisplay.html'), 'r') as display_file:
                display = display_file.read()
                template = Template(display)
                context = Context({'handle': url})
            return template.render(context)
        except ValidationError, e:
            return '<b style="color:red;">' + '<br/>'.join(e.messages) + '</b>'


    def _post_result(self, request):
        return self.handle if self.handle is not None else ''


class AdvancedBlobHosterModule(PopupModule):
    
    
    def __init__(self):
        self.handle = None

        with open(os.path.join(TEMPLATES_PATH, 'AdvancedBLOBHoster.html'), 'r') as blobhoster_file:        
            blobhoster = blobhoster_file.read()            
            template = Template(blobhoster)
            context = Context({'url_form': URLForm() ,'file_form': BLOBHosterForm()})
            popup_content = template.render(context)
        
        PopupModule.__init__(self, popup_content=popup_content, button_label='Upload File',
                             scripts=[os.path.join(SCRIPTS_PATH, 'advancedblobhoster.js')])

    
    def _get_module(self, request):
        return PopupModule.get_module(self, request)

    
    def _get_display(self, request):
        if 'data' in request.GET:
            if len(request.GET['data']) > 0:
                return '<b>Handle: </b> <a href="' + request.GET['data'] + '">' + request.GET['data'] + '</a>' 
        return 'No files selected'

    
    def _get_result(self, request):
        if 'data' in request.GET:
            if len(request.GET['data']) > 0:
                return request.GET['data']
        return ''

    
    def _post_display(self, request):     
        self.handle = '' 
        selected_option = request.POST['blob_form']
        if selected_option == "url":
            url_form = URLForm(request.POST)
            if url_form.is_valid():
                self.handle = url_form.data['url']
                with open(os.path.join(TEMPLATES_PATH, 'RemoteBLOBHosterDisplay.html'), 'r') as display_file:
                    display = display_file.read()
                    template = Template(display)
                    context = Context({'handle': self.handle})
                return template.render(context)
            else:
                return '<b style="color:red;">Enter a valid URL.</b>'           
        elif selected_option == "file":            
            uploaded_file = request.FILES['file']
            bh_factory = BLOBHosterFactory(BLOB_HOSTER, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD, MDCS_URI)
            blob_hoster = bh_factory.createBLOBHoster()
            self.handle = blob_hoster.save(blob=uploaded_file, filename=uploaded_file.name, userid=str(request.user.id))

            with open(os.path.join(TEMPLATES_PATH, 'BLOBHosterDisplay.html'), 'r') as display_file:
                display = display_file.read()
                template = Template(display)
                context = Context({'filename': uploaded_file.name, 'handle': self.handle})

            return template.render(context)

    
    def _post_result(self, request):
        return self.handle if self.handle is not None else ''


class RawXMLModule(TextAreaModule):
    def __init__(self):
        self.parser = HTMLParser()

        TextAreaModule.__init__(self, label="Raw XML", data="Insert XML Data here...")

    def _get_module(self, request):
        xml_string = ''
        if 'data' in request.GET:
            data = request.GET['data']
            xml_data = etree.fromstring(data)
            for xml_data_element in xml_data:
                xml_string += etree.tostring(xml_data_element)
        
        if xml_string != '':
            self.data = xml_string
        return TextAreaModule.get_module(self, request)

    def _get_display(self, request):
        data = request.GET['data'] if 'data' in request.GET else ''
        return self.disp(data)

    def disp(self, data):
        if data == '':
            return '<span class="notice">Please enter XML in the text area located above</span>'
        try:
            self.parse_data(data)
            return '<span class="success">XML entered is well-formed</span>'
        except XMLSyntaxError, e:
            return '<span class="error">XML error: ' + e.message + '</span>'

    def parse_data(self, data):
        unescaped_data = self.parser.unescape(data)
        etree.fromstring(''.join(['<root>', unescaped_data ,'</root>']))
        return data

    def _get_result(self, request):
        if 'data' not in request.GET:
            return ''

        try:
            return self.parse_data(request.GET['data'])
        except XMLSyntaxError:
            return ''

    def _is_data_valid(self, data):
        try:
            self.parse_data(data)
            return True
        except XMLSyntaxError:
            return False

    def _post_display(self, request):
        data = request.POST['data'] if 'data' in request.POST else ''
        return self.disp(data)

    def _post_result(self, request):
        if 'data' not in request.POST:
            return ''

        try:
            return self.parse_data(request.POST['data'])
        except XMLSyntaxError:
            return ''


class HandleModule(PopupModule):
    def __init__(self):
        scripts = [os.path.join(SCRIPTS_PATH, 'handle.js')]
        styles = []
        
        popup_content = "<p style='color:red;'>"
        popup_content += "Warning: You are about to request an handle for this document.<br/>" 
        popup_content += "Clicking on 'Save' will generate a request to the Handle System."
        popup_content += "A unique handle will be created for this document and it will be registered on the Handle System." 
        popup_content += "</p>"
        button_label = "Get a unique handle"
                
        PopupModule.__init__(self, scripts, styles, popup_content, button_label)

    def _get_module(self, request):
        self.handle = ""
        if 'data' in request.GET:
            self.handle = request.GET['data']        
        return PopupModule.get_module(self, request)

    def _get_display(self, request):
        if self.handle == '':
            message = "<b style='color:red;'>"
            message += "This document is not associated to any handle."
            message += "</b><br/>"
            return message
        else:
            return '<b>Handle</b>: ' + self.handle 

    def _get_result(self, request):
        return self.handle

    def _post_display(self, request):
        self.handle = ''    
        if 'data' in request.POST:
            if request.POST['data'] != '':
                self.handle = request.POST['data']
                message = "<b style='color:red;'>"
                message += "An handle has already been associated to this document."
                message += "</b><br/>"
                message += '<b>Handle</b>: ' + self.handle                  
                return message
            
            # get a unique handle from the handle provider
            url_validator = URLValidator()
            try:
                handle_server_api = HANDLE_SERVER_URL + '/registrar/objects/?type=' + HANDLE_SERVER_SCHEMA
                url_validator(handle_server_api)
                try:
                    headers = {}
                    data = json.dumps({})
                    r = requests.post(handle_server_api, data=data, headers=headers, auth=(HANDLE_SERVER_USER, HANDLE_SERVER_PSWD))
                    if r.status_code != 200:
                        return 'The Handle System returned an error.'
                    try:
                        location = r.headers['location']
                        self.handle = HANDLE_SERVER_URL + '/registrar' + location
                    except:
                        return 'The Handle System did not return a valid handle.'
                except:
                    return 'An error occurred while trying to contact the Handle System.'
            except:
                return 'Invalid URL for the Handle System.'
            return '<b>Handle</b>: ' + self.handle 
        else:
            return ''

    def _post_result(self, request):
        return self.handle


class EnumAutoCompleteModule(AutoCompleteModule):

    def __init__(self):
        scripts = [os.path.join(SCRIPTS_PATH, 'enum_auto_complete.js')]
        AutoCompleteModule.__init__(self, scripts=scripts)

    @staticmethod
    def display_element(element=None, data=None):
        if element is None or element == "":
            return "No element selected"
        else:
            display_str = "Selected element: "+str(element) + " "

            if element in data:
                display_str += '<i class="fa fa-check" style="color: green"></i>'
            else:
                display_str += '<i class="fa fa-times" style="color: red"></i>'

            return display_str

    @staticmethod
    def get_enumerations(namespaces, prefix, doctree, xsd_xpath=None):
        enums = []

        # get the values of the enumeration
        xml_doctree_str = doctree
        xml_doctree = etree.fromstring(xml_doctree_str)

        namespace = namespaces[prefix]

        xpath_namespaces = {}
        for prefix, ns in namespaces.iteritems():
            xpath_namespaces[prefix] = ns[1:-1]

        # get the element where the module is attached
        xsd_element = xml_doctree.xpath(xsd_xpath, namespaces=xpath_namespaces)[0]
        enumeration_list = xsd_element.findall('./{0}restriction/{0}enumeration'.format(namespace))

        for enumeration in enumeration_list:
            enums.append(enumeration.attrib['value'])

        return enums

    def _get_module(self, request):
        return AutoCompleteModule.get_module(self, request)

    def _get_display(self, request):
        xsd_xpath = request.GET['xsd_xpath']
        display_str = '<span class="hide">' + xsd_xpath + '</span>'

        if 'data' in request.GET:
            data = self.get_enumerations(request.session['namespaces'], request.session['defaultPrefix'],
                                         request.session['xmlDocTree'], xsd_xpath)

            display_str += self.display_element(request.GET['data'], data)
        else:
            display_str += self.display_element()

        return display_str

    def _get_result(self, request):
        return request.GET['data'] if 'data' in request.GET else ''

    def _post_display(self, request):
        xsd_xpath = request.POST['xsd_xpath']

        if 'list' in request.POST:
            data = self.get_enumerations(request.session['namespaces'], request.session['defaultPrefix'],
                                         request.session['xmlDocTree'], xsd_xpath)
            response_list = []

            for term in data:
                if request.POST['list'].lower() in term.lower():
                    response_list.append(term)

            return response_list

        if 'data' in request.POST:
            display_str = '<span class="hide">' + xsd_xpath + '</span>'

            if 'data' in request.POST:
                data = self.get_enumerations(request.session['namespaces'], request.session['defaultPrefix'],
                                             request.session['xmlDocTree'], xsd_xpath)

                display_str += self.display_element(request.POST['data'], data)
            else:
                display_str += self.display_element()

            return display_str

    def _post_result(self, request):
        return request.POST['data'] if 'data' in request.POST else ''


class AutoKeyRefModule(OptionsModule):
    def __init__(self):
        OptionsModule.__init__(self, options={}, scripts=[os.path.join(SCRIPTS_PATH, 'autokey.js')])

    def _get_module(self, request):
        # look for existing values
        try:
            # keyrefId = request.GET['keyref'] if 'keyref' in request.GET else None
            module_id = request.GET['module_id']
            module = SchemaElement.objects().get(pk=module_id)
            keyrefId = module.options['params']['keyref']
            # register the module id in the structure
            if str(module_id) not in request.session['keyrefs'][keyrefId]['module_ids']:
                request.session['keyrefs'][keyrefId]['module_ids'].append(str(module_id))

            # get the list of values for this key
            keyId = request.session['keyrefs'][keyrefId]['refer']
            values = []
            modules_ids = request.session['keys'][keyId]['module_ids']
            for key_module_id in modules_ids:
                key_module = SchemaElement.objects().get(pk=key_module_id)
                if key_module.options['data'] is not None:
                    values.append(key_module.options['data'])

            # add empty value
            self.options.update({'': ''})
            for value in values:
                self.options.update({str(value): str(value)})

            self.selected = ''
            if 'data' in request.GET:
                self.selected = request.GET['data']
            elif 'data' in module.options and module.options['data'] is not None:
                self.selected = str(module.options['data'])
        except Exception:
            self.options = {}
        return OptionsModule.get_module(self, request)

    def _get_display(self, request):
        return ''

    def _get_result(self, request):
        return self.selected

    def _post_display(self, request):
        return ''

    def _post_result(self, request):
        if 'data' in request.POST:
            return request.POST['data']
        return ''
