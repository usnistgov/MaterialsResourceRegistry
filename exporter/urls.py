from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
   url('', include('exporter.builtin.urls')),
   url('', include('exporter.pop.urls')),
   url('', include('exporter.csv.urls')),
   url('', include('exporter.json.urls')),
   # url('', include('exporter.graph.urls')),
)

