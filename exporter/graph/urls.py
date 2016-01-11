from django.conf.urls import patterns, url

urlpatterns = patterns('',
   url('', 'exporter.graph.models.GRAPHExporter', {'name':'GRAPH', 'available_for_all':False}),
)

