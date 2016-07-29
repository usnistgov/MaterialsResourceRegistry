################################################################################
#
# File Name: tests_models.py
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
from mgi.models import Template, TemplateVersion, Type, TypeVersion, XMLdata, FormData, delete_template_and_version, delete_type_and_version, delete_template, delete_type, Status
from bson.objectid import ObjectId

class tests_model(RegressionTest):

    def test_delete_template_and_version(self):
        numberTemplate = len(Template.objects())
        numberTemplateVersion = len(TemplateVersion.objects())
        template = self.createTemplate()
        delete_template_and_version(str(template.id))
        self.assertEquals(len(Template.objects()), numberTemplate)
        self.assertEquals(len(TemplateVersion.objects()), numberTemplateVersion)

    def test_delete_type_and_version(self):
        self.assertEquals(len(Type.objects()), 0)
        self.assertEquals(len(TypeVersion.objects()), 0)
        type = self.createType()
        delete_type_and_version(str(type.id))
        self.assertEquals(len(Type.objects()), 0)
        self.assertEquals(len(TypeVersion.objects()), 0)

    def test_delete_template_no_dependencies(self):
        template = self.createTemplate()
        delete_template(str(template.id))
        self.assertEquals(len(Template.objects()), 0)
        self.assertEquals(len(TemplateVersion.objects()), 0)

    def test_delete_template_with_dependencies(self):
        template = self.createTemplate()
        XMLdata(schemaID=str(template.id), title='testRecord', xml='<test>test xmldata</test>').save()
        FormData(template=str(template.id), name='testFormData', xml_data='testest', user=str(1)).save()
        listDependencies = delete_template(str(template.id))
        self.assertEquals(len(Template.objects()), 1)
        self.assertEquals(len(TemplateVersion.objects()), 1)
        self.assertEquals(listDependencies, 'testFormData, testRecord')

    def test_delete_type_no_dependencies(self):
        type = self.createType()
        delete_type(str(type.id))
        self.assertEquals(len(Type.objects()), 0)
        self.assertEquals(len(TypeVersion.objects()), 0)

    def test_delete_type_with_dependencies(self):
        type = self.createType()
        Type(title='testType', filename='filename', content='content', hash='hash', dependencies=[str(type.id)]).save()
        Template(title='testTemplate', filename='filename', content='content', hash='hash', dependencies=[str(type.id)]).save()
        listDependencies = delete_type(str(type.id))
        self.assertEquals(len(Type.objects()), 2)
        self.assertEquals(len(TypeVersion.objects()), 1)
        self.assertEquals(listDependencies, 'testType, testTemplate')

    def test_change_status_case_deleted(self):
        self.change_status_case_deleted(ispublished=False)

    def test_change_status_case_deleted_published(self):
        self.change_status_case_deleted(ispublished=True)

    def test_change_status_case_inactive(self):
        self.change_status_case_inactive(ispublished=False)

    def test_change_status_case_inactive_published(self):
        self.change_status_case_inactive(ispublished=True)

    def test_change_status_case_active(self):
        self.change_status_case_active(ispublished=False)

    def test_change_status_case_active(self):
        self.change_status_case_active(ispublished=True)

    def change_status_case_deleted(self, ispublished):
        id = self.createXMLData(ispublished=ispublished)
        XMLdata.change_status(id, Status.DELETED, ispublished)
        list_xmldata = XMLdata.find({'_id': ObjectId(id)})
        self.assertEquals(Status.DELETED, list_xmldata[0]['status'])
        self.assertEquals(Status.DELETED, list_xmldata[0]['content']['Resource']['@status'])
        if ispublished:
            self.assertNotEquals(None, list_xmldata[0].get('oai_datestamp', None))
        else:
            self.assertEquals(None, list_xmldata[0].get('oai_datestamp', None))

    def change_status_case_inactive(self, ispublished):
        id = self.createXMLData(ispublished=ispublished)
        XMLdata.change_status(id, Status.INACTIVE, ispublished)
        list_xmldata = XMLdata.find({'_id': ObjectId(id)})
        self.assertEquals(Status.INACTIVE, list_xmldata[0]['status'])
        self.assertEquals(Status.INACTIVE, list_xmldata[0]['content']['Resource']['@status'])
        if ispublished:
            self.assertNotEquals(None, list_xmldata[0].get('oai_datestamp', None))
        else:
            self.assertEquals(None, list_xmldata[0].get('oai_datestamp', None))

    def change_status_case_active(self, ispublished):
        id = self.createXMLData(ispublished=ispublished)
        XMLdata.change_status(id, Status.INACTIVE)
        list_xmldata = XMLdata.find({'_id': ObjectId(id)})
        self.assertEquals(Status.INACTIVE, list_xmldata[0]['status'])
        self.assertEquals(Status.INACTIVE, list_xmldata[0]['content']['Resource']['@status'])
        XMLdata.change_status(id, Status.ACTIVE, ispublished)
        list_xmldata = XMLdata.find({'_id': ObjectId(id)})
        self.assertEquals(Status.ACTIVE, list_xmldata[0]['status'])
        self.assertEquals(Status.ACTIVE, list_xmldata[0]['content']['Resource']['@status'])
        if ispublished:
            self.assertNotEquals(None, list_xmldata[0].get('oai_datestamp', None))
        else:
            self.assertEquals(None, list_xmldata[0].get('oai_datestamp', None))




