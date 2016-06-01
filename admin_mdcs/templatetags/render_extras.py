from django.template import Template, Variable, TemplateSyntaxError
from django import template
import os
from django.conf import settings
import xmltodict
import lxml.etree as etree

register = template.Library()

class RenderAsTemplateNode(template.Node):
    def __init__(self, item_to_be_rendered):
        self.item_to_be_rendered = Variable(item_to_be_rendered)

    def render(self, context):
        try:
            actual_item = self.item_to_be_rendered.resolve(context)
            return Template(actual_item).render(context)
        except template.VariableDoesNotExist:
            return ''

@register.tag(name='render_as_template')
def render_as_template(parser, args):
    content = args.split_contents()
    if len(content) !=2:
        raise TemplateSyntaxError("'%s' takes only one argument"
                                  " (a variable representing a template to render)" % content[0])

    return RenderAsTemplateNode(content[1])

@register.filter(name='render_xml_as_html')
def render_xml_as_html(value):
    try:
        dict = value
        xsltPath = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'xml2html.xsl')
        xslt = etree.parse(xsltPath)
        transform = etree.XSLT(xslt)
        xmlString = xmltodict.unparse(dict)
        if (xmlString != ""):
            dom = etree.XML(xmlString.encode('utf-8'))
            newdom = transform(dom)
            xmlTree = str(newdom)
            return xmlTree
        else:
            return dict
    except:
        return dict