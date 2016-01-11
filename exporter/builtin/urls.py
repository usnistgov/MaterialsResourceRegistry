from django.conf.urls import patterns, url

urlpatterns = patterns('',
   url('', 'exporter.builtin.models.BasicExporter', {'name':'XML',  'available_for_all':True}),
   url('', 'exporter.builtin.models.XSLTExporter',  {'name':'XSLT', 'available_for_all':False}),
)

