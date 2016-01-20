from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
   url('', include('exporter.diffusion.csv.urls')),
   # url('', include('exporter.diffusion.graph.urls')),
   url('', include('exporter.diffusion.pop.urls')),
)

