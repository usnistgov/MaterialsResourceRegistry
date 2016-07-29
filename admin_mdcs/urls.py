################################################################################
#
# File Name: urls.py
# Application: admin_mdcs
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

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include(admin.site.urls)),
    url(r'^user-management', include(admin.site.urls)),
    url(r'^user-requests$', 'admin_mdcs.views.user_requests', name='user_requests'),
    url(r'^contact-messages$', 'admin_mdcs.views.contact_messages', name='contact_messages'),
    url(r'^xml-schemas$', 'admin_mdcs.views.manage_schemas', name='xml-schemas'),
    url(r'^xml-schemas/manage-schemas', 'admin_mdcs.views.manage_schemas', name='xml-schemas-manage-schemas'),
    url(r'^xml-schemas/manage-types', 'admin_mdcs.views.manage_types', name='xml-schemas-manage-types'),
    url(r'^repositories$', 'admin_mdcs.views.federation_of_queries', name='federation_of_queries'),
    url(r'^repositories/add-repository', 'admin_mdcs.views.add_repository', name='add_repository'),
    url(r'^repositories/refresh-repository', 'admin_mdcs.views.refresh_repository', name='refresh_repository'),
    url(r'^website$', 'admin_mdcs.views.website', name='website'),
    url(r'^website/privacy-policy$', 'admin_mdcs.views.privacy_policy_admin', name='privacy-policy-admin_mdcs'),
    url(r'^website/terms-of-use$', 'admin_mdcs.views.terms_of_use_admin', name='terms-of-use-admin_mdcs'),
    url(r'^website/help$', 'admin_mdcs.views.help_admin', name='help-admin_mdcs'),
    url(r'^remove_message', 'admin_mdcs.ajax.remove_message'),
    url(r'^edit_instance', 'admin_mdcs.ajax.edit_instance'),
    url(r'^delete_instance', 'admin_mdcs.ajax.delete_instance'),
    url(r'^accept_request', 'admin_mdcs.ajax.accept_request'),
    url(r'^deny_request', 'admin_mdcs.ajax.deny_request'),
    url(r'^set_current_version', 'admin_mdcs.ajax.set_current_version'),
    url(r'^assign_delete_custom_message', 'admin_mdcs.ajax.assign_delete_custom_message'),
    url(r'^delete_version', 'admin_mdcs.ajax.delete_version'),
    url(r'^restore_object', 'admin_mdcs.ajax.restore_object'),
    url(r'^restore_version', 'admin_mdcs.ajax.restore_version'),
    url(r'^edit_information', 'admin_mdcs.ajax.edit_information'),
    url(r'^delete_object', 'admin_mdcs.ajax.delete_object'),
    url(r'^resolve_dependencies', 'admin_mdcs.ajax.resolve_dependencies'),
    url(r'^add_bucket', 'admin_mdcs.ajax.add_bucket'),
    url(r'^delete_bucket', 'admin_mdcs.ajax.delete_bucket'),
    url(r'^upload_xsd', 'admin_mdcs.views.upload_xsd'),
    url(r'^manage_versions', 'admin_mdcs.views.manage_versions'),
    url(r'^modules', 'admin_mdcs.views.modules'),
    url(r'^insert_module', 'admin_mdcs.ajax.insert_module'),
    url(r'^remove_module', 'admin_mdcs.ajax.remove_module'),
    url(r'^save_modules', 'admin_mdcs.ajax.save_modules'),
    url(r'^exporters', 'admin_mdcs.views.exporters'),
    url(r'^resultXslt', 'admin_mdcs.views.result_xslt'),
    url(r'^save_exporters', 'admin_mdcs.ajax.save_exporters'),
    url(r'^save_result_xslt', 'admin_mdcs.ajax.save_result_xslt'),
    url(r'^xml-schemas/manage-xslt', 'admin_mdcs.views.manage_xslt', name='xml-schemas-manage-xslt'),
    url(r'^xml-schemas/manage-result-xslt', 'admin_mdcs.views.manage_result_xslt', name='xml-schemas-manage-result-xslt'),
    url(r'^xml-schemas/delete-xslt', 'admin_mdcs.views.delete_xslt', name='xml-schemas-delete-xslt'),
    url(r'^xml-schemas/delete-result-xslt', 'admin_mdcs.views.delete_result_xslt', name='xml-schemas-delete-result-xslt'),
    url(r'^xml-schemas/edit-xslt', 'admin_mdcs.views.edit_xslt', name='xml-schemas-edit-xslt'),
    url(r'^xml-schemas/edit-result-xslt', 'admin_mdcs.views.edit_result_xslt', name='xml-schemas-edit-result-xslt'),
)
