from django.conf.urls import patterns, url

urlpatterns = patterns('',
   url('', 'exporter.curator.json.models.JSONExporter', {'name':'JSON', 'available_for_all':True}),
)

