from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^resources$', 'modules.views.load_resources_view', name='load_resources'),
    url(r'^curator/', include('modules.curator.urls')),
    url(r'^diffusion/', include('modules.diffusion.urls')),    
    url(r'^examples/', include('modules.examples.urls')),
    url(r'^registry/', include('modules.registry.urls')),
)

excluded = ['load_resources']
