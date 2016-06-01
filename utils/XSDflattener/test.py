# import XSDflattener
# import unittest
# import lxml.etree as etree
# from io import BytesIO

# class TestSimpleXSD(unittest.TestCase):
# 	def setUp(self):
# 		print "In method", self._testMethodName
#
# 	def test_one_file(self):
# 		# makes sure that a file without includes provides the same file
# 		file = open('time-unit-type.xsd','r')
# 		content = file.read()
#
# 		flatenner = XSDflattener.XSDFlattenerURL(content)
# 		flat = flatenner.get_flat()
#
# 		print flat
#
# 		# try to build the schema, would throw an exception if incorrect
# 		xmlTree = etree.parse(BytesIO(flat.encode('utf-8')))
# 		xmlSchema = etree.XMLSchema(xmlTree)
#
# 		# 1 simple type
# 		self.assertEquals(len(xmlTree.getroot().getchildren()), 1)
#
#
# # 	def test_includes_URL(self):
# # 		# file with includes using URLs
# # 		file = open('time-type.xsd','r')
# # 		content = file.read()
# #
# # 		flatenner = XSDflattener.XSDFlattenerURL(content)
# # 		flat = flatenner.get_flat()
# #
# # 		print flat
# #
# # 		# try to build the schema, would throw an exception if incorrect
# # 		xmlTree = etree.parse(BytesIO(flat.encode('utf-8')))
# # 		xmlSchema = etree.XMLSchema(xmlTree)
# #
# # 		# 2 types from includes + 1 type in the file
# # 		self.assertEquals(len(xmlTree.getroot().getchildren()), 3)
#
# 	def test_includes_local(self):
# 		# file with includes using path
# 		file = open('time-type2.xsd','r')
# 		content = file.read()
#
# 		flatenner = XSDflattener.XSDFlattenerLocal(content)
# 		flat = flatenner.get_flat()
#
# 		print flat
#
# 		xmlTree = etree.parse(BytesIO(flat.encode('utf-8')))
# 		xmlSchema = etree.XMLSchema(xmlTree)
#
# 		self.assertEquals(len(xmlTree.getroot().getchildren()), 3)
#
# 	def test_multiple_includes_local(self):
# 		# file with includes using path
# 		file = open('complex.xsd','r')
# 		content = file.read()
#
# 		flatenner = XSDflattener.XSDFlattenerLocal(content)
# 		flat = flatenner.get_flat()
#
# 		print flat
#
# 		xmlTree = etree.parse(BytesIO(flat.encode('utf-8')))
# 		xmlSchema = etree.XMLSchema(xmlTree)
#
# 		self.assertEquals(len(xmlTree.getroot().getchildren()), 4)
#
# if __name__ == '__main__':
#     unittest.main()