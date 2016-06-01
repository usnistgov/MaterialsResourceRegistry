################################################################################
#
# File Name: urls.py
# Application: explore
# Purpose:   
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume Sousa Amaral
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^keyword',  'explore.views.index_keyword', name='expore-index-keyword'),
    url(r'^detail_result_keyword$', 'explore.views.explore_detail_result_keyword', name='explore-detail-result-keyword'),
    url(r'^verify_template_is_selected', 'explore.ajax.verify_template_is_selected'),
    url(r'^get_results_by_instance_keyword', 'explore.ajax.get_results_by_instance_keyword'),
    url(r'^back_to_query', 'explore.ajax.back_to_query'),
    url(r'^start_export', 'explore.views.start_export'),
    url(r'^custom-view', 'explore.ajax.custom_view'),
    url(r'^load_refinements', 'explore.ajax.load_refinements'),
)