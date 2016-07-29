################################################################################
#
# File Name: urls.py
# Application: mgi
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

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from user_dashboard.views import UserDashboardPasswordChangeFormView

urlpatterns = patterns(
    '',
    url(r'^$', 'mgi.views.home', name='home'),
    url(r'^admin/', include('admin_mdcs.urls')),
    url(r'^curate/', include('curate.urls')),
    url(r'^explore/', include('explore.urls')),
    #url(r'^compose/', include('compose.urls')),
    url(r'^rest/', include('api.urls')),
    url(r'^modules/', include('modules.urls')),
    url(r'^docs/api', include('rest_framework_swagger.urls')),
    url(r'^all-options', 'mgi.views.all_options', name='all-options'),
    url(r'^browse-all', 'mgi.views.browse_all', name='browse-all'),
    url(r'^login', 'django.contrib.auth.views.login',{'template_name': 'login.html'}),
    url(r'^request-new-account', 'mgi.views.request_new_account', name='request-new-account'),   
    url(r'^logout', 'mgi.views.logout_view', name='logout'),
    url(r'^dashboard/', include('user_dashboard.urls')),
    url(r'^help', 'mgi.views.help', name='help'),
    url(r'^contact', 'mgi.views.contact', name='contact'),
    url(r'^privacy-policy', 'mgi.views.privacy_policy', name='privacy-policy'),
    url(r'^terms-of-use', 'mgi.views.terms_of_use', name='terms-of-use'),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^oai_pmh/', include('oai_pmh.urls')),
    url(r'^password/change/$', UserDashboardPasswordChangeFormView.as_view(success_url='/'),
        name="password_change"),
    url(r'^password/', include('password_policies.urls')),
)+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns += staticfiles_urlpatterns()



