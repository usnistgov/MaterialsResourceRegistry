################################################################################
#
# File Name: tests.py
# Application: explore
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

from testing.models import RegressionTest
from explore.ajax import build_criteria, manageRegexBeforeExe, ORCriteria, ANDCriteria, invertQuery
from mgi.models import create_template, XMLdata
from mgi.settings import BASE_DIR
from os.path import join


RESOURCES_PATH = join(BASE_DIR, 'explore', 'tests', 'data')


def load_template(template_path):
    """
    Load the template to search on
    :param template_path:
    :return:
    """
    # Open the the file
    with open(template_path, 'r') as template_file:
        # read the file content
        template_content = template_file.read()
        return create_template(template_content, template_path, template_path)


def load_data(data_path, template_id):
    """
    Load the data to search
    :param data_path:
    :param template_id
    :return:
    """
    # Open the the file
    with open(data_path, 'r') as data_file:
        # read the file content
        data_content = data_file.read()
        # add the type in database
        XMLdata(template_id, xml=data_content).save()


class ExploreTestSuite(RegressionTest):
    def setUp(self):
        # call parent setUp
        super(ExploreTestSuite, self).setUp()
        # add a template
        template = load_template(join(RESOURCES_PATH, 'schema.xsd'))
        # load data
        load_data(join(RESOURCES_PATH, '1.xml'), str(template.id))
        load_data(join(RESOURCES_PATH, '2.xml'), str(template.id))
        load_data(join(RESOURCES_PATH, '3.xml'), str(template.id))

    def test_numeric_true(self):
        criteria = build_criteria("content.root.integer", "=", 1, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)

    def test_numeric_false(self):
        criteria = build_criteria("content.root.integer", "=", 4, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_numeric_not(self):
        criteria = build_criteria("content.root.integer", "=", 1, "xs:int", "xs", isNot=True)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_numeric_inferior(self):
        criteria = build_criteria("content.root.integer", "lt", 3, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_numeric_inferior_equals(self):
        criteria = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)

    def test_numeric_superior(self):
        criteria = build_criteria("content.root.integer", "gt", 1, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_numeric_superior_equals(self):
        criteria = build_criteria("content.root.integer", "gte", 1, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)

    def test_decimal_true(self):
        criteria = build_criteria("content.root.float", "=", 1, "xs:float", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)

    def test_decimal_false(self):
        criteria = build_criteria("content.root.float", "=", 4, "xs:float", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_decimal_not(self):
        criteria = build_criteria("content.root.float", "=", 1, "xs:float", "xs", isNot=True)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_str_true(self):
        criteria = build_criteria("content.root.str", "is", "test1", "xs:string", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)

    def test_str_false(self):
        criteria = build_criteria("content.root.str", "is", "test4", "xs:string", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_str_not(self):
        criteria = build_criteria("content.root.str", "is", "test1", "xs:string", "xs", isNot=True)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_regex_true(self):
        criteria = build_criteria("content.root.str", "like", "test", "xs:string", "xs")
        manageRegexBeforeExe(criteria)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)

    def test_regex_false(self):
        criteria = build_criteria("content.root.str", "like", "set", "xs:string", "xs")
        manageRegexBeforeExe(criteria)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_regex_not(self):
        criteria = build_criteria("content.root.str", "like", "test", "xs:string", "xs", isNot=True)
        manageRegexBeforeExe(criteria)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_or_numeric_0(self):
        criteria1 = build_criteria("content.root.integer", "=", 0, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "gte", 4, "xs:int", "xs")
        criteria = ORCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_or_numeric_1(self):
        criteria1 = build_criteria("content.root.integer", "=", 0, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "gte", 3, "xs:int", "xs")
        criteria = ORCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)

    def test_or_numeric_2(self):
        criteria1 = build_criteria("content.root.integer", "=", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "gte", 3, "xs:int", "xs")
        criteria = ORCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_or_numeric_3(self):
        criteria1 = build_criteria("content.root.integer", "=", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "gte", 2, "xs:int", "xs")
        criteria = ORCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)

    def test_or_numeric_not(self):
        criteria1 = build_criteria("content.root.integer", "=", 1, "xs:int", "xs", isNot=True)
        criteria2 = build_criteria("content.root.integer", "gte", 1, "xs:int", "xs")
        criteria = ORCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)

    def test_and_numeric_0(self):
        criteria1 = build_criteria("content.root.integer", "=", 0, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "gte", 4, "xs:int", "xs")
        criteria = ANDCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_and_numeric_1(self):
        criteria1 = build_criteria("content.root.integer", "=", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        criteria = ANDCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)

    def test_and_numeric_2(self):
        criteria1 = build_criteria("content.root.integer", "gt", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        criteria = ANDCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_and_numeric_3(self):
        criteria1 = build_criteria("content.root.integer", "gte", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        criteria = ANDCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)

    def test_and_numeric_not(self):
        criteria1 = build_criteria("content.root.integer", "=", 1, "xs:int", "xs", isNot=True)
        criteria2 = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        criteria = ANDCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_enum_true(self):
        criteria = build_criteria("content.root.enum", "is", "a", "enum", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)

    def test_enum_false(self):
        criteria = build_criteria("content.root.enum", "is", "d", "enum", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_enum_not(self):
        criteria = build_criteria("content.root.enum", "is", "a", "enum", "xs", isNot=True)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_invert_numeric(self):
        criteria = build_criteria("content.root.integer", "=", 1, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)
        inverted = invertQuery(criteria)
        inverted_results = XMLdata.executeQueryFullResult(inverted)
        self.assertTrue(len(inverted_results) == 2)

    def test_invert_str(self):
        criteria = build_criteria("content.root.str", "is", "test1", "xs:string", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)
        inverted = invertQuery(criteria)
        inverted_results = XMLdata.executeQueryFullResult(inverted)
        self.assertTrue(len(inverted_results) == 2)

    def test_invert_or_numeric(self):
        criteria1 = build_criteria("content.root.integer", "gt", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        criteria = ORCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)
        inverted = invertQuery(criteria)
        inverted_results = XMLdata.executeQueryFullResult(inverted)
        self.assertTrue(len(inverted_results) == 3)

    def test_invert_and_numeric(self):
        criteria1 = build_criteria("content.root.integer", "gt", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        criteria = ANDCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)
        inverted = invertQuery(criteria)
        inverted_results = XMLdata.executeQueryFullResult(inverted)
        self.assertTrue(len(inverted_results) == 3)


class ExploreNSTestSuite(RegressionTest):
    def setUp(self):
        # call parent setUp
        super(ExploreNSTestSuite, self).setUp()
        # add a template
        template = load_template(join(RESOURCES_PATH, 'schema-attr.xsd'))
        # load data
        load_data(join(RESOURCES_PATH, '1-attr.xml'), str(template.id))
        load_data(join(RESOURCES_PATH, '2-attr.xml'), str(template.id))
        load_data(join(RESOURCES_PATH, '3-attr.xml'), str(template.id))

    def test_numeric_true(self):
        criteria = build_criteria("content.root.integer", "=", 1, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)

    def test_numeric_false(self):
        criteria = build_criteria("content.root.integer", "=", 4, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_numeric_not(self):
        criteria = build_criteria("content.root.integer", "=", 1, "xs:int", "xs", isNot=True)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_numeric_inferior(self):
        criteria = build_criteria("content.root.integer", "lt", 3, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_numeric_inferior_equals(self):
        criteria = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)

    def test_numeric_superior(self):
        criteria = build_criteria("content.root.integer", "gt", 1, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_numeric_superior_equals(self):
        criteria = build_criteria("content.root.integer", "gte", 1, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)

    def test_decimal_true(self):
        criteria = build_criteria("content.root.float", "=", 1, "xs:float", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)

    def test_decimal_false(self):
        criteria = build_criteria("content.root.float", "=", 4, "xs:float", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_decimal_not(self):
        criteria = build_criteria("content.root.float", "=", 1, "xs:float", "xs", isNot=True)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_str_true(self):
        criteria = build_criteria("content.root.str", "is", "test1", "xs:string", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)

    def test_str_false(self):
        criteria = build_criteria("content.root.str", "is", "test4", "xs:string", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_str_not(self):
        criteria = build_criteria("content.root.str", "is", "test1", "xs:string", "xs", isNot=True)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_regex_true(self):
        criteria = build_criteria("content.root.str", "like", "test", "xs:string", "xs")
        manageRegexBeforeExe(criteria)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)

    def test_regex_false(self):
        criteria = build_criteria("content.root.str", "like", "set", "xs:string", "xs")
        manageRegexBeforeExe(criteria)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_regex_not(self):
        criteria = build_criteria("content.root.str", "like", "test", "xs:string", "xs", isNot=True)
        manageRegexBeforeExe(criteria)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_or_numeric_0(self):
        criteria1 = build_criteria("content.root.integer", "=", 0, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "gte", 4, "xs:int", "xs")
        criteria = ORCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_or_numeric_1(self):
        criteria1 = build_criteria("content.root.integer", "=", 0, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "gte", 3, "xs:int", "xs")
        criteria = ORCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)

    def test_or_numeric_2(self):
        criteria1 = build_criteria("content.root.integer", "=", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "gte", 3, "xs:int", "xs")
        criteria = ORCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_or_numeric_3(self):
        criteria1 = build_criteria("content.root.integer", "=", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "gte", 2, "xs:int", "xs")
        criteria = ORCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)

    def test_or_numeric_not(self):
        criteria1 = build_criteria("content.root.integer", "=", 1, "xs:int", "xs", isNot=True)
        criteria2 = build_criteria("content.root.integer", "gte", 1, "xs:int", "xs")
        criteria = ORCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)

    def test_and_numeric_0(self):
        criteria1 = build_criteria("content.root.integer", "=", 0, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "gte", 4, "xs:int", "xs")
        criteria = ANDCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_and_numeric_1(self):
        criteria1 = build_criteria("content.root.integer", "=", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        criteria = ANDCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)

    def test_and_numeric_2(self):
        criteria1 = build_criteria("content.root.integer", "gt", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        criteria = ANDCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_and_numeric_3(self):
        criteria1 = build_criteria("content.root.integer", "gte", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        criteria = ANDCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)

    def test_and_numeric_not(self):
        criteria1 = build_criteria("content.root.integer", "=", 1, "xs:int", "xs", isNot=True)
        criteria2 = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        criteria = ANDCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_enum_true(self):
        criteria = build_criteria("content.root.enum", "is", "a", "enum", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)

    def test_enum_false(self):
        criteria = build_criteria("content.root.enum", "is", "d", "enum", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 0)

    def test_enum_not(self):
        criteria = build_criteria("content.root.enum", "is", "a", "enum", "xs", isNot=True)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)

    def test_invert_numeric(self):
        criteria = build_criteria("content.root.integer", "=", 1, "xs:int", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)
        inverted = invertQuery(criteria)
        inverted_results = XMLdata.executeQueryFullResult(inverted)
        self.assertTrue(len(inverted_results) == 2)

    def test_invert_str(self):
        criteria = build_criteria("content.root.str", "is", "test1", "xs:string", "xs")
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)
        inverted = invertQuery(criteria)
        inverted_results = XMLdata.executeQueryFullResult(inverted)
        self.assertTrue(len(inverted_results) == 2)

    def test_invert_or_numeric(self):
        criteria1 = build_criteria("content.root.integer", "gt", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        criteria = ORCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 3)
        inverted = invertQuery(criteria)
        inverted_results = XMLdata.executeQueryFullResult(inverted)
        self.assertTrue(len(inverted_results) == 3)

    def test_invert_and_numeric(self):
        criteria1 = build_criteria("content.root.integer", "gt", 1, "xs:int", "xs")
        criteria2 = build_criteria("content.root.integer", "lte", 3, "xs:int", "xs")
        criteria = ANDCriteria(criteria1, criteria2)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 2)
        inverted = invertQuery(criteria)
        inverted_results = XMLdata.executeQueryFullResult(inverted)
        self.assertTrue(len(inverted_results) == 3)


class ExploreEncodingTestSuite(RegressionTest):
    def setUp(self):
        # call parent setUp
        super(ExploreEncodingTestSuite, self).setUp()
        # add a template
        template = load_template(join(RESOURCES_PATH, 'schema.xsd'))
        # load data
        load_data(join(RESOURCES_PATH, 'encoding.xml'), str(template.id))

    def test_str_encoding(self):
        criteria = build_criteria("content.root.str", "is", "test", "xs:string", "xs", isNot=True)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)


class ExploreNSEncodingTestSuite(RegressionTest):
    def setUp(self):
        # call parent setUp
        super(ExploreNSEncodingTestSuite, self).setUp()
        # add a template
        template = load_template(join(RESOURCES_PATH, 'schema-attr.xsd'))
        # load data
        load_data(join(RESOURCES_PATH, 'encoding-attr.xml'), str(template.id))

    def test_str_encoding(self):
        criteria = build_criteria("content.root.str", "is", "test", "xs:string", "xs", isNot=True)
        results = XMLdata.executeQueryFullResult(criteria)
        self.assertTrue(len(results) == 1)
