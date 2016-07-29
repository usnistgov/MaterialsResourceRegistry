from django.http.request import HttpRequest
from django.test.testcases import TestCase
from os.path import join
from django.utils.importlib import import_module
from lxml import etree
from mgi.tests import DataHandler
from utils.XSDParser.parser import generate_complex_content


class ParserCreateComplexContentTestSuite(TestCase):
    """
    """
    # FIXME restriction for complexContent are not working

    def setUp(self):
        extension_data = join('utils', 'XSDParser', 'tests', 'data', 'parser', 'complex_content')
        self.extension_data_handler = DataHandler(extension_data)

        self.maxDiff = None

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0

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
        xsd_tree = self.extension_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_complex_content(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_dict = self.extension_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_dict)

        # result_string = '<div>' + result_string[0] + '</div>'
        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.extension_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_extension(self):
        xsd_files = join('extension', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_complex_content(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_dict = self.extension_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_dict)

        # result_string = '<div>' + result_string[0] + '</div>'
        # result_html = etree.fromstring(result_string)
        # expected_html = self.extension_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))


class ParserReloadComplexContentTestSuite(TestCase):
    """
    """
    # FIXME restriction for complexContent are not working

    def setUp(self):
        extension_data = join('utils', 'XSDParser', 'tests', 'data', 'parser', 'complex_content')
        self.extension_data_handler = DataHandler(extension_data)

        self.maxDiff = None

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0

        # set default namespace
        namespace = "http://www.w3.org/2001/XMLSchema"
        self.namespace = "{" + namespace + "}"
        self.request.session['defaultPrefix'] = 'xs'
        self.request.session['namespaces'] = {'xs': namespace}

        from utils.XSDParser import parser
        from curate.ajax import load_config
        parser.load_config(self.request, load_config())

    def test_reload_restriction(self):
        xsd_files = join('restriction', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))

        result_string = generate_complex_content(self.request, xsd_element, xsd_tree, full_path='/root',
                                                 edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_dict = self.extension_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_dict)

        # result_string = '<div>' + result_string[0] + '</div>'
        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.extension_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_extension(self):
        xsd_files = join('extension', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))

        result_string = generate_complex_content(self.request, xsd_element, xsd_tree, full_path='/root',
                                                 edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_dict = self.extension_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_dict)

        # result_string = '<div>' + result_string[0] + '</div>'
        # result_html = etree.fromstring(result_string)
        # expected_html = self.extension_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))
