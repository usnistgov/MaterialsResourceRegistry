# ################################################################################
# #
# # File Name: tests.py
# # Application: compose
# # Purpose:
# #
# # Author: Sharief Youssef
# #         sharief.youssef@nist.gov
# #
# #         Guillaume SOUSA AMARAL
# #         guillaume.sousa@nist.gov
# #
# # Sponsor: National Institute of Standards and Technology (NIST)
# #
# ################################################################################
# from django.http.request import HttpRequest
# from django.test import TestCase
#
# from mgi.common import update_dependencies
# from mgi.models import create_type, create_template
# from mgi.settings import BASE_DIR
# from os.path import join
# from django.utils.importlib import import_module
# from lxml import etree
# from utils.XMLValidation.xml_schema import _lxml_validate_xsd, validate_xml_schema, _lxml_validate_xml, \
#     validate_xml_data
#
# RESOURCES_PATH = join(BASE_DIR, 'utils', 'XMLValidation', 'tests', 'data')
# TEST_LXML = True
#
#
# class ValidateXSDTestSuite(TestCase):
#     """
#     Test suite for the XSD Validation
#     """
#
#     def setUp(self):
#         # create the request
#         self.request = HttpRequest()
#         # create the session
#         engine = import_module('django.contrib.sessions.backends.db')
#         session_key = None
#         self.request.session = engine.SessionStore(session_key)
#
#     def load_template(self, template_path):
#         """
#         Load the template to use in validation
#         :param template_path:
#         :return:
#         """
#         # Open the the file
#         with open(template_path, 'r') as template_file:
#             # read the file content
#             self.xsd_string = template_file.read()
#             self.xsd_tree = etree.fromstring(self.xsd_string)
#
#     def load_type(self, type_path):
#         """
#         Load the type to use in validation
#         :param type_path:
#         :return:
#         """
#         # Open the the file
#         with open(type_path, 'r') as type_file:
#             # read the file content
#             type_content = type_file.read()
#             # add the type in database
#             type_object = create_type(type_content, 'type_name', type_path)
#             return type_object
#
#     # def test_empty(self):
#     #     # load template
#     #     template_path = join(RESOURCES_PATH, 'empty.xsd')
#     #     self.assertRaises(Exception, self.load_template(template_path))
#     #
#     #     # test LXML
#     #     self.assertRaises(Exception, _lxml_validate_xsd(self.xsd_tree))
#     #     # test global method
#     #     self.assertRaises(Exception, validate_xml_schema(self.xsd_tree))
#     #
#     #     # test Xerces
#     #     if platform.system() != "Windows":
#     #         _xerces_validate_xsd("")
#
#     def test_basic(self):
#         # load template
#         template_path = join(RESOURCES_PATH, 'basic.xsd')
#         self.load_template(template_path)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertEquals(_lxml_validate_xsd(self.xsd_tree), None)
#         # test global method
#         self.assertEquals(validate_xml_schema(self.xsd_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertEquals(_xerces_validate_xsd(self.xsd_string), None)
#
#     def test_no_root(self):
#         # load template
#         template_path = join(RESOURCES_PATH, 'no_root.xsd')
#         self.load_template(template_path)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertEquals(_lxml_validate_xsd(self.xsd_tree), None)
#         # test global method
#         self.assertEquals(validate_xml_schema(self.xsd_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertEquals(_xerces_validate_xsd(self.xsd_string), None)
#
#     def test_include_filesystem(self):
#         # load template
#         template_path = join(RESOURCES_PATH, 'include.xsd')
#         self.load_template(template_path)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertNotEquals(_lxml_validate_xsd(self.xsd_tree), None)
#         # test global method
#         self.assertNotEquals(validate_xml_schema(self.xsd_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertNotEquals(_xerces_validate_xsd(self.xsd_string), None)
#
#     def test_include_django(self):
#         # load type
#         type_path = join(RESOURCES_PATH, 'to-include.xsd')
#         type_object = self.load_type(type_path)
#
#         # load template
#         template_path = join(RESOURCES_PATH, 'include.xsd')
#         self.load_template(template_path)
#
#         update_dependencies(self.xsd_tree, {'to-include.xsd': str(type_object.id)})
#         self.xsd_string = etree.tostring(self.xsd_tree)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertEquals(_lxml_validate_xsd(self.xsd_tree), None)
#         # test global method
#         self.assertEquals(validate_xml_schema(self.xsd_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertEquals(_xerces_validate_xsd(self.xsd_string), None)
#
#     def test_import_filesystem(self):
#         # load template
#         template_path = join(RESOURCES_PATH, 'import.xsd')
#         self.load_template(template_path)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertNotEquals(_lxml_validate_xsd(self.xsd_tree), None)
#         # test global method
#         self.assertNotEquals(validate_xml_schema(self.xsd_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertNotEquals(_xerces_validate_xsd(self.xsd_string), None)
#
#     def test_import_django(self):
#         # load type
#         type_path = join(RESOURCES_PATH, 'to-import.xsd')
#         type_object = self.load_type(type_path)
#
#         # load template
#         template_path = join(RESOURCES_PATH, 'import.xsd')
#         self.load_template(template_path)
#
#         update_dependencies(self.xsd_tree, {'to-import.xsd': str(type_object.id)})
#         self.xsd_string = etree.tostring(self.xsd_tree)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertEquals(_lxml_validate_xsd(self.xsd_tree), None)
#         # test global method
#         self.assertEquals(validate_xml_schema(self.xsd_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertEquals(_xerces_validate_xsd(self.xsd_string), None)
#
#     def test_import_external(self):
#         # load template
#         template_path = join(RESOURCES_PATH, 'import-external.xsd')
#         self.load_template(template_path)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertEquals(_lxml_validate_xsd(self.xsd_tree), None)
#         # test global method
#         self.assertEquals(validate_xml_schema(self.xsd_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertEquals(_xerces_validate_xsd(self.xsd_string), None)
#
#     def test_1_1(self):
#         # load template
#         template_path = join(RESOURCES_PATH, '1.1.xsd')
#         self.load_template(template_path)
#
#         # test LXML
#         if TEST_LXML:
#             # TODO: if AssertionError: LXML added support of 1.1
#             self.assertNotEquals(_lxml_validate_xsd(self.xsd_tree), None)
#         # test global method
#         # TODO: if AssertionError: LXML added support of 1.1
#         self.assertNotEquals(validate_xml_schema(self.xsd_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertEquals(_xerces_validate_xsd(self.xsd_string), None)
#
#
# class ValidateXMLTestSuite(TestCase):
#     """
#     Test suite for the XML Validation
#     """
#
#     def setUp(self):
#         # create the request
#         self.request = HttpRequest()
#         # create the session
#         engine = import_module('django.contrib.sessions.backends.db')
#         session_key = None
#         self.request.session = engine.SessionStore(session_key)
#
#     def load_template(self, template_path):
#         """
#         Load the template to use in validation
#         :param template_path:
#         :return:
#         """
#         # Open the the file
#         with open(template_path, 'r') as template_file:
#             # read the file content
#             self.xsd_string = template_file.read()
#             self.xsd_tree = etree.fromstring(self.xsd_string)
#
#     def load_type(self, type_path):
#         """
#         Load the type to use in validation
#         :param type_path:
#         :return:
#         """
#         # Open the the file
#         with open(type_path, 'r') as type_file:
#             # read the file content
#             type_content = type_file.read()
#             # add the type in database
#             type_object = create_type(type_content, 'type_name', type_path)
#             return type_object
#
#     def load_data(self, data_path):
#         # Open the the file
#         with open(data_path, 'r') as data_file:
#             # read the file content
#             self.xml_string = data_file.read()
#             self.xml_tree = etree.fromstring(self.xml_string)
#
#     def test_basic_ok(self):
#         # load template
#         template_path = join(RESOURCES_PATH, 'basic.xsd')
#         self.load_template(template_path)
#
#         # load data
#         data_path = join(RESOURCES_PATH, 'basic_ok.xml')
#         self.load_data(data_path)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertEquals(_lxml_validate_xml(self.xsd_tree, self.xml_tree), None)
#         # test global method
#         self.assertEquals(validate_xml_data(self.xsd_tree, self.xml_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertEquals(_xerces_validate_xml(self.xsd_string, self.xml_string), None)
#
#     def test_basic_nok(self):
#         # load template
#         template_path = join(RESOURCES_PATH, 'basic.xsd')
#         self.load_template(template_path)
#
#         # load data
#         data_path = join(RESOURCES_PATH, 'basic_nok.xml')
#         self.load_data(data_path)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertNotEquals(_lxml_validate_xml(self.xsd_tree, self.xml_tree), None)
#         # test global method
#         self.assertNotEquals(validate_xml_data(self.xsd_tree, self.xml_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertNotEquals(_xerces_validate_xml(self.xsd_string, self.xml_string), None)
#
#     def test_no_root_ok(self):
#         # load template
#         template_path = join(RESOURCES_PATH, 'no_root.xsd')
#         self.load_template(template_path)
#
#         # load data
#         data_path = join(RESOURCES_PATH, 'no_root_ok.xml')
#         self.load_data(data_path)
#
#         # test LXML
#         if TEST_LXML:
#             # TODO: if AssertionError: LXML added support of 1.1
#             self.assertNotEquals(_lxml_validate_xml(self.xsd_tree, self.xml_tree), None)
#         # test global method
#         # TODO: if AssertionError: LXML added support of 1.1
#         self.assertNotEquals(validate_xml_data(self.xsd_tree, self.xml_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertEquals(_xerces_validate_xml(self.xsd_string, self.xml_string), None)
#
#     def test_no_root_nok(self):
#         # load template
#         template_path = join(RESOURCES_PATH, 'no_root.xsd')
#         self.load_template(template_path)
#
#         # load data
#         data_path = join(RESOURCES_PATH, 'no_root_nok.xml')
#         self.load_data(data_path)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertNotEquals(_lxml_validate_xml(self.xsd_tree, self.xml_tree), None)
#         # test global method
#         self.assertNotEquals(validate_xml_data(self.xsd_tree, self.xml_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertNotEquals(_xerces_validate_xml(self.xsd_string, self.xml_string), None)
#
#     def test_include_django_ok(self):
#         # load type
#         type_path = join(RESOURCES_PATH, 'to-include.xsd')
#         type_object = self.load_type(type_path)
#
#         # load template
#         template_path = join(RESOURCES_PATH, 'include.xsd')
#         self.load_template(template_path)
#
#         update_dependencies(self.xsd_tree, {'to-include.xsd': str(type_object.id)})
#         self.xsd_string = etree.tostring(self.xsd_tree)
#
#         # load data
#         data_path = join(RESOURCES_PATH, 'include_ok.xml')
#         self.load_data(data_path)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertEquals(_lxml_validate_xml(self.xsd_tree, self.xml_tree), None)
#         # test global method
#         self.assertEquals(validate_xml_data(self.xsd_tree, self.xml_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertEquals(_xerces_validate_xml(self.xsd_string, self.xml_string), None)
#
#     def test_include_django_nok(self):
#         # load type
#         type_path = join(RESOURCES_PATH, 'to-include.xsd')
#         type_object = self.load_type(type_path)
#
#         # load template
#         template_path = join(RESOURCES_PATH, 'include.xsd')
#         self.load_template(template_path)
#
#         update_dependencies(self.xsd_tree, {'to-include.xsd': str(type_object.id)})
#         self.xsd_string = etree.tostring(self.xsd_tree)
#
#         # load data
#         data_path = join(RESOURCES_PATH, 'include_nok.xml')
#         self.load_data(data_path)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertNotEquals(_lxml_validate_xml(self.xsd_tree, self.xml_tree), None)
#         # test global method
#         self.assertNotEquals(validate_xml_data(self.xsd_tree, self.xml_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertNotEquals(_xerces_validate_xml(self.xsd_string, self.xml_string), None)
#
#     def test_import_django_ok(self):
#         # load type
#         type_path = join(RESOURCES_PATH, 'to-import.xsd')
#         type_object = self.load_type(type_path)
#
#         # load template
#         template_path = join(RESOURCES_PATH, 'import.xsd')
#         self.load_template(template_path)
#
#         update_dependencies(self.xsd_tree, {'to-import.xsd': str(type_object.id)})
#         self.xsd_string = etree.tostring(self.xsd_tree)
#
#         # load data
#         data_path = join(RESOURCES_PATH, 'import_ok.xml')
#         self.load_data(data_path)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertEquals(_lxml_validate_xml(self.xsd_tree, self.xml_tree), None)
#         # test global method
#         self.assertEquals(validate_xml_data(self.xsd_tree, self.xml_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertEquals(_xerces_validate_xml(self.xsd_string, self.xml_string), None)
#
#     def test_import_django_nok(self):
#         # load type
#         type_path = join(RESOURCES_PATH, 'to-import.xsd')
#         type_object = self.load_type(type_path)
#
#         # load template
#         template_path = join(RESOURCES_PATH, 'import.xsd')
#         self.load_template(template_path)
#
#         update_dependencies(self.xsd_tree, {'to-import.xsd': str(type_object.id)})
#         self.xsd_string = etree.tostring(self.xsd_tree)
#
#         # load data
#         data_path = join(RESOURCES_PATH, 'import_nok.xml')
#         self.load_data(data_path)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertNotEquals(_lxml_validate_xml(self.xsd_tree, self.xml_tree), None)
#         # test global method
#         self.assertNotEquals(validate_xml_data(self.xsd_tree, self.xml_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertNotEquals(_xerces_validate_xml(self.xsd_string, self.xml_string), None)
#
#     def test_import_external_ok(self):
#         # load template
#         template_path = join(RESOURCES_PATH, 'import-external.xsd')
#         self.load_template(template_path)
#
#         # load data
#         data_path = join(RESOURCES_PATH, 'import_external_ok.xml')
#         self.load_data(data_path)
#
#         # test LXML
#         if TEST_LXML:
#             # TODO: if AssertionError: LXML added support of 1.1
#             self.assertNotEquals(_lxml_validate_xml(self.xsd_tree, self.xml_tree), None)
#         # test global method
#         # TODO: if AssertionError: LXML added support of 1.1
#         self.assertNotEquals(validate_xml_data(self.xsd_tree, self.xml_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertEquals(_xerces_validate_xml(self.xsd_string, self.xml_string), None)
#
#     def test_import_external_nok(self):
#         # load template
#         template_path = join(RESOURCES_PATH, 'import-external.xsd')
#         self.load_template(template_path)
#
#         # load data
#         data_path = join(RESOURCES_PATH, 'import_external_nok.xml')
#         self.load_data(data_path)
#
#         # test LXML
#         if TEST_LXML:
#             self.assertNotEquals(_lxml_validate_xml(self.xsd_tree, self.xml_tree), None)
#         # test global method
#         self.assertNotEquals(validate_xml_data(self.xsd_tree, self.xml_tree), None)
#
#         # # test Xerces
#         # if TEST_XERCES:
#         #     if platform.system() != "Windows":
#         #         self.assertNotEquals(_xerces_validate_xml(self.xsd_string, self.xml_string), None)
