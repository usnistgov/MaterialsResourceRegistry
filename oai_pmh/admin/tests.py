################################################################################
#
# File Name: tests.py
# Application: oai_pmh/admin
# Purpose:
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from oai_pmh.tests.models import OAI_PMH_Test
from mgi.models import OaiRegistry, OaiRecord, OaiSettings
import json

class tests_OAI_PMH_admin(OAI_PMH_Test):

    def test_oai_pmh_admin_no_data(self):
        url = '/oai_pmh/admin/oai-pmh'
        r = self.doRequestGetAdminClientLogged(url=url)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.content)
        self.assertIsNotNone(r.context[0].dicts[1].get('registry_form'))
        self.assertEquals(len(r.context[0].dicts[1].get('registries')), 0)

    def test_oai_pmh_admin_with_data(self):
        self.dump_oai_registry()
        url = '/oai_pmh/admin/oai-pmh'
        r = self.doRequestGetAdminClientLogged(url=url)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.content)
        self.assertIsNotNone(r.context[0].dicts[1].get('registry_form'))
        self.assertEquals(len(r.context[0].dicts[1].get('registries')), len(OaiRegistry.objects()))

    def test_oai_pmh_user_no_data(self):
        url = '/oai_pmh/admin/oai-pmh'
        r = self.doRequestGetUserClientLogged(url=url)
        self.assertEquals(r.status_code, 302)

    def test_oai_pmh_check_registry_not_logged(self):
        url = '/oai_pmh/admin/check/registry'
        r = self.doRequestPost(url=url)
        self.assertEquals(r.status_code, 302)

    def test_oai_pmh_check_registry_logged_no_url(self):
        url = '/oai_pmh/admin/check/registry'
        r = self.doRequestPostAdminClientLogged(url=url)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.content)
        result = json.loads(r.content)
        self.assertFalse(result.get('isAvailable'))

    def test_oai_pmh_check_registry_logged_bad_url(self):
        url = '/oai_pmh/admin/check/registry'
        r = self.doRequestPostAdminClientLogged(url=url, data={'url': 'http://test.com/'})
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.content)
        result = json.loads(r.content)
        self.assertFalse(result.get('isAvailable'))

    def test_oai_pmh_detail_registry(self):
        self.dump_oai_registry()
        url = '/oai_pmh/admin/oai-pmh-detail-registry'
        id = '5731fc7fa530af33ed232f6b'
        data = {'id': id}
        r = self.doRequestGetAdminClientLogged(url=url, data=data)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.context)
        self.assertIsNotNone(r.context.dicts[1].get('metadataformats'))
        self.assertIsNotNone(r.context.dicts[1].get('sets'))
        self.assertEqual(r.context.dicts[1].get('nbRecords'), OaiRecord.objects(registry=id).count())
        self.assertIsNotNone(r.context.dicts[1].get('registry'))

    def test_oai_pmh_check_harvest_data_post(self):
        self.dump_oai_registry()
        url = '/oai_pmh/admin/check/harvest-data'
        r = self.doRequestPostAdminClientLogged(url=url)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.content)
        result = json.loads(r.content)
        self.assertFalse(result[0].get('isHarvesting'))
        self.assertEquals(result[0].get('registry_id'), '5731fc7fa530af33ed232f6b')
        self.assertIsNotNone(result[0].get('lastUpdate'))

    def test_oai_pmh_my_infos(self):
        self.dump_oai_settings()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        url = '/oai_pmh/admin/oai-pmh-my-infos/'
        r = self.doRequestGetAdminClientLogged(url=url)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.context)
        self.assertIsNotNone(r.context[0].dicts[1].get('sets'))
        self.assertIsNotNone(r.context[0].dicts[1].get('metadataformat_form'))
        self.assertIsNotNone(r.context[0].dicts[1].get('template_metadataformat_form'))
        self.assertIsNotNone(r.context[0].dicts[1].get('metadataFormats'))
        self.assertIsNotNone(r.context[0].dicts[1].get('set_form'))
        self.assertIsNotNone(r.context[0].dicts[1].get('defaultMetadataFormats'))
        self.assertIsNotNone(r.context[0].dicts[1].get('templateMetadataFormats'))
        self.assertEquals(r.context[0].dicts[1].get('data_provider').get('name'), OaiSettings.objects.get().repositoryName)

    def test_oai_pmh_check_update_info_no_data(self):
        url = '/oai_pmh/admin/check/update-info'
        r = self.doRequestPostAdminClientLogged(url=url)
        self.isStatusOK(r.status_code)
        self.assertEquals(len(json.loads(r.content)), 0)

    def test_oai_pmh_check_update_info_with_data(self):
        self.dump_oai_registry()
        url = '/oai_pmh/admin/check/update-info'
        r = self.doRequestPostAdminClientLogged(url=url)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.content)
        result = json.loads(r.content)
        self.assertIsNone(result[0].get('isHarvesting'))
        self.assertEquals(result[0].get('registry_id'), '5731fc7fa530af33ed232f6b')
        self.assertIsNotNone(result[0].get('name'))
