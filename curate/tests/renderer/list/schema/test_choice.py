from importlib import import_module
from mgi import settings
from django.test.client import Client
from django.test.testcases import TestCase, SimpleTestCase
from os.path import join

from curate.parser import generate_form
from curate.tests.renderer.list.schema import XSD_FILES_PATH, HTML_FILES_PATH, retrieve_rendered_form
from mgi.models import FormData
from mgi.tests import DataHandler, are_equals
from lxml import etree


class ChoiceCreateSchemaTestSuite(SimpleTestCase):
    """
    """

    def setUp(self):
        xsd_files_path = join(XSD_FILES_PATH, 'choice')
        self.xsd_handler = DataHandler(xsd_files_path)

        html_files_path = join(HTML_FILES_PATH, 'choice')
        self.html_handler = DataHandler(html_files_path)

        engine = import_module('django.contrib.sessions.backends.db')
        session = engine.SessionStore()
        session.save()

        self.client.cookies['sessionid'] = session.session_key

        session['curate_edit'] = False

        form_data = FormData()
        form_data.name = ''
        form_data.user = ''
        form_data.template = ''

        form_data.save()

        session['curateFormData'] = str(form_data.pk)
        session['nb_html_tags'] = 0
        session['implicit_extension'] = True
        session['mapTagID'] = {}
        session['nbChoicesID'] = 0
        session.save()

    # def test_any_basic(self):
    #     pass
    #
    # def test_any_unbounded(self):
    #     pass

    def test_choice_basic(self):
        file_path = join('choice', 'basic')

        xsd_data = self.xsd_handler.get_xsd(file_path)

        session = self.client.session
        session['xmlDocTree'] = etree.tostring(xsd_data)
        session.save()

        result = retrieve_rendered_form(self.client)
        expected_result = self.html_handler.get_html(file_path)

        self.assertTrue(are_equals(result[1], expected_result))


    # def test_choice_unbounded(self):
    #     pass
    #
    # def test_element_basic(self):
    #     pass
    #
    # def test_element_unbounded(self):
    #     pass
    #
    # def test_group_basic(self):
    #     pass
    #
    # def test_group_unbounded(self):
    #     pass
    #
    # def test_multiple_basic(self):
    #     pass
    #
    # def test_multiple_unbounded(self):
    #     pass
    #
    # def test_sequence_basic(self):
    #     pass
    #
    # def test_sequence_unbounded(self):
    #     pass


class ChoiceReloadSchemaTestSuite(TestCase):
    def setUp(self):
        pass

    # def test_any_basic(self):
    #     pass
    #
    # def test_any_unbounded(self):
    #     pass
    #
    # def test_choice_basic(self):
    #     pass
    #
    # def test_choice_unbounded(self):
    #     pass
    #
    # def test_element_basic(self):
    #     pass
    #
    # def test_element_unbounded(self):
    #     pass
    #
    # def test_group_basic(self):
    #     pass
    #
    # def test_group_unbounded(self):
    #     pass
    #
    # def test_multiple_basic(self):
    #     pass
    #
    # def test_multiple_unbounded(self):
    #     pass
    #
    # def test_sequence_basic(self):
    #     pass
    #
    # def test_sequence_unbounded(self):
    #     pass

