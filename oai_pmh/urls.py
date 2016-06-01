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

urlpatterns = patterns(
    'oai_pmh.views',
    url(r'^oai-pmh-build-request$', 'oai_pmh_build_request', name='oai_pmh_build_request'),
    url(r'^download-xml-build-req$', 'download_xml_build_req'),
    url(r'^registry/(?P<registry>[-\w]+)/all_sets/$', 'all_sets'),
    url(r'^registry/(?P<registry>[-\w]+)/all_metadataprefix/$', 'all_metadataprefix'),
    url(r'^getdata/$', 'getData'),
    url(r'^admin/', include('oai_pmh.admin.urls')),
    url(r'^api/', include('oai_pmh.api.urls')),
    url(r'^explore/', include('oai_pmh.explore.urls')),
    url(r'^server/', include('oai_pmh.server.urls'), name='oai_server'),
)

