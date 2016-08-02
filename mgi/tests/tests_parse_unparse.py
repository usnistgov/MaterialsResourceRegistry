################################################################################
#
# File Name: tests.py
# Application: compose
# Purpose:
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from mgi.models import XMLdata
from os.path import join
import os
from django.utils.importlib import import_module
from testing.models import RegressionTest
from utils.XSDhash import XSDhash

settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)

RESOURCES_PATH = join(settings.BASE_DIR, 'mgi', 'tests', 'data')


def _strip(input_str):
    return XSDhash.get_hash(input_str)


class ParseUnparseTestSuite(RegressionTest):

    def SetUp(self):
        # call parent setUp
        super(ParseUnparseTestSuite, self).setUp()

    def test_parse_unparse_accent(self):
        with open(join(RESOURCES_PATH, 'accent.xml'), 'r') as data_file:
            data_content = data_file.read()
            # test parsing
            xml_data = XMLdata(xml=data_content)
            # test unparsing
            xml_string = XMLdata.unparse(xml_data.content['content'])
            self.assertEquals(_strip(data_content), _strip(xml_string))

    def test_parse_unparse_accent_attr(self):
        with open(join(RESOURCES_PATH, 'accent_attr.xml'), 'r') as data_file:
            data_content = data_file.read()
            # test parsing
            xml_data = XMLdata(xml=data_content)
            # test unparsing
            xml_string = XMLdata.unparse(xml_data.content['content'])
            self.assertEquals(_strip(data_content), _strip(xml_string))

    def test_parse_unparse_number(self):
        with open(join(RESOURCES_PATH, 'number.xml'), 'r') as data_file:
            data_content = data_file.read()
            # test parsing
            xml_data = XMLdata(xml=data_content)
            # test unparsing
            xml_string = XMLdata.unparse(xml_data.content['content'])
            self.assertEquals(_strip(data_content), _strip(xml_string))

    def test_parse_unparse_number_attr(self):
        with open(join(RESOURCES_PATH, 'number_attr.xml'), 'r') as data_file:
            data_content = data_file.read()
            # test parsing
            xml_data = XMLdata(xml=data_content)
            # test unparsing
            xml_string = XMLdata.unparse(xml_data.content['content'])
            self.assertEquals(_strip(data_content), _strip(xml_string))

    def test_parse_unparse_list(self):
        with open(join(RESOURCES_PATH, 'list.xml'), 'r') as data_file:
            data_content = data_file.read()
            # test parsing
            xml_data = XMLdata(xml=data_content)
            # test unparsing
            xml_string = XMLdata.unparse(xml_data.content['content'])
            self.assertEquals(_strip(data_content), _strip(xml_string))

    def test_parse_unparse_test(self):
        with open(join(RESOURCES_PATH, 'test.xml'), 'r') as data_file:
            data_content = data_file.read()
            # test parsing
            xml_data = XMLdata(xml=data_content)
            # test unparsing
            xml_string = XMLdata.unparse(xml_data.content['content'])
            self.assertEquals(_strip(data_content), _strip(xml_string))
