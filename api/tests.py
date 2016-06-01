################################################################################
#
# File Name: tests.py
# Application: api
# Purpose:
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from testing.models import TokenTest, TemplateVersion, XMLDATA_VALID_CONTENT, FAKE_ID, XMLdata

class tests_token(TokenTest):

    def test_select_all_schema_admin(self):
        r = self.doRequestGet(self.get_token_admin(), url="/rest/templates/select/all")
        if r.status_code == 200:
            self.assertTrue(r.text != '')
        else:
            self.assertFalse(False)

    def test_select_all_schema_user(self):
        r = self.doRequestGet(self.get_token_user(), url="/rest/templates/select/all")
        self.isStatusUnauthorized(r.status_code)

    def test_select_schema_error_no_param(self):
        r = self.doRequestGet(self.get_token_admin(), url="/rest/templates/select")
        self.isStatusBadRequest(r.status_code)

    def test_select_schema_error_no_schema(self):
        param = {'id':'test'}
        r = self.doRequestGet(self.get_token_admin(), url="/rest/templates/select",params=param)
        self.isStatusNotFound(r.status_code)

    def test_select_schema_error_user(self):
        param = {'id':'test'}
        r = self.doRequestGet(self.get_token_user(), url="/rest/templates/select",params=param)
        self.isStatusUnauthorized(r.status_code)

    def test_select_schema_admin_id(self):
        templateID = self.createTemplate()
        param = {'id': templateID.id}
        r = self.doRequestGet(self.get_token_admin(), url="/rest/templates/select",params=param)
        self.isStatusOK(r.status_code)

    def test_explore_error(self):
        r = self.doRequestGet(self.get_token_admin(), url="/rest/explore/select/all", params={'dataformat': 'error'})
        self.isStatusBadRequest(r.status_code)

    def test_explore_admin(self):
        self.createXMLData()
        r = self.doRequestGet(self.get_token_admin(), url="/rest/explore/select/all")
        self.isStatusOK(r.status_code)

    def test_explore_user(self):
        r = self.doRequestGet(self.get_token_user(), url="/rest/explore/select/all")
        self.isStatusOK(r.status_code)

    def test_explore_delete_error_no_param(self):
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/explore/delete")
        self.isStatusBadRequest(r.status_code)

    def test_explore_delete_error_wrong_id(self):
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/explore/delete", params={'id': 'test'})
        self.isStatusNotFound(r.status_code)

    def test_explore_delete_user(self):
        id = str(self.createXMLData())
        r = self.doRequestDelete(self.get_token_user(), url="/rest/explore/delete", params={'id': id})
        self.isStatusNoContent(r.status_code)

    def test_explore_delete_admin(self):
        id = str(self.createXMLData())
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/explore/delete", params={'id': id})
        self.isStatusNoContent(r.status_code)

    def test_delete_schema_error_version_id_admin(self):
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'templateVersion': 'ver', 'id':'test'})
        self.isStatusBadRequest(r.status_code)

    def test_delete_schema_error_version_next_admin(self):
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'templateVersion': 'ver', 'next':'test'})
        self.isStatusBadRequest(r.status_code)

    def test_delete_schema_error_version_id_next_admin(self):
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'templateVersion': 'ver', 'id':'test', 'next':'test'})
        self.isStatusBadRequest(r.status_code)

    def test_delete_schema_error_version_not_exist_admin(self):
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'templateVersion': 'ver'})
        self.isStatusNotFound(r.status_code)

    def test_delete_schema_error_user(self):
        r = self.doRequestDelete(self.get_token_user(), url="/rest/templates/delete", params={'templateVersion': 'ver', 'id':'test', 'next':'test'})
        self.isStatusUnauthorized(r.status_code)

    def test_delete_schema_error_version_already_deleted_admin(self):
        templateVersion = self.createTemplateVersionDeleted()
        r = self.doRequestDelete(self.get_token_user(), url="/rest/templates/delete", params={'templateVersion': str(templateVersion.id)})
        self.isStatusUnauthorized(r.status_code)

    def test_delete_schema_version_admin(self):
        templateVersion = self.createTemplateVersion()
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'templateVersion': str(templateVersion.id)})
        self.isStatusOK(r.status_code)

    def test_delete_schema_no_id_admin(self):
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete")
        self.isStatusBadRequest(r.status_code)

    def test_delete_schema_bad_id_delete_schema(self):
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'id':'abcdefghijklmn'})
        self.isStatusNotFound(r.status_code)

    def test_delete_schema_next_not_found_admin(self):
        template1 = self.createTemplate()
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'id':str(template1.id), 'next':'abcdefghijklmn'})
        self.isStatusNotFound(r.status_code)

    def test_delete_schema_2_templates_different_version_admin(self):
        templateVersion1 = self.createTemplateVersion()
        templateVersion2 = self.createTemplateVersion()
        template1 = self.createTemplateWithTemplateVersion(str(templateVersion1.id))
        template2 = self.createTemplateWithTemplateVersion(str(templateVersion2.id))
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'id':str(template1.id), 'next':str(template2.id)})
        self.isStatusBadRequest(r.status_code)

    def test_delete_schema_templateversion_deleted_admin(self):
        templateVersion1 = self.createTemplateVersionDeleted()
        template1 = self.createTemplateWithTemplateVersion(str(templateVersion1.id))
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'id':str(template1.id)})
        self.isStatusBadRequest(r.status_code)

    def test_delete_schema_templateversion_current_no_next_admin(self):
        templateVersion1 = self.createTemplateVersion()
        template1 = self.createTemplateWithTemplateVersion(str(templateVersion1.id))
        templateVersion1.current = str(template1.id)
        templateVersion1.save()
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'id':str(template1.id)})
        self.isStatusBadRequest(r.status_code)

    def test_delete_schema_next_same_as_current_admin(self):
        templateVersion1 = self.createTemplateVersion()
        template1 = self.createTemplateWithTemplateVersion(str(templateVersion1.id))
        templateVersion1.current = str(template1.id)
        templateVersion1.save()
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'id':str(template1.id), 'next':str(template1.id)})
        self.isStatusBadRequest(r.status_code)

    def test_delete_schema_template_not_current_and_next_admin(self):
        templateVersion1 = self.createTemplateVersion()
        template1 = self.createTemplateWithTemplateVersion(str(templateVersion1.id))
        template2 = self.createTemplateWithTemplateVersion(str(templateVersion1.id))
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'id':str(template1.id), 'next':str(template2.id)})
        self.isStatusBadRequest(r.status_code)

    def test_delete_schema_template_and_next_admin(self):
        templateVersion1 = self.createTemplateVersion()
        template1 = self.createTemplateWithTemplateVersion(str(templateVersion1.id))
        template2 = self.createTemplateWithTemplateVersion(str(templateVersion1.id))
        templateVersion1.current = str(template1.id)
        templateVersion1.save()
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'id':str(template1.id), 'next':str(template2.id)})
        self.isStatusNoContent(r.status_code)
        templateVersion = TemplateVersion.objects.get(pk=template1.templateVersion)
        self.assertTrue(templateVersion.current == str(template2.id))

    def test_delete_schema_template_and_deleted_next_admin(self):
        templateVersion1 = self.createTemplateVersion()
        template1 = self.createTemplateWithTemplateVersion(str(templateVersion1.id))
        template2 = self.createTemplateWithTemplateVersion(str(templateVersion1.id))
        templateVersion1.current = str(template1.id)
        templateVersion1.deletedVersions.append(str(template2.id))
        templateVersion1.save()
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'id':str(template1.id), 'next':str(template2.id)})
        self.isStatusBadRequest(r.status_code)

    def test_delete_schema_template_not_current_no_next_admin(self):
        templateVersion1 = self.createTemplateVersion()
        template1 = self.createTemplateWithTemplateVersion(str(templateVersion1.id))
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'id':str(template1.id)})
        self.isStatusNoContent(r.status_code)
        templateVersion = TemplateVersion.objects.get(pk=template1.templateVersion)
        self.assertTrue(str(template1.id) in templateVersion.deletedVersions)

    def test_delete_schema_deleted_template_not_current_no_next_admin(self):
        templateVersion1 = self.createTemplateVersion()
        template1 = self.createTemplateWithTemplateVersion(str(templateVersion1.id))
        templateVersion1.deletedVersions.append(str(template1.id))
        templateVersion1.save()
        r = self.doRequestDelete(self.get_token_admin(), url="/rest/templates/delete", params={'id':str(template1.id)})
        self.isStatusBadRequest(r.status_code)

    def test_curate_error_serializer_admin(self):
        data = {'content': '<test> test xml </test>'}
        r = self.doRequestPost(self.get_token_admin(), url="/rest/curate", data=data)
        self.isStatusBadRequest(r.status_code)

    def test_curate_error_schema_admin(self):
        data = {'title': 'test', 'schema': FAKE_ID, 'content': '<test> test xml </test>'}
        r = self.doRequestPost(self.get_token_admin(), url="/rest/curate", data=data)
        self.isStatusBadRequest(r.status_code)

    def test_curate_error_schema_deleted_admin(self):
        templateVersion1 = self.createTemplateVersion()
        template1 = self.createTemplateWithTemplateVersion(str(templateVersion1.id))
        templateVersion1.deletedVersions.append(str(template1.id))
        templateVersion1.save()
        data = {'title': 'test', 'schema':str(template1.id), 'content': '<test> test xml </test>'}
        r = self.doRequestPost(self.get_token_admin(), url="/rest/curate", data=data)
        self.isStatusBadRequest(r.status_code)

    def test_curate_schema_error_xml_syntax_admin(self):
        templateVersion1 = self.createTemplateVersion()
        template1 = self.createTemplateWithTemplateVersionValidContent(str(templateVersion1.id))
        data = {'title': 'test', 'schema': str(template1.id), 'content': '<test> test xml </test>'}
        r = self.doRequestPost(self.get_token_admin(), url="/rest/curate", data=data)
        self.isStatusBadRequest(r.status_code)

    def test_curate_schema_error_xml_validation_admin(self):
        templateVersion1 = self.createTemplateVersion()
        template1 = self.createTemplateWithTemplateVersionValidContent(str(templateVersion1.id))
        data = {'title': 'test', 'schema': str(template1.id), 'content': XMLDATA_VALID_CONTENT + '<'}
        r = self.doRequestPost(self.get_token_admin(), url="/rest/curate", data=data)
        self.isStatusBadRequest(r.status_code)

    def test_curate_schema_admin(self):
        self.assertTrue(len(XMLdata.objects()) == 0)
        templateVersion1 = self.createTemplateVersion()
        template1 = self.createTemplateWithTemplateVersionValidContent(str(templateVersion1.id))
        data = {'title': 'test', 'schema': str(template1.id), 'content': XMLDATA_VALID_CONTENT}
        r = self.doRequestPost(self.get_token_admin(), url="/rest/curate", data=data)
        self.isStatusCreated(r.status_code)
        self.assertTrue(len(XMLdata.objects()) == 1)

    def test_curate_schema_user(self):
        self.assertTrue(len(XMLdata.objects()) == 0)
        templateVersion1 = self.createTemplateVersion()
        template1 = self.createTemplateWithTemplateVersionValidContent(str(templateVersion1.id))
        data = {'title': 'test', 'schema': str(template1.id), 'content': XMLDATA_VALID_CONTENT}
        r = self.doRequestPost(self.get_token_user(), url="/rest/curate", data=data)
        self.isStatusCreated(r.status_code)
        self.assertTrue(len(XMLdata.objects()) == 1)
