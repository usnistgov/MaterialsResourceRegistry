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
from io import BytesIO

from lxml import etree

from mgi.common import update_dependencies
from mgi.models import create_type, Type, create_template, Template
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


class CreateSchemaTestSuite(RegressionTest):

    def SetUp(self):
        # call parent setUp
        super(CreateSchemaTestSuite, self).setUp()

    def test_create_type(self):
        with open(join(RESOURCES_PATH, 'bType.xsd'), 'r') as data_file:
            data_content = data_file.read()
            create_type(data_content, "b", "bType.xsd")
            self.assertEquals(len(Type.objects()), 1)

    def test_create_type_same_name(self):
        with open(join(RESOURCES_PATH, 'bType.xsd'), 'r') as data_file:
            data_content = data_file.read()
            create_type(data_content, "b", "bType.xsd")
            self.assertEquals(len(Type.objects()), 1)
            with self.assertRaises(Exception):
                create_type(data_content, "b", "bType.xsd")

    def test_create_template(self):
        with open(join(RESOURCES_PATH, 'a.xsd'), 'r') as data_file:
            data_content = data_file.read()
            create_template(data_content, "a", "a.xsd")
            self.assertEquals(len(Template.objects()), 1)

    def test_create_template_same_name(self):
        with open(join(RESOURCES_PATH, 'a.xsd'), 'r') as data_file:
            data_content = data_file.read()
            create_template(data_content, "a", "a.xsd")
            self.assertEquals(len(Template.objects()), 1)
            with self.assertRaises(Exception):
                create_template(data_content, "a", "a.xsd")

    def test_create_template_dependency(self):
        with open(join(RESOURCES_PATH, 'bType.xsd'), 'r') as data_file:
            data_content = data_file.read()
            dependency = create_type(data_content, "b", "bType.xsd")
            self.assertEquals(len(Type.objects()), 1)

        with open(join(RESOURCES_PATH, 'a.xsd'), 'r') as data_file:
            data_content = data_file.read()
            xml_tree = etree.parse(BytesIO(data_content.encode('utf-8')))
            update_dependencies(xml_tree, {'bType.xsd': str(dependency.id)})
            data_content = etree.tostring(xml_tree)
            create_template(data_content, "a", "a.xsd", dependencies=[str(dependency.id)])
            self.assertEquals(len(Template.objects()), 1)
