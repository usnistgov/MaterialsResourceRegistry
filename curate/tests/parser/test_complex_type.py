"""
"""
from django.http.request import HttpRequest
from django.test.testcases import TestCase
from os.path import join
from django.utils.importlib import import_module
from lxml import etree
from mgi.tests import DataHandler, are_equals

from curate.parser import generate_complex_type


class ParserCreateComplexTypeTestSuite(TestCase):
    """
    """

    def setUp(self):
        complex_type_data = join('curate', 'tests', 'data', 'parser', 'complex_type')
        self.complex_type_data_handler = DataHandler(complex_type_data)

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
        self.request.session['keys'] = {}
        self.request.session['keyrefs'] = {}

        # set default namespace
        namespace = "http://www.w3.org/2001/XMLSchema"
        self.namespace = "{" + namespace + "}"
        self.request.session['defaultPrefix'] = 'xs'
        self.request.session['namespaces'] = {'xs': namespace}

    def test_create_simple_content(self):
        xsd_files = join('simple_content', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.complex_type_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.complex_type_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_complex_content(self):
        xsd_files = join('complex_content', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType[1]', namespaces=self.request.session['namespaces'])[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.complex_type_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # self.assertEqual(result_string[0], '')
        # result_string = '<div>' + result_string[0] + '</div>'
        # result_html = etree.fromstring(result_string)
        # expected_html = self.complex_type_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    # FIXME group not supported
    # def test_create_group(self):
    #     xsd_files = join('group', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]
    #
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, self.namespace, full_path='')
    #     # print result_string
    #     self.assertEqual(result_string[0], '')
    #
    #     expected_element = {
    #         'tag': 'complex_type',
    #         'occurs': (1, 1, 1),
    #         'module': None,
    #         'value': None,
    #         'children': []
    #     }
    #
    #     self.assertDictEqual(result_string[1], expected_element)
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.complex_type_data_handler.get_html(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    # FIXME all is not suported
    # def test_create_all(self):
    #     xsd_files = join('all', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]
    #
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, self.namespace, full_path='')
    #     # print result_string
    #
    #     expected_element = {
    #     }
    #
    #     self.assertDictEqual(result_string[1], expected_element)
    #
    #     result_string = '<div>' + result_string[0] + '</div>'
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.complex_type_data_handler.get_html(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    def test_create_choice(self):
        xsd_files = join('choice', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.complex_type_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.complex_type_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_sequence(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.complex_type_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_string = '<div>' + result_string[0] + '</div>'
        #
        # result_html = etree.fromstring(result_string)
        # expected_html = self.complex_type_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_attribute(self):
        xsd_files = join('attribute', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.complex_type_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.complex_type_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    # FIXME attributeGroup not supported
    # def test_create_attribute_group(self):
    #     xsd_files = join('attribute_group', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType')[0]
    #
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #     self.assertEqual(result_string, '')
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.complex_type_data_handler.get_html(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    # FIXME anyAttribute not supported
    # def test_create_any_attribute(self):
    #     xsd_files = join('any_attribute', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType')[0]
    #
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #     self.assertEqual(result_string, '')
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.complex_type_data_handler.get_html(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_multiple(self):
        xsd_files = join('multiple', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, full_path='')

        expected_element = self.complex_type_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_string = '<div>' + result_string[0] + '</div>'
        # # print result_string
        #
        # result_html = etree.fromstring(result_string)
        # expected_html = self.complex_type_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))


class ParserReloadComplexTypeTestSuite(TestCase):
    """
    """

    def setUp(self):
        complex_type_data = join('curate', 'tests', 'data', 'parser', 'complex_type')
        self.complex_type_data_handler = DataHandler(complex_type_data)

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
        self.request.session['keys'] = {}
        self.request.session['keyrefs'] = {}

        # set default namespace
        namespace = "http://www.w3.org/2001/XMLSchema"
        self.namespace = "{" + namespace + "}"
        self.request.session['defaultPrefix'] = 'xs'
        self.request.session['namespaces'] = {'xs': namespace}

    def test_reload_simple_content(self):
        xsd_files = join('simple_content', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        xml_value = xml_tree.xpath("/root", namespaces=self.request.session['namespaces'])[0].text

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, full_path='/root',
                                              default_value=xml_value, edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.complex_type_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.complex_type_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_complex_content(self):
        xsd_files = join('complex_content', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, full_path='/root',
                                              edit_data_tree=edit_data_tree)

        expected_element = self.complex_type_data_handler.get_json(xsd_files + '.reload')
        self.assertDictEqual(result_string[1], expected_element)

        # print result_string

        # result_html = etree.fromstring(result_string)
        # expected_html = self.complex_type_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))
    #
    # FIXME group not implemented
    # def test_reload_group(self):
    #     xsd_files = join('simple_content', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                         edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.complex_type_data_handler.get_html(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    # def test_reload_all(self):
    #     xsd_files = join('all', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, self.namespace, full_path='/root',
    #                                           edit_data_tree=edit_data_tree)
    #     # print result_string
    #
    #     expected_element = {
    #     }
    #
    #     self.assertDictEqual(result_string[1], expected_element)
    #
    #     result_string = '<div>' + result_string[0] + '</div>'
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.complex_type_data_handler.get_html(xsd_files + '.reload')
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_choice(self):
        xsd_files = join('choice', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, full_path='/root',
                                              edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.complex_type_data_handler.get_json(xsd_files + '.reload')
        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.complex_type_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_sequence(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, full_path='/root',
                                              edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.complex_type_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_string = '<div>' + result_string[0] + '</div>'
        #
        # result_html = etree.fromstring(result_string)
        # expected_html = self.complex_type_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_attribute(self):
        xsd_files = join('attribute', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, full_path='/root',
                                              edit_data_tree=edit_data_tree)
        # print result_string
        expected_element = self.complex_type_data_handler.get_json(xsd_files + '.reload')
        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string)
        # expected_html = self.complex_type_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    # FIXME implement attributeGroup
    # def test_reload_attribute_group(self):
    #     xsd_files = join('simple_content', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                         edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.complex_type_data_handler.get_html(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # FIXME implement anyAttribute
    # def test_reload_any_attribute(self):
    #     xsd_files = join('simple_content', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                         edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.complex_type_data_handler.get_html(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_multiple(self):
        # fixme test broken
        xsd_files = join('multiple', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType', namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, full_path='/root',
                                              edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.complex_type_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)
        # result_string = '<div>' + result_string[0] + '</div>'
        #
        # result_html = etree.fromstring(result_string)
        # expected_html = self.complex_type_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

