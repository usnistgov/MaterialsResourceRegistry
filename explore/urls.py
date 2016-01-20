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

from explore import views

urlpatterns = patterns('',
#     url(r'^$', views.index, name='index'),
#     url(r'^select-template', views.index),
    url(r'^keyword',  'explore.views.index_keyword', name='expore-index-keyword'),
#     url(r'^customize-template$', 'explore.views.explore_customize_template', name='expore-customize-template'),
#     url(r'^perform-search$', 'explore.views.explore_perform_search', name='explore-perform-search'),
    url(r'^detail_result_keyword$', 'explore.views.explore_detail_result_keyword', name='explore-detail-result-keyword'),
#     url(r'^detail_result$', 'explore.views.explore_detail_result', name='explore-detail-result'),
#     url(r'^results$', 'explore.views.explore_results', name='explore-results'),
#     url(r'^all_results$', 'explore.views.explore_all_results', name='explore-all-results'),
#     url(r'^all_versions_results$', 'explore.views.explore_all_versions_results', name='explore-all-versions-results'),
#     url(r'^set_current_template', 'explore.ajax.set_current_template'),
#     url(r'^set_current_user_template', 'explore.ajax.set_current_user_template'),
#     url(r'^update_user_inputs', 'explore.ajax.update_user_inputs'),
    url(r'^verify_template_is_selected', 'explore.ajax.verify_template_is_selected'),
#     url(r'^generate_xsd_tree_for_querying_data', 'explore.ajax.generate_xsd_tree_for_querying_data'),
#     url(r'^save_custom_data', 'explore.ajax.save_custom_data'),
#     url(r'^get_custom_form', 'explore.ajax.get_custom_form'),
#     url(r'^set_current_criteria', 'explore.ajax.set_current_criteria'),
#     url(r'^select_element', 'explore.ajax.select_element'),
#     url(r'^execute_query', 'explore.ajax.execute_query'),
    url(r'^get_results_by_instance_keyword', 'explore.ajax.get_results_by_instance_keyword'),
#     url(r'^get_results_by_instance', 'explore.ajax.get_results_by_instance'),    
#     url(r'^add_field', 'explore.ajax.add_field'),
#     url(r'^remove_field', 'explore.ajax.remove_field'),
#     url(r'^save_query', 'explore.ajax.save_query'), 
#     url(r'^add_saved_query_to_form', 'explore.ajax.add_saved_query_to_form'),
#     url(r'^delete_query', 'explore.ajax.delete_query'),
#     url(r'^clear_criterias', 'explore.ajax.clear_criterias'),  
#     url(r'^clear_queries', 'explore.ajax.clear_queries'),
#     url(r'^insert_sub_element_query', 'explore.ajax.insert_sub_element_query'),  
#     url(r'^prepare_sub_element_query', 'explore.ajax.prepare_sub_element_query'),  
    url(r'^back_to_query', 'explore.ajax.back_to_query'),
#     url(r'^get_results', 'explore.ajax.get_results'),
#     url(r'^delete_result', 'explore.ajax.delete_result'),
    url(r'^update_publish', 'explore.ajax.update_publish'),
    url(r'^update_unpublish', 'explore.ajax.update_unpublish'),
    url(r'^start_export', 'explore.views.start_export'),
    url(r'^custom-view', 'explore.ajax.custom_view'),
    url(r'^load_refinements', 'explore.ajax.load_refinements'),
)
