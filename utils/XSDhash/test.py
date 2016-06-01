# import XSDhash
# import unittest


# class TestSimpleXSD(unittest.TestCase):
# 	def setUp(self):
# 		print "In method", self._testMethodName
# 		file = open('chemical-element.xsd','r')
# 		self.content = file.read()
# 		self.hash = XSDhash.get_hash(self.content)
#
# 	def test_same(self):
# 		# makes sure that the same XSD produces the same hash
# 		file = open('chemical-element.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertEqual(self.hash, hash)
#
# 	def test_spaces(self):
# 		# makes sure that an XSD with additional spaces produces the same hash
# 		file = open('spaces-in-element.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertEqual(self.hash, hash)
#
# 	def test_spaces2(self):
# 		# makes sure that an XSD with additional spaces, returns,tabs produces the same hash
# 		file = open('spaces-return-tab.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertEqual(self.hash, hash)
#
# 	def test_comments(self):
# 		# makes sure that an XSD with documentation tags produces different hash
# 		file = open('different-comments.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertEqual(self.hash, hash)
#
# 	def test_different_annotations(self):
# 		# makes sure that an XSD with different comments produces the same hash
# 		file = open('different-annotation.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertEqual(self.hash, hash)
#
# 	def test_different_annotations_levels(self):
# 		# makes sure that an XSD with different comments produces the same hash
# 		file = open('annotations-levels.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertEqual(self.hash, hash)
#
# 	def test_different_namespace(self):
# 		# makes sure that an XSD with different comments produces the same hash
# 		file = open('namespace.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertNotEqual(self.hash, hash)
#
# 	def test_wrong_enum(self):
# 		# makes sure that an XSD with different enumeration does not produce the same hash
# 		file = open('wrong-enum.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertNotEqual(self.hash, hash)
#
# class TestComplexXSD(unittest.TestCase):
# 	def setUp(self):
# 		print "In method", self._testMethodName
# 		file = open('composition.xsd','r')
# 		self.content = file.read()
# 		self.hash = XSDhash.get_hash(self.content)
#
# 	def test_same(self):
# 		# makes sure that the same XSD produces the same hash
# 		file = open('composition.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertEqual(self.hash, hash)
#
# 	def test_order(self):
# 		# makes sure that an XSD with elements in a different order produces the same hash
# 		file = open('order.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertEqual(self.hash, hash)
#
# 	def test_root(self):
# 		# makes sure that an XSD with different root names does not produce the same hash
# 		file = open('root-name.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertNotEqual(self.hash, hash)
#
# 	def test_type(self):
# 		# makes sure that an XSD with different type names does not produce the same hash
# 		file = open('type-name.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertNotEqual(self.hash, hash)
#
# class TestMoreComplexXSD(unittest.TestCase):
# 	def setUp(self):
# 		print "In method", self._testMethodName
# 		file = open('demo.diffusion.xsd','r')
# 		self.content = file.read()
# 		self.hash = XSDhash.get_hash(self.content)
#
# 	def test_same(self):
# 		# makes sure that the same XSD produces the same hash
# 		file = open('demo.diffusion.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertEqual(self.hash, hash)
#
# 	def test_order(self):
# 		# makes sure that an XSD with elements in a different order produces the same hash
# 		file = open('order2.xsd','r')
# 		content = file.read()
# 		hash = XSDhash.get_hash(content)
# 		print "self.hash: " + self.hash
# 		print "hash: " + hash
# 		self.assertEqual(self.hash, hash)
#
# if __name__ == '__main__':
#     unittest.main()