"""
"""
from django.utils.importlib import import_module
from os import walk
from django.http.request import HttpRequest
from django.test.testcases import TestCase
from os.path import join, splitext
from lxml import etree
from curate.models import SchemaElement
from curate.parser import generate_form
from curate.renderer.list import ListRenderer
from curate.renderer.xml import XmlRenderer
from mgi.models import FormData
from mgi.settings import SITE_ROOT
from mgi.tests import DataHandler


class RendererMainTestSuite(TestCase):
    """
    """

    def setUp(self):
        schema_data = join('curate', 'tests', 'data', 'parser')
        self.schema_data_handler = DataHandler(schema_data)

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition

        form_data = FormData()
        form_data.name = ''
        form_data.user = ''
        form_data.template = ''

        form_data.save()

        self.request.session['curateFormData'] = form_data.pk

    def test_list_renderer(self):
        main_directory = self.schema_data_handler.dirname
        main_dir_len = len(main_directory) + 1

        filepath_list = []

        for root, dirs, files in walk(main_directory):
            for filename in files:
                file_ext = splitext(filename)

                if file_ext[1] == '.xsd':
                    full_path = join(root, file_ext[0])
                    filepath_list.append(full_path[main_dir_len:])

        report_content = []
        error_count = 0

        for filepath in filepath_list:
            report_line = filepath

            try:
                xsd_data = self.schema_data_handler.get_xsd2(filepath)
                self.request.session['xmlDocTree'] = etree.tostring(xsd_data)

                root_pk = generate_form(self.request)
                root_element = SchemaElement.objects.get(pk=root_pk)

                renderer = ListRenderer(root_element)
                renderer.render()

                if len(renderer.warnings) != 0:
                    report_line += ',NOK,' + ','.join(renderer.warnings) + '\n'
                    error_count += 1
                else:  # No warnings yielded by the renderer
                    report_line += ',OK\n'
            except Exception as e:
                report_line += ',NOK,' + e.message + '\n'
                error_count += 1

            report_content.append(report_line)

        with open(join(SITE_ROOT, 'full_tests_report.csv'), 'w') as report_file:
            report_file.writelines(report_content)

        self.assertEqual(error_count, 0)

    def test_xml_renderer(self):
        main_directory = self.schema_data_handler.dirname
        main_dir_len = len(main_directory) + 1

        filepath_list = []

        for root, dirs, files in walk(main_directory):
            for filename in files:
                file_ext = splitext(filename)

                if file_ext[1] == '.xsd':
                    full_path = join(root, file_ext[0])
                    filepath_list.append(full_path[main_dir_len:])

        report_content = []
        error_count = 0

        for filepath in filepath_list:
            report_line = filepath

            try:
                xsd_data = self.schema_data_handler.get_xsd2(filepath)
                self.request.session['xmlDocTree'] = etree.tostring(xsd_data)

                root_pk = generate_form(self.request)
                root_element = SchemaElement.objects.get(pk=root_pk)

                renderer = XmlRenderer(root_element)
                renderer.render()

                if len(renderer.warnings) != 0:
                    report_line += ',NOK,' + ','.join(renderer.warnings) + '\n'
                    error_count += 1
                else:  # No warnings yielded by the renderer
                    report_line += ',OK\n'
            except Exception as e:
                report_line += ',NOK,' + e.message + '\n'
                error_count += 1

            report_content.append(report_line)

        with open(join(SITE_ROOT, 'full_tests_report.csv'), 'w') as report_file:
            report_file.writelines(report_content)

    # def test_sample_file(self):
    #     filepath = 'restriction/simple_type/basic'
    #
    #     try:
    #         xsd_data = self.schema_data_handler.get_xsd2(filepath)
    #         self.request.session['xmlDocTree'] = etree.tostring(xsd_data)
    #
    #         root_pk = generate_form(self.request)
    #     except Exception as e:
    #         print "Exception: "+e
