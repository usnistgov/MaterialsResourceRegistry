from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
   url('', include('exporter.curator.json.urls')),
)

