from django.conf.urls import patterns, url

urlpatterns = patterns('',
   url('', 'exporter.diffusion.csv.models.CSVExporter', {'name':'CSV', 'available_for_all':False}),
)

