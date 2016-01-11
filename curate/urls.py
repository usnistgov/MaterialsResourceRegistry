################################################################################
#
# File Name: urls.py
# Application: curate
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

from django.conf.urls import patterns, url

from curate import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^select-template', views.index),
    url(r'^enter-data$', 'curate.views.curate_enter_data', name='curate-enter-data'),
    url(r'^enter-data/download-XSD$', 'curate.views.curate_enter_data_downloadxsd', name='curate-enter-data-downloadxsd'),
    url(r'^enter-data/download_current_xml$', 'curate.ajax.download_current_xml', name='download_current_xml'),
    url(r'^view-data$', 'curate.views.curate_view_data', name='curate-view-data'),
    url(r'^view-data/download-XML/$', 'curate.views.curate_view_data_downloadxml', name='curate-view-data-downloadxml'),
    url(r'^generate_xsd_form', 'curate.ajax.generate_xsd_form'),
    url(r'^init_curate', 'curate.ajax.init_curate'),
    url(r'^clear_fields', 'curate.ajax.clear_fields'),
    url(r'^save_form', 'curate.ajax.save_form'),
    url(r'^view_data', 'curate.ajax.view_data'),
    url(r'^validate_xml_data', 'curate.ajax.validate_xml_data'),
    url(r'^verify_template_is_selected', 'curate.ajax.verify_template_is_selected'),
    url(r'^generate', 'curate.ajax.generate_absent'),
    url(r'^can_duplicate', 'curate.ajax.can_duplicate'),
    url(r'^duplicate', 'curate.ajax.duplicate'),
    url(r'^can_remove', 'curate.ajax.can_remove'),
    url(r'^remove', 'curate.ajax.remove'),
    url(r'^set_current_template', 'curate.ajax.set_current_template'),
    url(r'^set_current_user_template', 'curate.ajax.set_current_user_template'),
    url(r'^load_xml', 'curate.ajax.load_xml'),
    url(r'^download_xml', 'curate.ajax.download_xml'),
    url(r'^save_xml_data_to_db', 'curate.views.save_xml_data_to_db'),
    url(r'^start_curate', 'curate.views.start_curate'),
    url(r'^delete-form', 'curate.ajax.delete_form'),
    url(r'^cancel-form', 'curate.ajax.cancel_form'),
)
