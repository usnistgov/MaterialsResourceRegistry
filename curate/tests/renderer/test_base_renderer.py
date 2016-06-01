from django.template.base import Template
from django.test.testcases import TestCase
from os.path import join
from django.template import loader
from curate.models import SchemaElement
from curate.renderer import BaseRenderer
from mgi.tests import VariableTypesGenerator


class InitTestSuite(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.type_generator = VariableTypesGenerator()

    def test_template_list_not_set(self):
        renderer = BaseRenderer()

        # Loose comparison is enough for this test
        self.assertEqual(len(renderer.templates), 0)

    def test_template_list_is_correct_dict(self):

        template_list = {
            "t1": Template('a'),
            "t2": Template('b'),
            "t3": Template('c')
        }

        base_renderer = BaseRenderer()
        base_renderer.templates.update(template_list)

        renderer = BaseRenderer(template_list)

        self.assertEqual(renderer.templates.keys(), base_renderer.templates.keys())

        for tpl_key in renderer.templates.keys():
            try:
                renderer._load_template(tpl_key)
            except Exception as exc:
                self.fail(exc.message)

    def test_template_list_is_incorrect_dict(self):
        template = None

        try:
            for template in self.type_generator.generate_types_excluding([]):
                template_list = {
                    "wrong": template
                }

                with self.assertRaises(Exception):
                    renderer = BaseRenderer(template_list)
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
                    BaseRenderer(template_list)
        except AssertionError as error:
            template_list_type = str(type(template_list))
            error.message += ' (template_list type: ' + template_list_type + ')'
            raise AssertionError(error.message)


class LoadTemplateTestSuite(TestCase):

    def setUp(self):
        self.renderer = BaseRenderer()
        self.type_generator = VariableTypesGenerator()

    def test_key_exists_data_none(self):
        btn_template_path = join('renderer', 'default', 'buttons', 'collapse.html')
        template_list = {
            "btn": loader.get_template(btn_template_path)
        }

        self.renderer.templates.update(template_list)
        self.renderer._load_template('btn')

    def test_key_not_exists(self):
        with self.assertRaises(Exception):
            self.renderer._load_template('unexisting_key')

    def test_key_not_str(self):
        tpl_key = None

        try:
            for tpl_key in self.type_generator.generate_types_excluding(['str', 'unicode']):
                with self.assertRaises(Exception):
                    self.renderer._load_template(tpl_key)
        except AssertionError as error:
            tpl_key_type = str(type(tpl_key))
            error.message += ' (tpl_key type: ' + tpl_key_type + ')'
            raise AssertionError(error.message)

    def test_tpl_data_is_dict(self):
        btn_template_path = join('renderer', 'default', 'buttons', 'add.html')
        template_list = {
            "btn": loader.get_template(btn_template_path)
        }

        self.renderer.templates.update(template_list)
        self.renderer._load_template('btn', {'is_hidden': True})

    def test_tpl_data_not_dict(self):
        tpl_data = None
        btn_template_path = join('renderer', 'default', 'buttons', 'add.html')
        template_list = {
            "btn": loader.get_template(btn_template_path)
        }
        self.renderer.templates.update(template_list)

        try:
            for tpl_data in self.type_generator.generate_types_excluding(['dict', 'none']):
                with self.assertRaises(Exception):
                    self.renderer._load_template('btn', tpl_data)
        except AssertionError as error:
            tpl_data_type = str(type(tpl_data))
            error.message += ' (tpl_data type: ' + tpl_data_type + ')'
            raise AssertionError(error.message)
