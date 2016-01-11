################################################################################
#
# File Name: urls.py
# Application: compose
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

from compose import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^select-template', views.index),
    url(r'^build-template$', 'compose.views.compose_build_template', name='compose-build-template'),
    url(r'^download-XSD$', 'compose.views.compose_downloadxsd', name='compose-downloadxsd'),
    url(r'^verify_template_is_selected', 'compose.ajax.verify_template_is_selected'),
    url(r'^is_new_template', 'compose.ajax.is_new_template'),
    url(r'^change_root_type_name', 'compose.ajax.change_root_type_name'),
    url(r'^set_current_template', 'compose.ajax.set_current_template'),
    url(r'^set_current_user_template', 'compose.ajax.set_current_user_template'),
    url(r'^load_xml', 'compose.ajax.load_xml'),
    url(r'^save_template', 'compose.ajax.save_template'),
    url(r'^save_type', 'compose.ajax.save_type'),
    url(r'^change_xsd_type', 'compose.ajax.change_xsd_type'),
    url(r'^set_occurrences', 'compose.ajax.set_occurrences'),
    url(r'^delete_element', 'compose.ajax.delete_element'),
    url(r'^rename_element', 'compose.ajax.rename_element'),
    url(r'^insert_element_sequence', 'compose.ajax.insert_element_sequence'),
    url(r'^get_occurrences', 'compose.ajax.get_occurrences'),
    url(r'^download_template', 'compose.ajax.download_template'),
)
