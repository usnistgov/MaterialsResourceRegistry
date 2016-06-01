from django.test.testcases import TestCase
from os.path import join
from lxml import etree
from curate.models import SchemaElement
from curate.renderer import HtmlRenderer
from mgi.tests import DataHandler, VariableTypesGenerator, are_equals


class RenderFormErrorTestSuite(TestCase):

    def setUp(self):
        form_error_data = join('curate', 'tests', 'data', 'renderer', 'default')
        self.form_error_data_handler = DataHandler(form_error_data)
        self.types_generator = VariableTypesGenerator()
        self.renderer = HtmlRenderer()

    def test_message_str(self):
        form_error_message = 'Sample error message'

        result_string = self.renderer._render_form_error(form_error_message)
        self.assertEqual(result_string, self.renderer._render_form_error(unicode(form_error_message)))

        result_html = etree.fromstring(result_string)
        expected_html = self.form_error_data_handler.get_html('form_error')

        self.assertTrue(are_equals(result_html, expected_html))

    # def test_message_not_str(self):
    #     error_message = 'string'
    #
    #     try:
    #         for error_message in self.types_generator.generate_types_excluding(['str', 'unicode']):
    #             with self.assertRaises(Exception):
    #                 self.renderer._render_form_error(error_message)
    #     except AssertionError as error:
    #         error_message_type = str(type(error_message))
    #         error.message += ' (error_message type: ' + error_message_type + ')'
    #         raise AssertionError(error.message)


class RenderWarningTestSuite(TestCase):
    pass