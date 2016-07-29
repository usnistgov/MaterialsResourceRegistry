from django.test.testcases import TestCase
from os.path import join

from mgi.tests import VariableTypesGenerator, DataHandler


class AbstractRenderLiTestSuite(TestCase):
    def setUp(self):
        li_data = join('utils', 'XSDParser', 'tests', 'data', 'renderer', 'default', 'li')
        self.li_data_handler = DataHandler(li_data)

        self.types_generator = VariableTypesGenerator()

        self.content = 'lorem ipsum'
        self.tag_id = '0'
        self.element_tag = 'element'

    # def test_default_parameters(self):
    #     result_string = render_li(self.content, self.tag_id, self.element_tag)
    #     self.assertEqual(result_string, render_li(unicode(self.content), unicode(self.tag_id),
    #                                               unicode(self.element_tag)))
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.li_data_handler.get_html2('default')
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_use_str_text_str(self):
    #     use = 'use'
    #     text = 'text'
    #
    #     result_string = render_li(self.content, self.tag_id, self.element_tag, use, text)
    #     self.assertEqual(result_string, render_li(unicode(self.content), unicode(self.tag_id),
    #                                               unicode(self.element_tag), use, text))
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.li_data_handler.get_html2('use_str_text_str')
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_use_str_text_none(self):
    #     use = 'use'
    #     text = None
    #
    #     result_string = render_li(self.content, self.tag_id, self.element_tag, use, text)
    #     self.assertEqual(result_string, render_li(unicode(self.content), unicode(self.tag_id),
    #                                               unicode(self.element_tag), use, text))
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.li_data_handler.get_html2('use_str_text_none')
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_use_none_text_str(self):
    #     use = None
    #     text = 'text'
    #
    #     result_string = render_li(self.content, self.tag_id, self.element_tag, use, text)
    #     self.assertEqual(result_string, render_li(unicode(self.content), unicode(self.tag_id),
    #                                               unicode(self.element_tag), use, text))
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.li_data_handler.get_html2('use_none_text_str')
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_text_not_str_not_none(self):
    #     use = 'string'
    #     text = 'string'
    #
    #     try:
    #         for text in self.types_generator.generate_types_excluding(['str', 'unicode', 'none']):
    #             with self.assertRaises(Exception):
    #                 render_li(self.content, self.tag_id, self.element_tag, use, text)
    #     except AssertionError as error:
    #         text_type = str(type(text))
    #         error.message += ' (use type: ' + text_type + ')'
    #         raise AssertionError(error.message)
    #
    # def test_use_not_str_not_none(self):
    #     use = 'string'
    #
    #     try:
    #         for use in self.types_generator.generate_types_excluding(['str', 'unicode', 'none']):
    #             with self.assertRaises(Exception):
    #                 render_li(self.content, self.tag_id, self.element_tag, use)
    #     except AssertionError as error:
    #         use_type = str(type(use))
    #         error.message += ' (use type: ' + use_type + ')'
    #         raise AssertionError(error.message)
    #
    # def test_content_not_str(self):
    #     content = 'string'
    #
    #     try:
    #         for content in self.types_generator.generate_types_excluding(['str', 'unicode']):
    #             with self.assertRaises(Exception):
    #                 render_li(content, self.tag_id, self.element_tag)
    #     except AssertionError as error:
    #         content_type = str(type(content))
    #         error.message += ' (content type: ' + content_type + ')'
    #         raise AssertionError(error.message)
    #
    # def test_element_tag_not_str(self):
    #     element_tag = 'string'
    #
    #     try:
    #         for element_tag in self.types_generator.generate_types_excluding(['str', 'unicode']):
    #             with self.assertRaises(Exception):
    #                 render_li(self.content, self.tag_id, element_tag)
    #     except AssertionError as error:
    #         element_tag_type = str(type(element_tag))
    #         error.message += ' (element_tag type: ' + element_tag_type + ')'
    #         raise AssertionError(error.message)
    #
    # def test_tag_id_not_parsable(self):
    #     class TestTagID(object):
    #         item = None
    #
    #         def __str__(self):
    #             return 'undefined' + self.item
    #
    #     with self.assertRaises(Exception):
    #         render_li(self.content, TestTagID(), self.element_tag)
