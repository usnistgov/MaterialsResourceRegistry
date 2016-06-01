################################################################################
#
# File Name: tests.py
# Application: oai_pmh/explore
# Purpose:
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from mgi.models import OaiRecord
from oai_pmh.tests.models import OAI_PMH_Test
import json
from bson.objectid import ObjectId
from oai_pmh.explore.ajax import get_results_by_instance_keyword
from django.test.client import RequestFactory
from django.contrib.auth.models import User


class tests_OAI_PMH_ajax(OAI_PMH_Test):

    def test_results_by_instance_keyword_no_data(self):
        url = '/oai_pmh/explore/get_results_by_instance_keyword/'
        req = RequestFactory().get(url)
        req.session = {}
        req.user = User.objects.get(username='admin')
        r = get_results_by_instance_keyword(req)
        result = json.loads(r)
        self.assertEquals(result.get('count'), 0)
        self.assertEquals(result.get('resultString'), '')
        self.assertEquals(result.get('resultsByKeyword'), [])

    def test_results_by_instance_keyword_with_data(self):
        OaiRecord.initIndexes()
        self.dump_oai_registry()
        self.dump_template()
        self.dump_oai_my_metadata_format()
        data = {'keyword': 'MGI', 'schemas[]': ['software', 'service']}
        url = '/oai_pmh/explore/get_results_by_instance_keyword/'
        req = RequestFactory().get(url, data=data)
        req.session = {}
        req.user = User.objects.get(username='admin')
        r = get_results_by_instance_keyword(req)
        result = json.loads(r)
        self.assertIsNotNone(result.get('resultString'))
        self.assertEquals(result.get('count'), 1)
        self.assertEquals(result.get('resultsByKeyword'), [])

    def test_results_by_instance_keyword_with_data_and_suggestions(self):
        OaiRecord.initIndexes()
        self.dump_oai_registry()
        self.dump_template()
        self.dump_oai_my_metadata_format()
        data = {'keyword': 'MGI', 'schemas[]': ['software', 'service'], 'onlySuggestions': json.dumps(True)}
        url = '/oai_pmh/explore/get_results_by_instance_keyword/'
        req = RequestFactory().get(url, data=data)
        req.session = {}
        req.user = User.objects.get(username='admin')
        r = get_results_by_instance_keyword(req)
        result = json.loads(r)
        self.assertEquals(result.get('resultString'), '')
        self.assertEquals(result.get('count'), 1)
        self.assertEquals(result.get('resultsByKeyword')[0].get('label'), 'mgi')
        self.assertEquals(result.get('resultsByKeyword')[0].get('value'), 'mgi')


class tests_OAI_PMH_explore(OAI_PMH_Test):

    def test_keyword(self):
        self.dump_oai_registry()
        url = '/oai_pmh/explore/keyword/'
        r = self.doRequestGetAdminClientLogged(url=url)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.context)

    def test_keyword_no_authentification(self):
        url = '/oai_pmh/explore/keyword/'
        r = self.doRequestGet(url=url)
        self.isStatusOK(r.status_code)
        self.assertIn('login', r.url)

    def test_get_metadata_format(self):
        self.dump_oai_registry()
        self.dump_oai_my_metadata_format()
        self.dump_template()
        url = '/oai_pmh/explore/get_metadata_formats/'
        data = {'registries[]': ['5731fc7fa530af33ed232f6b']}
        r = self.doRequestGetAdminClientLogged(url=url, data=data)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.context)
        self.assertTrue(any('metadata_formats_Form' in key for key in r.context.dicts))

    def test_get_metadata_format_detail_no_data_no_param(self):
        url = '/oai_pmh/explore/get_metadata_formats_detail/'
        r = self.doRequestGetAdminClientLogged(url=url)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.context)
        self.assertEqual(len(r.context.dicts[1].get('list_metadata_formats_info')), 0)
        self.assertIsNone(r.context.dicts[1].get('local'))

    def test_get_metadata_format_detail_no_local(self):
        self.dump_oai_registry()
        url = '/oai_pmh/explore/get_metadata_formats_detail/'
        dict = json.dumps({'oai-pmh': ['5731fc7fa530af33ed232f76', '5731fc7fa530af33ed232f77']})
        data = {'metadataFormats': dict}
        r = self.doRequestGetAdminClientLogged(url=url, data=data)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.context)
        self.assertEqual(len(r.context.dicts[1].get('list_metadata_formats_info')), 2)
        self.assertIsNone(r.context.dicts[1].get('local'))

    def test_get_metadata_format_detail_with_local(self):
        self.dump_oai_registry()
        self.dump_template()
        url = '/oai_pmh/explore/get_metadata_formats_detail/'
        dict = json.dumps({'oai-pmh': ['5731fc7fa530af33ed232f76', '5731fc7fa530af33ed232f77'], 'local': 'test'})
        data = {'metadataFormats': dict}
        r = self.doRequestGetAdminClientLogged(url=url, data=data)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.context)
        self.assertEqual(len(r.context.dicts[1].get('list_metadata_formats_info')), 2)
        self.assertEqual(r.context.dicts[1].get('local'), 'test')

    def test_explore_detail_result_keyword_no_title(self):
        self.dump_oai_record()
        url = '/oai_pmh/explore/detail_result_keyword'
        data = {'id': '5731fe36a530af33ed232f82'}
        r = self.doRequestGetAdminClientLogged(url=url, data=data)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.context)
        self.assertIsNotNone(r.context[0].dicts[1].get('XMLHolder'))
        self.assertEqual(r.context[0].dicts[1].get('title'), OaiRecord.objects.get(pk=ObjectId('5731fe36a530af33ed232f82')).identifier)

    def test_explore_detail_result_keyword_with_title(self):
        self.dump_oai_record()
        url = '/oai_pmh/explore/detail_result_keyword'
        data = {'id': '5731fe36a530af33ed232f82', 'title': 'test_title'}
        r = self.doRequestGetAdminClientLogged(url=url, data=data)
        self.isStatusOK(r.status_code)
        self.assertIsNotNone(r.context)
        self.assertIsNotNone(r.context[0].dicts[1].get('XMLHolder'))
        self.assertEqual(r.context[0].dicts[1].get('title'), 'test_title')
