################################################################################
#
# File Name: urls.py
# Application: user_dashboard
# Purpose:
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    url(r'^$', 'user_dashboard.views.dashboard'),
    url(r'^detail$', 'user_dashboard.views.dashboard_detail_resource'),
    url(r'^my-profile$', 'user_dashboard.views.my_profile', name='my-profile'),
    url(r'^resources$', 'user_dashboard.views.dashboard_resources', name='dashboard-resources'),
    url(r'^my-profile/favorites$', 'user_dashboard.views.my_profile_favorites', name='my-profile-favorites'),
    url(r'^my-profile/edit', 'user_dashboard.views.my_profile_edit', name='my-profile-edit'),
    url(r'^my-profile/change-password', 'user_dashboard.views.my_profile_change_password', name='my-profile-change-password'),
    url(r'^drafts', 'user_dashboard.views.dashboard_my_drafts', name='dashboard-my-drafts'),
    url(r'^delete_result', 'user_dashboard.ajax.delete_result'),
    url(r'^update_publish', 'user_dashboard.ajax.update_publish'),
    url(r'^update_unpublish', 'user_dashboard.ajax.update_unpublish'),
)+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns += staticfiles_urlpatterns()