from django.http.request import HttpRequest
from django.test.testcases import TestCase
from os.path import join
from django.utils.importlib import import_module
from lxml import etree
from mgi.tests import DataHandler
from utils.XSDParser.parser import generate_choice


class ParserCreateChoiceTestSuite(TestCase):
    """
    """

    def setUp(self):
        choice_data = join('utils', 'XSDParser', 'tests', 'data', 'parser', 'choice')
        self.choice_data_handler = DataHandler(choice_data)

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

    def test_create_element_basic(self):
        xsd_files = join('element', 'basic')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_choice(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.choice_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.choice_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_element_unbounded(self):
        xsd_files = join('element', 'unbounded')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_choice(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.choice_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.choice_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    # FIXME group test are not good since it is not supported by the parser
    # def test_create_group_basic(self):
    #     xsd_files = join('group', 'basic')
    #     xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.choice_data_handler.get_html(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_group_unbounded(self):
    #     xsd_files = join('group', 'unbounded')
    #     xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.choice_data_handler.get_html(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    # FIXME choice test are not good since it is not supported by the parser
    # def test_create_choice_basic(self):
    #     xsd_files = join('choice', 'basic')
    #     xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.choice_data_handler.get_html(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_choice_unbounded(self):
    #     xsd_files = join('choice', 'unbounded')
    #     xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.choice_data_handler.get_html(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    def test_create_sequence_basic(self):
        # FIXME Not working
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_choice(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.choice_data_handler.get_json(xsd_files)
        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.choice_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_sequence_unbounded(self):
        # FIXME Not working
        xsd_files = join('sequence', 'unbounded')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_choice(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.choice_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.choice_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    # TODO implement later
    # def test_create_any_basic(self):
    #     pass
    #
    # def test_create_any_unbounded(self):
    #     pass


class ParserReloadChoiceTestSuite(TestCase):
    """
    """

    def setUp(self):
        choice_data = join('utils', 'XSDParser', 'tests', 'data', 'parser', 'choice')
        self.choice_data_handler = DataHandler(choice_data)

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

    def test_reload_element_basic(self):
        xsd_files = join('element', 'basic')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.choice_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_choice(self.request, xsd_element, xsd_tree, full_path='/root',
                                        edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.choice_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.choice_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_element_unbounded(self):
        # FIXME correct the bug here
        xsd_files = join('element', 'unbounded')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.choice_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_choice(self.request, xsd_element, xsd_tree, full_path='/root',
                                        edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.choice_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.choice_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    # TODO implement later
    # def test_reload_group_basic(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.choice_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.choice_data_handler.get_html(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    # def test_reload_group_unbounded(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.choice_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.choice_data_handler.get_html(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_choice_basic(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.choice_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.choice_data_handler.get_html(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_choice_unbounded(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.choice_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.choice_data_handler.get_html(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_sequence_basic(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.choice_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_choice(self.request, xsd_element, xsd_tree, full_path='/root',
                                        edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.choice_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.choice_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_sequence_unbounded(self):
        # fixme reload sequence unbounded has a bug
        # fixme choice iter and inner element repeated

        xsd_files = join('sequence', 'unbounded')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.choice_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_choice(self.request, xsd_element, xsd_tree, full_path='/root',
                                        edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.choice_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

    # TODO implement later
    # def test_reload_any_basic(self):
    #     pass
    #
    # def test_reload_any_unbounded(self):
    #     pass
