################################################################################
#
# File Name: urls.py
# Application: Informatics Core
# Description:
#
# Author: Pierre Francois RIGODIAT
#         pierre-francois.rigodiat@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'oai_pmh.api.views',
    #OAI-PMH Verbs
    url(r'^listobjectallrecords$', 'listObjectAllRecords', name='api_listObjectAllRecords'), #ListRecords
    url(r'^objectidentify$', 'objectIdentify', name='api_objectIdentify'), #Identify
    url(r'^listobjectmetadataformats$', 'listObjectMetadataFormats', name='api_listObjectMetadataFormats'), #ListMF
    url(r'^listobjectsets$', 'listObjectSets', name='api_listObjectSets'), #List Set
    url(r'^listidentifiers$', 'listIdentifiers', name='api_listIdentifiers'), #List Identify
    url(r'^getrecord$', 'getRecord', name='api_getRecord'), #GetRecord
    #Manage Data Providers
    url(r'^select/registry$', 'select_registry'),
    url(r'^add/registry$', 'add_registry', name='api_add_registry'),
    url(r'^update/registry$', 'update_registry', name='api_update_registry'),
    url(r'^update/registry-info$', 'update_registry_info', name='api_update_registry_info'),
    url(r'^delete/registry$', 'delete_registry', name='api_delete_registry'),
    url(r'^deactivate/registry$', 'deactivate_registry', name='api_deactivate_registry'),
    url(r'^reactivate/registry$', 'reactivate_registry', name='api_reactivate_registry'),
    #Manage my server
    url(r'^update/my-registry$', 'update_my_registry', name="api_update_my_registry"),
    #Manage my server's metadata formats
    url(r'^add/my-metadataFormat$', 'add_my_metadataFormat', name='api_add_my_metadataFormat'),
    url(r'^add/my-template-metadataFormat', 'add_my_template_metadataFormat', name='api_add_my_template_metadataFormat'),
    url(r'^update/my-metadataFormat$', 'update_my_metadataFormat', name='api_update_my_metadataFormat'),
    url(r'^delete/my-metadataFormat$', 'delete_my_metadataFormat', name='api_delete_my_metadataFormat'),
    #Manage my server's sets
    url(r'^add/my-set$', 'add_my_set', name='api_add_my_set'),
    url(r'^update/my-set$', 'update_my_set', name='api_update_my_set'),
    url(r'^delete/my-set$', 'delete_my_set', name='api_delete_my_set'),
    #Get data
    url(r'^getdata/$', 'getData', name='api_get_data'),
    #Harvest data
    url(r'^harvest$', 'harvest', name='api_harvest'),
    #Harvest configuration
    url(r'^update/registry-harvest$', 'update_registry_harvest', name='api_update_registry_harvest'),
    #Manage XSLT
    url(r'^upload/xslt$', 'upload_oai_pmh_xslt', name='api_upload_oai_pmh_xslt'),
    url(r'^oai-pmh-conf/xslt$', 'oai_pmh_conf_xslt', name='api_oai_pmh_conf_xslt'),
    url(r'^edit/xslt', 'edit_oai_pmh_xslt', name='api_edit_oai_pmh_xslt'),
    url(r'^delete/xslt$', 'delete_oai_pmh_xslt', name='api_delete_oai_pmh_xslt'),


    url(r'^select/all/registries$', 'select_all_registries', name='api_select_all_registries'),
)
