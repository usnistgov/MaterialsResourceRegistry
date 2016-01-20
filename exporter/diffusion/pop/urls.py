from django.conf.urls import patterns, url

urlpatterns = patterns('',
   url('', 'exporter.diffusion.pop.models.POPExporter', {'name':'POP', 'available_for_all':False}),
)

