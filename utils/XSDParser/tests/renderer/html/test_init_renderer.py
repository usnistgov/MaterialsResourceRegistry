from django.template.base import Template
from django.test.testcases import TestCase
from mgi.tests import VariableTypesGenerator
from utils.XSDParser.renderer import HtmlRenderer


class InitTestSuite(TestCase):
    """ Test suite for initialization of the HtmlRenderer
    """

    def setUp(self):
        self.maxDiff = None
        self.type_generator = VariableTypesGenerator()

    def test_template_list_not_set(self):
        renderer = HtmlRenderer()

        expected_template_keys = [
            'form_error',
            'warning',
            'input',
            'select',
            'btn_add',
            'btn_del',
            'btn_collapse',
        ]

        self.assertEqual(len(renderer.templates), len(expected_template_keys))
        for key in renderer.templates.keys():
            self.assertIn(key, expected_template_keys)

        # self.assertEqual(template_keys, expected_template_keys)
        # TODO test template values to make sure that no template has been modified

    def test_template_list_is_correct_dict(self):
        template_list = {
            "t1": Template('a'),
            "t2": Template('b'),
            "t3": Template('c')
        }

        base_renderer = HtmlRenderer()
        base_renderer.templates.update(template_list)

        base_keys = base_renderer.templates.keys()
        base_keys.sort()

        renderer = HtmlRenderer(template_list)

        renderer_keys = renderer.templates.keys()
        renderer_keys.sort()

        self.assertEqual(renderer_keys, base_keys)

        for key in base_keys:
            self.assertEqual(
                base_renderer._load_template(key),
                renderer._load_template(key)
            )

    def test_template_list_is_incorrect_dict(self):
        template = None

        try:
            for template in self.type_generator.generate_types_excluding([]):
                template_list = {
                    "wrong": template
                }

                with self.assertRaises(Exception):
                    renderer = HtmlRenderer(template_list)
                    renderer._load_template("wrong")
        except AssertionError as error:
            template_type = str(type(template))
            error.message += ' (template type: ' + template_type + ')'
            raise AssertionError(error.message)

    def test_template_list_not_dict(self):
        template_list = None

        try:
            for template_list in self.type_generator.generate_types_excluding(['dict', 'none']):
                with self.assertRaises(Exception):
                    HtmlRenderer(template_list)
        except AssertionError as error:
            template_list_type = str(type(template_list))
            error.message += ' (template_list type: ' + template_list_type + ')'
            raise AssertionError(error.message)