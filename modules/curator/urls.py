from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^blob-hoster', 'modules.curator.views.blob_hoster', name='BLOB Hoster'),
    url(r'^remote-blob-hoster', 'modules.curator.views.remote_blob_hoster', name='Remote BLOB Hoster'),
    url(r'^advanced-blob-hoster', 'modules.curator.views.advanced_blob_hoster', name='Advanced BLOB Hoster'),
    url(r'^raw-xml', 'modules.curator.views.raw_xml', name='Raw XML'),
    url(r'^handle', 'modules.curator.views.handle', name='Handle'),
    url(r'^enum-autocomplete', 'modules.curator.views.enum_autocomplete', name='Enumeration Auto-complete'),
    url(r'^auto-keyref', 'modules.curator.views.auto_keyref', name='_auto_keyref'),
    url(r'^get-updated-keys', 'modules.curator.views.get_updated_keys', name='_get_updated_keys'),
)
