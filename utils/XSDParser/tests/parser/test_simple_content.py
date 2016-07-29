from django.http.request import HttpRequest
from django.test.testcases import TestCase
from os.path import join
from django.utils.importlib import import_module
from mgi.common import SCHEMA_NAMESPACE
from mgi.tests import DataHandler
from utils.XSDParser.parser import generate_simple_content


class ParserCreateSimpleContentTestSuite(TestCase):
    """
    """

    def setUp(self):
        simple_content_data = join('utils', 'XSDParser', 'tests', 'data', 'parser', 'simple_content')
        self.simple_content_data_handler = DataHandler(simple_content_data)

        self.maxDiff = None

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['keys'] = {}
        self.request.session['keyrefs'] = {}

        # set default namespace
        self.namespace = {
            'xs': SCHEMA_NAMESPACE
        }
        self.request.session['defaultPrefix'] = 'xs'
        self.request.session['namespaces'] = self.namespace

        from utils.XSDParser import parser
        from curate.ajax import load_config
        parser.load_config(self.request, load_config())

    def test_restriction(self):
        xsd_files = join('restriction', 'basic')
        xsd_tree = self.simple_content_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:simpleContent', namespaces=self.namespace)[0]

        result_string = generate_simple_content(self.request, xsd_element, xsd_tree)
        expected_element = self.simple_content_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

    def test_extension(self):
        xsd_files = join('extension', 'basic')
        xsd_tree = self.simple_content_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:simpleContent', namespaces=self.namespace)[0]

        result_string = generate_simple_content(self.request, xsd_element, xsd_tree)
        expected_element = self.simple_content_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)


class ParserReloadSimpleContentTestSuite(TestCase):
    """
    """

    def setUp(self):
        simple_content_data = join('utils', 'XSDParser', 'tests', 'data', 'parser', 'simple_content')
        self.simple_content_data_handler = DataHandler(simple_content_data)

        self.maxDiff = None

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = True  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['keys'] = {}
        self.request.session['keyrefs'] = {}

        # set default namespace
        self.namespace = {
            'xs': SCHEMA_NAMESPACE
        }
        self.request.session['defaultPrefix'] = 'xs'
        self.request.session['namespaces'] = self.namespace

        from utils.XSDParser import parser
        from curate.ajax import load_config
        parser.load_config(self.request, load_config())

    def test_restriction(self):
        xsd_files = join('restriction', 'basic')

        xsd_tree = self.simple_content_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:simpleContent', namespaces=self.namespace)[0]

        xml_tree = self.simple_content_data_handler.get_xml(xsd_files)

        result_string = generate_simple_content(self.request, xsd_element, xsd_tree, full_path='/root',
                                                default_value='child0', edit_data_tree=xml_tree)

        expected_element = self.simple_content_data_handler.get_json(xsd_files + '.reload')
        self.assertDictEqual(result_string[1], expected_element)

    def test_extension(self):
        xsd_files = join('extension', 'basic')
        xsd_tree = self.simple_content_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:simpleContent', namespaces=self.namespace)[0]

        xml_tree = self.simple_content_data_handler.get_xml(xsd_files)
        xml_value = xml_tree.xpath("/root", namespaces=self.namespace)[0].text

        result_string = generate_simple_content(self.request, xsd_element, xsd_tree, full_path='/root',
                                                default_value=xml_value, edit_data_tree=xml_tree)

        expected_element = self.simple_content_data_handler.get_json(xsd_files + '.reload')
        self.assertDictEqual(result_string[1], expected_element)
