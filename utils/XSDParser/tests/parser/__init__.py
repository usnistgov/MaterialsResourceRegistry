"""
"""
from lxml import etree
from django.test import TestCase


class ParserDefaultTestCase(TestCase):

    def parser_test_datastructures(self, xsd_files, data_handler, xsd_xpath, namespaces, test_function, request):
        xsd_tree = etree.ElementTree(data_handler.get_xsd(xsd_files))
        xsd_element = xsd_tree.xpath(xsd_xpath, namespaces=namespaces)[0]

        default_namespace = namespaces['xs'].replace('{', '')
        default_namespace = default_namespace.replace('}', '')

        result_string = test_function(request, xsd_element, xsd_tree, default_namespace, full_path='')
        expected_element = data_handler.get_json(xsd_files)

        self.assertDictEqual(result_string[1], expected_element)
