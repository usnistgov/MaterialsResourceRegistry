################################################################################
#
# File Name: tests_mgiutils.py
# Application: mgi
# Description:
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from testing.models import RegressionTest
from mgi.models import XMLdata, FormData, Type, Template
from mgi.mgiutils import getListNameFromDependencies

class tests_mgiutils(RegressionTest):

    def test_getListNameFromDependencies_XMLdata(self):
        self.createXMLData(schemaID='test')
        self.assertEquals('test', getListNameFromDependencies(XMLdata.find({'schema': 'test'})))

    def test_getListNameFromDependencies_FormData(self):
        FormData(template='test', name='testFormData', xml_data='testest', user=str(1)).save()
        self.assertEquals('testFormData', getListNameFromDependencies(list(FormData.objects(name='testFormData'))))

    def test_getListNameFromDependencies_Type(self):
        Type(title='testType', filename='filename', content='content', hash='hash').save()
        self.assertEquals('testType', getListNameFromDependencies(list(Type.objects(title='testType'))))

    def test_getListNameFromDependencies_Template(self):
        Template(title='testTemplate', filename='filename', content='content', hash='hash').save()
        self.assertEquals('testTemplate', getListNameFromDependencies(list(Template.objects(title='testTemplate'))))