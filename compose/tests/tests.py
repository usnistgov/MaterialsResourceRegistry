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
from django.http.request import HttpRequest
from testing.models import RegressionTest
from compose.ajax import insert_element_sequence
from mgi.models import create_type
from mgi.settings import BASE_DIR
from os.path import join
from django.utils.importlib import import_module
from utils.XMLValidation.xml_schema import validate_xml_schema
from lxml import etree

RESOURCES_PATH = join(BASE_DIR, 'compose', 'tests', 'data')


class ComposerTestSuite(RegressionTest):
    """
    Test suite for the Compose application
    """

    def setUp(self):
        # call parent setUp
        super(ComposerTestSuite, self).setUp()
        # create the request
        self.request = HttpRequest()
        # create the session
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)
        # init the session
        self.request.session['includedTypesCompose'] = []

    def load_template(self, template_path):
        """
        Load the template to use in the composer
        :param template_path:
        :return:
        """
        # Open the the file
        with open(template_path, 'r') as template_file:
            # read the file content
            template_content = template_file.read()
            self.request.session['newXmlTemplateCompose'] = template_content

    def load_type(self, type_path):
        """
        Load the type to use in the composer
        :param type_path:
        :return:
        """
        # Open the the file
        with open(type_path, 'r') as type_file:
            # read the file content
            type_content = type_file.read()
            # add the type in database
            type_object = create_type(type_content, type_file.name, type_path)
            # set the type
            self.request.POST['typeID'] = type_object.id
            self.request.POST['typeName'] = 'type_name'

    def check_result(self, expected_code=200):
        """
        Check that the result template is valid
        :return:
        """
        self.assertEqual(self.response.status_code, expected_code)

        composed_template = self.request.session['newXmlTemplateCompose']
        self.assertEquals(validate_xml_schema(etree.fromstring(composed_template)), None)

    def test_base_type(self):
        template_path = join(RESOURCES_PATH, 'base.xsd')
        type_path = join(RESOURCES_PATH, 'type.xsd')

        self.load_template(template_path)
        self.load_type(type_path)

        self.request.POST['xpath'] = 'xs:element/xs:complexType/xs:sequence'

        self.response = insert_element_sequence(self.request)

        self.check_result()

    def test_base_type_ns(self):
        template_path = join(RESOURCES_PATH, 'base.xsd')
        type_path = join(RESOURCES_PATH, 'type-ns.xsd')

        self.load_template(template_path)
        self.load_type(type_path)

        self.request.POST['xpath'] = 'xs:element/xs:complexType/xs:sequence'

        self.response = insert_element_sequence(self.request)

        self.check_result()

    def test_base_type_ns2(self):
        template_path = join(RESOURCES_PATH, 'base.xsd')
        type_path = join(RESOURCES_PATH, 'type-ns2.xsd')

        self.load_template(template_path)
        self.load_type(type_path)

        self.request.POST['xpath'] = 'xs:element/xs:complexType/xs:sequence'

        self.response = insert_element_sequence(self.request)

        self.check_result()

    def test_base_ns_type(self):
        template_path = join(RESOURCES_PATH, 'base-ns.xsd')
        type_path = join(RESOURCES_PATH, 'type.xsd')

        self.load_template(template_path)
        self.load_type(type_path)

        self.request.POST['xpath'] = 'xs:element/xs:complexType/xs:sequence'

        self.response = insert_element_sequence(self.request)

        self.check_result()

    def test_base_ns_type_ns(self):
        template_path = join(RESOURCES_PATH, 'base-ns.xsd')
        type_path = join(RESOURCES_PATH, 'type-ns.xsd')

        self.load_template(template_path)
        self.load_type(type_path)

        self.request.POST['xpath'] = 'xs:element/xs:complexType/xs:sequence'

        self.response = insert_element_sequence(self.request)

        self.check_result()

    def test_base_ns_type_ns2(self):
        template_path = join(RESOURCES_PATH, 'base-ns.xsd')
        type_path = join(RESOURCES_PATH, 'type-ns2.xsd')

        self.load_template(template_path)
        self.load_type(type_path)

        self.request.POST['xpath'] = 'xs:element/xs:complexType/xs:sequence'

        self.response = insert_element_sequence(self.request)

        # base and type use the same prefix for different namespaces
        self.check_result(expected_code=400)

    def test_base_type_ns_type_ns2(self):
        template_path = join(RESOURCES_PATH, 'base.xsd')
        type_path = join(RESOURCES_PATH, 'type-ns.xsd')
        type_path2 = join(RESOURCES_PATH, 'type-ns2.xsd')

        self.load_template(template_path)

        self.load_type(type_path)
        self.request.POST['xpath'] = 'xs:element/xs:complexType/xs:sequence'
        self.response = insert_element_sequence(self.request)

        self.load_type(type_path2)
        self.request.POST['xpath'] = 'xs:element/xs:complexType/xs:sequence'
        self.response = insert_element_sequence(self.request)

        # type ns and type ns2 use the same prefix for different namespaces
        self.check_result(expected_code=400)

    def test_base_ns_type_ns_type_ns2(self):
        template_path = join(RESOURCES_PATH, 'base-ns.xsd')
        type_path = join(RESOURCES_PATH, 'type-ns.xsd')
        type_path2 = join(RESOURCES_PATH, 'type-ns2.xsd')

        self.load_template(template_path)

        self.load_type(type_path)
        self.request.POST['xpath'] = 'xs:element/xs:complexType/xs:sequence'
        self.response = insert_element_sequence(self.request)

        self.load_type(type_path2)
        self.request.POST['xpath'] = 'xs:element/xs:complexType/xs:sequence'
        self.response = insert_element_sequence(self.request)

        # base and type use the same prefix for different namespaces
        self.check_result(expected_code=400)
