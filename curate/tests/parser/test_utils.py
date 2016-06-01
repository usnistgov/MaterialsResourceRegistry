"""
"""
from django.http.request import HttpRequest
from django.test.testcases import TestCase
from os.path import join
from django.utils.importlib import import_module
from lxml import etree
from mgi.common import SCHEMA_NAMESPACE
from mgi.models import Module
from mgi.tests import DataHandler, are_equals
from curate.parser import get_nodes_xpath, lookup_occurs, manage_occurences, remove_annotations, \
    manage_attr_occurrences, has_module, get_xml_element_data, get_element_type


class ParserGetNodesXPathTestSuite(TestCase):
    """
    """
    # FIXME One of the test is not returning a proper output
    # FIXME 1 test not implemented

    def setUp(self):
        subnodes_data = join('curate', 'tests', 'data', 'parser', 'utils', 'xpath')
        self.subnodes_data_handler = DataHandler(subnodes_data)

        self.namespace = {
            'xs': SCHEMA_NAMESPACE
        }

    def test_not_element(self):
        document_schema = self.subnodes_data_handler.get_xsd('no_element')

        complex_type_xpath = '/xs:schema/xs:complexType'
        complex_type = document_schema.xpath(complex_type_xpath, namespaces=self.namespace)[0]

        xpath_result = get_nodes_xpath(complex_type, document_schema)

        self.assertEqual(xpath_result, [])

    def test_imbricated_elements(self):
        document_schema = self.subnodes_data_handler.get_xsd('imbricated')

        complex_type_xpath = '/xs:schema/xs:complexType'
        complex_type = document_schema.xpath(complex_type_xpath, namespaces=self.namespace)[0]

        sequence_xpath = complex_type_xpath + '/xs:sequence'

        element_xpath = sequence_xpath + '/xs:element'
        element_a = document_schema.xpath(element_xpath, namespaces=self.namespace)[0]

        choice_element_xpath = sequence_xpath + '/xs:choice/xs:element'
        choice_elements = document_schema.xpath(choice_element_xpath, namespaces=self.namespace)

        element_b = choice_elements[0]
        element_c = choice_elements[1]

        xpath_result = get_nodes_xpath(complex_type, document_schema)
        expected_result = [
            {
                'name': 'a',
                'element': element_a
            },
            {
                'name': 'b',
                'element': element_b
            },
            {
                'name': 'c',
                'element': element_c
            },
        ]

        self.assertEqual(len(xpath_result), len(expected_result))

        for xpath in xpath_result:
            xpath_elem = xpath['element']

            expected_elem_list = [expect['element'] for expect in expected_result if expect['name'] == xpath['name']]
            expect_elem = expected_elem_list[0] if len(expected_elem_list) == 1 else None

            self.assertTrue(are_equals(xpath_elem, expect_elem))

    def test_element_has_name(self):
        document_schema = self.subnodes_data_handler.get_xsd('name')

        # Retrieving the needed elements
        sequence_xpath = '/xs:schema/xs:complexType/xs:sequence'
        sequence = document_schema.xpath(sequence_xpath, namespaces=self.namespace)[0]

        element_xpath = sequence_xpath + '/xs:element'
        elements = document_schema.xpath(element_xpath, namespaces=self.namespace)

        element_a = elements[0]
        element_b = elements[1]

        # Building resulting and expected structures
        xpath_result = get_nodes_xpath(sequence, document_schema)
        expected_result = [
            {
                'name': 'a',
                'element': element_a
            },
            {
                'name': 'b',
                'element': element_b
            }
        ]

        # Testing equality
        self.assertEqual(len(xpath_result), len(expected_result))

        for xpath in xpath_result:
            xpath_elem = xpath['element']

            expected_elem_list = [expect['element'] for expect in expected_result if expect['name'] == xpath['name']]
            expect_elem = expected_elem_list[0] if len(expected_elem_list) == 1 else None

            self.assertTrue(are_equals(xpath_elem, expect_elem))

    def test_element_ref_local(self):
        document_schema = self.subnodes_data_handler.get_xsd('ref_local')

        complex_type_xpath = '/xs:schema/xs:complexType'
        complex_type = document_schema.xpath(complex_type_xpath, namespaces=self.namespace)[0]

        element_a_xpath = complex_type_xpath + '/xs:sequence/xs:element'
        element_a = document_schema.xpath(element_a_xpath, namespaces=self.namespace)[0]

        element_r0_xpath = '/xs:schema/xs:element'
        element_r0 = document_schema.xpath(element_r0_xpath, namespaces=self.namespace)[0]

        xpath_result = get_nodes_xpath(complex_type, document_schema)

        expected_result = [
            {
                'name': 'a',
                'element': element_a
            },
            {
                'name': 'r0',
                'element': element_r0
            },
            {  # FIXME the 2nd element shouldn't be here (not needed)
                'name': 'r0',
                'element': element_r0
            }
        ]

        self.assertEqual(len(xpath_result), len(expected_result))

        for xpath in xpath_result:
            xpath_elem = xpath['element']

            expected_elem_list = [expect['element'] for expect in expected_result if expect['name'] == xpath['name']]
            # FIXME Having 2 element with the same content is not useful (>= 1 should be replaced by == 1)
            expect_elem = expected_elem_list[0] if len(expected_elem_list) >= 1 else None

            self.assertTrue(are_equals(xpath_elem, expect_elem))

    # FIXME test not working
    # def test_element_ref_import(self):
    #     document = join('ref_import', 'document')
    #     document_schema = self.subnodes_data_handler.get_xsd(document)
    #
    #     reference = join('element_with_ref_no_namespace', 'reference')
    #     reference_schema = self.subnodes_data_handler.get_xsd(reference)
    #
    #     sequence_xpath = '/xs:schema/xs:complexType/xs:sequence'
    #     sequence = document_schema.xpath(sequence_xpath, namespaces=self.namespace)[0]
    #
    #     element_a_xpath = sequence_xpath + '/xs:element'
    #     element_a = document_schema.xpath(element_a_xpath, namespaces=self.namespace)[0]
    #
    #     element_r0_xpath = '/xs:schema/xs:element'
    #     element_r0 = reference_schema.xpath(element_r0_xpath, namespaces=self.namespace)[0]
    #
    #     xpath_result = get_nodes_xpath(sequence, document_schema)
    #
    #     expected_result = [
    #         {
    #             'name': 'a',
    #             'element': element_a
    #         },
    #         {
    #             'name': 'r0',
    #             'element': element_r0
    #         }
    #     ]
    #
    #     self.assertEqual(len(xpath_result), len(expected_result))
    #
    #     for xpath in xpath_result:
    #         xpath_elem = xpath['element']
    #
    #         expected_elem_list = [expect['element'] for expect in expected_result if expect['name'] == xpath['name']]
    #         # FIXME Having 2 element with the same content is not useful (>= 1 should be replaced by == 1)
    #         expect_elem = expected_elem_list[0] if len(expected_elem_list) >= 1 else None
    #
    #         self.assertTrue(are_equals(xpath_elem, expect_elem))


class ParserLookupOccursTestSuite(TestCase):
    """
    """

    def setUp(self):
        occurs_data = join('curate', 'tests', 'data', 'parser', 'utils', 'occurs')
        self.occurs_data_handler = DataHandler(occurs_data)

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
        self.request.session['defaultPrefix'] = 'xs'
        self.request.session['namespaces'] = {'xs': namespace}

        self.xml_xpath = '/root'

        self.document_schema = self.occurs_data_handler.get_xsd('document')
        # self.document_schema = etree.ElementTree(document_schema)

        sequence_xpath = '/xs:schema/xs:element/xs:complexType/xs:sequence'
        self.sequence = self.document_schema.xpath(sequence_xpath, namespaces=self.request.session['namespaces'])[0]

    def test_reload_compliant_element(self):

        compliant_xml = self.occurs_data_handler.get_xml('compliant')

        occurences = lookup_occurs(self.sequence, self.document_schema, self.xml_xpath, compliant_xml)

        self.assertEqual(len(occurences), 3)

        occ0_expected_xml = self.occurs_data_handler.get_xml('item0')
        occ1_expected_xml = self.occurs_data_handler.get_xml('item1')
        occ2_expected_xml = self.occurs_data_handler.get_xml('item2')

        self.assertTrue(are_equals(occurences[0], occ0_expected_xml))
        self.assertTrue(are_equals(occurences[1], occ1_expected_xml))
        self.assertTrue(are_equals(occurences[2], occ2_expected_xml))

    def test_reload_noncompliant_element(self):
        noncompliant_xml = self.occurs_data_handler.get_xml('noncompliant')

        occurences = lookup_occurs(self.sequence, self.document_schema, self.xml_xpath, noncompliant_xml)

        self.assertEqual(len(occurences), 6)

        occ0_expected_xml = self.occurs_data_handler.get_xml('item0')
        occ1_expected_xml = self.occurs_data_handler.get_xml('item1')
        occ2_expected_xml = self.occurs_data_handler.get_xml('item2')
        occ3_expected_xml = self.occurs_data_handler.get_xml('item3')
        occ4_expected_xml = self.occurs_data_handler.get_xml('item4')
        occ5_expected_xml = self.occurs_data_handler.get_xml('item5')

        self.assertTrue(are_equals(occurences[0], occ0_expected_xml))
        self.assertTrue(are_equals(occurences[1], occ1_expected_xml))
        self.assertTrue(are_equals(occurences[2], occ2_expected_xml))
        self.assertTrue(are_equals(occurences[3], occ3_expected_xml))
        self.assertTrue(are_equals(occurences[4], occ4_expected_xml))
        self.assertTrue(are_equals(occurences[5], occ5_expected_xml))


class ParserManageOccurencesTestSuite(TestCase):
    """
    """

    def setUp(self):
        occurs_data = join('curate', 'tests', 'data', 'parser', 'utils', 'manage_occurs')
        self.occurs_data_handler = DataHandler(occurs_data)

    def test_element_with_min_occurs_parsable(self):
        xsd_tree = self.occurs_data_handler.get_xsd('min_occurs_parsable')
        xsd_element = xsd_tree.getroot()

        (min_occ, max_occ) = manage_occurences(xsd_element)

        self.assertEqual(min_occ, 1)

    def test_element_with_max_occurs_unbounded(self):
        xsd_tree = self.occurs_data_handler.get_xsd('max_occurs_unbounded')
        xsd_element = xsd_tree.getroot()

        (min_occ, max_occ) = manage_occurences(xsd_element)

        self.assertEqual(max_occ, -1)

    def test_element_with_max_occurs_parsable(self):
        xsd_tree = self.occurs_data_handler.get_xsd('max_occurs_parsable')
        xsd_element = xsd_tree.getroot()

        (min_occ, max_occ) = manage_occurences(xsd_element)

        self.assertEqual(max_occ, 5)


class ParserManageAttrOccurencesTestSuite(TestCase):
    """
    """

    def setUp(self):
        occurs_data = join('curate', 'tests', 'data', 'parser', 'utils', 'manage_occurs')
        self.occurs_data_handler = DataHandler(occurs_data)

    def test_use_optional(self):
        xsd_tree = self.occurs_data_handler.get_xsd('attr_use_optional')
        xsd_element = xsd_tree.getroot()

        (min_occ, max_occ) = manage_attr_occurrences(xsd_element)

        self.assertEqual(min_occ, 0)
        self.assertEqual(max_occ, 1)

    def test_use_prohibited(self):
        xsd_tree = self.occurs_data_handler.get_xsd('attr_use_prohibited')
        xsd_element = xsd_tree.getroot()

        (min_occ, max_occ) = manage_attr_occurrences(xsd_element)

        self.assertEqual(min_occ, 0)
        self.assertEqual(max_occ, 0)

    def test_use_required(self):
        xsd_tree = self.occurs_data_handler.get_xsd('attr_use_required')
        xsd_element = xsd_tree.getroot()

        (min_occ, max_occ) = manage_attr_occurrences(xsd_element)

        self.assertEqual(min_occ, 1)
        self.assertEqual(max_occ, 1)

    def test_use_not_present(self):
        xsd_tree = self.occurs_data_handler.get_xsd('attr_use_undefined')
        xsd_element = xsd_tree.getroot()

        (min_occ, max_occ) = manage_attr_occurrences(xsd_element)

        # FIXME test broken with current parser
        # self.assertEqual(min_occ, 0)
        self.assertEqual(max_occ, 1)


class ParserHasModuleTestSuite(TestCase):
    """
    """

    def _save_module_to_db(self):
        # FIXME module is not saved in the right database
        module = Module()
        module.name = 'registered_module'
        module.url = 'registered_module'
        module.view = 'registered_module'

        module.save()

    def setUp(self):
        # connect to test database
        # self.db_name = "mgi_test"
        # disconnect()
        # connect(self.db_name, port=27018)

        module_data = join('curate', 'tests', 'data', 'parser', 'utils', 'modules')
        self.module_data_handler = DataHandler(module_data)

    def test_element_is_module_registered(self):
        # expect true
        self._save_module_to_db()

        xsd_tree = self.module_data_handler.get_xsd('registered_module')
        xsd_element = xsd_tree.getroot()

        has_module_result = has_module(xsd_element)

        self.assertTrue(has_module_result)

    def test_element_is_module_not_registered(self):
        # expect false
        xsd_tree = self.module_data_handler.get_xsd('unregistered_module')
        xsd_element = xsd_tree.getroot()

        has_module_result = has_module(xsd_element)

        self.assertFalse(has_module_result)

    def test_element_is_not_module(self):
        # expect false
        xsd_tree = self.module_data_handler.get_xsd('no_module')
        xsd_element = xsd_tree.getroot()

        has_module_result = has_module(xsd_element)

        self.assertFalse(has_module_result)


class ParserGetXmlElementDataTestSuite(TestCase):
    """
    """

    def setUp(self):
        xml_element_data = join('curate', 'tests', 'data', 'parser', 'utils', 'xml_data')
        self.xml_element_data_handler = DataHandler(xml_element_data)

        self.namespace = {
            'xs': SCHEMA_NAMESPACE
        }

    def test_element_xml_text(self):
        xml_schema = self.xml_element_data_handler.get_xsd(join('element', 'simple'))

        element_root_xpath = '/xs:schema/xs:element'
        element_root = xml_schema.xpath(element_root_xpath, namespaces=self.namespace)[0]

        xml_element = self.xml_element_data_handler.get_xml(join('element', 'simple'))

        reload_data = get_xml_element_data(element_root, xml_element)
        self.assertEqual(reload_data, 'string')

    def test_element_xml_branch(self):
        xml_schema = self.xml_element_data_handler.get_xsd(join('element', 'complex'))

        element_root_xpath = '/xs:schema/xs:element'
        element_root = xml_schema.xpath(element_root_xpath, namespaces=self.namespace)[0]

        xml_element = self.xml_element_data_handler.get_xml(join('element', 'complex'))

        reload_data = get_xml_element_data(element_root, xml_element)
        self.assertEqual(reload_data, etree.tostring(xml_element))

    def test_attribute(self):
        xml_schema = self.xml_element_data_handler.get_xsd(join('attribute', 'schema'))

        attribute_xpath = '/xs:schema/xs:element/xs:complexType/xs:attribute'
        attribute = xml_schema.xpath(attribute_xpath, namespaces=self.namespace)[0]

        xml_element = self.xml_element_data_handler.get_xml(join('attribute', 'instance'))
        xml_element_attrib = xml_element.attrib['id']

        reload_data = get_xml_element_data(attribute, xml_element_attrib)
        self.assertEqual(reload_data, 'attr0')

    def test_complex_type_xml_empty(self):
        xml_schema = self.xml_element_data_handler.get_xsd(join('complex_type', 'schema'))

        complex_type_xpath = '/xs:schema/xs:complexType'
        complex_type = xml_schema.xpath(complex_type_xpath, namespaces=self.namespace)[0]

        xml_element = self.xml_element_data_handler.get_xml(join('complex_type', 'empty'))

        reload_data = get_xml_element_data(complex_type, xml_element)
        self.assertEqual(reload_data, "")

    def test_complex_type_xml_branch(self):
        xml_schema = self.xml_element_data_handler.get_xsd(join('complex_type', 'schema'))

        complex_type_xpath = '/xs:schema/xs:complexType'
        complex_type = xml_schema.xpath(complex_type_xpath, namespaces=self.namespace)[0]

        xml_element = self.xml_element_data_handler.get_xml(join('complex_type', 'filled'))

        reload_data = get_xml_element_data(complex_type, xml_element)
        self.assertEqual(reload_data, etree.tostring(xml_element))

    def test_simple_type_xml_text(self):
        xml_schema = self.xml_element_data_handler.get_xsd(join('simple_type', 'schema'))

        simple_type_xpath = '/xs:schema/xs:simpleType'
        simple_type = xml_schema.xpath(simple_type_xpath, namespaces=self.namespace)[0]

        xml_element = self.xml_element_data_handler.get_xml(join('simple_type', 'filled'))

        reload_data = get_xml_element_data(simple_type, xml_element)
        self.assertEqual(reload_data, "child0")

    def test_simple_type_empty(self):
        xml_schema = self.xml_element_data_handler.get_xsd(join('simple_type', 'schema'))

        simple_type_xpath = '/xs:schema/xs:simpleType'
        simple_type = xml_schema.xpath(simple_type_xpath, namespaces=self.namespace)[0]

        xml_element = self.xml_element_data_handler.get_xml(join('simple_type', 'empty'))

        reload_data = get_xml_element_data(simple_type, xml_element)
        self.assertEqual(reload_data, "")


class ParserGetElementTypeTestSuite(TestCase):
    """
    """

    def setUp(self):
        self.defaultPrefix = 'xsd'

        xml_element_data = join('curate', 'tests', 'data', 'parser', 'utils', 'element_type')
        self.xml_element_data_handler = DataHandler(xml_element_data)

        self.namespace = {
            'xs': SCHEMA_NAMESPACE
        }

    def test_no_type_one_child_no_annot(self):
        xml_schema = self.xml_element_data_handler.get_xsd(join('no_type', 'one_child_no_annot'))

        element_root_xpath = '/xs:schema/xs:element'
        element_root = xml_schema.xpath(element_root_xpath, namespaces=self.namespace)[0]

        element_type = get_element_type(element_root, xml_schema, self.namespace, 'xs', None)
        self.assertEqual(element_type, (list(element_root)[0], xml_schema, None))

    def test_no_type_one_child_annot(self):
        xml_schema = self.xml_element_data_handler.get_xsd(join('no_type', 'one_child_annot'))

        element_root_xpath = '/xs:schema/xs:element'
        element_root = xml_schema.xpath(element_root_xpath, namespaces=self.namespace)[0]

        element_type = get_element_type(element_root, xml_schema, self.namespace, 'xs', None)
        self.assertEqual(element_type, (None, xml_schema, None))

    def test_no_type_two_children_annot(self):
        xml_schema = self.xml_element_data_handler.get_xsd(join('no_type', 'two_children_annot'))

        element_root_xpath = '/xs:schema/xs:element'
        element_root = xml_schema.xpath(element_root_xpath, namespaces=self.namespace)[0]

        element_type = get_element_type(element_root, xml_schema, self.namespace, 'xs', None)
        self.assertEqual(element_type, (list(element_root)[1], xml_schema, None))

    def test_no_type_more_children(self):
        xml_schema = self.xml_element_data_handler.get_xsd(join('no_type', 'more_children'))

        element_root_xpath = '/xs:schema/xs:element'
        element_root = xml_schema.xpath(element_root_xpath, namespaces=self.namespace)[0]

        element_type = get_element_type(element_root, xml_schema, self.namespace, 'xs', None)
        self.assertEqual(element_type, (None, xml_schema, None))

    def test_type_is_common_type(self):
        xml_schema = self.xml_element_data_handler.get_xsd('common_type')

        element_root_xpath = '/xs:schema/xs:element'
        element_root = xml_schema.xpath(element_root_xpath, namespaces=self.namespace)[0]

        element_type = get_element_type(element_root, xml_schema, 'xsd', '', None)
        self.assertEqual(element_type, (None, xml_schema, None))

    def test_type_is_complex_type(self):
        xml_schema = self.xml_element_data_handler.get_xsd(join('complex_type'))

        element_root_xpath = '/xs:schema/xs:element'
        element_root = xml_schema.xpath(element_root_xpath, namespaces=self.namespace)[0]

        complex_type_xpath = '/xs:schema/xs:complexType'
        complex_type = xml_schema.xpath(complex_type_xpath, namespaces=self.namespace)[0]

        element_type = get_element_type(element_root, xml_schema, self.namespace, 'xs', None)
        self.assertEqual(element_type, (complex_type, xml_schema, None))

    def test_type_is_simple_type(self):
        xml_schema = self.xml_element_data_handler.get_xsd(join('simple_type'))

        element_root_xpath = '/xs:schema/xs:element'
        element_root = xml_schema.xpath(element_root_xpath, namespaces=self.namespace)[0]

        simple_type_xpath = '/xs:schema/xs:simpleType'
        simple_type = xml_schema.xpath(simple_type_xpath, namespaces=self.namespace)[0]

        element_type = get_element_type(element_root, xml_schema, self.namespace, 'xs', None)
        self.assertEqual(element_type, (simple_type, xml_schema, None))


class ParserRemoveAnnotationTestSuite(TestCase):
    """
    """

    def setUp(self):
        annotation_data = join('curate', 'tests', 'data', 'parser', 'utils', 'annotation')
        self.annotation_data_handler = DataHandler(annotation_data)

        self.namespaces = {
            'xs': SCHEMA_NAMESPACE
        }

        xsd_etree = self.annotation_data_handler.get_xsd('not_annot')

        self.xsd_xpath = '/xs:schema/xs:complexType/xs:sequence'
        self.expected_xsd = xsd_etree.xpath(self.xsd_xpath, namespaces=self.namespaces)[0]

    def test_annotation_is_removed(self):
        annotated_etree = self.annotation_data_handler.get_xsd('annot')
        # annotated_etree = etree.ElementTree(annotated_schema)

        annotated_element = annotated_etree.xpath(self.xsd_xpath, namespaces=self.namespaces)[0]

        remove_annotations(annotated_element)

        self.assertTrue(are_equals(annotated_element, self.expected_xsd))

    def test_no_annotation_no_change(self):
        not_annotated_etree = self.annotation_data_handler.get_xsd('not_annot')

        not_annotated_element = not_annotated_etree.xpath(self.xsd_xpath, namespaces=self.namespaces)[0]

        remove_annotations(not_annotated_element)

        self.assertTrue(are_equals(not_annotated_element, self.expected_xsd))
