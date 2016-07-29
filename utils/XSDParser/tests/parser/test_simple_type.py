"""
"""
from django.http.request import HttpRequest
from django.test.testcases import TestCase
from os.path import join
from django.utils.importlib import import_module
from lxml import etree
from mgi.tests import DataHandler
from utils.XSDParser.parser import generate_simple_type


class ParserCreateSimpleTypeTestSuite(TestCase):
    """
    """

    def setUp(self):
        simple_type_data = join('utils', 'XSDParser', 'tests', 'data', 'parser', 'simple_type')
        self.simple_type_data_handler = DataHandler(simple_type_data)

        self.maxDiff = None

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['implicit_extension'] = True

        # set default namespace
        namespace = "http://www.w3.org/2001/XMLSchema"
        self.namespace = "{" + namespace + "}"
        self.request.session['defaultPrefix'] = 'xs'
        self.request.session['namespaces'] = {'xs': namespace}

        from utils.XSDParser import parser
        from curate.ajax import load_config
        parser.load_config(self.request, load_config())

    def test_create_restriction(self):
        xsd_files = join('restriction', 'basic')
        xsd_tree = self.simple_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:simpleType', namespaces=self.request.session['namespaces'])[0]

        result_string = generate_simple_type(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_dict = self.simple_type_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_dict)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.simple_type_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_list(self):
        xsd_files = join('list', 'basic')
        xsd_tree = self.simple_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:simpleType', namespaces=self.request.session['namespaces'])[0]

        result_string = generate_simple_type(self.request, xsd_element, xsd_tree, full_path='')

        expected_dict = self.simple_type_data_handler.get_json(xsd_files)
        self.assertDictEqual(result_string[1], expected_dict)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.simple_type_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    # FIXME Union test is not good cause it has not been implemented on the server
    # def test_create_union(self):
    #     xsd_files = join('union', 'basic')
    #     xsd_tree = self.simple_type_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/simpleType')[0]
    #
    #     result_string = generate_simple_type(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #     self.assertEqual(result_string, '')
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.simple_type_data_handler.get_html(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))


class ParserReloadSimpleTypeTestSuite(TestCase):
    """
    """

    def setUp(self):
        simple_type_data = join('utils', 'XSDParser', 'tests', 'data', 'parser', 'simple_type')
        self.simple_type_data_handler = DataHandler(simple_type_data)

        self.maxDiff = None

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['implicit_extension'] = True

        # set default namespace
        namespace = "http://www.w3.org/2001/XMLSchema"
        self.namespace = "{" + namespace + "}"
        self.request.session['defaultPrefix'] = 'xs'
        self.request.session['namespaces'] = {'xs': namespace}

        from utils.XSDParser import parser
        from curate.ajax import load_config
        parser.load_config(self.request, load_config())

    def test_reload_restriction(self):
        # FIXME relaod restriction doesn't work
        xsd_files = join('restriction', 'basic')
        xsd_tree = self.simple_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:simpleType', namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.simple_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        xml_value = xml_tree.xpath("/root", namespaces=self.request.session['namespaces'])[0].text

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))

        result_string = generate_simple_type(self.request, xsd_element, xsd_tree, full_path='/root',
                                             default_value=xml_value, edit_data_tree=edit_data_tree)
        # print result_string

        expected_dict = self.simple_type_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_dict)

    def test_reload_list(self):
        # FIXME list reload is not working
        xsd_files = join('list', 'basic')
        xsd_tree = self.simple_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:simpleType', namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.simple_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_simple_type(self.request, xsd_element, xsd_tree, full_path='/root',
                                             edit_data_tree=edit_data_tree)
        # print result_string

        expected_dict = self.simple_type_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_dict)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.simple_type_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

        # fixme support for union is not there yet
        # def test_reload_union(self):
        #     xsd_files = join('restriction', 'basic')
        #     xsd_tree = self.simple_type_data_handler.get_xsd(xsd_files)
        #     xsd_element = xsd_tree.xpath('/schema/simpleType')[0]
        #
        #     self.request.session['curate_edit'] = True
        #
        #     xml_tree = self.simple_type_data_handler.get_xml(xsd_files)
        #     xml_data = etree.tostring(xml_tree)
        #
        #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        #     etree.set_default_parser(parser=clean_parser)
        #     # load the XML tree from the text
        #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        #     result_string = generate_simple_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
        #                                        edit_data_tree=edit_data_tree)
        #     print result_string
        #
        #     # result_html = etree.fromstring(result_string)
        #     # expected_html = self.simple_type_data_handler.get_html(xsd_files + '.reload')
        #     #
        #     # self.assertTrue(are_equals(result_html, expected_html))

