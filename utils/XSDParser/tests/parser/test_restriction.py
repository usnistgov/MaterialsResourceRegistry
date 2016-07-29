"""
"""
from django.http.request import HttpRequest
from django.test.testcases import TestCase
from os.path import join
from django.utils.importlib import import_module
from mgi.common import SCHEMA_NAMESPACE
from mgi.tests import DataHandler
from utils.XSDParser.parser import generate_restriction


class ParserCreateRestrictionTestSuite(TestCase):
    """
    """

    def setUp(self):
        restriction_data = join('utils', 'XSDParser', 'tests', 'data', 'parser', 'restriction')
        self.restriction_data_handler = DataHandler(restriction_data)

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.maxDiff = None

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0

        # set default namespace
        self.namespace = {
            'xs': SCHEMA_NAMESPACE
        }
        self.request.session['defaultPrefix'] = 'xs'
        self.request.session['namespaces'] = self.namespace

        from utils.XSDParser import parser
        from curate.ajax import load_config
        parser.load_config(self.request, load_config())

    def test_enumeration(self):
        xsd_files = join('enumeration', 'basic')
        xsd_tree = self.restriction_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:simpleType/xs:restriction',
                                     namespaces=self.namespace)[0]

        result_string = generate_restriction(self.request, xsd_element, xsd_tree)
        # print result_string

        expected_element = self.restriction_data_handler.get_json(xsd_files)
        self.assertDictEqual(result_string[1], expected_element)

    def test_simple_type(self):
        xsd_files = join('simple_type', 'basic')
        xsd_tree = self.restriction_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:simpleType/xs:restriction',
                                     namespaces=self.namespace)[0]

        result_string = generate_restriction(self.request, xsd_element, xsd_tree)
        # print result_string

        expected_element = self.restriction_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

    # def test_create_multiple(self):
    #     xsd_files = join('multiple', 'basic')
    #     xsd_tree = etree.ElementTree(self.restriction_data_handler.get_xsd(xsd_files))
    #     xsd_element = xsd_tree.xpath('/xs:schema/xs:simpleType/xs:restriction',
    #                                  namespaces=self.request.session['namespaces'])[0]
    #
    #     result_string = generate_restriction(self.request, xsd_element, xsd_tree, full_path='')
    #     # print result_string
    #
    #     expected_element = self.restriction_data_handler.get_json(xsd_files)
    #     self.assertDictEqual(result_string[1], expected_element)


class ParserReloadRestrictionTestSuite(TestCase):
    """
    """

    def setUp(self):
        restriction_data = join('utils', 'XSDParser', 'tests', 'data', 'parser', 'restriction')
        self.restriction_data_handler = DataHandler(restriction_data)

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.maxDiff = None

        self.request.session['curate_edit'] = True  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0

        # set default namespace
        self.namespace = {
            'xs': SCHEMA_NAMESPACE
        }
        self.request.session['defaultPrefix'] = 'xs'
        self.request.session['namespaces'] = self.namespace

        self.xml_xpath = '/root'

        from utils.XSDParser import parser
        from curate.ajax import load_config
        parser.load_config(self.request, load_config())

    def test_enumeration(self):
        xsd_files = join('enumeration', 'basic')
        xsd_tree = self.restriction_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:simpleType/xs:restriction',
                                     namespaces=self.namespace)[0]

        xml_tree = self.restriction_data_handler.get_xml(xsd_files)
        # xml_data = etree.tostring(xml_tree)

        xml_data_value = xml_tree.xpath(self.xml_xpath)[0].text

        # clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        # etree.set_default_parser(parser=clean_parser)

        # load the XML tree from the text
        # edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_restriction(self.request, xsd_element, xsd_tree, full_path=self.xml_xpath,
                                             edit_data_tree=xml_tree, default_value=xml_data_value)

        expected_element = self.restriction_data_handler.get_json(join('enumeration', 'reload'))

        self.assertDictEqual(result_string[1], expected_element)

    def test_simple_type(self):
        xsd_files = join('simple_type', 'basic')
        xsd_tree = self.restriction_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:simpleType/xs:restriction',
                                     namespaces=self.namespace)[0]

        xml_tree = self.restriction_data_handler.get_xml(xsd_files)
        xml_data_value = xml_tree.xpath(self.xml_xpath)[0].text

        result_string = generate_restriction(self.request, xsd_element, xsd_tree, full_path=self.xml_xpath,
                                             edit_data_tree=xml_tree, default_value=xml_data_value)

        expected_element = self.restriction_data_handler.get_json(join('simple_type', 'reload'))

        self.assertDictEqual(result_string[1], expected_element)

    # def test_reload_multiple(self):
    #     pass
