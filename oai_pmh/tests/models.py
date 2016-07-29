
################################################################################
#
# File Name: models.py
# Application: oai_pmh/tests
# Purpose:
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from testing.models import RegressionTest, DUMP_OAI_PMH_TEST_PATH, join
from mgi.models import OaiMyMetadataFormat, OaiTemplMfXslt, OaiMySet, OaiSettings, OaiXslt, OaiIdentify,\
    OaiMetadataFormat, OaiSet, OaiRecord, OaiRegistry

class OAI_PMH_Test(RegressionTest):


    def dump_oai_my_metadata_format(self):
        self.assertEquals(len(OaiMyMetadataFormat.objects()), 0)
        self.restoreDump(join(DUMP_OAI_PMH_TEST_PATH, 'oai_my_metadata_format.bson'), 'oai_my_metadata_format')
        self.assertTrue(len(OaiMyMetadataFormat.objects()) > 0)

    def dump_oai_my_metadata_format_bad(self):
        self.assertEquals(len(OaiMyMetadataFormat.objects()), 0)
        self.restoreDump(join(DUMP_OAI_PMH_TEST_PATH, 'oai_my_metadata_format_bad.bson'), 'oai_my_metadata_format')
        self.assertTrue(len(OaiMyMetadataFormat.objects()) > 0)

    def dump_oai_my_set(self):
        self.assertEquals(len(OaiMySet.objects()), 0)
        self.restoreDump(join(DUMP_OAI_PMH_TEST_PATH, 'oai_my_set.bson'), 'oai_my_set')
        self.assertTrue(len(OaiMySet.objects()) > 0)

    def dump_oai_my_set_bad(self):
        self.assertEquals(len(OaiMySet.objects()), 0)
        self.restoreDump(join(DUMP_OAI_PMH_TEST_PATH, 'oai_my_set_bad.bson'), 'oai_my_set')
        self.assertTrue(len(OaiMySet.objects()) > 0)

    def dump_oai_settings(self):
        self.assertEquals(len(OaiSettings.objects()), 0)
        self.restoreDump(join(DUMP_OAI_PMH_TEST_PATH, 'oai_settings.bson'), 'oai_settings')
        self.assertTrue(len(OaiSettings.objects()) > 0)

    def dump_oai_settings_bad(self):
        self.assertEquals(len(OaiSettings.objects()), 0)
        self.restoreDump(join(DUMP_OAI_PMH_TEST_PATH, 'oai_settings_bad.bson'), 'oai_settings')
        self.assertTrue(len(OaiSettings.objects()) > 0)

    def dump_oai_templ_mf_xslt(self):
        self.assertEquals(len(OaiTemplMfXslt.objects()), 0)
        self.restoreDump(join(DUMP_OAI_PMH_TEST_PATH, 'oai_templ_mf_xslt.bson'), 'oai_templ_mf_xslt')
        self.assertTrue(len(OaiTemplMfXslt.objects()) > 0)

    def dump_oai_xslt(self):
        self.assertEquals(len(OaiXslt.objects()), 0)
        self.restoreDump(join(DUMP_OAI_PMH_TEST_PATH, 'oai_xslt.bson'), 'oai_xslt')
        self.assertTrue(len(OaiXslt.objects()) > 0)

    def dump_oai_registry(self, dumpRecords=True, dumpSets=True, dumpMetadataFormats=True):
        self.assertEquals(len(OaiRegistry.objects()), 0)
        self.restoreDump(join(DUMP_OAI_PMH_TEST_PATH, 'oai_registry.bson'), 'oai_registry')
        self.assertTrue(len(OaiRegistry.objects()) > 0)
        self.dump_oai_identify()
        if dumpMetadataFormats:
            self.dump_oai_metadata_format()
        if dumpSets:
            self.dump_oai_set()
        if dumpRecords:
            self.dump_oai_record()

    def dump_oai_identify(self):
        self.assertEquals(len(OaiIdentify.objects()), 0)
        self.restoreDump(join(DUMP_OAI_PMH_TEST_PATH, 'oai_identify.bson'), 'oai_identify')
        self.assertTrue(len(OaiIdentify.objects()) > 0)

    def dump_oai_metadata_format(self):
        self.assertEquals(len(OaiMetadataFormat.objects()), 0)
        self.restoreDump(join(DUMP_OAI_PMH_TEST_PATH, 'oai_metadata_format.bson'), 'oai_metadata_format')
        self.assertTrue(len(OaiMetadataFormat.objects()) > 0)

    def dump_oai_set(self):
        self.assertEquals(len(OaiSet.objects()), 0)
        self.restoreDump(join(DUMP_OAI_PMH_TEST_PATH, 'oai_set.bson'), 'oai_set')
        self.assertTrue(len(OaiSet.objects()) > 0)

    def dump_oai_record(self):
        self.assertEquals(len(OaiRecord.objects()), 0)
        self.restoreDump(join(DUMP_OAI_PMH_TEST_PATH, 'oai_record.bson'), 'oai_record')
        self.assertTrue(len(OaiRecord.objects()) > 0)
