from io import BytesIO
from mgi.common import LXML_SCHEMA_NAMESPACE
from modules.models import Module
from modules.builtin.models import CheckboxesModule, OptionsModule, InputModule, \
    TextAreaModule
import os
import lxml.etree as etree
from pymongo import MongoClient
from django.utils.importlib import import_module
from mgi import models as mgi_models, common
import random
import string
from mgi.models import Status
from forms import NamePIDForm
from django.template import Context, Template
import HTMLParser
import json
from collections import OrderedDict

from utils.XSDRefinements.Tree import TreeInfo, print_tree

settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
MONGODB_URI = settings.MONGODB_URI
MGI_DB = settings.MGI_DB

RESOURCES_PATH = os.path.join(settings.SITE_ROOT, 'modules', 'registry', 'resources')
TEMPLATES_PATH = os.path.join(RESOURCES_PATH, 'html')
SCRIPTS_PATH = os.path.join(RESOURCES_PATH, 'js')
STYLES_PATH = os.path.join(RESOURCES_PATH, 'css')


class NamePIDModule(Module):
    """
    Name PID Module
    """
    def __init__(self):
        Module.__init__(self, scripts=[os.path.join(SCRIPTS_PATH, 'namepid.js')])
        # This modules automatically manages occurences
        self.is_managing_occurences = True

    def _get_module(self, request):
        with open(os.path.join(TEMPLATES_PATH, 'name_pid.html'), 'r') as template_file:
            template_content = template_file.read()
            template = Template(template_content)

            self.params = {}

            xml_xpath = request.GET['xml_xpath']
            xml_xpath = xml_xpath.split('/')[-1]
            idx = xml_xpath.rfind("[")
            xml_xpath = xml_xpath[0:idx]
            if ':' in xml_xpath:
                xml_xpath = xml_xpath.split(':')[1]

            self.params['tag'] = xml_xpath

            if 'data' in request.GET:
                xml_element = etree.fromstring(request.GET['data'])
                self.params['name'] = xml_element.text if xml_element.text is not None else ''
                if 'pid' in xml_element.attrib:
                    self.params['pid'] = xml_element.attrib['pid'] if xml_element.attrib['pid'] is not None else ''

            context = Context({'form': NamePIDForm(self.params)})
            return template.render(context)

    def _get_display(self, request):
        return ''

    def _get_result(self, request):
        pid = ' pid="' + self.params['pid'] + '"' if 'pid' in self.params else ''
        name = self.params['name'] if 'name' in self.params else ''
        return '<' + self.params['tag'] + pid + '>' + name + '</' + self.params['tag'] + '>'

    def _post_display(self, request):
        form = NamePIDForm(request.POST)
        if not form.is_valid():
            return '<p style="color:red;">Entered values are not correct.</p>'
        return ''

    def _post_result(self, request):
        pid = ' pid="' + request.POST['pid'] + '"' if 'pid' in request.POST and len(request.POST['pid']) > 0 else ''
        if 'name' in request.POST and request.POST['name'] != '':
            return '<' + request.POST['tag'] + pid + '>' + request.POST['name'] + '</' + request.POST['tag'] + '>'

        return '<' + request.POST['tag'] + pid + '></' + request.POST['tag'] + '>'


class RegistryCheckboxesModule(CheckboxesModule):
    """
    Module to transform an enumeration in checkboxes
    """
    def __init__(self, xml_tag):
        self.xml_tag = xml_tag
        self.selected = []
        CheckboxesModule.__init__(self, options={}, label='', name='')

        # This modules automatically manages occurences
        self.is_managing_occurences = True

    def _get_module(self, request):
        self.selected = []
        # get the values of the enumeration
        xml_doc_tree_str = request.session['xmlDocTree']
        xml_doc_tree = etree.fromstring(xml_doc_tree_str)

        namespaces = common.get_namespaces(BytesIO(str(xml_doc_tree_str)))

        # get the element where the module is attached
        xsd_element = xml_doc_tree.xpath(request.GET['xsd_xpath'], namespaces=namespaces)[0]
        xsd_element_type = xsd_element.attrib['type']
        # remove ns prefix if present
        if ':' in xsd_element_type:
            xsd_element_type = xsd_element_type.split(':')[1]
        xpath_type = "./{0}simpleType[@name='{1}']".format(LXML_SCHEMA_NAMESPACE, xsd_element_type)
        elementType = xml_doc_tree.find(xpath_type)
        enumeration_list = elementType.findall('./{0}restriction/{0}enumeration'.format(LXML_SCHEMA_NAMESPACE))
        
        for enumeration in enumeration_list:
            self.options[enumeration.attrib['value']] = enumeration.attrib['value']
        if 'data' in request.GET:
            data = request.GET['data']
            # get XML to reload
            reload_data = etree.fromstring("<root>" + data + "</root>")
            for child in reload_data:
                if child.text is not None:
                    self.selected.append(child.text.strip())
        
        return CheckboxesModule.get_module(self, request)

    def _get_display(self, request):
        self.wrong_values = []
        for value in self.selected:
            if value not in self.options.values():
                self.wrong_values.append(value)
        if len(self.wrong_values) > 0:
            return '<span style="color:red;">Incorrect values found: ' + ', '.join(self.wrong_values) + "</span>"

        return ''

    def _get_result(self, request):
        xml_result = ''
        for value in self.selected:
            if value not in self.wrong_values:
                xml_result += '<' + self.xml_tag + '>' + value + '</' + self.xml_tag + '>'
        return xml_result

    def _post_display(self, request):
        return ''

    def _post_result(self, request):
        xml_result = ''
        if 'data[]' in request.POST:
            for value in dict(request.POST)['data[]']:
                xml_result += '<' + self.xml_tag + '>' + value + '</' + self.xml_tag + '>'
        return xml_result


class StatusModule(OptionsModule):
    """
    Module to manage the status attribute
    """
    def __init__(self):
        self.options = {
            Status.INACTIVE: 'Inactive',
            Status.ACTIVE: 'Active',
        }

        OptionsModule.__init__(self, options=self.options, disabled=True)

    def _get_module(self, request):
        self.selected = Status.ACTIVE
        if 'data' in request.GET:
            if request.GET['data'] in self.options.keys():
                self.disabled = False
                self.selected = request.GET['data']
        return OptionsModule.get_module(self, request)

    def _get_display(self, request):
        return ''

    def _get_result(self, request):
        return self.selected

    def _post_display(self, request):
        return ''

    def _post_result(self, request):
        return str(request.POST['data'])


class LocalIDModule(InputModule):
    """
    Module to manage the Local ID attribute
    """
    def __init__(self):
        InputModule.__init__(self, disabled=True)

    def _get_module(self, request):
        if 'data' in request.GET:
            self.default_value = request.GET['data']
        else:
            # create a connection
            client = MongoClient(MONGODB_URI)
            # connect to the db 'mgi'
            db = client[MGI_DB]
            # get the xmldata collection
            xmldata = db['xmldata']
            # find all objects of the collection
            cursor = xmldata.find()
            # build a list with the objects
            existing_localids = []
            for result in cursor:
                try:
                    existing_localids.append(result['content']['Resource']['@localid'])
                except:
                    pass

            N = 20
            localid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
            while localid in existing_localids:
                localid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

            self.default_value = localid
        return InputModule.get_module(self, request)

    def _get_display(self, request):
        return ''

    def _get_result(self, request):
        return self.default_value

    def _post_display(self, request):
        return ''

    def _post_result(self, request):
        return str(request.POST['data'])


class DescriptionModule(TextAreaModule):
    """
    Module to replace description fields by textareas
    """
    def __init__(self):
        self.data = ''
        TextAreaModule.__init__(self)

    def _get_module(self, request):
        if 'data' in request.GET:
            self.data = str(request.GET['data'].encode("utf-8"))
        return TextAreaModule.get_module(self, request)

    def _get_display(self, request):
        return ''

    def _get_result(self, request):
        # return '<description>' + self.data + '</description>'
        return self.data

    def _post_display(self, request):
        return ''

    def _post_result(self, request):
        # return '<description>' + request.POST['data'] + '</description>'
        return request.POST['data']


class TypeModule(InputModule):
    """
    Module to lock type field to selected resource type
    """

    templates = {
        'organization': 'Organization',
        'datacollection': 'Data Collection',
        'repository': 'Repository',
        'projectarchive': 'Project Archive',
        'database': 'Database',
        'dataset': 'Dataset',
        'service': 'Service',
        'informational': 'Informational',
        'software': 'Software',
    }

    def __init__(self):
        self.default_value = ''
        InputModule.__init__(self, disabled=True)

    def _get_module(self, request):
        if 'data' in request.GET:
            self.default_value = request.GET['data']
            # if data present and not in enumeration, can be edited
            if self.default_value not in self.templates.values():
                self.disabled = False
        else:
            if 'currentTemplateID' in request.session:
                try:
                    template = mgi_models.Template.objects().get(pk=request.session['currentTemplateID'])
                    template_name = template.title
                    try:
                        self.default_value = self.templates[template_name]
                    except:
                        self.disabled = False
                        self.default_value = ''
                except:
                    self.disabled = False
                    self.default_value = ''
            else:
                self.disabled = False
                self.default_value = ''
        return InputModule.get_module(self, request)

    def _get_display(self, request):
        if self.default_value not in self.templates.values():
            return '<span style="color:red;">Type should be in ' + ','.join(self.templates.values()) + ' </span>'
        return ''

    def _get_result(self, request):
        return self.default_value

    def _post_display(self, request):
        if request.POST['data'] not in self.templates.values():
            return '<span style="color:red;">Type should be in ' + ', '.join(self.templates.values()) + ' </span>'
        return ''

    def _post_result(self, request):
        return str(request.POST['data'])


class FancyTreeModule(Module):
    """
    Module to transform an enumeration in fancy tree
    """
    def __init__(self, xml_tag):
        self.xml_tag = xml_tag
        self.selected = []
        Module.__init__(self, scripts=[os.path.join(SCRIPTS_PATH, 'fancy_tree.js')])

        # This modules automatically manages occurrences
        self.is_managing_occurences = True

    def _get_module(self, request):
        # Get HTML of the module
        with open(os.path.join(TEMPLATES_PATH, 'fancy_tree.html'), 'r') as template_file:
            template_content = template_file.read()
            template = Template(template_content)

        # *** GET RELOAD DATA ***

        # If data are provided to reload the module
        if 'data' in request.GET:
            # get the data
            data = request.GET['data']
            # build tree of data to reload (need a root element because data is a list of xml elements)
            reload_data = etree.fromstring("<root>" + data + "</root>")
            # Iterate xml elements
            for reload_data_element in list(reload_data):
                try:
                    # The xml element to be reloaded is the child
                    child = reload_data_element[0]

                    # remove namespace form tag name if present: {namespace}tag
                    tag_name = child.tag
                    if "}" in tag_name:
                        end_namespace_index = tag_name.index("}")
                        tag_name = tag_name[end_namespace_index+1:]

                    # get the content of the xml element
                    child_text = etree.tostring(child)
                    # remove namespace from xml value if present: <tag xmlns="">value</tag>
                    if "xmlns=" in child_text:
                        end_tag_index = child_text.index(">")
                        xml_value = child_text[:len(tag_name)+1] + child_text[end_tag_index:]
                    else:
                        xml_value = child_text

                    # add selected value to list
                    self.selected.append(xml_value)
                except (IndexError, Exception):
                    pass

        # *** GET POSSIBLE VALUES FROM ENUMERATION AND BUILD FANCY TREE ***

        # load XSD string
        xml_doc_tree_str = request.session['xmlDocTree']
        # build XSD tree
        xml_doc_tree = etree.fromstring(xml_doc_tree_str)

        # get namespaces used in the schema
        namespaces = common.get_namespaces(BytesIO(str(xml_doc_tree_str)))

        # get the element where the module is attached
        xsd_element = xml_doc_tree.xpath(request.GET['xsd_xpath'], namespaces=namespaces)[0]
        # get the type name of the element
        xsd_element_type = xsd_element.attrib['type']
        # remove ns prefix if present
        if ':' in xsd_element_type:
            xsd_element_type = xsd_element_type.split(':')[1]
        # xpath to the type in the schema
        xpath_type = "./{0}complexType[@name='{1}']".format(LXML_SCHEMA_NAMESPACE, xsd_element_type)
        # find the type in the schema
        element_type = xml_doc_tree.find(xpath_type)
        # look for the choice in the type
        choice_element = element_type.find("./{0}choice".format(LXML_SCHEMA_NAMESPACE))
        # get all elements of the choice
        choice_children = list(choice_element)

        # declare an empty tree
        tree = OrderedDict()
        # iterate trough all options to build the tree
        for choice_child in choice_children:
            # get choice element name
            choice_child_name = choice_child.attrib["name"]
            # get choice element type
            choice_child_type_name = choice_child.attrib["type"]
            # remove ns prefix if present
            if ':' in choice_child_type_name:
                choice_child_type_name = choice_child_type_name.split(':')[1]

            # get the xpath of the choice element type
            choice_child_type_xpath = "./{0}simpleType[@name='{1}']".format(LXML_SCHEMA_NAMESPACE,
                                                                            choice_child_type_name)
            # find the type in the schema using the xpath
            choice_child_type = xml_doc_tree.find(choice_child_type_xpath)

            # get the list of possible values for this choice
            list_enumeration = choice_child_type.findall(".//{0}enumeration".format(LXML_SCHEMA_NAMESPACE))

            # build the fancy tree for this choice element
            tree = _build_tree(tree, choice_child_name, list_enumeration, self.selected)

        # declare empty source data for the client fancy tree
        source_data = OrderedDict()
        for root, child_tree in sorted(tree.iteritems()):
            # add tree to source data
            source_data.update(child_tree)

        # set context with printed fancy tree, to be loaded on the page
        context = Context({'source_data': print_tree(source_data),
                           'module_id': request.GET['module_id']})
        return template.render(context)

    def _get_display(self, request):
        return ''

    def _get_result(self, request):
        xml_result = ''
        for value in self.selected:
            xml_result += '<' + self.xml_tag + '>' + value + '</' + self.xml_tag + '>'
        return xml_result

    def _post_display(self, request):
        return ''

    def _post_result(self, request):
        html_parser = HTMLParser.HTMLParser()
        xml_result = ''
        if 'data[]' in request.POST:
            for value in dict(request.POST)['data[]']:
                if value != '':
                    xml_result += '<' + self.xml_tag + '>' + html_parser.unescape(value) + '</' + self.xml_tag + '>'
        return xml_result


def _create_xml_node(node_name, child_name):
    return "<{0}>{1}</{0}>".format(node_name, child_name)


def _build_tree(tree, root, enums, selected_values):
    for enum in sorted(enums, key=lambda x: x.attrib['value']):
        t = tree
        t = t.setdefault(TreeInfo(title=root), OrderedDict())
        groups = enum.attrib['value'].split(':')
        split_index = 0
        for part in groups:
            split_index += 1
            key = _create_xml_node(root, ':'.join(groups[:split_index]))
            g = TreeInfo(title=part, key=key)
            if key in selected_values:
                g.selected = True
            t = t.setdefault(g, OrderedDict())
    return tree

