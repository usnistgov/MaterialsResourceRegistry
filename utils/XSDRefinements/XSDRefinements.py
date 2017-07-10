from io import BytesIO
from mgi import common
from mgi.common import LXML_SCHEMA_NAMESPACE
from utils.XSDflattener.XSDflattener import XSDFlattenerURL
from mgi.models import Template, TemplateVersion
import lxml.etree as etree
from utils.XSDRefinements import Tree
from collections import OrderedDict


def loads_refinements_trees(template_name, category=False):
    ref_xml_schema_content, namespaces = _get_flatten_schema_and_namespaces(template_name)
    xml_doc_tree = etree.parse(BytesIO(ref_xml_schema_content))
    target_ns_prefix = common.get_target_namespace_prefix(namespaces, xml_doc_tree)
    target_ns_prefix = "{}:".format(target_ns_prefix) if target_ns_prefix != '' else ''

    simple_types = xml_doc_tree.findall("./{0}simpleType".format(LXML_SCHEMA_NAMESPACE))
    trees = OrderedDict()
    for simple_type in simple_types:
        try:
            enums = simple_type.findall("./{0}restriction/{0}enumeration".format(LXML_SCHEMA_NAMESPACE))
            if len(enums) > 0:
                element = xml_doc_tree.findall(".//{0}element[@type='{1}']".format(LXML_SCHEMA_NAMESPACE,
                                                                                   target_ns_prefix +
                                                                                   simple_type.attrib['name']))
                if len(element) > 1:
                    print "error: more than one element using the enumeration ({0})".format(str(len(element)))
                else:
                    element = element[0]
                    # get the label of refinements
                    label = _get_label(element, xml_doc_tree, target_ns_prefix)
                    query = []

                    while element is not None:
                        if element.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
                            query.insert(0, element.attrib['name'])
                        elif element.tag == "{0}simpleType".format(LXML_SCHEMA_NAMESPACE):
                            element = _get_simple_type_or_complex_type_info(xml_doc_tree, target_ns_prefix, element,
                                                                            query)
                        elif element.tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):
                            element = _get_simple_type_or_complex_type_info(xml_doc_tree, target_ns_prefix, element,
                                                                            query)
                        elif element.tag == "{0}extension".format(LXML_SCHEMA_NAMESPACE):
                            element = _get_extension_info(xml_doc_tree, element, query)

                        element = element.getparent()

                    dot_query = ".".join(query)
                    trees = Tree.build_tree(tree=trees, root=label, enums=enums, dot_query=dot_query, category=category)
        except:
            print "ERROR AUTO GENERATION OF REFINEMENTS."

    return trees


def _get_flatten_schema_and_namespaces(template_name):
    schemas = Template.objects(title=template_name)
    schema_id = TemplateVersion.objects().get(pk=schemas[0].templateVersion).current
    schema = Template.objects().get(pk=schema_id)
    flattener = XSDFlattenerURL(schema.content.encode('utf-8'))
    ref_xml_schema_content = flattener.get_flat()
    # find the namespaces
    namespaces = common.get_namespaces(BytesIO(schema.content.encode('utf-8')))

    return ref_xml_schema_content, namespaces


def _get_label(element, xml_doc_tree, target_ns_prefix):
    # By default, use the element's app_info
    app_info = common.getAppInfo(element)
    # Check if the element is embedded in a choice. If yes, we use the first parent complexType to get the label.
    parent = element.getparent()
    if parent is not None and parent.tag == "{0}choice".format(LXML_SCHEMA_NAMESPACE):
        while parent.getparent() is not None:
            parent = parent.getparent()
            if parent.tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):
                parent = _get_simple_type_or_complex_type_info(xml_doc_tree, target_ns_prefix, parent)
                app_info = common.getAppInfo(parent)
                break

    label = app_info['label'] if 'label' in app_info else element.attrib['name']
    label = label if label is not None else element.attrib['name']

    return label


def _get_simple_type_or_complex_type_info(xml_doc_tree, target_ns_prefix, element, query=None):
    try:
        to_search_element = xml_doc_tree.findall(".//{0}element[@type='{1}']".format(LXML_SCHEMA_NAMESPACE,
                                                 target_ns_prefix + element.attrib['name']))
        if len(to_search_element) == 0:
            print "warning: impossible to find the element using the enumeration ({0})".format(str(len(element)))
            element = _find_extension(xml_doc_tree, target_ns_prefix, element)
        elif len(to_search_element) > 1:
            print "error: more than one element using the enumeration ({0})".format(str(len(element)))
        else:
            element = to_search_element[0]
            if query is not None:
                query.insert(0, element.attrib['name'])
    except:
        pass

    return element


def _get_extension_info(xml_doc_tree, element, query=None):
    try:
        to_search_element = xml_doc_tree.findall(".//{0}element[@type='{1}']".format(LXML_SCHEMA_NAMESPACE,
                                                 element.attrib['base']))
        if len(to_search_element) == 0:
            print "warning: impossible to find the element using the enumeration ({0})".format(str(len(element)))
        elif len(to_search_element) > 1:
            print "error: more than one element using the enumeration ({0})".format(str(len(element)))
        else:
            element = to_search_element[0]
            if query is not None:
                query.insert(0, element.attrib['name'])
    except:
        pass

    return element


def _find_extension(xml_doc_tree, target_ns_prefix, element):
    try:
        to_search_element = xml_doc_tree.findall(".//{0}extension[@base='{1}']".format(LXML_SCHEMA_NAMESPACE,
                                                 target_ns_prefix +
                                                 element.attrib['name']))
        if len(to_search_element) == 0:
            print "warning: impossible to find the enumeration ({0})".format(str(len(element)))
        elif len(to_search_element) > 1:
            print "error: more than one enumeration using the element ({0})".format(str(len(element)))
        else:
            element = to_search_element[0]
    except:
        pass

    return element
