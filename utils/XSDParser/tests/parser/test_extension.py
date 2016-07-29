from django.conf import settings
from django.http.request import HttpRequest
from django.test.testcases import TestCase
from os.path import join
from django.utils.importlib import import_module
from lxml import etree
from mgi.common import SCHEMA_NAMESPACE
from mgi.tests import DataHandler
from utils.XSDParser.parser import generate_extension


class ParserCreateExtensionTestSuite(TestCase):
    """
    """

    def setUp(self):
        extension_data = join('utils', 'XSDParser', 'tests', 'data', 'parser', 'extension')
        self.extension_data_handler = DataHandler(extension_data)

        self.maxDiff = None

        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()

        store['curate_edit'] = False  # Data edition
        store['nb_html_tags'] = 0
        store['mapTagID'] = {}
        store['nbChoicesID'] = 0
        store['keys'] = {}
        store['keyrefs'] = {}

        # set default namespace
        self.namespace = "{" + SCHEMA_NAMESPACE + "}"
        store['defaultPrefix'] = 'xs'
        store['namespaces'] = {'xs': SCHEMA_NAMESPACE}

        store.save()
        self.session = store

        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

        self.request = HttpRequest()
        self.request.session = self.session

        from utils.XSDParser import parser
        from curate.ajax import load_config
        parser.load_config(self.request, load_config())


    # def test_create_group(self):
    #     xsd_files = join('group', 'basic')
    #     xsd_tree = self.extension_data_handler.get_xsd(xsd_files))
    #     xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent/xs:extension',
    #                                  namespaces=self.request.session['namespaces'])[0]
    #
    #     result_string = generate_extension(self.request, xsd_element, xsd_tree, self.namespace, full_path='')
    #     # print result_string
    #
    #     expected_dict = {
    #     }
    #
    #     self.assertDictEqual(result_string[1], expected_dict)
    #
    #     result_string = '<div>' + result_string[0] + '</div>'
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.extension_data_handler.get_html(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    # def test_create_all(self):
    #     xsd_files = join('all', 'basic')
    #     xsd_tree = self.extension_data_handler.get_xsd(xsd_files))
    #     xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent/xs:extension',
    #                                  namespaces=self.request.session['namespaces'])[0]
    #
    #     result_string = generate_extension(self.request, xsd_element, xsd_tree, self.namespace, full_path='')
    #     # print result_string
    #
    #     expected_dict = self.extension_data_handler.get_json(xsd_files)
    #
    #     self.assertDictEqual(result_string[1], expected_dict)
    #
    #     result_string = '<div>' + result_string[0] + '</div>'
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.extension_data_handler.get_html(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    def test_choice(self):
        xsd_files = join('choice', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent/xs:extension',
                                     namespaces=self.session['namespaces'])[0]

        result_string = generate_extension(self.request, xsd_element, xsd_tree, full_path='')

        expected_dict = self.extension_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_dict)

    def test_sequence(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent/xs:extension',
                                     namespaces=self.session['namespaces'])[0]

        self.session['keys'] = {}
        self.session.save()

        self.request.session = self.session

        result_string = generate_extension(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_dict = self.extension_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_dict)

    def test_attribute(self):
        xsd_files = join('attribute', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:simpleContent/xs:extension',
                                     namespaces=self.session['namespaces'])[0]

        self.session['keys'] = {}
        self.session['keyrefs'] = {}
        self.session.save()

        self.request.session = self.session

        result_string = generate_extension(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_dict = self.extension_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_dict)

    # def test_create_attribute_group(self):
    #     xsd_files = join('attribute_group', 'basic')
    #     xsd_tree = etree.ElementTree(self.extension_data_handler.get_xsd(xsd_files))
    #     xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:simpleContent/xs:extension',
    #                                  namespaces=self.request.session['namespaces'])[0]
    #
    #     result_string = generate_extension(self.request, xsd_element, xsd_tree, self.namespace, full_path='')
    #     # print result_string
    #
    #     expected_dict = {'value': None, 'tag': 'extension', 'occurs': (1, 1, 1), 'module': None, 'children': []}
    #
    #     self.assertDictEqual(result_string[1], expected_dict)
    #
    #     self.assertEqual(result_string[0], '')
    #     # result_string = '<div>' + result_string[0] + '</div>'
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.extension_data_handler.get_html(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_any_attribute(self):
    #     xsd_files = join('any_attribute', 'basic')
    #     xsd_tree = etree.ElementTree(self.extension_data_handler.get_xsd(xsd_files))
    #     xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:simpleContent/xs:extension',
    #                                  namespaces=self.request.session['namespaces'])[0]
    #
    #     result_string = generate_extension(self.request, xsd_element, xsd_tree, self.namespace, full_path='')
    #     # print result_string
    #
    #     expected_dict = {'value': None, 'tag': 'extension', 'occurs': (1, 1, 1), 'module': None, 'children': []}
    #
    #     self.assertDictEqual(result_string[1], expected_dict)
    #
    #     self.assertEqual(result_string[0], '')
    #     # result_string = '<div>' + result_string[0] + '</div>'
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.extension_data_handler.get_html(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_multiple(self):
        xsd_files = join('multiple', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent/xs:extension',
                                     namespaces=self.session['namespaces'])[0]

        result_string = generate_extension(self.request, xsd_element, xsd_tree, full_path='')

        expected_dict = self.extension_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_dict)


class ParserReloadExtensionTestSuite(TestCase):
    """
    """

    def setUp(self):
        extension_data = join('utils', 'XSDParser', 'tests', 'data', 'parser', 'extension')
        self.extension_data_handler = DataHandler(extension_data)

        self.maxDiff = None

        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()

        # Session dictionary update
        store['curate_edit'] = True  # Data edition
        store['nb_html_tags'] = 0
        store['mapTagID'] = {}
        store['nbChoicesID'] = 0
        store['keys'] = {}
        store['keyrefs'] = {}

        # set default namespace
        self.namespace = "{" + SCHEMA_NAMESPACE + "}"
        store['defaultPrefix'] = 'xs'
        store['namespaces'] = {'xs': SCHEMA_NAMESPACE}

        store.save()
        self.session = store

        self.request = HttpRequest()
        self.request.session = self.session

        from utils.XSDParser import parser
        from curate.ajax import load_config
        parser.load_config(self.request, load_config())

    # def test_reload_group(self):
    #     xsd_files = join('group', 'basic')
    #     xsd_tree = etree.ElementTree(self.extension_data_handler.get_xsd(xsd_files))
    #     xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent/xs:extension',
    #                                  namespaces=self.request.session['namespaces'])[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.extension_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_extension(self.request, xsd_element, xsd_tree, self.namespace, full_path='/test0',
    #                                        edit_data_tree=edit_data_tree)
    #     # print result_string
    #     # result_string = '<div>' + result_string + '</div>'
    #
    #     expected_dict = {
    #     }
    #
    #     self.assertDictEqual(result_string[1], expected_dict)
    #
    #     result_string = '<div>' + result_string[0] + '</div>'
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.extension_data_handler.get_html(xsd_files + '.reload')
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    # def test_reload_all(self):
    #     # fixme bugs
    #     xsd_files = join('all', 'basic')
    #     xsd_tree = etree.ElementTree(self.extension_data_handler.get_xsd(xsd_files))
    #     xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent/xs:extension',
    #                                  namespaces=self.request.session['namespaces'])[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.extension_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_extension(self.request, xsd_element, xsd_tree, self.namespace, full_path='/test1',
    #                                        edit_data_tree=edit_data_tree)
    #     # print result_string
    #     # result_string = '<div>' + result_string + '</div>'
    #
    #     expected_dict = {}
    #
    #     self.assertDictEqual(result_string[1], expected_dict)
    #
    #     result_string = '<div>' + result_string[0] + '</div>'
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.extension_data_handler.get_html(xsd_files + '.reload')
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    def test_choice(self):
        xsd_files = join('choice', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent/xs:extension',
                                     namespaces=self.session['namespaces'])[0]

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        xml_value = xml_tree.xpath('/test2', namespaces=self.session['namespaces'])[0].text

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)

        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))

        result_string = generate_extension(self.request, xsd_element, xsd_tree, full_path='/test2',
                                           default_value=xml_value, edit_data_tree=edit_data_tree)

        expected_dict = self.extension_data_handler.get_json(xsd_files+'.reload')

        self.assertDictEqual(result_string[1], expected_dict)

    def test_sequence(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent/xs:extension',
                                     namespaces=self.session['namespaces'])[0]

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        xml_value = ''

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_extension(self.request, xsd_element, xsd_tree, full_path='/root[1]',
                                           default_value=xml_value, edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_dict = self.extension_data_handler.get_json(xsd_files+'.reload')

        self.assertDictEqual(result_string[1], expected_dict)

    def test_attribute(self):
        xsd_files = join('attribute', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:simpleContent/xs:extension',
                                     namespaces=self.session['namespaces'])[0]

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)

        xml_value = xml_tree.xpath('/root[1]', namespaces=self.session['namespaces'])[0].text

        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_extension(self.request, xsd_element, xsd_tree, full_path='/root[1]',
                                           default_value=xml_value, edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_dict = self.extension_data_handler.get_json(xsd_files+'.reload')

        self.assertDictEqual(result_string[1], expected_dict)

    # def test_reload_attribute_group(self):
    #     xsd_files = join('attribute_group', 'basic')
    #     xsd_tree = self.extension_data_handler.get_xsd(xsd_files))
    #     xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:simpleContent/xs:extension',
    #                                  namespaces=self.request.session['namespaces'])[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.extension_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_extension(self.request, xsd_element, xsd_tree, self.namespace, full_path='/test5',
    #                                        edit_data_tree=edit_data_tree)
    #     # print result_string
    #     # result_string = '<div>' + result_string + '</div>'
    #
    #     expected_dict = {'value': None, 'tag': 'extension', 'occurs': (1, 1, 1), 'module': None, 'children': []}
    #
    #     self.assertDictEqual(result_string[1], expected_dict)
    #     self.assertEqual(result_string[0], '')
    #
    #     # result_string = '<div>' + result_string[0] + '</div>'
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.extension_data_handler.get_html(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_any_attribute(self):
    #     xsd_files = join('any_attribute', 'basic')
    #     xsd_tree = self.extension_data_handler.get_xsd(xsd_files))
    #     xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:simpleContent/xs:extension',
    #                                  namespaces=self.request.session['namespaces'])[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.extension_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_extension(self.request, xsd_element, xsd_tree, self.namespace, full_path='/test6',
    #                                        edit_data_tree=edit_data_tree)
    #     # print result_string
    #     # result_string = '<div>' + result_string + '</div>'
    #
    #     expected_dict = {'value': None, 'tag': 'extension', 'occurs': (1, 1, 1), 'module': None, 'children': []}
    #
    #     self.assertDictEqual(result_string[1], expected_dict)
    #
    #     self.assertEqual(result_string[0], '')
    #     # result_string = '<div>' + result_string[0] + '</div>'
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.extension_data_handler.get_html(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_multiple(self):
        xsd_files = join('multiple', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element/xs:complexType/xs:complexContent/xs:extension',
                                     namespaces=self.request.session['namespaces'])[0]

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)

        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        # default_value = edit_data_tree.xpath('/root[1]', namespaces=self.request.session['namespaces'])

        result_string = generate_extension(self.request, xsd_element, xsd_tree, full_path='/root[1]',
                                           default_value=edit_data_tree, edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_dict = self.extension_data_handler.get_json(xsd_files+'.reload')

        self.assertDictEqual(result_string[1], expected_dict)
