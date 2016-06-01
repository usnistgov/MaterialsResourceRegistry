from django.http.request import HttpRequest
from django.test.testcases import TestCase
from os.path import join
from django.utils.importlib import import_module
from lxml import etree
# from curate.tests.parser import ParserDefaultTestCase
from mgi.tests import DataHandler, are_equals
from curate.parser import generate_sequence


class ParserCreateSequenceTestSuite(TestCase):
    """
    """

    def setUp(self):
        sequence_data = join('curate', 'tests', 'data', 'parser', 'sequence')
        self.sequence_data_handler = DataHandler(sequence_data)

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

    def test_create_element_basic(self):
        xsd_files = join('element', 'basic')
        xsd_xpath = '/xs:schema/xs:complexType/xs:sequence'

        # self.parser_test_datastructures(xsd_files, self.sequence_data_handler, xsd_xpath,
        #                                 self.request.session['namespaces'],
        #                                 generate_sequence, self.request)

        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath(xsd_xpath,
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='')

        expected_element = self.sequence_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_element_unbounded(self):
        xsd_files = join('element', 'unbounded')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='')

        expected_element = self.sequence_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(join('element', 'unbounded'))
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    # def test_create_group_basic(self):
    #     # FIXME change test and implement group support on the parser
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('group', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')
    #     self.assertEqual(result_string, "")
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.sequence_data_handler.get_html(join('element', 'element'))
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_group_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('group', 'unbounded'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('group', 'unbounded'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    def test_create_choice_basic(self):
        xsd_files = join('choice', 'basic')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.sequence_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(join('choice', 'basic'))
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_choice_unbounded(self):
        xsd_files = join('choice', 'unbounded')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.sequence_data_handler.get_json(xsd_files)
        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(join('choice', 'unbounded'))
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_sequence_basic(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.sequence_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(join('sequence', 'basic'))
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_sequence_unbounded(self):
        xsd_files = join('sequence', 'unbounded')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.sequence_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(join('sequence', 'unbounded'))
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    # def test_create_any_basic(self):
    #     # FIXME How do we want to handle any's?
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('any', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')
    #     self.assertEqual(result_string, '')
    #
    # def test_create_any_unbounded(self):
    #     # FIXME How do we want to handle any's?
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('any', 'unbounded'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('any', 'unbounded'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    def test_create_multiple_basic(self):
        xsd_files = join('multiple', 'basic')
        xsd_tree = self.sequence_data_handler.get_xsd(join('multiple', 'basic'))
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='')

        expected_element = self.sequence_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_string = '<div>' + result_string[0] + '</div>'
        #
        # result_html = etree.fromstring(result_string)
        # expected_html = self.sequence_data_handler.get_html(join('multiple', 'basic'))
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_multiple_unbounded(self):
        xsd_files = join('multiple', 'unbounded')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='')
        # print result_string

        expected_element = self.sequence_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(join('multiple', 'unbounded'))
        #
        # self.assertTrue(are_equals(result_html, expected_html))


class ParserReloadSequenceTestSuite(TestCase):
    """
    """

    def setUp(self):
        sequence_data = join('curate', 'tests', 'data', 'parser', 'sequence')
        self.sequence_data_handler = DataHandler(sequence_data)

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

    def test_reload_element_basic(self):
        xsd_files = join('element', 'basic')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='/root',
                                          edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.sequence_data_handler.get_json(xsd_files + '.reload')
        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_element_unbounded(self):
        # fixme correct bug
        xsd_files = join('element', 'unbounded')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='/root',
                                          edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.sequence_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    # fixme implement groups
    # def test_reload_group_basic(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.sequence_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.sequence_data_handler.get_html(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_group_unbounded(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.sequence_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.sequence_data_handler.get_html(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_choice_basic(self):
        xsd_files = join('choice', 'basic')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='/root',
                                          edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.sequence_data_handler.get_json(xsd_files + '.reload')
        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_choice_unbounded(self):
        xsd_files = join('choice', 'unbounded')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='/root',
                                          edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.sequence_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_sequence_basic(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='/root',
                                          edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.sequence_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_sequence_unbounded(self):
        xsd_files = join('sequence', 'unbounded')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='/root',
                                          edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = self.sequence_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    # TODO implement tests
    # def test_reload_any_basic(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.sequence_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.sequence_data_handler.get_html(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_any_unbounded(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.sequence_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.sequence_data_handler.get_html(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_multiple_basic(self):
        xsd_files = join('multiple', 'basic')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='/root',
                                          edit_data_tree=edit_data_tree)

        expected_element = self.sequence_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_string = '<div>' + result_string[0] + '</div>'
        #
        # result_html = etree.fromstring(result_string)
        # expected_html = self.sequence_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_multiple_unbounded(self):
        xsd_files = join('multiple', 'unbounded')
        xsd_tree = self.sequence_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, full_path='/root',
                                          edit_data_tree=edit_data_tree)

        expected_element = self.sequence_data_handler.get_json(xsd_files + '.reload')
        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.sequence_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))


