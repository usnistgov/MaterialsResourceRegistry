from HTMLParser import HTMLParser
from modules.builtin.models import PopupModule, TextAreaModule, InputModule
from modules.exceptions import ModuleError
from modules.curator.forms import BLOBHosterForm, URLForm
from django.template import Context, Template
from django.conf import settings
import os
from mgi.settings import BLOB_HOSTER, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD, MDCS_URI,\
    HANDLE_SERVER_URL, HANDLE_SERVER_SCHEMA, HANDLE_SERVER_USER, HANDLE_SERVER_PSWD
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
        self.handle = blob_hoster.save(blob=uploaded_file, filename=uploaded_file.name)

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
            self.handle = blob_hoster.save(blob=uploaded_file, filename=uploaded_file.name)

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
    
