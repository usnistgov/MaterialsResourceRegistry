from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
   url('', include('exporter.builtin.urls')),
   url('', include('exporter.curator.urls')),
   url('', include('exporter.diffusion.urls')),
)

