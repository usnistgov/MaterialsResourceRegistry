################################################################################
#
# File Name: tests_views.py
# Application: dashboard
# Description:
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from testing.models import RegressionTest, FAKE_ID
from mgi.models import XMLdata
from unittest import skip

class tests_user_dashboard_views(RegressionTest):

    def test_dashboard_records_no_param_ispublished(self):
        userId = self.getUser().id
        self.createXMLData(ispublished=True, iduser=userId)
        self.createXMLData(ispublished=False, iduser=userId)
        url = '/dashboard/resources'
        r = self.doRequestGetUserClientLogged(url=url)
        self.assertEquals(2, len(r.context[1].get('XMLdatas')))

    def test_dashboard_records_ispublished(self):
        userId = self.getUser().id
        self.createXMLData(ispublished=True, iduser=userId)
        self.createXMLData(ispublished=False, iduser=userId)
        data = {'ispublished': True}
        url = '/dashboard/resources'
        r = self.doRequestGetUserClientLogged(url=url, data=data)
        self.assertEquals(1, len(r.context[1].get('XMLdatas')))

    def test_dashboard_records_isnotpublished(self):
        userId = self.getUser().id
        self.createXMLData(ispublished=True, iduser=userId)
        self.createXMLData(ispublished=False, iduser=userId)
        data = {'ispublished': False}
        url = '/dashboard/resources'
        r = self.doRequestGetUserClientLogged(url=url, data=data)
        self.assertEquals(1, len(r.context[1].get('XMLdatas')))

    def test_dashboard_records_multiple_records_different_user(self):
        userId = self.getUser().id
        self.createXMLData(iduser=userId)
        self.createXMLData(iduser=userId+1)
        url = '/dashboard/resources'
        r = self.doRequestGetUserClientLogged(url=url)
        self.assertEquals(1, len(r.context[1].get('XMLdatas')))

    def test_dashboard_records_admin(self):
        userId = self.getUser().id
        adminId = self.getAdmin().id
        self.createXMLData(iduser=userId)
        self.createXMLData(iduser=adminId)
        url = '/dashboard/resources'
        r = self.doRequestGetAdminClientLogged(url=url)
        self.assertEquals(1, len(r.context.__getitem__('XMLdatas')))
        self.assertEquals(1, len(r.context.__getitem__('OtherUsersXMLdatas')))

    def test_dashboard_my_forms_user_no_xmldataid(self):
        userId = self.getUser().id
        template = self.createTemplate()
        self.createFormData(user=userId, name='name', template=str(template.id))
        url = '/dashboard/drafts'
        r = self.doRequestGetUserClientLogged(url=url)
        self.assertEquals(1, len(r.context[1].get('forms')))

    def test_dashboard_my_forms_user_with_xmldataid(self):
        userId = self.getUser().id
        template = self.createTemplate()
        self.createFormData(user=userId, name='name', template=str(template.id), xml_data_id=FAKE_ID)
        url = '/dashboard/drafts'
        r = self.doRequestGetUserClientLogged(url=url)
        self.assertEquals(0, len(r.context[1].get('forms')))

    def test_dashboard_my_forms_admin_no_xmldataid(self):
        userId = self.getUser().id
        adminId = self.getAdmin().id
        template = self.createTemplate()
        self.createFormData(user=userId, name='nameuser', template=str(template.id))
        self.createFormData(user=adminId, name='nameadmin', template=str(template.id))
        url = '/dashboard/drafts'
        r = self.doRequestGetAdminClientLogged(url=url)
        self.assertEquals(1, len(r.context[1].get('forms')))
        self.assertEquals(1, len(r.context[1].get('otherUsersForms')))

    @skip("Only on MDCS")
    def test_dashboard_templates_user(self):
        userId = self.getUser().id
        self.createTemplate(user=userId)
        url = '/dashboard/templates'
        r = self.doRequestGetUserClientLogged(url=url)
        self.assertEquals(1, len(r.context[1].get('objects')))

    @skip("Only on MDCS")
    def test_dashboard_templates_user_no_template(self):
        userId = self.getUser().id
        self.createTemplate(user=userId+1)
        url = '/dashboard/templates'
        r = self.doRequestGetUserClientLogged(url=url)
        self.assertEquals(0, len(r.context[1].get('objects')))

    @skip("Only on MDCS")
    def test_dashboard_templates_admin(self):
        userId = self.getUser().id
        adminId = self.getAdmin().id
        self.createTemplate(user=userId)
        self.createTemplate(user=adminId)
        url = '/dashboard/templates'
        r = self.doRequestGetAdminClientLogged(url=url)
        self.assertEquals(1, len(r.context[1].get('objects')))
        self.assertEquals(1, len(r.context[1].get('otherUsersObjects')))

    @skip("Only on MDCS")
    def test_dashboard_types_user(self):
        userId = self.getUser().id
        self.createType(user=userId)
        url = '/dashboard/types'
        r = self.doRequestGetUserClientLogged(url=url)
        self.assertEquals(1, len(r.context[1].get('objects')))

    @skip("Only on MDCS")
    def test_dashboard_types_user_no_template(self):
        userId = self.getUser().id
        self.createType(user=userId + 1)
        url = '/dashboard/types'
        r = self.doRequestGetUserClientLogged(url=url)
        self.assertEquals(0, len(r.context[1].get('objects')))

    @skip("Only on MDCS")
    def test_dashboard_types_admin(self):
        userId = self.getUser().id
        adminId = self.getAdmin().id
        self.createType(user=userId)
        self.createType(user=adminId)
        url = '/dashboard/types'
        r = self.doRequestGetAdminClientLogged(url=url)
        self.assertEquals(1, len(r.context[1].get('objects')))
        self.assertEquals(1, len(r.context[1].get('otherUsersObjects')))

    def test_dashboard_detail_record_form(self):
        userId = self.getUser().id
        template = self.createTemplate()
        formData = self.createFormData(user=userId, name='name', template=str(template.id), xml_data='<test>test xmldata</test>')
        url = '/dashboard/detail'
        data = {'type': 'form', 'id': str(formData.id)}
        r = self.doRequestGetUserClientLogged(url=url, data=data)
        self.assertEquals('name', r.context[1].get('title'))
        self.assertIsNotNone(r.context[1].get('XMLHolder'))

    def test_dashboard_detail_record_record(self):
        userId = self.getUser().id
        template = self.createTemplate()
        xmldataid = self.createXMLData(iduser=userId, schemaID=template.id)
        url = '/dashboard/detail'
        data = {'type': 'record', 'id': str(xmldataid)}
        r = self.doRequestGetUserClientLogged(url=url, data=data)
        self.assertEquals('test', r.context[1].get('title'))
        self.assertIsNotNone(r.context[1].get('XMLHolder'))

    def test_change_owner_record_no_data(self):
        url = '/dashboard/change-owner-record'
        r = self.doRequestPostUserClientLogged(url=url)
        self.isStatusBadRequest(r.status_code)

    def test_change_owner_record(self):
        userId = self.getUser().id
        adminId = self.getAdmin().id
        template = self.createTemplate()
        xmldataid = self.createXMLData(iduser=userId, schemaID=template.id)
        self.assertEquals(str(userId), str(XMLdata.get(xmldataid)['iduser']))
        url = '/dashboard/change-owner-record'
        data = {'recordID': str(xmldataid), 'userID': str(adminId)}
        r = self.doRequestPostUserClientLogged(url=url, data=data)
        self.assertEquals(str(adminId), str(XMLdata.get(xmldataid)['iduser']))
        self.isStatusOK(r.status_code)
