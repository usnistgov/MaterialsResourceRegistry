################################################################################
#
# File Name: tests.py
# Application: oai_pmh/server
# Purpose:
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from oai_pmh.tests.models import OAI_PMH_Test
from mgi.models import OaiSettings, OaiMySet, OaiMyMetadataFormat, Template, XMLdata, Status
from oai_pmh.server.exceptions import BAD_VERB, NO_SET_HIERARCHY, BAD_ARGUMENT, DISSEMINATE_FORMAT, NO_RECORDS_MATCH, NO_METADATA_FORMAT, ID_DOES_NOT_EXIST
from testing.models import OAI_SCHEME, OAI_REPO_IDENTIFIER
import datetime
URL = '/oai_pmh/server'

class tests_OAI_PMH_server(OAI_PMH_Test):

    def setUp(self):
        super(tests_OAI_PMH_server, self).setUp()
        self.dump_oai_settings()
        self.doHarvest(True)

    def doHarvest(self, harvest):
        information = OaiSettings.objects.get()
        information.enableHarvesting = harvest
        information.save()

    def doRequestServer(self, data=None):
        return self.doRequestGet(URL, params=data)

    def test_no_setting(self):
        self.clean_db()
        r = self.doRequestServer()
        self.isStatusInternalError(r.status_code)

    def test_no_harvesting(self):
        self.doHarvest(False)
        r = self.doRequestServer()
        self.isStatusNotFound(r.status_code)

    def test_no_verb(self):
        r = self.doRequestServer()
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, BAD_VERB)

    def test_bad_verb(self):
        r = self.doRequestServer(data={'verb': 'test'})
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, BAD_VERB)

    def test_illegal_argument(self):
        r = self.doRequestServer(data={'verb': 'Identify', 'test': 'test'})
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, BAD_ARGUMENT)

    def test_duplicate(self):
        data = {'verb': ['ListSets', 'ListSets']}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, BAD_ARGUMENT)

    def test_identify(self):
        data = {'verb': 'Identify'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagExist(r.text, 'Identify')

    def test_listSets_no_sets(self):
        data = {'verb': 'ListSets'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, NO_SET_HIERARCHY)

    def test_listSets(self):
        self.dump_oai_my_set()
        data = {'verb': 'ListSets'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagExist(r.text, 'ListSets')
        self.checkTagCount(r.text, 'set', len(OaiMySet.objects().all()))

    def test_list_identifiers_error_argument_metadataprefix_missing(self):
        data = {'verb': 'ListIdentifiers', 'from':'test'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, BAD_ARGUMENT)

    def test_list_identifiers_error_date_from(self):
        data = {'verb': 'ListIdentifiers', 'metadataPrefix': 'test', 'from': 'test'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, BAD_ARGUMENT)

    def test_list_identifiers_error_date_until(self):
        data = {'verb': 'ListIdentifiers', 'metadataPrefix': 'test', 'until': 'test'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, BAD_ARGUMENT)

    def test_list_identifiers_error_no_metadataformat(self):
        data = {'verb': 'ListIdentifiers', 'metadataPrefix': 'oai_dc', 'from': '2015-01-01T12:12:12Z', 'until': '2016-01-01T12:12:12Z'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, DISSEMINATE_FORMAT)

    def test_list_identifiers_error_with_no_set(self):
        self.dump_oai_my_metadata_format()
        data = {'verb': 'ListIdentifiers', 'metadataPrefix': 'oai_dc', 'from': '2015-01-01T12:12:12Z', 'until': '2016-01-01T12:12:12Z', 'set': 'test'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, NO_RECORDS_MATCH)

    def test_list_identifiers_error_with_bad_set(self):
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        data = {'verb': 'ListIdentifiers', 'metadataPrefix': 'oai_dc', 'from': '2015-01-01T12:12:12Z', 'until': '2016-01-01T12:12:12Z', 'set': 'test'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, NO_RECORDS_MATCH)

    def test_list_identifiers_with_no_xmldata(self):
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_my_metadata_format()
        self.dump_template()
        data = {'verb': 'ListIdentifiers', 'metadataPrefix': 'oai_dc', 'from': '2015-01-01T12:12:12Z', 'until': '2016-01-01T12:12:12Z'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, NO_RECORDS_MATCH)

    def test_list_identifiers_with_set(self):
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        data = {'verb': 'ListIdentifiers', 'metadataPrefix': 'oai_dc', 'from': '2015-01-01T12:12:12Z', 'until': '2017-01-01T12:12:12Z', 'set': 'soft'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagExist(r.text, 'ListIdentifiers')

    def test_list_identifiers_with_no_set(self):
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_my_metadata_format()
        self.dump_xmldata()
        data = {'verb': 'ListIdentifiers', 'metadataPrefix': 'oai_dc', 'from': '2015-01-01T12:12:12Z', 'until': '2017-01-01T12:12:12Z'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagExist(r.text, 'ListIdentifiers')

    def test_list_metadataformat_no_data(self):
        data = {'verb': 'ListMetadataFormats'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, NO_METADATA_FORMAT)

    def test_list_metadataformat_no_xmldata(self):
        self.dump_template()
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_my_metadata_format()
        identifier = '%s:%s:id/%s' % (OAI_SCHEME, OAI_REPO_IDENTIFIER, '572a51dca530afee94f3b35c')
        data = {'verb': 'ListMetadataFormats', 'identifier': identifier}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, ID_DOES_NOT_EXIST)

    def test_list_metadataformat_no_identifier(self):
        self.dump_oai_my_metadata_format()
        data = {'verb': 'ListMetadataFormats'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagExist(r.text, 'ListMetadataFormats')
        self.checkTagCount(r.text, 'metadataFormat', len(OaiMyMetadataFormat.objects().all()))

    def test_list_metadataformat_with_identifier(self):
        self.dump_xmldata()
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_my_metadata_format()
        idXMLdata = str(XMLdata.find({'title':'MPInterfaces.xml'})[0]['_id'])
        identifier = '%s:%s:id/%s' % (OAI_SCHEME, OAI_REPO_IDENTIFIER, idXMLdata)
        data = {'verb': 'ListMetadataFormats', 'identifier': identifier}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagExist(r.text, 'ListMetadataFormats')
        self.checkTagExist(r.text, 'metadataFormat')

    def test_get_record_missing_identifier(self):
        identifier = '%s:%s:id/%s' % (OAI_SCHEME, OAI_REPO_IDENTIFIER, '572a51dca530afee94f3b35c')
        data = {'verb': 'GetRecord', 'metadataPrefix': 'oai_dc'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, BAD_ARGUMENT)

    def test_get_record_missing_metadataprefix(self):
        identifier = '%s:%s:id/%s' % (OAI_SCHEME, OAI_REPO_IDENTIFIER, '572a51dca530afee94f3b35c')
        data = {'verb': 'GetRecord', 'identifier': identifier}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, BAD_ARGUMENT)

    def test_get_record_bad_id(self):
        identifier = '%s:%s:id/%s' % (OAI_SCHEME, OAI_REPO_IDENTIFIER, 'ttest')
        data = {'verb': 'GetRecord', 'identifier': identifier, 'metadataPrefix': 'oai_dc'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, ID_DOES_NOT_EXIST)

    def test_get_record_id_does_not_exist(self):
        identifier = '%s:%s:id/%s' % (OAI_SCHEME, OAI_REPO_IDENTIFIER, '000051dca530afee94f30000')
        data = {'verb': 'GetRecord', 'identifier': identifier, 'metadataPrefix': 'oai_dc'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, ID_DOES_NOT_EXIST)

    def test_get_record_no_templ_xslt(self):
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.dump_oai_my_metadata_format()
        idXMLdata = str(XMLdata.find({'title': 'MGI Code Catalog.xml'})[0]['_id'])
        identifier = '%s:%s:id/%s' % (OAI_SCHEME, OAI_REPO_IDENTIFIER, idXMLdata)
        data = {'verb': 'GetRecord', 'identifier': identifier, 'metadataPrefix': 'oai_dc'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, DISSEMINATE_FORMAT)

    def test_get_record(self):
        self.dump_oai_my_set()
        self.dump_xmldata()
        self.dump_oai_my_metadata_format()
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_xslt()
        idXMLdata = str(XMLdata.find({'title': 'MGI Code Catalog.xml'})[0]['_id'])
        identifier = '%s:%s:id/%s' % (OAI_SCHEME, OAI_REPO_IDENTIFIER, idXMLdata)
        data = {'verb': 'GetRecord', 'identifier': identifier, 'metadataPrefix': 'oai_dc'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagExist(r.text, 'GetRecord')
        self.checkTagExist(r.text, 'record')

    def test_get_list_record_missing_metadataprefix(self):
        data = {'verb': 'ListRecords', 'set': 'soft'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, BAD_ARGUMENT)

    def test_get_list_record_bad_until_date(self):
        data = {'verb': 'ListRecords', 'set': 'soft', 'metadataPrefix': 'oai_dc', 'until': 'test'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, BAD_ARGUMENT)

    def test_get_list_record_bad_from_date(self):
        data = {'verb': 'ListRecords', 'set': 'soft', 'metadataPrefix': 'oai_dc', 'from': 'test'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, BAD_ARGUMENT)

    def test_get_list_record_no_metadataformat(self):
        data = {'verb': 'ListRecords', 'set': 'soft', 'metadataPrefix': 'oai_dc'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, DISSEMINATE_FORMAT)

    def test_get_list_record_no_set_in_database(self):
        self.dump_oai_my_metadata_format()
        data = {'verb': 'ListRecords', 'set': 'soft', 'metadataPrefix': 'oai_dc'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, NO_RECORDS_MATCH)

    def test_get_list_record_no_templaet_in_database(self):
        self.dump_oai_my_metadata_format()
        data = {'verb': 'ListRecords', 'metadataPrefix': 'oai_dc'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, NO_RECORDS_MATCH)

    def test_get_list_record_with_set(self):
        self.dump_oai_my_set()
        self.dump_oai_templ_mf_xslt()
        self.dump_xmldata()
        self.dump_oai_my_metadata_format()
        self.dump_oai_xslt()
        data = {'verb': 'ListRecords', 'metadataPrefix': 'oai_dc', 'set': 'soft'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagExist(r.text, 'ListRecords')
        self.checkTagExist(r.text, 'record')

    def test_get_list_record_no_xmldata(self):
        self.dump_oai_my_set()
        self.dump_oai_templ_mf_xslt()
        self.dump_template()
        self.dump_oai_my_metadata_format()
        self.dump_oai_xslt()
        data = {'verb': 'ListRecords', 'metadataPrefix': 'oai_dc'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, NO_RECORDS_MATCH)

    def test_get_xsd_not_found(self):
        self.dump_oai_registry()
        url = URL + '/XSD/AllResources.xsd'
        r = self.doRequestGet(url=url)
        self.isStatusNotFound(r.status_code)

    def test_get_xsd(self):
        self.dump_oai_registry()
        self.dump_template()
        url = URL + '/XSD/AllResources.xsd'
        r = self.doRequestGet(url=url)
        self.isStatusOK(r.status_code)
        objInDatabase = Template.objects.get(filename='AllResources.xsd')
        self.assertEquals(objInDatabase.content, r.content)

    def test_list_identifiers_deleted(self):
        self.list_test_deleted('ListIdentifiers')

    def test_list_records_deleted(self):
        self.list_test_deleted('ListRecords')

    def test_get_record_deleted(self):
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        template = Template.objects(filename='Software.xsd').get()
        dataSoft = XMLdata.find({'schema': str(template.id), 'status': {'$ne': Status.DELETED}})
        if len(dataSoft) > 0:
            xmlDataId = dataSoft[0]['_id']
            identifier = '%s:%s:id/%s' % (OAI_SCHEME, OAI_REPO_IDENTIFIER, xmlDataId)
            data = {'verb': 'GetRecord', 'identifier': identifier, 'metadataPrefix': 'oai_soft'}
            r = self.doRequestServer(data=data)
            self.isStatusOK(r.status_code)
            #Check attribute status='deleted' of header doesn't exist
            self.checkTagExist(r.text, 'GetRecord')
            self.checkTagExist(r.text, 'record')
            #Delete one record
            XMLdata.update(xmlDataId, {'status': Status.DELETED})
            r = self.doRequestServer(data=data)
            self.isStatusOK(r.status_code)
            #Check attribute status='deleted' of header does exist
            self.checkTagExist(r.text, 'GetRecord')
            # Only for NMRR
            self.checkTagWithParamExist(r.text, 'header', 'status="deleted"')

    def list_test_deleted(self, verb):
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        data = {'verb': verb, 'metadataPrefix': 'oai_soft'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        #Check attribute status='deleted' of header doesn't exist
        self.checkTagExist(r.text, verb)
        #Delete one record
        template = Template.objects(filename='Software.xsd').get()
        dataSoft = XMLdata.find({'schema': str(template.id), 'status': {'$ne': Status.DELETED}})
        if len(dataSoft) > 0:
            XMLdata.update(dataSoft[0]['_id'], {'status': Status.DELETED})
            r = self.doRequestServer(data=data)
            self.isStatusOK(r.status_code)
            self.checkTagExist(r.text, verb)
            #Check attribute status='deleted' of header does exist
            self.checkTagWithParamExist(r.text, 'header', 'status="deleted"')

    def test_check_dates_form_until(self):
        self.dump_oai_templ_mf_xslt()
        self.dump_oai_xslt()
        self.dump_oai_my_metadata_format()
        self.dump_oai_my_set()
        self.dump_xmldata()
        data = {'verb': 'ListRecords', 'metadataPrefix': 'oai_dc', 'from': '2016-05-04T19:00:00Z', 'until': '2016-05-04T19:48:39Z', 'set': 'soft'}
        r = self.doRequestServer(data=data)
        self.isStatusOK(r.status_code)
        self.checkTagErrorCode(r.text, NO_RECORDS_MATCH)
