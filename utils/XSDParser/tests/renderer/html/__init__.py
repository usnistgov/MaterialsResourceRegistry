""" Test suites for the HTML parser
"""
from curate.models import SchemaElement
from utils.XSDParser.renderer import HtmlRenderer


def create_mock_html_renderer():
    element = SchemaElement()
    element.tag = "mock"

    return HtmlRenderer(element)


def create_mock_db_input(value='', placeholder='', title=''):
    input_element = SchemaElement()
    input_element.tag = "input"

    input_element.value = value
    input_element.options = {
        'title': title,
        'placeholder': placeholder
    }

    input_element.pk = 'mock'

    return input_element

