"""
"""
from os.path import join
from curate.models import SchemaElement
from curate.parser import generate_form
from curate.renderer.list import ListRenderer

XSD_FILES_PATH = join('curate', 'tests', 'data', 'parser')
HTML_FILES_PATH = join('curate', 'tests', 'data', 'renderer', 'list')


def retrieve_rendered_form(request):
    """Retrieve a form

    :param request:
    :return:
    """
    root_pk = generate_form(request)
    root_element = SchemaElement.objects.get(pk=root_pk)

    renderer = ListRenderer(root_element)
    return renderer.render()
