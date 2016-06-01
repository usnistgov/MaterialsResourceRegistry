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
from django.conf.urls import patterns, url, include
from ajax import get_results_by_instance_keyword
urlpatterns = patterns(
    'oai_pmh.explore.views',
    url(r'^keyword',  'index_keyword', name='index-keyword'),
    url(r'^get_results_by_instance_keyword', get_results_by_instance_keyword),
    url(r'^get_metadata_formats_detail', 'get_metadata_formats_detail'),
    url(r'^get_metadata_formats', 'get_metadata_formats'),
    url(r'^detail_result_keyword$', 'explore_detail_result_keyword', name='explore-detail-result-keyword'),
)

