from django.template.base import Template
from django.test.testcases import TestCase
from curate.models import SchemaElement
from mgi.tests import VariableTypesGenerator
from utils.XSDParser.renderer.list import AbstractListRenderer


class AbstractInitTestSuite(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.type_generator = VariableTypesGenerator()

    # FIXME Correct import and tests
    # def test_xsd_data_is_schema_element(self):
    #     xsd_data = SchemaElement()
    #     xsd_data.tag = "test"
    #
    #     renderer = AbstractListRenderer(xsd_data)
    #
    #     self.assertEqual(xsd_data, renderer.data)
    #
    # def test_xsd_data_not_schema_element(self):
    #     xsd_data = None
    #
    #     try:
    #         for xsd_data in self.type_generator.generate_types_excluding([]):
    #             with self.assertRaises(Exception):
    #                 AbstractListRenderer(xsd_data)
    #     except AssertionError as error:
    #         xsd_data_type = str(type(xsd_data))
    #         error.message += ' (xsd_data type: ' + xsd_data_type + ')'
    #         raise AssertionError(error.message)
    #
    # def test_template_list_not_set(self):
    #     xsd_data = SchemaElement()
    #     xsd_data.tag = "test"
    #
    #     renderer = AbstractListRenderer(xsd_data)
    #
    #     # Loose comparison is enough for this test
    #     self.assertEqual(len(renderer.templates), 7)
    #
    # def test_template_list_is_correct_dict(self):
    #     xsd_data = SchemaElement()
    #     xsd_data.tag = "test"
    #
    #     template_list = {
    #         "t1": Template('a'),
    #         "t2": Template('b'),
    #         "t3": Template('c')
    #     }
    #
    #     base_renderer = AbstractListRenderer(xsd_data)
    #     base_renderer.templates.update(template_list)
    #
    #     renderer = AbstractListRenderer(xsd_data)
    #
    #     self.assertEqual(renderer.templates.keys(), base_renderer.templates.keys())
    #
    # def test_template_list_is_incorrect_dict(self):
    #     xsd_data = SchemaElement()
    #     xsd_data.tag = "test"
    #
    #     template = None
    #
    #     try:
    #         for template in self.type_generator.generate_types_excluding([]):
    #             template_list = {
    #                 "wrong": template
    #             }
    #
    #             with self.assertRaises(Exception):
    #                 AbstractListRenderer(xsd_data, template_list)
    #     except AssertionError as error:
    #         template_type = str(type(template))
    #         error.message += ' (template type: ' + template_type + ')'
    #         raise AssertionError(error.message)
    #
    # def test_template_list_not_dict(self):
    #     xsd_data = SchemaElement()
    #     xsd_data.tag = "test"
    #
    #     template_list = None
    #
    #     try:
    #         for template_list in self.type_generator.generate_types_excluding(['dict', 'none']):
    #             with self.assertRaises(Exception):
    #                 AbstractListRenderer(xsd_data, template_list)
    #     except AssertionError as error:
    #         template_list_type = str(type(template_list))
    #         error.message += ' (template_list type: ' + template_list_type + ')'
    #         raise AssertionError(error.message)
