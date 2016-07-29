################################################################################
#
# File Name: tests_ajax.py
# Application: dashboard
# Description:
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from testing.models import RegressionTest
from mgi.models import Template, Type, XMLdata, TemplateVersion, TypeVersion, SchemaElement, FormData, Status
import json
from unittest import skip
import lxml.etree as etree

class tests_user_dashboard_ajax(RegressionTest):

    @skip("Only on MDCS")
    def test_edit_information_template(self):
        template = self.createTemplate()
        url='/dashboard/edit_information'
        data = {'objectID': template.id, 'objectType': 'Template', 'newName': ' othername', 'newFilename': 'otherfilename '}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        modifiedTemplate = Template.objects.get(pk=template.id)
        self.assertEquals('otherfilename', modifiedTemplate.filename)
        self.assertEquals('othername', modifiedTemplate.title)

    @skip("Only on MDCS")
    def test_edit_information_type(self):
        type = self.createType()
        url='/dashboard/edit_information'
        data = {'objectID': type.id, 'objectType': 'Type', 'newName': 'othername ', 'newFilename': ' otherfilename'}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        modifiedType = Type.objects.get(pk=type.id)
        self.assertEquals('otherfilename', modifiedType.filename)
        self.assertEquals('othername', modifiedType.title)

    @skip("Only on MDCS")
    def test_edit_information_template_same_name(self):
        self.createTemplate(title='othername')
        template = self.createTemplate()
        url = '/dashboard/edit_information'
        data = {'objectID': template.id, 'objectType': 'Template', 'newName': ' othername', 'newFilename': 'otherfilename '}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        modifiedTemplate = Template.objects.get(pk=template.id)
        self.assertNotEquals('otherfilename', modifiedTemplate.filename)
        self.assertNotEquals('othername', modifiedTemplate.title)
        self.assertEquals('test', modifiedTemplate.filename)
        self.assertEquals('test', modifiedTemplate.title)
        result = json.loads(r.content)
        self.assertEquals('True', result.get('name'))

    @skip("Only on MDCS")
    def test_edit_information_type_same_filename(self):
        self.createType(filename='otherfilename')
        type = self.createType()
        url = '/dashboard/edit_information'
        data = {'objectID': type.id, 'objectType': 'Type', 'newName': 'othername ', 'newFilename': ' otherfilename'}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        modifiedType = Type.objects.get(pk=type.id)
        self.assertNotEquals('otherfilename', modifiedType.filename)
        self.assertNotEquals('othername', modifiedType.title)
        self.assertEquals('test', modifiedType.filename)
        self.assertEquals('test', modifiedType.title)
        result = json.loads(r.content)
        self.assertEquals('True', result.get('filename'))

    def test_delete_result(self):
        id = self.createXMLData()
        self.assertIsNotNone(XMLdata.get(id))
        url = '/dashboard/delete_result'
        data = {'result_id': str(id)}
        r = self.doRequestGetAdminClientLogged(url=url, data=data)
        self.assertIsNone(XMLdata.get(id))

    def test_update_publish(self):
        id = self.createXMLData()
        self.assertEquals(False, XMLdata.get(id)['ispublished'])
        url = '/dashboard/update_publish'
        data = {'result_id': str(id)}
        r = self.doRequestGetAdminClientLogged(url=url, data=data)
        self.assertEquals(True, XMLdata.get(id)['ispublished'])

    def test_update_unpublish(self):
        id = self.createXMLData(ispublished=True)
        self.assertEquals(True, XMLdata.get(id)['ispublished'])
        url = '/dashboard/update_unpublish'
        data = {'result_id': str(id)}
        r = self.doRequestGetAdminClientLogged(url=url, data=data)
        self.assertEquals(False, XMLdata.get(id)['ispublished'])

    @skip("Only on MDCS")
    def test_delete_object_template(self):
        template = self.createTemplate()
        url = '/dashboard/delete_object'
        data = {'objectID': template.id, 'objectType': 'Template'}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        self.assertEquals(0, len(Template.objects()))
        self.assertEquals(0, len(TemplateVersion.objects()))

    @skip("Only on MDCS")
    def test_delete_object_type(self):
        type = self.createType()
        url = '/dashboard/delete_object'
        data = {'objectID': type.id, 'objectType': 'Type'}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        self.assertEquals(0, len(Type.objects()))
        self.assertEquals(0, len(TypeVersion.objects()))

    @skip("Only on MDCS")
    def test_delete_object_template_with_dependencie(self):
        self.assertEquals(0, len(Template.objects()))
        template = self.createTemplate()
        self.assertEquals(1, len(Template.objects()))
        self.createXMLData(schemaID=template.id)
        url = '/dashboard/delete_object'
        data = {'objectID': template.id, 'objectType': 'Template'}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        self.assertEquals(1, len(Template.objects()))
        self.assertEquals(1, len(TemplateVersion.objects()))

    @skip("Only on MDCS")
    def test_delete_object_type_with_dependencie(self):
        type = self.createType()
        otherType = self.createType()
        otherType.dependencies = [str(type.id)]
        otherType.save()
        url = '/dashboard/delete_object'
        data = {'objectID': type.id, 'objectType': 'Type'}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        self.assertIsNotNone(Type.objects(pk=type.id).get())

    def test_update_publish_draft(self):
        status = Status.ACTIVE
        new_xml = "<Resource localid='' status='"+status+"'><identity>" \
               "<title>My new software</title></identity><curation><publisher>PF</publisher><contact><name></name>" \
               "</contact></curation><content><description>This is a new record</description><subject></subject>" \
               "<referenceURL></referenceURL></content></Resource>"
        id = self.createXMLData(ispublished=True)
        xmlData = XMLdata.get(id)
        self.assertNotEquals(new_xml, XMLdata.unparse(xmlData['content']))
        adminId = self.getAdmin().id
        template = self.createTemplate()
        elements = SchemaElement.objects().all()
        self.assertEqual(len(elements), 0)
        elementsForm = FormData.objects().all()
        self.assertEqual(len(elementsForm), 0)
        formData = self.createFormData(user=adminId, name='name', template=str(template.id), xml_data=new_xml,
                                       xml_data_id=str(id))
        url = '/dashboard/update_publish_draft'
        data = {'draft_id': str(formData.id)}
        r = self.doRequestGetAdminClientLogged(url=url, data=data)
        xmlDataInDatabase = XMLdata.get(id)
        elements = SchemaElement.objects().all()
        self.assertEqual(len(elements), 0)
        elementsForm = FormData.objects().all()
        self.assertEqual(len(elementsForm), 0)
        self.assertEquals(etree.XML(new_xml).text, etree.XML(str(XMLdata.unparse(xmlDataInDatabase['content']))).text)
        self.assertEquals(True, xmlDataInDatabase.get('ispublished'))
        self.assertEquals(str(adminId), xmlDataInDatabase.get('iduser'))
        self.assertNotEquals(xmlData.get('lastmodificationdate'), xmlDataInDatabase.get('lastmodificationdate'))
        self.assertNotEquals(xmlData.get('publicationdate'), xmlDataInDatabase.get('publicationdate'))
        self.assertEquals(status, xmlDataInDatabase.get('status'))



