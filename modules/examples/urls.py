from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'positive-integer', 'modules.examples.views.positive_integer', name='Positive Integer'),
    url(r'autocomplete', 'modules.examples.views.example_autocomplete', name='Example autocomplete'),
    url(r'chemical-element-mapping', 'modules.examples.views.chemical_element_mapping', name='Chemical Element Mapping'),
    url(r'list-to-graph', 'modules.examples.views.list_to_graph', name='List to Graph'),
    url(r'countries-module', 'modules.examples.views.countries', name='Countries'),
    url(r'flag-module', 'modules.examples.views.flag', name='Flags'),
    url(r'chemical-element-selection', 'modules.examples.views.chemical_element_selection', name='Chemical Element Selection'),
    url(r'^auto-key-randint', 'modules.examples.views.auto_key_randint', name='Auto Key (Random Int)'),
    url(r'^auto-key-randstr', 'modules.examples.views.auto_key_randstr', name='Auto Key (Random Str)'),
    url(r'^auto-key-seqint', 'modules.examples.views.auto_key_int_sequence', name='Auto Key (Sequence of Int)'),
)
