################################################################################
#
# File Name: urls.py
# Application: api
# Purpose:   
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from django.conf.urls import patterns, url, include
from api.views import docs, ping

urlpatterns = patterns(
    'api.views',
    url(r'^saved_queries/select/all$','select_all_savedqueries'),
    url(r'^saved_queries/select$','select_savedquery'),
    url(r'^saved_queries/delete$','delete_savedquery'),
    url(r'^saved_queries/add$','add_savedquery'),
    url(r'^curate$', 'curate', name='curate'),
    url(r'^explore/select/all$', 'explore', name='explore'),
    url(r'^explore/data/download$', 'explore_detail_data_download', name='explore_detail_data_download'),
    url(r'^explore/select$', 'explore_detail', name='explore_detail'),
    url(r'^explore/delete$', 'explore_delete', name='explore_delete'),
    url(r'^explore/query-by-example$', 'query_by_example', name='query_by_example'),
    url(r'^templates/add$','add_schema', name='add_schema'),
    url(r'^templates/select$','select_schema'),
    url(r'^templates/delete$','delete_schema'),
    url(r'^templates/restore$','restore_schema'),
    url(r'^templates/select/all$','select_all_schemas'),
    url(r'^templates/versions/select/all$','select_all_schemas_versions'),
    url(r'^templates/versions/current$','current_template_version'),
    url(r'^types/add$','add_type', name='add_type'),
    url(r'^types/select$','select_type'),
    url(r'^types/delete$','delete_type'),
    url(r'^types/restore$','restore_type'),
    url(r'^types/select/all$','select_all_types'),
    url(r'^types/versions/select/all$','select_all_types_versions'),
    url(r'^types/versions/current$','current_type_version'),
    url(r'^types/get-dependency$','get_dependency'),
    url(r'^repositories/select/all$','select_all_repositories'),
    url(r'^repositories/select','select_repository'),
    url(r'^repositories/add$','add_repository'),
    url(r'^repositories/delete$','delete_repository'),
    url(r'^users/select/all$','select_all_users'),
    url(r'^users/select','select_user'),
    url(r'^users/add$','add_user'),
    url(r'^users/delete$','delete_user'),
    url(r'^users/update$','update_user'),
    url(r'^blob$','blob'),
    url(r'^exporter/select/all$','select_all_exporters'),
    url(r'^exporter/select$','select_exporter'),
    url(r'^exporter/xslt/add$','add_xslt', name='add_xslt'),
    # url(r'^exporter/xslt/select/all$','select_all_xslt_exporters'),
    # url(r'^exporter/xslt/select$','select_xslt_exporter'),
    url(r'^exporter/xslt/delete$','delete_xslt'),
    url(r'^exporter/export','export'),
    url('', include([url(r'^ping$', ping)], namespace='ping')),
    url(r'^.*$', include([url(r'', docs)], namespace='error_redirect')),    
)


