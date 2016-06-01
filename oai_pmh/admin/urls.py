################################################################################
#
# File Name: url.py
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
    'oai_pmh.admin.views',
    url(r'^oai-pmh$', 'oai_pmh', name='oai_pmh'),
    #Manage Data Providers
    url(r'^check/registry$', 'check_registry'),
    url(r'^add/registry', 'add_registry'),
    url(r'^update/registry$', 'update_registry'),
    url(r'^update/registry-info$', 'update_registry_info'),
    url(r'^delete/registry$', 'delete_registry'),
    url(r'^oai-pmh-detail-registry$', 'oai_pmh_detail_registry', name='oai_pmh_detail_registry'),
    url(r'^check/update-info', 'check_update_info', name='check_update_info'),
    url(r'^deactivate/registry$', 'deactivate_registry'),
    url(r'^reactivate/registry$', 'reactivate_registry'),
    #Manage my server's metadata formats
    url(r'^add/my-metadataFormat', 'add_my_metadataFormat'),
    url(r'^add/my-template-metadataFormat', 'add_my_template_metadataFormat'),
    url(r'^update/my-metadataFormat$', 'update_my_metadataFormat'),
    url(r'^delete/my-metadataFormat', 'delete_my_metadataFormat'),
    #Manage my server's sets
    url(r'^add/my-set', 'add_my_set'),
    url(r'^update/my-set$', 'update_my_set'),
    url(r'^delete/my-set', 'delete_my_set'),
    #Manage my server
    url(r'^oai-pmh-my-infos', 'oai_pmh_my_infos', name='oai_pmh_my_infos'),
    url(r'^update/my-registry$', 'update_my_registry'),
    #Harvest
    url(r'^check/harvest-data', 'check_harvest_data', name='check_harvest_data'),
    url(r'^harvest', 'harvest', name='harvest'),
    #Manage XSLT
    url(r'^oai-pmh-conf-xslt$', 'oai_pmh_conf_xslt', name='oai_pmh_conf_xslt'),
    url(r'^manage-xslt', 'manage_oai_pmh_xslt', name='manage_oai_pmh_xslt'),
    url(r'^delete-xslt', 'delete_oai_pmh_xslt', name='delete_oai_pmh_xslt'),
    url(r'^edit-xslt', 'edit_oai_pmh_xslt', name='edit_oai_pmh_xslt'),
    #Harvest configuration
    url(r'^update/registry-harvest$', 'update_registry_harvest'),
)

