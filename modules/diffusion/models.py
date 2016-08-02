from modules.builtin.models import PopupModule
from django.conf import settings
import os
from modules.exceptions import ModuleError
import json
from modules.diffusion.forms import ExcelUploaderForm
from django.template import Context, Template
import lxml.etree as etree
from xlrd import open_workbook

RESOURCES_PATH = os.path.join(settings.SITE_ROOT, 'modules', 'diffusion', 'resources')
TEMPLATES_PATH = os.path.join(RESOURCES_PATH, 'html')
SCRIPTS_PATH = os.path.join(RESOURCES_PATH, 'js')
STYLES_PATH = os.path.join(RESOURCES_PATH, 'css')


class PeriodicTableModule(PopupModule):
    
    def __init__(self):
        with open(os.path.join(TEMPLATES_PATH, 'periodic.html'), 'r') as periodic_file:        
            periodic_table = periodic_file.read()

        PopupModule.__init__(self, popup_content=periodic_table, button_label='Select Element',
                             styles=[os.path.join(STYLES_PATH, 'periodic.css')],
                             scripts=[os.path.join(SCRIPTS_PATH, 'periodic.js')])

    def _get_module(self, request):
        return PopupModule.get_module(self, request)

    def _get_display(self, request):
        if 'data' in request.GET:
            return 'Chosen element: ' + str(request.GET['data'])
        return 'No selected element.'

    def _get_result(self, request):
        if 'data' in request.GET:
            return str(request.GET['data'])
        return ''

    def _post_display(self, request):
        if 'selectedElement' not in request.POST:
            return self._get_display(request)
        else:
            return 'Chosen element: ' + request.POST['selectedElement']

    def _post_result(self, request):
        if 'selectedElement' not in request.POST:
            return self._get_result(request)

        return request.POST['selectedElement']


class PeriodicTableMultipleModule(PopupModule):

    def __init__(self):
        with open(os.path.join(TEMPLATES_PATH, 'periodic_multiple.html'), 'r') as periodic_file:
            periodic_table = periodic_file.read()

        PopupModule.__init__(self, popup_content=periodic_table, button_label='Select Elements',
                             styles=[os.path.join(STYLES_PATH, 'periodic.css'),
                                     os.path.join(STYLES_PATH, 'periodic_multiple.css')],
                             scripts=[os.path.join(SCRIPTS_PATH, 'periodic_multiple.js')])

    def _get_module(self, request):
        return PopupModule.get_module(self, request)

    def _get_display(self, request):
        if 'data' in request.GET:
            if len(request.GET['data']) > 0:
                constituents = etree.fromstring("<constituents>" + request.GET['data'] + "</constituents>")
                
                if len(constituents) == 0:
                    return 'No element selected.'
                else:
                    constituents_disp = '<table class="table table-striped element-list">'
                    constituents_disp += '<thead><tr>'
                    constituents_disp += '<th>Element</th>'
                    constituents_disp += '<th>Quantity</th>'
                    constituents_disp += '<th>Purity</th>'
                    constituents_disp += '<th>Error</th>'
                    constituents_disp += '</tr></thead>'
                    constituents_disp += '<tbody>'
    
                    for constituent in constituents:
                        constituent_elements = list(constituent)
                        name = ""
                        quantity = ""
                        purity = ""
                        error = ""
                        for constituent_element in constituent_elements:
                            if constituent_element.tag == 'element':
                                if constituent_element.text is None:
                                    name = ''
                                else:
                                    name = constituent_element.text
                            elif constituent_element.tag == 'quantity':
                                if constituent_element.text is None:
                                    quantity = ''
                                else:
                                    quantity = constituent_element.text
                            elif constituent_element.tag == 'purity':
                                if constituent_element.text is None:
                                    purity = ''
                                else:
                                    purity = constituent_element.text
                            elif constituent_element.tag == 'error':
                                if constituent_element.text is None:
                                    error = ''
                                else:
                                    error = constituent_element.text
                    
                        constituents_disp += '<tr>'
                        constituents_disp += "<td>" + name + "</td>"
                        constituents_disp += "<td>" + quantity + "</td>"
                        constituents_disp += "<td>" + purity + "</td>"
                        constituents_disp += "<td>" + error + "</td>"
                        constituents_disp += '</tr>'
    
                    constituents_disp += '</tbody>'
                    constituents_disp += '</table>'
    
                return constituents_disp
            else:
                return 'No element selected.'
        return 'No element selected.'

    def _get_result(self, request):
        if 'data' in request.GET:
            return request.GET['data']
        return ''

    def _post_display(self, request):
        if 'elementList' in request.POST:
            element_list = json.loads(request.POST['elementList'])

            if len(element_list) == 0:
                return 'No element selected.'
            else:
                element_list_disp = '<table class="table table-striped element-list">'
                element_list_disp += '<thead><tr>'
                element_list_disp += '<th>Element</th>'
                element_list_disp += '<th>Quantity</th>'
                element_list_disp += '<th>Purity</th>'
                element_list_disp += '<th>Error</th>'
                element_list_disp += '</tr></thead>'
                element_list_disp += '<tbody>'

                for element in element_list:
                    element_list_disp += '<tr>'
                    element_list_disp += "<td>" + element['name'] + "</td>"
                    element_list_disp += "<td>" + element['qty'] + "</td>"
                    element_list_disp += "<td>" + element['pur'] + "</td>"
                    element_list_disp += "<td>" + element['err'] + "</td>"
                    element_list_disp += '</tr>'

                element_list_disp += '</tbody>'
                element_list_disp += '</table>'

            return element_list_disp
        else:
            return self._get_display(request)

    def _post_result(self, request):
        if 'elementList' in request.POST:
            element_list = json.loads(request.POST['elementList'])

            if len(element_list) == 0:
                element_list_xml = self._get_result(request)
            else:
                element_list_xml = ""

                for element in element_list:
                    element_list_xml += '<constituent>'
                    element_list_xml += "<element>" + element['name'] + "</element>"
                    element_list_xml += "<quantity>" + element['qty'] + "</quantity>"
                    element_list_xml += "<purity>" + element['pur'] + "</purity>"
                    element_list_xml += "<error>" + element['err'] + "</error>"
                    element_list_xml += '</constituent>'

            return element_list_xml
        else:
            return self._get_result(request)


class ExcelUploaderModule(PopupModule):
    def __init__(self):
        self.table = None
        self.table_name = None
        
        with open(os.path.join(TEMPLATES_PATH, 'ExcelUploader.html'), 'r') as excel_uploader_file:        
            excel_uploader = excel_uploader_file.read()            
            template = Template(excel_uploader)
            context = Context({'form': ExcelUploaderForm()})
            popup_content = template.render(context)
        
        PopupModule.__init__(self, popup_content=popup_content, button_label='Upload Excel File',
                             scripts=[os.path.join(SCRIPTS_PATH, 'exceluploader.js')],
                             styles=[os.path.join(STYLES_PATH, 'exceluploader.css')])

    def _get_module(self, request):
        if 'data' in request.GET:
            if len(request.GET['data']) > 0:
                xml_table = etree.fromstring("<table>" + request.GET['data'] + "</table>")
    
                self.table_name = 'name'
                self.table = {
                    'headers': [],
                    'values': []
                }
    
                headers = xml_table[0]
                for header in headers.iter('column'):
                    self.table['headers'].append(header.text)
    
                values = xml_table[1]
    
                for row in values.iter('row'):
                    value_list = []
    
                    for data in row.iter('column'):
                        value_list.append(data.text)
    
                    self.table['values'].append(value_list)

        return PopupModule.get_module(self, request)

    def _get_display(self, request):
        if 'data' in request.GET:
            return self.extract_html_from_table()

        return 'No file selected'

    def _get_result(self, request):
        if 'data' in request.GET:
            return request.GET['data']
        return ''

    def is_valid_table(self):
        if self.table_name is None:
            return False

        if type(self.table) != dict:
            return False

        table_keys_set = set(self.table.keys())

        if len(table_keys_set.intersection(('headers', 'values'))) != 2:
            return False

        return True

    def extract_xml_from_table(self):
        if not self.is_valid_table():
            return ""

        root = etree.Element("table")
        root.set("name", self.table_name)
        header = etree.SubElement(root, "headers")
        values = etree.SubElement(root, "rows")

        col_index = 0
        for header_name in self.table['headers']:
            header_cell = etree.SubElement(header, 'column')

            header_cell.set('id', str(col_index))
            header_cell.text = header_name

            col_index += 1

        row_index = 0
        for value_list in self.table['values']:
            value_row = etree.SubElement(values, 'row')
            value_row.set('id', str(row_index))
            col_index = 0

            for value in value_list:
                value_cell = etree.SubElement(value_row, 'column')

                value_cell.set('id', str(col_index))
                value_cell.text = value

                col_index += 1

            row_index += 1

        xml_string = etree.tostring(header)
        xml_string += etree.tostring(values)

        return xml_string

    def extract_html_from_table(self):
        if not self.is_valid_table():
            return "Table has not been uploaded or is not of correct format."

        table = etree.Element("table")
        table.set('class', 'table table-striped excel-file')
        header = etree.SubElement(table, "thead")
        header_row = etree.SubElement(header, "tr")

        for header_name in self.table['headers']:
            header_cell = etree.SubElement(header_row, 'th')
            header_cell.text = header_name

        values = etree.SubElement(table, "tbody")

        for value_list in self.table['values']:
            value_row = etree.SubElement(values, 'tr')

            for value in value_list:
                value_cell = etree.SubElement(value_row, 'td')
                value_cell.text = value

        div = etree.Element("div")
        div.set('class', 'excel_table')
        div.append(table)

        return etree.tostring(div)

    def _post_display(self, request):
        form = ExcelUploaderForm(request.POST, request.FILES)
        if not form.is_valid():
            raise ModuleError('Data not properly sent to server. Please set "file" in POST data.')

        try:
            input_excel = request.FILES['file']
            book = open_workbook(file_contents=input_excel.read())
            sheet = book.sheet_by_index(0)

            table = {
                'headers': [],
                'values': []
            }

            for row_index in range(sheet.nrows):
                row_values = []

                for col_index in range(sheet.ncols):
                    cell_text = str(sheet.cell(row_index, col_index).value)

                    if row_index == 0:
                        table['headers'].append(cell_text)
                    else:
                        row_values.append(cell_text)

                if len(row_values) != 0:
                    table['values'].append(row_values)

            self.table = table
            self.table_name = str(input_excel)

            return self.extract_html_from_table()
        except:
            return 'Something went wrong. Be sure to upload an Excel file, with correct format.' 

    def _post_result(self, request):
        return self.extract_xml_from_table()


class PeriodicTableMultipleModuleShort(PopupModule):

    def __init__(self):
        with open(os.path.join(TEMPLATES_PATH, 'periodic_multiple.html'), 'r') as periodic_file:
            periodic_table = periodic_file.read()

        PopupModule.__init__(self, popup_content=periodic_table, button_label='Select Elements',
                             styles=[os.path.join(STYLES_PATH, 'periodic.css'),
                                     os.path.join(STYLES_PATH, 'periodic_multiple.css')],
                             scripts=[os.path.join(SCRIPTS_PATH, 'periodic_multiple.js')])

    def _get_module(self, request):
        return PopupModule.get_module(self, request)

    def _get_display(self, request):
        if 'data' in request.GET:
            if len(request.GET['data']) > 0:
                constituents = etree.fromstring("<constituents>" + request.GET['data'] + "</constituents>")

                if len(constituents) == 0:
                    return 'No element selected.'
                else:
                    constituents_disp = '<table class="table table-striped element-list">'
                    constituents_disp += '<thead><tr>'
                    constituents_disp += '<th>Element</th>'
                    constituents_disp += '<th>Quantity</th>'
                    constituents_disp += '<th>Purity</th>'
                    constituents_disp += '</tr></thead>'
                    constituents_disp += '<tbody>'

                    for constituent in constituents:
                        constituent_elements = list(constituent)
                        name = ""
                        quantity = ""
                        purity = ""

                        for constituent_element in constituent_elements:
                            if constituent_element.tag == 'element':
                                if constituent_element.text is None:
                                    name = ''
                                else:
                                    name = constituent_element.text
                            elif constituent_element.tag == 'quantity':
                                if constituent_element.text is None:
                                    quantity = ''
                                else:
                                    quantity = constituent_element.text
                            elif constituent_element.tag == 'purity':
                                if constituent_element.text is None:
                                    purity = '0'
                                else:
                                    purity = constituent_element.text


                        constituents_disp += '<tr>'
                        constituents_disp += "<td>" + name + "</td>"
                        constituents_disp += "<td>" + quantity + "</td>"
                        constituents_disp += "<td>" + purity + "</td>"

                        constituents_disp += '</tr>'

                    constituents_disp += '</tbody>'
                    constituents_disp += '</table>'

                return constituents_disp
            else:
                return 'No element selected.'
        return 'No element selected.'

    def _get_result(self, request):
        if 'data' in request.GET:
            return request.GET['data']
        return ''

    def _post_display(self, request):
        if 'elementList' in request.POST:
            element_list = json.loads(request.POST['elementList'])

            if len(element_list) == 0:
                return 'No element selected.'
            else:
                element_list_disp = '<table class="table table-striped element-list">'
                element_list_disp += '<thead><tr>'
                element_list_disp += '<th>Element</th>'
                element_list_disp += '<th>Quantity</th>'
                element_list_disp += '<th>Purity</th>'

                element_list_disp += '</tr></thead>'
                element_list_disp += '<tbody>'

                for element in element_list:
                    element_list_disp += '<tr>'
                    element_list_disp += "<td>" + element['name'] + "</td>"
                    element_list_disp += "<td>" + element['qty'] + "</td>"
                    element_list_disp += "<td>" + element['pur'] + "</td>"

                    element_list_disp += '</tr>'

                element_list_disp += '</tbody>'
                element_list_disp += '</table>'
            return element_list_disp
        else:
            return self._get_display(request)

    def _post_result(self, request):
        if 'elementList' in request.POST:
            element_list = json.loads(request.POST['elementList'])

            if len(element_list) == 0:
                element_list_xml = self._get_result(request)
            else:
                element_list_xml = ""

                for element in element_list:
                    element_list_xml += '<constituent>'
                    element_list_xml += "<element>" + element['name'] + "</element>"
                    element_list_xml += "<quantity>" + element['qty'] + "</quantity>"
                    if element['pur'] != '':
                        element_list_xml += "<purity>" + element['pur'] + "</purity>"


                    element_list_xml += '</constituent>'
            return element_list_xml
        else:
            return self._get_result(request)
