from django.template.base import Template
from django.test.testcases import TestCase
from os.path import join
from lxml import etree
from curate.models import SchemaElement
from curate.renderer import DefaultRenderer
from mgi.tests import VariableTypesGenerator, DataHandler, are_equals


# class InitTestSuite(TestCase):
#
#     def setUp(self):
#         self.maxDiff = None
#         self.type_generator = VariableTypesGenerator()
#
#     def test_xsd_data_is_schema_element(self):
#         xsd_data = SchemaElement()
#         xsd_data.tag = "test"
#
#         renderer = DefaultRenderer(xsd_data)
#
#         self.assertEqual(xsd_data, renderer.data)
#
#     def test_xsd_data_not_schema_element(self):
#         xsd_data = None
#
#         try:
#             for xsd_data in self.type_generator.generate_types_excluding([]):
#                 with self.assertRaises(Exception):
#                     DefaultRenderer(xsd_data)
#         except AssertionError as error:
#             xsd_data_type = str(type(xsd_data))
#             error.message += ' (xsd_data type: ' + xsd_data_type + ')'
#             raise AssertionError(error.message)
#
#     def test_template_list_not_set(self):
#         xsd_data = SchemaElement()
#         xsd_data.tag = "test"
#
#         renderer = DefaultRenderer(xsd_data)
#
#         # Loose comparison is enough for this test
#         self.assertEqual(len(renderer.templates), 7)
#
#     def test_template_list_is_correct_dict(self):
#         xsd_data = SchemaElement()
#         xsd_data.tag = "test"
#
#         template_list = {
#             "t1": Template('a'),
#             "t2": Template('b'),
#             "t3": Template('c')
#         }
#
#         base_renderer = DefaultRenderer(xsd_data)
#         base_renderer.templates.update(template_list)
#
#         renderer = DefaultRenderer(xsd_data, template_list)
#
#         self.assertEqual(renderer.templates.keys(), base_renderer.templates.keys())
#
#     def test_template_list_is_incorrect_dict(self):
#         xsd_data = SchemaElement()
#         xsd_data.tag = "test"
#
#         template = None
#
#         try:
#             for template in self.type_generator.generate_types_excluding([]):
#                 template_list = {
#                     "wrong": template
#                 }
#
#                 with self.assertRaises(Exception):
#                     DefaultRenderer(xsd_data, template_list)
#         except AssertionError as error:
#             template_type = str(type(template))
#             error.message += ' (template type: ' + template_type + ')'
#             raise AssertionError(error.message)
#
#     def test_template_list_not_dict(self):
#         xsd_data = SchemaElement()
#         xsd_data.tag = "test"
#
#         template_list = None
#
#         try:
#             for template_list in self.type_generator.generate_types_excluding(['dict', 'none']):
#                 with self.assertRaises(Exception):
#                     DefaultRenderer(xsd_data, template_list)
#         except AssertionError as error:
#             template_list_type = str(type(template_list))
#             error.message += ' (template_list type: ' + template_list_type + ')'
#             raise AssertionError(error.message)
#
#
# class LoadTemplateTestSuite(TestCase):
#
#     def setUp(self):
#         xsd_data = SchemaElement()
#         xsd_data.tag = "test"
#
#         self.renderer = DefaultRenderer(xsd_data)
#
#         self.type_generator = VariableTypesGenerator()
#
#     def test_key_exists_data_none(self):
#         self.renderer._load_template('btn_collapse')
#
#     def test_key_not_exists(self):
#         with self.assertRaises(Exception):
#             self.renderer._load_template('unexisting_key')
#
#     def test_key_not_str(self):
#         tpl_key = None
#
#         try:
#             for tpl_key in self.type_generator.generate_types_excluding(['str', 'unicode']):
#                 with self.assertRaises(Exception):
#                     self.renderer._load_template(tpl_key)
#         except AssertionError as error:
#             tpl_key_type = str(type(tpl_key))
#             error.message += ' (tpl_key type: ' + tpl_key_type + ')'
#             raise AssertionError(error.message)
#
#     def test_tpl_data_is_dict(self):
#         self.renderer._load_template('btn_add', {'is_hidden': True})
#
#     def test_tpl_data_not_dict(self):
#         tpl_data = None
#
#         try:
#             for tpl_data in self.type_generator.generate_types_excluding(['dict', 'none']):
#                 with self.assertRaises(Exception):
#                     self.renderer._load_template('btn_add', tpl_data)
#         except AssertionError as error:
#             tpl_data_type = str(type(tpl_data))
#             error.message += ' (tpl_data type: ' + tpl_data_type + ')'
#             raise AssertionError(error.message)

# class RenderFormErrorTestSuite(TestCase):
#
#     def setUp(self):
#         form_error_data = join('curate', 'tests', 'data', 'renderer', 'default')
#         self.form_error_data_handler = DataHandler(form_error_data)
#
#         self.types_generator = VariableTypesGenerator()
#
#         element = SchemaElement()
#         element.tag = "test"
#
#         self.renderer = DefaultRenderer(element)
#
#     def test_message_str(self):
#         form_error_message = 'Sample error message'
#
#         result_string = self.renderer._render_form_error(form_error_message)
#         # print result_string
#         self.assertEqual(result_string, self.renderer._render_form_error(unicode(form_error_message)))
#
#         result_html = etree.fromstring(result_string)
#         expected_html = self.form_error_data_handler.get_html('form_error')
#
#         self.assertTrue(are_equals(result_html, expected_html))
#
#     def test_message_not_str(self):
#         error_message = 'string'
#
#         try:
#             for error_message in self.types_generator.generate_types_excluding(['str', 'unicode']):
#                 with self.assertRaises(Exception):
#                     self.renderer._render_form_error(error_message)
#         except AssertionError as error:
#             error_message_type = str(type(error_message))
#             error.message += ' (error_message type: ' + error_message_type + ')'
#             raise AssertionError(error.message)
