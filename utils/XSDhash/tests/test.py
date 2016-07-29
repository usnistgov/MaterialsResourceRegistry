from testing.models import RegressionTest
from utils.XSDhash import XSDhash
from mgi.settings import BASE_DIR
from os.path import join

RESOURCES_PATH = join(BASE_DIR, 'utils', 'XSDhash', 'tests', 'data')


class TestSimpleXSD(RegressionTest):
    def setUp(self):
        print "In method", self._testMethodName
        file = open(join(RESOURCES_PATH, 'chemical-element.xsd'), 'r')
        self.content = file.read()
        self.hash = XSDhash.get_hash(self.content)

    def test_same(self):
        # makes sure that the same XSD produces the same hash
        file = open(join(RESOURCES_PATH, 'chemical-element.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertEqual(self.hash, hash)

    def test_spaces(self):
        # makes sure that an XSD with additional spaces produces the same hash
        file = open(join(RESOURCES_PATH, 'spaces-in-element.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertEqual(self.hash, hash)

    def test_spaces2(self):
        # makes sure that an XSD with additional spaces, returns,tabs produces the same hash
        file = open(join(RESOURCES_PATH, 'spaces-return-tab.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertEqual(self.hash, hash)

    def test_comments(self):
        # makes sure that an XSD with documentation tags produces different hash
        file = open(join(RESOURCES_PATH, 'different-comments.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertEqual(self.hash, hash)

    def test_different_annotations(self):
        # makes sure that an XSD with different comments produces the same hash
        file = open(join(RESOURCES_PATH, 'different-annotation.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertEqual(self.hash, hash)

    def test_different_annotations_levels(self):
        # makes sure that an XSD with different comments produces the same hash
        file = open(join(RESOURCES_PATH, 'annotations-levels.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertEqual(self.hash, hash)

    def test_different_namespace(self):
        # makes sure that an XSD with different comments produces the same hash
        file = open(join(RESOURCES_PATH, 'namespace.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertNotEqual(self.hash, hash)

    def test_wrong_enum(self):
        # makes sure that an XSD with different enumeration does not produce the same hash
        file = open(join(RESOURCES_PATH, 'wrong-enum.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertNotEqual(self.hash, hash)


class TestComplexXSD(RegressionTest):
    def setUp(self):
        print "In method", self._testMethodName
        file = open(join(RESOURCES_PATH, 'composition.xsd'), 'r')
        self.content = file.read()
        self.hash = XSDhash.get_hash(self.content)

    def test_same(self):
        # makes sure that the same XSD produces the same hash
        file = open(join(RESOURCES_PATH, 'composition.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertEqual(self.hash, hash)

    def test_order(self):
        # makes sure that an XSD with elements in a different order produces the same hash
        file = open(join(RESOURCES_PATH, 'order.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertEqual(self.hash, hash)

    def test_root(self):
        # makes sure that an XSD with different root names does not produce the same hash
        file = open(join(RESOURCES_PATH, 'root-name.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertNotEqual(self.hash, hash)

    def test_type(self):
        # makes sure that an XSD with different type names does not produce the same hash
        file = open(join(RESOURCES_PATH, 'type-name.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertNotEqual(self.hash, hash)


class TestMoreComplexXSD(RegressionTest):
    def setUp(self):
        print "In method", self._testMethodName
        file = open(join(RESOURCES_PATH, 'demo.diffusion.xsd'), 'r')
        self.content = file.read()
        self.hash = XSDhash.get_hash(self.content)

    def test_same(self):
        # makes sure that the same XSD produces the same hash
        file = open(join(RESOURCES_PATH, 'demo.diffusion.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertEqual(self.hash, hash)

    def test_order(self):
        # makes sure that an XSD with elements in a different order produces the same hash
        file = open(join(RESOURCES_PATH, 'order2.xsd'), 'r')
        content = file.read()
        hash = XSDhash.get_hash(content)
        print "self.hash: " + self.hash
        print "hash: " + hash
        self.assertEqual(self.hash, hash)
