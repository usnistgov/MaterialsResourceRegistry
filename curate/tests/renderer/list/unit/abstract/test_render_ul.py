from django.test.testcases import TestCase


class AbstractRenderUlTestSuite(TestCase):

    def setUp(self):
        ul_data = join('curate', 'tests', 'data', 'renderer', 'default', 'ul')
        self.ul_data_handler = DataHandler(ul_data)

        self.types_generator = VariableTypesGenerator()
        self.content = '<li>lorem ipsum</li>'

    def test_elem_id_str_chosen_true(self):
        element_id = 'string'
        chosen = True

        result_string = render_ul(self.content, element_id, chosen)
        self.assertEqual(result_string, render_ul(unicode(self.content), unicode(element_id), chosen))
        # print result_string

        result_html = etree.fromstring(result_string)
        expected_html = self.ul_data_handler.get_html2('elem_str_ch_true')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_elem_id_str_chosen_false(self):
        element_id = 'string'
        chosen = False

        result_string = render_ul(self.content, element_id, chosen)
        self.assertEqual(result_string, render_ul(unicode(self.content), unicode(element_id), chosen))
        # print result_string

        result_html = etree.fromstring(result_string)
        expected_html = self.ul_data_handler.get_html2('elem_str_ch_false')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_elem_id_empty_str_chosen_true(self):
        element_id = ''
        chosen = True

        result_string = render_ul(self.content, element_id, chosen)
        self.assertEqual(result_string, render_ul(unicode(self.content), unicode(element_id), chosen))
        # print result_string

        result_html = etree.fromstring(result_string)
        expected_html = self.ul_data_handler.get_html2('elem_empty_ch_true')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_elem_id_empty_str_chosen_false(self):
        element_id = ''
        chosen = False

        result_string = render_ul(self.content, element_id, chosen)
        self.assertEqual(result_string, render_ul(unicode(self.content), unicode(element_id), chosen))
        # print result_string

        result_html = etree.fromstring(result_string)
        expected_html = self.ul_data_handler.get_html2('elem_empty_ch_false')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_elem_id_none_chosen_true(self):
        element_id = None
        chosen = True

        result_string = render_ul(self.content, element_id, chosen)
        self.assertEqual(result_string, render_ul(unicode(self.content), element_id, chosen))
        # print result_string

        result_html = etree.fromstring(result_string)
        expected_html = self.ul_data_handler.get_html2('elem_none_ch_true')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_elem_id_none_chosen_false(self):
        element_id = 'string'
        chosen = True

        result_string = render_ul(self.content, element_id, chosen)
        self.assertEqual(result_string, render_ul(unicode(self.content), element_id, chosen))
        # print result_string

        result_html = etree.fromstring(result_string)
        expected_html = self.ul_data_handler.get_html2('elem_str_ch_true')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_content_not_str(self):
        content = 'string'
        element_id = 'string'
        chosen = True

        try:
            for content in self.types_generator.generate_types_excluding(['str', 'unicode']):
                with self.assertRaises(Exception):
                    render_ul(content, element_id, chosen)
        except AssertionError as error:
            content_type = str(type(content))
            error.message += ' (content type: ' + content_type + ')'
            raise AssertionError(error.message)

    def test_elem_id_not_str_not_none(self):
        content = 'string'
        element_id = 'string'
        chosen = True

        try:
            for element_id in self.types_generator.generate_types_excluding(['str', 'unicode', 'none']):
                with self.assertRaises(Exception):
                    render_ul(content, element_id, chosen)
        except AssertionError as error:
            element_id_type = str(type(element_id))
            error.message += ' (element_id type: ' + element_id_type + ')'
            raise AssertionError(error.message)

    def test_chosen_not_bool(self):
        content = 'string'
        element_id = 'string'
        chosen = True

        try:
            for chosen in self.types_generator.generate_types_excluding(['bool']):
                with self.assertRaises(Exception):
                    render_ul(content, element_id, chosen)
        except AssertionError as error:
            chosen_type = str(type(chosen))
            error.message += ' (content type: ' + chosen_type + ')'
            raise AssertionError(error.message)