"""
"""
from django.test.testcases import TestCase
from lxml import etree
from os.path import join
from mgi.tests import DataHandler, VariableTypesGenerator, are_equals
from utils.XSDParser.renderer import HtmlRenderer


class RendererRenderButtonsTestSuite(TestCase):
    """ render_buttons test suite
    """

    def setUp(self):
        buttons_data = join('utils', 'XSDParser', 'tests', 'data', 'parser', 'utils', 'buttons')
        self.buttons_data_handler = DataHandler(buttons_data)

        self.types_generator = VariableTypesGenerator()
        self.default_tag_id = 'string'

        self.renderer = HtmlRenderer()

    def _expected_form(self, is_add_present, is_del_present):
        add_tpl_name = "add_shown" if is_add_present else "add_hidden"
        del_tpl_name = "remove_shown" if is_del_present else "remove_hidden"

        add_html = self.buttons_data_handler.get_html(add_tpl_name)
        del_html = self.buttons_data_handler.get_html(del_tpl_name)

        span = etree.Element('span')
        span.append(add_html)
        span.append(del_html)

        return span

    def test_add_del_false(self):
        is_add_present = False
        is_del_present = False

        form = self.renderer._render_buttons(is_add_present, is_del_present)
        self.assertEqual(form, "")

    def test_add_true_del_false(self):
        is_add_present = True
        is_del_present = False

        # form_string = self.renderer._render_buttons(is_add_present, is_del_present, self.default_tag_id)
        form_string = self.renderer._render_buttons(is_add_present, is_del_present)
        form = etree.fromstring('<span>' + form_string + '</span>')

        expected_form = self._expected_form(is_add_present, is_del_present)
        # expected_form_wrapped = '<span>' + self.addButtonPresent + self.delButtonHidden + '</span>'

        self.assertTrue(
            are_equals(form, expected_form)
            # self._xmlStringAreEquals(form_wrapped, expected_form_wrapped)
        )

    def test_add_del_true(self):
        is_add_present = True
        is_del_present = True

        # form_string = render_buttons(is_add_present, is_del_present, self.default_tag_id)
        form_string = self.renderer._render_buttons(is_add_present, is_del_present)
        # form_wrapped = '<span>' + form + '</span>'
        form = etree.fromstring('<span>' + form_string + '</span>')

        expected_form = self._expected_form(is_add_present, is_del_present)
        # expected_form_wrapped = '<span>' + self.addButtonPresent + self.delButtonPresent + '</span>'

        self.assertTrue(
            are_equals(form, expected_form)
        )

    def test_add_false_del_true(self):
        is_add_present = False
        is_del_present = True

        # form_string = render_buttons(is_add_present, is_del_present, self.default_tag_id)
        form_string = self.renderer._render_buttons(is_add_present, is_del_present)
        # form_wrapped = '<span>' + form + '</span>'
        form = etree.fromstring('<span>' + form_string + '</span>')

        expected_form = self._expected_form(is_add_present, is_del_present)
        # expected_form_wrapped = '<span>' + self.addButtonHidden + self.delButtonPresent + '</span>'

        self.assertTrue(
            are_equals(form, expected_form)
            # self._xmlStringAreEquals(form_wrapped, expected_form_wrapped)
        )

    def test_add_button_not_bool(self):
        is_add_present = True
        try:
            for is_add_present in self.types_generator.generate_types_excluding(['bool']):
                with self.assertRaises(Exception):
                    # render_buttons(is_add_present, True, self.default_tag_id)
                    self.renderer._render_buttons(is_add_present, True)
        except AssertionError as error:
            is_add_present_type = str(type(is_add_present))
            error.message += ' (is_add_present type: ' + is_add_present_type + ')'
            raise AssertionError(error.message)

    def test_del_button_not_bool(self):
        is_del_present = True
        try:
            for is_del_present in self.types_generator.generate_types_excluding(['bool']):
                with self.assertRaises(Exception):
                    # render_buttons(True, is_del_present, self.default_tag_id)
                    self.renderer._render_buttons(True, is_del_present)
        except AssertionError as error:
            is_del_present_type = str(type(is_del_present))
            error.message += ' (is_del_present type: ' + is_del_present_type + ')'
            raise AssertionError(error.message)

    def test_tag_id_not_str(self):
        for tag_id in self.types_generator.generate_types_excluding(['str']):
            for is_add_present in [True, False]:
                for is_del_present in [True, False]:
                    try:
                        # render_buttons(is_add_present, is_del_present, tag_id)
                        self.renderer._render_buttons(is_add_present, is_del_present)
                    except Exception as exc:
                        tag_id_type = str(type(tag_id))
                        self.fail('Unexpected exception raised with tag_id of type ' + tag_id_type + ':' + exc.message)

                        
class RendererRenderCollapseButtonTestSuite(TestCase):
    """
    """

    def setUp(self):
        collapse_data = join('utils', 'XSDParser', 'tests', 'data', 'renderer', 'default')
        self.collapse_data_handler = DataHandler(collapse_data)

        self.renderer = HtmlRenderer()

    def test_button(self):
        result_string = self.renderer._render_collapse_button()
        result_html = etree.fromstring(result_string)

        expected_html = self.collapse_data_handler.get_html('collapse')

        self.assertTrue(are_equals(result_html, expected_html))
