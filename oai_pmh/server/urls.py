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
from django.conf.urls import patterns, url
from oai_pmh.server.views import OAIProvider

urlpatterns = patterns(
    'oai_pmh.server.views',
    #Put the schema name in the schema attribute (/XSD/schemaNameInTheURL)
    url(r'^(?i)XSD/(?P<schema>.*)', 'get_xsd', name="getXSD"),
    url(r'^', OAIProvider.as_view()),
)

