from django.http.request import HttpRequest
from django.test.testcases import TestCase
from os.path import join
from django.utils.importlib import import_module
from lxml import etree
from mgi.tests import DataHandler, are_equals
from curate.parser import generate_element


class ParserGenerateElementTestSuite(TestCase):
    """
    """

    def setUp(self):
        element_data = join('curate', 'tests', 'data', 'parser', 'element')
        self.element_data_handler = DataHandler(element_data)

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
        namespace = "http://www.w3.org/2001/XMLSchema"
        self.namespace = "{" + namespace + "}"
        self.request.session['defaultPrefix'] = 'xs'
        self.request.session['namespaces'] = {'xs': namespace}

    def test_create_simple_type_basic(self):
        xsd_files = join('simple_type', 'basic')
        xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element', namespaces=self.request.session['namespaces'])[0]

        result_string = generate_element(self.request, xsd_element, xsd_tree, full_path='')

        expected_element = self.element_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.element_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_simple_type_unbounded(self):
        xsd_files = join('simple_type', 'unbounded')
        xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence/xs:element',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_element(self.request, xsd_element, xsd_tree, full_path='')

        expected_element = self.element_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.element_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_complex_type_basic(self):
        xsd_files = join('complex_type', 'basic')
        xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element', namespaces=self.request.session['namespaces'])[0]

        result_string = generate_element(self.request, xsd_element, xsd_tree, full_path='')

        expected_element = self.element_data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.element_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_complex_type_unbounded(self):
        xsd_files = join('complex_type', 'unbounded')
        xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence/xs:element',
                                     namespaces=self.request.session['namespaces'])[0]

        result_string = generate_element(self.request, xsd_element, xsd_tree, full_path='')

        expected_element = self.element_data_handler.get_json(xsd_files)
        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.element_data_handler.get_html(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    # def test_create_unique_basic(self):
    #     # TODO implement when support for unique is wanted
    #     xsd_files = join('unique', 'basic')
    #     xsd_tree = self.element_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.element_data_handler.get_html(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_unique_unbounded(self):
    #     # TODO implement when support for unique is wanted
    #     xsd_files = join('unique', 'unbounded')
    #     xsd_tree = self.element_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.element_data_handler.get_html(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_key_basic(self):
    #     # TODO implement when support for key is wanted
    #     xsd_files = join('key', 'basic')
    #     xsd_tree = self.element_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.element_data_handler.get_html(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_key_unbounded(self):
    #     # TODO implement when support for key is wanted
    #     xsd_files = join('key', 'unbounded')
    #     xsd_tree = self.element_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.element_data_handler.get_html(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_keyref_basic(self):
    #     # TODO implement when support for keyref is wanted
    #     xsd_files = join('keyref', 'basic')
    #     xsd_tree = self.element_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.element_data_handler.get_html(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_keyref_unbounded(self):
    #     # TODO implement when support for keyref is wanted
    #     xsd_files = join('keyref', 'unbounded')
    #     xsd_tree = self.element_data_handler.get_xsd(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.element_data_handler.get_html(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    # TODO Implement unique, key and keyref for these tests
    # def test_create_simple_unique_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_simple_unique_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_simple_key_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_simple_key_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_simple_keyref_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_simple_keyref_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_complex_unique_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_complex_unique_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_complex_key_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_complex_key_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_complex_keyref_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_complex_keyref_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_multiple_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_multiple_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))


class ParserReloadElementTestSuite(TestCase):
    """
    """

    def setUp(self):
        element_data = join('curate', 'tests', 'data', 'parser', 'element')
        self.element_data_handler = DataHandler(element_data)

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
        namespace = "http://www.w3.org/2001/XMLSchema"
        self.namespace = "{" + namespace + "}"
        self.request.session['defaultPrefix'] = 'xs'
        self.request.session['namespaces'] = {'xs': namespace}

    def test_reload_simple_type_basic(self):
        xsd_files = join('simple_type', 'basic')
        xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element', namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.element_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))

        result_string = generate_element(self.request, xsd_element, xsd_tree, full_path='',
                                         edit_data_tree=edit_data_tree)

        expected_element = self.element_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.element_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_simple_type_unbounded(self):
        xsd_files = join('simple_type', 'unbounded')
        xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence/xs:element',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.element_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))

        result_string = generate_element(self.request, xsd_element, xsd_tree, full_path='/root',
                                         edit_data_tree=edit_data_tree)

        expected_element = self.element_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.element_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_complex_type_basic(self):
        xsd_files = join('complex_type', 'basic')
        xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:element', namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.element_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))

        result_string = generate_element(self.request, xsd_element, xsd_tree, full_path='',
                                         edit_data_tree=edit_data_tree)

        expected_element = self.element_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.element_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_complex_type_unbounded(self):
        xsd_files = join('complex_type', 'unbounded')
        xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:sequence/xs:element',
                                     namespaces=self.request.session['namespaces'])[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.element_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))

        result_string = generate_element(self.request, xsd_element, xsd_tree, full_path='/root',
                                         edit_data_tree=edit_data_tree)

        expected_element = self.element_data_handler.get_json(xsd_files + '.reload')

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string[0])
        # expected_html = self.element_data_handler.get_html(xsd_files + '.reload')
        #
        # self.assertTrue(are_equals(result_html, expected_html))

        # todo implement these test when the parser implement the functionalities
        # def test_reload_unique_basic(self):
        #     xsd_files = join('unique', 'basic')
        #     xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        #     xsd_element = xsd_tree.xpath('/schema/element')[0]
        #
        #     self.request.session['curate_edit'] = True
        #
        #     xml_tree = self.element_data_handler.get_xml(xsd_files)
        #     xml_data = etree.tostring(xml_tree)
        #
        #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        #     etree.set_default_parser(parser=clean_parser)
        #     # load the XML tree from the text
        #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        #
        #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='',
        #                                     edit_data_tree=edit_data_tree)
        #     print result_string
        #
        #     # result_html = etree.fromstring(result_string)
        #     # expected_html = self.element_data_handler.get_html(xsd_files + '.reload')
        #     #
        #     # self.assertTrue(are_equals(result_html, expected_html))

        # def test_reload_unique_unbounded(self):
        #     xsd_files = join('complex_type', 'unbounded')
        #     xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]
        #
        #     self.request.session['curate_edit'] = True
        #
        #     xml_tree = self.element_data_handler.get_xml(xsd_files)
        #     xml_data = etree.tostring(xml_tree)
        #
        #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        #     etree.set_default_parser(parser=clean_parser)
        #     # load the XML tree from the text
        #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        #
        #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='/root',
        #                                     edit_data_tree=edit_data_tree)
        #     print result_string
        #
        #     # result_html = etree.fromstring(result_string)
        #     # expected_html = self.element_data_handler.get_html(xsd_files + '.reload')
        #     #
        #     # self.assertTrue(are_equals(result_html, expected_html))
        #
        # def test_reload_key_basic(self):
        #     xsd_files = join('simple_type', 'basic')
        #     xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        #     xsd_element = xsd_tree.xpath('/schema/element')[0]
        #
        #     self.request.session['curate_edit'] = True
        #
        #     xml_tree = self.element_data_handler.get_xml(xsd_files)
        #     xml_data = etree.tostring(xml_tree)
        #
        #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        #     etree.set_default_parser(parser=clean_parser)
        #     # load the XML tree from the text
        #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        #
        #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='',
        #                                     edit_data_tree=edit_data_tree)
        #     print result_string
        #
        #     # result_html = etree.fromstring(result_string)
        #     # expected_html = self.element_data_handler.get_html(xsd_files + '.reload')
        #     #
        #     # self.assertTrue(are_equals(result_html, expected_html))
        #
        # def test_reload_key_unbounded(self):
        #     xsd_files = join('complex_type', 'unbounded')
        #     xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]
        #
        #     self.request.session['curate_edit'] = True
        #
        #     xml_tree = self.element_data_handler.get_xml(xsd_files)
        #     xml_data = etree.tostring(xml_tree)
        #
        #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        #     etree.set_default_parser(parser=clean_parser)
        #     # load the XML tree from the text
        #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        #
        #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='/root',
        #                                     edit_data_tree=edit_data_tree)
        #     print result_string
        #
        #     # result_html = etree.fromstring(result_string)
        #     # expected_html = self.element_data_handler.get_html(xsd_files + '.reload')
        #     #
        #     # self.assertTrue(are_equals(result_html, expected_html))
        #
        # def test_reload_keyref_basic(self):
        #     xsd_files = join('simple_type', 'basic')
        #     xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        #     xsd_element = xsd_tree.xpath('/schema/element')[0]
        #
        #     self.request.session['curate_edit'] = True
        #
        #     xml_tree = self.element_data_handler.get_xml(xsd_files)
        #     xml_data = etree.tostring(xml_tree)
        #
        #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        #     etree.set_default_parser(parser=clean_parser)
        #     # load the XML tree from the text
        #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        #
        #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='',
        #                                     edit_data_tree=edit_data_tree)
        #     print result_string
        #
        #     # result_html = etree.fromstring(result_string)
        #     # expected_html = self.element_data_handler.get_html(xsd_files + '.reload')
        #     #
        #     # self.assertTrue(are_equals(result_html, expected_html))
        #
        # def test_reload_keyref_unbounded(self):
        #     xsd_files = join('complex_type', 'unbounded')
        #     xsd_tree = self.element_data_handler.get_xsd(xsd_files)
        #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]
        #
        #     self.request.session['curate_edit'] = True
        #
        #     xml_tree = self.element_data_handler.get_xml(xsd_files)
        #     xml_data = etree.tostring(xml_tree)
        #
        #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        #     etree.set_default_parser(parser=clean_parser)
        #     # load the XML tree from the text
        #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        #
        #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='/root',
        #                                     edit_data_tree=edit_data_tree)
        #     print result_string
        #
        #     # result_html = etree.fromstring(result_string)
        #     # expected_html = self.element_data_handler.get_html(xsd_files + '.reload')
        #     #
        #     # self.assertTrue(are_equals(result_html, expected_html))

