# import XSDflattener
# import lxml.etree as etree
# from io import BytesIO
#
# from mgi.settings import BASE_DIR
# from os.path import join
#
# from testing.models import RegressionTest
#
# RESOURCES_PATH = join(BASE_DIR, 'utils', 'XSDflattener')
#
#
# class TestSimpleXSD(RegressionTest):
#
#     def test_one_file(self):
#         # makes sure that a file without includes provides the same file
#         file = open(join(RESOURCES_PATH, 'time-unit-type.xsd'), 'r')
#         content = file.read()
#
#         flatenner = XSDflattener.XSDFlattenerURL(content)
#         flat = flatenner.get_flat()
#
#         # try to build the schema, would throw an exception if incorrect
#         xml_tree = etree.parse(BytesIO(flat.encode('utf-8')))
#         etree.XMLSchema(xml_tree)
#
#         # 1 simple type
#         self.assertEquals(len(xml_tree.getroot().getchildren()), 1)
#
#     def test_includes_local(self):
#         # file with includes using path
#         file = open(join(RESOURCES_PATH, 'time-type2.xsd'), 'r')
#         content = file.read()
#
#         flatenner = XSDflattener.XSDFlattenerLocal(content)
#         flat = flatenner.get_flat()
#
#         xml_tree = etree.parse(BytesIO(flat.encode('utf-8')))
#         etree.XMLSchema(xml_tree)
#
#         self.assertEquals(len(xml_tree.getroot().getchildren()), 3)
#
#     def test_multiple_includes_local(self):
#         # file with includes using path
#         file = open(join(RESOURCES_PATH, 'complex.xsd'), 'r')
#         content = file.read()
#
#         flatenner = XSDflattener.XSDFlattenerLocal(content)
#         flat = flatenner.get_flat()
#
#         xml_tree = etree.parse(BytesIO(flat.encode('utf-8')))
#         etree.XMLSchema(xml_tree)
#
#         self.assertEquals(len(xml_tree.getroot().getchildren()), 4)
