from django.test.testcases import TestCase
from os.path import join
from lxml import etree
from curate.models import SchemaElement
from curate.renderer import HtmlRenderer
from curate.tests.renderer.html import create_mock_html_renderer, create_mock_db_input
from mgi.tests import DataHandler, VariableTypesGenerator, are_equals


class RendererRenderSelectTestSuite(TestCase):

    def setUp(self):
        select_data = join('curate', 'tests', 'data', 'renderer', 'default', 'select')
        self.select_data_handler = DataHandler(select_data)

        self.types_generator = VariableTypesGenerator()
        self.select_id = 'select'
        self.select_class = 'select'

        self.renderer = HtmlRenderer()

    def test_id_str_options_list(self):
        options = [
            ('opt1', 'opt1', False),
            ('opt2', 'opt2', False),
            ('opt3', 'opt3', True)
        ]

        result_string = self.renderer._render_select(self.select_id, self.select_class, options)
        self.assertEqual(
            result_string,
            self.renderer._render_select(unicode(self.select_id), self.select_class, options)
        )

        result_html = etree.fromstring(result_string)
        expected_html = self.select_data_handler.get_html('id_str_options_list')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_id_str_options_empty_list(self):
        options = []

        result_string = self.renderer._render_select(self.select_id, self.select_class, options)
        self.assertEqual(
            result_string,
            self.renderer._render_select(unicode(self.select_id), self.select_class, options)
        )

        result_html = etree.fromstring(result_string)
        expected_html = self.select_data_handler.get_html('id_str_options_empty')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_id_none_options_list(self):
        options = [
            ('opt1', 'opt1', False),
            ('opt2', 'opt2', False),
            ('opt3', 'opt3', True)
        ]

        result_string = self.renderer._render_select(None, self.select_class, options)
        self.assertEqual(result_string, self.renderer._render_select(None, self.select_class, options))
        # print result_string

        result_html = etree.fromstring(result_string)
        expected_html = self.select_data_handler.get_html('id_none_options_list')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_id_none_options_empty_list(self):
        options = []

        result_string = self.renderer._render_select(None, self.select_class, options)
        self.assertEqual(result_string, self.renderer._render_select(None, self.select_class, options))
        # print result_string

        result_html = etree.fromstring(result_string)
        expected_html = self.select_data_handler.get_html('id_none_options_empty')

        self.assertTrue(are_equals(result_html, expected_html))

    # def test_id_not_str_not_none(self):
    #     element_id = 'string'
    #
    #     try:
    #         for element_id in self.types_generator.generate_types_excluding(['str', 'unicode', 'none']):
    #             with self.assertRaises(Exception):
    #                 self.renderer._render_select(element_id, self.select_class, [])
    #     except AssertionError as error:
    #         element_id_type = str(type(element_id))
    #         error.message += ' (element_id type: ' + element_id_type + ')'
    #         raise AssertionError(error.message)

    # def test_options_not_list(self):
    #     options = []
    #
    #     try:
    #         for options in self.types_generator.generate_types_excluding(['list']):
    #             with self.assertRaises(Exception):
    #                 self.renderer._render_select(self.select_id, self.select_class, options)
    #     except AssertionError as error:
    #         options_type = str(type(options))
    #         error.message += ' (options type: ' + options_type + ')'
    #         raise AssertionError(error.message)

    # def test_options_not_list_of_tuple(self):
    #     options = [()]
    #
    #     try:
    #         for item in self.types_generator.generate_types_excluding(['tuple']):
    #             options[0] = item
    #
    #             with self.assertRaises(Exception):
    #                 self.renderer._render_select(self.select_id, self.select_class, options)
    #     except AssertionError as error:
    #         item_type = str(type(options[0]))
    #         error.message += ' (item type: ' + item_type + ')'
    #         raise AssertionError(error.message)

    # def test_options_malformed_list(self):
    #     options = [()]
    #
    #     try:
    #         for param in self.types_generator.generate_types_excluding(['str', 'unicode']):
    #             options[0] = (param, '', False)
    #             with self.assertRaises(Exception):
    #                 self.renderer._render_select(self.select_id, self.select_class, options)
    #
    #             options[0] = ('', param, False)
    #             with self.assertRaises(Exception):
    #                 self.renderer._render_select(self.select_id, self.select_class, options)
    #
    #         for param in self.types_generator.generate_types_excluding(['bool']):
    #             options[0] = ('', '', param)
    #             with self.assertRaises(Exception):
    #                 self.renderer._render_select(self.select_id, self.select_class, options)
    #
    #         with self.assertRaises(Exception):
    #             self.renderer._render_select(self.select_id, self.select_class, [('elem0', 'elem1')])
    #     except AssertionError as error:
    #         error.message += ' (option not considered as malformed: ' + str(options) + ')'
    #         raise AssertionError(error.message)

    # FIXME New version (merge with up)
    def test_select_id_is_db_elem(self):
        pass

    def test_select_id_not_db_element(self):
        pass

    def test_select_id_not_str(self):
        pass

    def test_select_class_is_str(self):
        pass

    def test_select_class_is_not_str(self):
        pass

    def test_options_list_is_list_with_good_tuples(self):
        pass

    def test_options_list_is_list_with_bad_tuples(self):
        pass

    def test_options_list_is_list_without_tuples(self):
        pass

    def test_options_list_is_not_list(self):
        pass


class RenderInputTestSuite(TestCase):
    def setUp(self):
        input_data = join('curate', 'tests', 'data', 'renderer', 'html', 'input')
        self.input_data_handler = DataHandler(input_data)

        self.types_generator = VariableTypesGenerator()
        self.renderer = HtmlRenderer()

    def test_input_placeholder_str(self):
        input_element = create_mock_db_input(
            placeholder='string'
        )
        result_string = self.renderer._render_input(input_element)

        result_html = etree.fromstring(result_string)
        expected_html = self.input_data_handler.get_html('placeholder')

        self.assertTrue(are_equals(result_html, expected_html))

    # def test_input_placeholder_not_str(self):
    #     placeholder = None
    #
    #     try:
    #         for placeholder in self.types_generator.generate_types_excluding(['str', 'unicode']):
    #             input_element = create_mock_db_input(
    #                 placeholder=placeholder
    #             )
    #
    #             with self.assertRaises(Exception):
    #                 self.renderer._render_input(input_element)
    #     except AssertionError as error:
    #         placeholder_type = str(type(placeholder))
    #         error.message += ' (title type: ' + placeholder_type + ')'
    #         raise AssertionError(error.message)

    def test_input_title_str(self):
        input_element = create_mock_db_input(
            title='string'
        )
        result_string = self.renderer._render_input(input_element)

        result_html = etree.fromstring(result_string)
        expected_html = self.input_data_handler.get_html('title')

        self.assertTrue(are_equals(result_html, expected_html))

    # def test_input_title_not_str(self):
    #     title = None
    #
    #     try:
    #         for title in self.types_generator.generate_types_excluding(['str', 'unicode']):
    #             with self.assertRaises(Exception):
    #                 input_element = create_mock_db_input(
    #                     title=title
    #                 )
    #
    #                 self.renderer._render_input(input_element)
    #     except AssertionError as error:
    #         title_type = str(type(title))
    #         error.message += ' (title type: ' + title_type + ')'
    #         raise AssertionError(error.message)

    def test_input_value_str(self):
        input_element = create_mock_db_input(
            value="string"
        )
        result_string = self.renderer._render_input(input_element)

        result_html = etree.fromstring(result_string)
        expected_html = self.input_data_handler.get_html('input_str')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_input_value_none(self):
        input_element = create_mock_db_input(
            value=None
        )
        result_string = self.renderer._render_input(input_element)

        result_html = etree.fromstring(result_string)
        expected_html = self.input_data_handler.get_html('input_none')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_input_not_schema_element(self):
        input_element = SchemaElement()

        try:
            for input_element in self.types_generator.possible_types:
                with self.assertRaises(TypeError):
                    self.renderer._render_input(input_element)
        except AssertionError as error:
            input_type = str(type(input_element))
            error.message += ' (input type: ' + input_type + ')'
            raise AssertionError(error.message)
