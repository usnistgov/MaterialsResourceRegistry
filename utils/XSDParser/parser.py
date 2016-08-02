"""
"""
import logging
import numbers
import traceback
import sys
import re
import textwrap
from urlparse import urlparse, parse_qsl
from curate.models import SchemaElement
from mgi.exceptions import MDCSError
from mgi.models import Module
from mgi import common
from lxml import etree
from io import BytesIO
import urllib2
from mgi.common import LXML_SCHEMA_NAMESPACE, getAppInfo
from utils.XSDParser.renderer.list import ListRenderer
from utils.XSDflattener.XSDflattener import XSDFlattenerURL

logger = logging.getLogger(__name__)


##################################################
# Part I: Utilities
##################################################

def _fmt_tooltip(text, width=80):
    return textwrap.fill(re.sub(r'\s+', ' ', text.strip()), width)

def load_schema_data_in_db(xsd_data):
    """

    Parameters:
        xsd_data:

    Returns:
    """
    xsd_element = SchemaElement()
    xsd_element.tag = xsd_data['tag']

    if xsd_data['value'] is not None:
        if isinstance(xsd_data['value'], numbers.Number):
            element_value = str(xsd_data['value'])
        else:
            element_value = xsd_data['value']

        element_value = element_value.lstrip()
        xsd_data['value'] = element_value.rstrip()

    xsd_element.value = xsd_data['value']

    if 'options' in xsd_data:
        if xsd_element.tag == 'module' and xsd_data['options']['data'] is not None:
            module_data = xsd_data['options']['data'].encode('utf-8')
            module_data = module_data.lstrip()
            xsd_data['options']['data'] = module_data.rstrip()

        xsd_element.options = xsd_data['options']

    if 'children' in xsd_data:
        children = []

        for child in xsd_data['children']:
            child_db = load_schema_data_in_db(child)
            children.append(child_db)

        if len(children) > 0:
            xsd_element.children = children

    if xsd_element.tag == 'choice-iter':
        if xsd_element.value is None:
            xsd_element.value = str(xsd_element.children[0].pk)
        else:  # Value set => Put the pk of the displayed child
            child_index = int(xsd_element.value)
            xsd_element.value = str(xsd_element.children[child_index].pk)

    xsd_element.save()
    return xsd_element


def delete_branch_from_db(element_id):
    """
    :param element_id:
    :return:
    """
    element = SchemaElement.objects.get(pk=element_id)

    for child in element.children:
        delete_branch_from_db(str(child.pk))

    element.delete()


def update_branch_xpath(element):
    element_xpath = element.options['xpath']['xml']
    xpath_index = 1

    for child in element.children:
        update_root_xpath(child, element_xpath, xpath_index)
        xpath_index += 1


def update_root_xpath(element, xpath, index):
    element_options = element.options

    if 'xpath' in element_options:
        xml_xpath = element_options['xpath']['xml']
        element_options['xpath']['xml'] = xml_xpath.replace(xpath+'[1]', xpath + '[' + str(index) + ']', 1)

        element.update(set__options=element_options)
        element.reload()

    for child in element.children:
        update_root_xpath(child, xpath, index)


def get_nodes_xpath(elements, xml_tree):
    """Perform a lookup in subelements to build xpath.

    Get nodes' xpath, only one level deep. It's not going to every leaves. Only need to know if the
    node is here.

    Parameters:
        elements: XML element
        xml_tree: xml_tree
    """
    # FIXME Making one function with get_subnode_xpath should be possible, both are doing the same job
    # FIXME same problems as in get_subnodes_xpath
    xpaths = []
    element_tag = None
    schema_location = None

    for element in elements:
        if element.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
            if 'name' in element.attrib:
                xpaths.append({'name': element.attrib['name'], 'element': element})
            elif 'ref' in element.attrib:
                # check if XML element or attribute
                if element.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
                    element_tag = 'element'
                elif element.tag == "{0}attribute".format(LXML_SCHEMA_NAMESPACE):
                    element_tag = 'attribute'

                # get schema namespaces
                xml_tree_str = etree.tostring(xml_tree)
                namespaces = common.get_namespaces(BytesIO(str(xml_tree_str)))
                ref = element.attrib['ref']
                ref_element, ref_tree, schema_location = get_ref_element(xml_tree, ref, namespaces,
                                                                         element_tag, schema_location)

                if ref_element is not None:
                    xpaths.append({'name': ref_element.attrib.get('name'), 'element': ref_element})
        else:
            xpaths.extend(get_nodes_xpath(element, xml_tree))
    return xpaths


def lookup_occurs(element, xml_tree, full_path, edit_data_tree):
    """Do a lookup in data to get the number of occurences of a sequence or choice without a name (not within a named
    complextype).

    get the number of times the sequence appears in the XML document that we are loading for editing
    algorithm:
    get all the possible nodes that can appear in the sequence
    for each node, count how many times it's found in the data
    the maximum count is the number of occurrences of the sequence
    only works if data are determinist enough: means we don't have an element outside the sequence, and the same in
    the sequence

    Parameters:
        element: XML element
        xml_tree: XML schema tree
        full_path: current node XPath
        edit_data_tree: XML data tree
    """
    # FIXME this function is not returning the correct output

    # get all possible xpaths of subnodes
    xpaths = get_nodes_xpath(element, xml_tree)
    elements_found = []

    # get target namespace prefix if one declared
    xml_tree_str = etree.tostring(xml_tree)
    namespaces = common.get_namespaces(BytesIO(str(xml_tree_str)))
    target_namespace_prefix = common.get_target_namespace_prefix(namespaces, xml_tree)
    if target_namespace_prefix != '':
        target_namespace_prefix += ":"

    # check if xpaths find a match in the document
    for xpath in xpaths:
        edit_elements = edit_data_tree.xpath(full_path + '/' + target_namespace_prefix + xpath['name'],
                                             namespaces=namespaces)
        elements_found.extend(edit_elements)

    return elements_found


def manage_occurences(element):
    """Store information about the occurrences of the element

    Parameters:
        element: xsd element

    Returns:
        JSON data
    """
    min_occurs = 1
    max_occurs = 1

    if 'minOccurs' in element.attrib:
        min_occurs = int(element.attrib['minOccurs'])

    if 'maxOccurs' in element.attrib:
        if element.attrib['maxOccurs'] == "unbounded":
            max_occurs = -1
        else:
            max_occurs = int(element.attrib['maxOccurs'])

    return min_occurs, max_occurs


def manage_attr_occurrences(element):
    """Store information about the occurrences of an attribute

    Parameters:
        element: XSD element

    Returns:
        JSON data
    """
    # FIXME attribute use defaults to optional not required

    min_occurs = 1
    max_occurs = 1

    if 'use' in element.attrib:
        if element.attrib['use'] == "optional":
            min_occurs = 0
        elif element.attrib['use'] == "prohibited":
            min_occurs = 0
            max_occurs = 0
        elif element.attrib['use'] == "required":
            pass

    return min_occurs, max_occurs


def has_module(request, element):
    """Look for a module in XML element's attributes

    Parameters:
        element: XML element

    Returns:
        True: the element has a module attribute
        False: the element doesn't have a module attribute
    """
    if request.session['PARSER_IGNORE_MODULES']:
        return False

    _has_module = False

    # check if a module is set for this element
    if '{http://mdcs.ns}_mod_mdcs_' in element.attrib:
        # get the url of the module
        url = element.attrib['{http://mdcs.ns}_mod_mdcs_']

        url = urlparse(url).path

        # check that the url is registered in the system
        if url in Module.objects.all().values_list('url'):
            _has_module = True

    return _has_module


def get_xml_element_data(xsd_element, xml_element):
    """Return the content of an xml element

    Parameters:
        xsd_element:
        xml_element:
    Returns:
    """
    reload_data = None
    prefix = '{0}'.format(LXML_SCHEMA_NAMESPACE)

    # get data
    if xsd_element.tag == prefix + "element":
        # leaf: get the value
        if len(list(xml_element)) == 0:
            if xml_element.text is not None:
                reload_data = xml_element.text
            else:  # if xml_element.text is None
                reload_data = ''
        else:  # branch: get the whole branch
            reload_data = etree.tostring(xml_element)
    elif xsd_element.tag == prefix + "attribute":
        return str(xml_element)
    elif xsd_element.tag == prefix + "complexType" or xsd_element.tag == prefix + "simpleType":
        # leaf: get the value
        if len(list(xml_element)) == 0:
            if xml_element.text is not None:
                reload_data = xml_element.text
            else:  # xml_element.text is None
                reload_data = ''
        else:  # branch: return children
            try:
                if list(xml_element) > 0:
                    reload_data = ''
                    for child in list(xml_element):
                        reload_data += etree.tostring(child)
            except:
                # FIXME in which case would we need that?
                reload_data = str(xml_element)

    return reload_data


def get_element_type(element, xml_tree, namespaces, default_prefix, target_namespace_prefix, schema_location=None,
                     attr='type'):
    """get XSD type to render. Returns the tree where the type was found.

    Parameters:
        element: XML element
        xml_tree: XSD tree of the template
        namespaces:
        default_prefix:
        target_namespace_prefix:
        schema_location:
        attr:

    Returns:
                    Returns the type if found
                        - complexType
                        - simpleType
                    Returns None otherwise:
                        - type from default namespace (xsd:...)
                        - no type
                    Returns:
                        - tree where the type has been found
                        - schema location where the type has been found
    """

    element_type = None
    try:
        if attr not in element.attrib:  # element with type declared below it
            for i in range(len(list(element))):
                if element[i].tag == "{0}simpleType".format(LXML_SCHEMA_NAMESPACE) or \
                            element[i].tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):
                    element_type = element[i]
                    break
        else:  # element with type attribute
            if element.attrib.get(attr) in common.getXSDTypes(default_prefix):
                element_type = None
            elif element.attrib.get(attr) is not None:  # FIXME is it possible?
                # TODO: manage namespaces
                # test if type of the element is a simpleType
                type_name = element.attrib.get(attr)
                if ':' in type_name:
                    type_ns_prefix = type_name.split(":")[0]
                    type_name = type_name.split(":")[1]
                    if type_ns_prefix != target_namespace_prefix:
                        # TODO: manage ref to imported elements (different target namespace)
                        # get all import elements
                        imports = xml_tree.findall('//{}import'.format(LXML_SCHEMA_NAMESPACE))
                        # find the referred document using the prefix
                        # the namespace is declared inline
                        if type_ns_prefix in element.nsmap:
                            for el_import in imports:
                                import_ns = el_import.attrib['namespace']
                                if element.nsmap[type_ns_prefix] == import_ns:
                                    xml_tree, schema_location = import_xml_tree(el_import)
                                    break
                        else:
                            if type_ns_prefix in namespaces:
                                for el_import in imports:
                                    import_ns = el_import.attrib['namespace']
                                    if namespaces[type_ns_prefix] == import_ns:
                                        xml_tree, schema_location = import_xml_tree(el_import)
                                        break

                xpath = "./{0}complexType[@name='{1}']".format(LXML_SCHEMA_NAMESPACE, type_name)
                element_type = xml_tree.find(xpath)
                if element_type is None:
                    # test if type of the element is a simpleType
                    xpath = "./{0}simpleType[@name='{1}']".format(LXML_SCHEMA_NAMESPACE, type_name)
                    element_type = xml_tree.find(xpath)
    except Exception as e:
        exception_message = "Something went wrong in get_element_type:  " + str(e)
        logger.fatal(exception_message)

        element_type = None

    return element_type, xml_tree, schema_location


def import_xml_tree(el_import):
    """
    Return tree after downloading import's schemaLocation
    :param el_import:
    :return:
    """
    # get the location of the schema
    ref_xml_schema_url = el_import.attrib['schemaLocation']
    schema_location = ref_xml_schema_url
    # download the file
    ref_xml_schema_file = urllib2.urlopen(ref_xml_schema_url)
    # read the content of the file
    ref_xml_schema_content = ref_xml_schema_file.read()
    # build the tree
    xml_tree = etree.parse(BytesIO(ref_xml_schema_content.encode('utf-8')))
    # look for includes
    includes = xml_tree.findall('//{}include'.format(LXML_SCHEMA_NAMESPACE))
    # if includes are present
    if len(includes) > 0:
        # create a flattener with the file content
        flattener = XSDFlattenerURL(ref_xml_schema_content)
        # flatten the includes
        ref_xml_schema_content = flattener.get_flat()
        # build the tree
        xml_tree = etree.parse(BytesIO(ref_xml_schema_content.encode('utf-8')))
    return xml_tree, schema_location


def remove_annotations(element):
    """Remove annotations of an element if present

    Parameters:
        element: XML element
    """
    # FIXME annotation is not always the first child

    if len(list(element)) != 0:  # If element has children
        if element[0].tag == "{0}annotation".format(LXML_SCHEMA_NAMESPACE):  # If first child is annotation
            element.remove(element[0])


def get_ref_element(xml_tree, ref, namespaces, element_tag, schema_location=None):
    """

    Parameters:
        xml_tree:
        ref:
        namespaces:
        element_tag:
        schema_location:

    Returns
        - ref_element: ref element when found
        - xml_tree: xml tree where element was found
        - schema_location: location of the schema where the element was found
    """
    if ':' in ref:
        # split the ref element
        ref_split = ref.split(":")
        # get the namespace prefix
        ref_namespace_prefix = ref_split[0]
        # get the element name
        ref_name = ref_split[1]
        # test if referencing element within the same schema (same target namespace)
        target_namespace_prefix = common.get_target_namespace_prefix(namespaces, xml_tree)
        # ref is in the same file
        if target_namespace_prefix == ref_namespace_prefix:
            ref_element = xml_tree.find("./{0}{1}[@name='{2}']".format(LXML_SCHEMA_NAMESPACE,
                                                                       element_tag, ref_name))
        else:# the ref might be in one of the imports
            # get all import elements
            imports = xml_tree.findall('//{}import'.format(LXML_SCHEMA_NAMESPACE))
            # find the referred document using the prefix
            for el_import in imports:
                import_ns = el_import.attrib['namespace']
                if namespaces[ref_namespace_prefix] == import_ns:
                    xml_tree, schema_location = import_xml_tree(el_import)

                    ref_element = xml_tree.find("./{0}{1}[@name='{2}']".format(LXML_SCHEMA_NAMESPACE,
                                                                               element_tag, ref_name))
                    break
    else:
        ref_element = xml_tree.find("./{0}{1}[@name='{2}']".format(LXML_SCHEMA_NAMESPACE, element_tag, ref))

    return ref_element, xml_tree, schema_location


def is_key(request, element, full_path):
    """
    Is the element used as a key
    :param request:
    :param element:
    :param full_path:
    :return:
    """
    # remove indexes from the xpath
    xpath = re.sub(r'\[[0-9]+\]', '', full_path)
    # remove namespaces
    for prefix in element.nsmap.keys():
        xpath = re.sub(r'{}:'.format(prefix), '', xpath)
    for key in request.session['keys'].keys():
        if request.session['keys'][key]['xpath'] == xpath:
            if request.session['keys'][key]['module'] is not None:
                element.attrib['{http://mdcs.ns}_mod_mdcs_'] = request.session['keys'][key]['module']
                return True
    return False


def is_key_ref(request, element, db_element, full_path):
    """
    Is the element used as a keyref
    :param request:
    :param element:
    :param db_element:
    :param full_path:
    :return:
    """
    # remove indexes from the xpath
    xpath = re.sub(r'\[[0-9]+\]', '', full_path)
    # remove namespaces
    for prefix in element.nsmap.keys():
        xpath = re.sub(r'{}:'.format(prefix), '', xpath)
    for keyref in request.session['keyrefs'].keys():
        if request.session['keyrefs'][keyref]['xpath'] == xpath:
            element.attrib['{http://mdcs.ns}_mod_mdcs_'] = '/curator/auto-keyref?keyref={}'.format(keyref)
            return True
    return False


def manage_key_keyref(request, element, full_path, xmlTree):
    """
    Store keys/keyrefs in data structure
    :param request:
    :param element:
    :param full_path:
    :param xmlTree:
    :return:
    """
    # get keys in element scope
    list_key = element.findall('{0}key'.format(LXML_SCHEMA_NAMESPACE))
    # get keyrefs in element scope
    list_keyref = element.findall('{0}keyref'.format(LXML_SCHEMA_NAMESPACE))

    # remove indexes from the xpath
    full_path = re.sub(r'\[[0-9]+\]', '', full_path)

    if len(list_key) > 0:
        for key in list_key:
            key_name = key.attrib['name']
            # print key_name

            selector = key.find('{0}selector'.format(LXML_SCHEMA_NAMESPACE))
            selector_xpath = selector.attrib['xpath']
            key_selector = full_path + '/' + selector_xpath
            # remove namespaces
            for prefix in selector.nsmap.keys():
                key_selector = re.sub(r'{}:'.format(prefix), '', key_selector)
            # print key_selector

            # FIXME: manage multiple fields
            fields = key.findall('{0}field'.format(LXML_SCHEMA_NAMESPACE))
            for field in fields:
                field_xpath = field.attrib['xpath']
                key_field = key_selector + '/' + field_xpath
                # print key_field

            # look if a module is attached to the key
            module = None
            if '{http://mdcs.ns}_mod_mdcs_' in key.attrib:
                # get the url of the module
                url = key.attrib['{http://mdcs.ns}_mod_mdcs_']
                url = urlparse(url).path
                # check that the url is registered in the system
                if url in Module.objects.all().values_list('url'):
                    module = "{0}?key={1}".format(url, key_name)

            request.session['keys'][key_name] = {'xpath': key_field, 'module_ids': [], 'module': module}

        for keyref in list_keyref:
            keyref_name = keyref.attrib['name']
            keyref_refer = keyref.attrib['refer']
            if ':' in keyref_refer:
                keyref_refer = keyref_refer.split(':')[1]
            # print keyref_name

            selector = keyref.find('{0}selector'.format(LXML_SCHEMA_NAMESPACE))
            selector_xpath = selector.attrib['xpath']
            keyref_selector = full_path + '/' + selector_xpath
            # remove namespaces
            for prefix in selector.nsmap.keys():
                keyref_selector = re.sub(r'{}:'.format(prefix), '', keyref_selector)
            # print keyref_selector

            # FIXME: manage multiple fields
            fields = keyref.findall('{0}field'.format(LXML_SCHEMA_NAMESPACE))
            for field in fields:
                field_xpath = field.attrib['xpath']
                keyref_field = keyref_selector + '/' + field_xpath
                # print keyref_field

            request.session['keyrefs'][keyref_name] = {'xpath': keyref_field, 'refer': keyref_refer, 'module_ids': []}


def get_element_form_default(xsd_tree):
    """
    Get the value of the elementFormDefault attribute
    :param xsd_tree:
    :return:
    """
    # default value
    element_form_default = "unqualified"

    root = xsd_tree.getroot()
    if 'elementFormDefault' in root.attrib:
        element_form_default = root.attrib['elementFormDefault']

    return element_form_default


def get_attribute_form_default(xsd_tree):
    """
    Get the value of the attributeFormDefault attribute
    :param xsd_tree:
    :return:
    """
    # default value
    attribute_form_default = "unqualified"

    root = xsd_tree.getroot()
    if 'attributeFormDefault' in root.attrib:
        attribute_form_default = root.attrib['attributeFormDefault']

    return attribute_form_default


def get_element_namespace(element, xsd_tree):
    """
    Get the namespace of the element
    :param element:
    :param xsd_tree:

    :return:
    """
    # get the root of the XSD document
    xsd_root = xsd_tree.getroot()

    # None by default, None means no namespace information needed, different from empty namespace
    element_ns = None

    # check if the element is root
    is_root = False
    # get XSD xpath
    xsd_path = xsd_tree.getpath(element)
    # the element is global (/xs:schema/xs:element)
    if xsd_path.count('/') == 2:
        is_root = True

    # root is always qualified, root from other schemas too
    if is_root:
        # if in a targetNamespace
        if 'targetNamespace' in xsd_root.attrib:
            # get the target namespace
            target_namespace = xsd_root.attrib['targetNamespace']
            element_ns = target_namespace
    else:
        # qualified elements
        if 'elementFormDefault' in xsd_root.attrib and xsd_root.attrib['elementFormDefault'] == 'qualified'\
                or 'attributeFormDefault' in xsd_root.attrib and xsd_root.attrib['attributeFormDefault'] == 'qualified':
            if 'targetNamespace' in xsd_root.attrib:
                # get the target namespace
                target_namespace = xsd_root.attrib['targetNamespace']
                element_ns = target_namespace
        # unqualified elements
        else:
            if 'targetNamespace' in xsd_root.attrib:
                element_ns = ""

    return element_ns


def get_extensions(xml_doc_tree, base_type_name):
    """Get all XML extensions of the XML Schema

    Parameters:
        request:
        element:
        xml_tree:
        full_path:
        edit_data_tree:

    Returns:
        list of extensions
    """
    #TODO: look for extensions in imported documents
    # get all extensions of the document
    extensions = xml_doc_tree.findall(".//{0}extension".format(LXML_SCHEMA_NAMESPACE))
    # keep only simple/complex type extensions, no built-in types
    custom_type_extensions = []
    for extension in extensions:
        base = extension.attrib['base']
        # TODO: manage namespaces
        if ":" in base:
            base = base.split(':')[1]
        if base_type_name == base:
            # get parent type that contains the extension
            type_extension = extension.getparent()
            while 'simpleType' not in type_extension.tag and 'complexType' not in type_extension.tag:
                type_extension = type_extension.getparent()
            custom_type_extensions.append(type_extension)

    return custom_type_extensions


##################################################
# Part II: Schema parsing
##################################################

def load_config(request, config):
    """
    Load configuration for the parser
    :param request:
    :param config:
    :return:
    """
    if 'config' in request.session:
        del request.session['config']

    properties = ['PARSER_APPLICATION',
                  'PARSER_MIN_TREE',
                  'PARSER_IGNORE_MODULES',
                  'PARSER_COLLAPSE',
                  'PARSER_AUTO_KEY_KEYREF',
                  'PARSER_IMPLICIT_EXTENSION_BASE']

    if config is not None:
        for property, value in config.iteritems():
            if property not in properties:
                raise MDCSError('Bad configuration parameter.')
            if not isinstance(value, bool):
                if property != 'PARSER_APPLICATION':
                    raise MDCSError('Bad type for configuration parameter.')
        request.session.update(config)
    else:
        raise MDCSError('Parser is expecting configuration parameters.')


def generate_form(request, xsd_doc_data, xml_doc_data=None, config=None):
    """Renders HTMl form for display.

    Parameters:
        request: HTTP request

    Returns:
        rendered HTMl form
    """
    request.session['implicit_extension'] = True

    # flatten the includes
    flattener = XSDFlattenerURL(xsd_doc_data)
    xml_doc_tree_str = flattener.get_flat()
    xml_doc_tree = etree.parse(BytesIO(xml_doc_tree_str.encode('utf-8')))

    request.session['xmlDocTree'] = xml_doc_tree_str

    if 'keys' in request.session:
        del request.session['keys']
    request.session['keys'] = {}
    if 'keyrefs' in request.session:
        del request.session['keyrefs']
    request.session['keyrefs'] = {}

    load_config(request, config)

    # if editing, get the XML data to fill the form
    edit_data_tree = None
    if 'curate_edit' in request.session and request.session['curate_edit']:
        # build the tree from data
        # transform unicode to str to support XML declaration
        if xml_doc_data is not None:
            # Load a parser able to clean the XML from blanks, comments and processing instructions
            clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
            # set the parser
            etree.set_default_parser(parser=clean_parser)
            # xml data not empty
            if xml_doc_data != "":
                # load the XML tree from the text
                edit_data_tree = etree.XML(str(xml_doc_data.encode('utf-8')))
            else:
                request.session['curate_edit'] = False
        else:  # no data found, not editing
            request.session['curate_edit'] = False

    # find all root elements
    elements = xml_doc_tree.findall("./{0}element".format(LXML_SCHEMA_NAMESPACE))

    try:
        if len(elements) == 1:  # One root
            form_content = generate_element(request, elements[0], xml_doc_tree, edit_data_tree=edit_data_tree)
        elif len(elements) > 1:  # Several root
            # look if a default choice to render is defined
            default_choice = False
            for element in elements:
                app_info = getAppInfo(element)
                if 'default' in app_info:
                    form_content = generate_element(request, element, xml_doc_tree, edit_data_tree=edit_data_tree)
                    default_choice = True
                    break
            if not default_choice:
                form_content = generate_choice(request, elements, xml_doc_tree, edit_data_tree=edit_data_tree)
        else:  # len(elements) == 0 (no root element)
            # TODO: does it make sense to get all simple types too?
            complex_types = xml_doc_tree.findall("./{0}complexType".format(LXML_SCHEMA_NAMESPACE))
            if len(complex_types) > 0:
                # look if a default choice to render is defined
                default_choice = False
                for complex_type in complex_types:
                    app_info = getAppInfo(complex_type)
                    if 'default' in app_info:
                        form_content = generate_choice_extensions(request, [complex_type], xml_doc_tree, None)
                        default_choice = True
                        break
                if not default_choice:
                    form_content = generate_choice_extensions(request, complex_types, xml_doc_tree, None)
            else:  # len(complex_types) == 0
                raise Exception("No possible root element detected")

        root_element = load_schema_data_in_db(form_content[1])

        request.session['curate_edit'] = False
        return root_element.pk
    except Exception as e:
        exc_info = sys.exc_info()

        # Adding information to the Exception message
        exception_message = "Schema parsing failed: " + str(e)
        logger.fatal(exception_message)

        traceback.print_exception(*exc_info)
        del exc_info

        request.session['curate_edit'] = False
        raise Exception(exception_message)


def generate_element(request, element, xml_tree, choice_info=None, full_path="", edit_data_tree=None,
                     schema_location=None, xml_element=None, force_generation=False):
    """Generate an HTML string that represents an XML element.

    Parameters:
        request: HTTP request
        element: XML element
        xml_tree: XML tree of the template
        choice_info:
        full_path:
        edit_data_tree:
        schema_location:
        xml_element:
        force_generation:

    Returns:
        JSON data
    """
    # FIXME if elif without else need to be corrected
    # FIXME Support for unique is not present
    # FIXME Support for key / keyref
    form_string = ""
    # get appinfo elements
    app_info = common.getAppInfo(element)

    # check if the element has a module
    _has_module = has_module(request, element)

    # FIXME see if we can avoid these basic initialization
    # FIXME this is not necessarily true (see attributes)
    min_occurs = 1
    max_occurs = 1

    text_capitalized = ''
    element_tag = ''
    edit_elements = []
    ##############################################

    # check if XML element or attribute
    if element.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
        min_occurs, max_occurs = manage_occurences(element)
        element_tag = 'element'
    elif element.tag == "{0}attribute".format(LXML_SCHEMA_NAMESPACE):
        min_occurs, max_occurs = manage_attr_occurrences(element)
        element_tag = 'attribute'

    # get schema namespaces
    xml_tree_str = etree.tostring(xml_tree)
    namespaces = common.get_namespaces(BytesIO(str(xml_tree_str)))

    db_element = {
        'tag': element_tag,  # 'element' or 'attribute'
        'options': {
            'name': text_capitalized,
            'min': min_occurs,
            'max': max_occurs,
            'module': None if not _has_module else True,
            'xpath': {
                'xsd': None,
                'xml': full_path
            },
            'schema_location': schema_location,
        },
        'value': None,
        'children': []
    }

    # get the name of the element, go find the reference if there's one
    if 'ref' in element.attrib:  # type is a reference included in the document
        ref = element.attrib['ref']
        ref_element, xml_tree, schema_location = get_ref_element(xml_tree, ref, namespaces,
                                                                 element_tag, schema_location)
        if ref_element is not None:
            text_capitalized = ref_element.attrib.get('name')
            element = ref_element
            # check if the element has a module
            _has_module = has_module(request, element)
        else:
            # the element was not found where it was supposed to be
            # could be a use case too complex for the current parser
            warning_message = "Ref element not found: " + str(element.attrib)
            logger.warning(warning_message)

            return form_string, db_element
    else:
        text_capitalized = element.attrib.get('name')

    xml_tree_str = etree.tostring(xml_tree)
    namespaces = common.get_namespaces(BytesIO(str(xml_tree_str)))
    target_namespace, target_namespace_prefix = common.get_target_namespace(namespaces, xml_tree)

    # build xpath
    # XML xpath:/root/element
    if element_tag == 'element':
        if target_namespace is not None:
            if target_namespace_prefix != '':
                if get_element_form_default(xml_tree) == "qualified":
                    full_path += '/{0}:{1}'.format(target_namespace_prefix, text_capitalized)
                elif "{0}:".format(target_namespace_prefix) in full_path:
                    full_path += '/{0}'.format(text_capitalized)
                else:
                    full_path += '/{0}:{1}'.format(target_namespace_prefix, text_capitalized)
            else:
                full_path += '/*[local-name()="{0}"]'.format(text_capitalized)
        else:
            full_path += "/{0}".format(text_capitalized)
    elif element_tag == 'attribute':
        if target_namespace is not None:
            if target_namespace_prefix != '':
                if get_attribute_form_default(xml_tree) == "qualified":
                    full_path += '/@{0}:{1}'.format(target_namespace_prefix, text_capitalized)
                elif "{0}:".format(target_namespace_prefix) in full_path:
                    full_path += '/@{0}'.format(text_capitalized)
                else:
                    full_path += '/@{0}:{1}'.format(target_namespace_prefix, text_capitalized)
            else:
                full_path += '/@*[local-name()="{0}"]'.format(text_capitalized)
        else:
            full_path += "/@{0}".format(text_capitalized)

    # print full_path

    # XSD xpath: /element/complexType/sequence
    xsd_xpath = xml_tree.getpath(element)

    db_element['options']['name'] = element.attrib.get('name')
    db_element['options']['xpath']['xsd'] = xsd_xpath
    db_element['options']['xpath']['xml'] = full_path
    if 'PARSER_APPLICATION' in request.session and request.session['PARSER_APPLICATION'] == 'EXPLORE':
        db_element['options']['type'] = element.attrib['type'] if 'type' in element.attrib else None

    # init variables for buttons management
    add_button = False
    delete_button = False
    nb_occurrences = 1  # nb of occurrences to render (can't be 0 or the user won't see this element at all)
    nb_occurrences_data = min_occurs  # nb of occurrences in loaded data or in form being rendered (can be 0)
    use = ""
    removed = False

    # loading data in the form
    if 'curate_edit' in request.session and request.session['curate_edit']:
        if xml_element is None:
            # get the number of occurrences in the data
            edit_elements = edit_data_tree.xpath(full_path, namespaces=namespaces)
            nb_occurrences_data = len(edit_elements)
        else:
            if xml_element is False:  # explicitly say to not generate the element
                edit_elements = []
                nb_occurrences_data = 1
            else:
                edit_elements = [xml_element]
                nb_occurrences_data = 1

        if nb_occurrences_data == 0:
            use = "removed"
            removed = True

        # manage buttons
        if nb_occurrences_data < max_occurs:
            add_button = True
        if nb_occurrences_data > min_occurs:
            delete_button = True

    else:  # starting an empty form
        # Don't generate the element if not necessary
        if request.session['PARSER_MIN_TREE'] and min_occurs == 0:
            use = "removed"
            removed = True

        if nb_occurrences_data < max_occurs:
            add_button = True
        if nb_occurrences_data > min_occurs:
            delete_button = True

    if _has_module:
        # block maxOccurs to one, the module should take care of occurrences when the element is replaced
        nb_occurrences = 1
        # max_occurs = 1
    elif nb_occurrences_data > nb_occurrences:
        nb_occurrences = nb_occurrences_data

    # get the element namespace
    element_ns = get_element_namespace(element, xml_tree)
    # set the element namespace
    # tag_ns = ' xmlns="{0}" '.format(element_ns) if element_ns is not None else ''
    ns_prefix = None
    if element_tag == "attribute" and target_namespace is not None:
        for prefix, ns in namespaces.iteritems():
            if ns == target_namespace:
                ns_prefix = prefix
                break

    # get the element type
    default_prefix = common.get_default_prefix(namespaces)

    db_element['options']['schema_location'] = schema_location
    db_element['options']['xmlns'] = element_ns
    db_element['options']['ns_prefix'] = ns_prefix

    element_type, xml_tree, schema_location = get_element_type(element, xml_tree, namespaces,
                                                               default_prefix, target_namespace_prefix,
                                                               schema_location)

    # management of elements inside a choice (don't display if not part of the currently selected choice)
    if choice_info:
        if 'curate_edit' in request.session and request.session['curate_edit']:
            if len(edit_elements) == 0:
                if request.session['PARSER_MIN_TREE']:
                    return form_string, db_element
        else:
            if choice_info.counter > 0:
                if request.session['PARSER_MIN_TREE']:
                    return form_string, db_element
    else:
        pass

    if force_generation:
        nb_occurrences = 1
        removed = False

    # if auto key/keyref is True, go find keys/keyrefs in element scope
    if request.session['PARSER_AUTO_KEY_KEYREF']:
        # TODO: for now, support key/keyref for attributes only
        if element_tag == 'attribute':
            if is_key(request, element, full_path):
                _has_module = True
                db_element['options']['module'] = None if not _has_module else True
            elif is_key_ref(request, element, db_element, full_path):
                _has_module = True
                db_element['options']['module'] = None if not _has_module else True
        if element_tag == 'element':
            # look if key/keyrefs are defined for the scope of this element
            manage_key_keyref(request, element, full_path, xml_tree)

    for x in range(0, int(nb_occurrences)):
        db_elem_iter = {
            'tag': 'elem-iter',
            'value': None,
            'children': []
        }

        # get the use from app info element
        app_info_use = app_info['use'] if 'use' in app_info else ''
        app_info_use = app_info_use if app_info_use is not None else ''
        use += ' ' + app_info_use

        li_content = ''

        if request.session['PARSER_COLLAPSE']:
            # the type is complex, can be collapsed
            if element_type is not None and element_type.tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):
                li_content += ''

        label = app_info['label'] if 'label' in app_info else text_capitalized
        label = label if label is not None else ''

        db_element['options']['label'] = label

        li_content += label

        # add buttons to add/remove elements
        buttons = ""
        if not (add_button is False and delete_button is False):
            pass

        # get the default value (from xsd or from loaded xml)
        default_value = ""
        if 'curate_edit' in request.session and request.session['curate_edit']:
            # if elements are found at this xpath
            if len(edit_elements) > 0:
                # it is an XML element
                if element_tag == 'element':
                    # get the value of the element x
                    if edit_elements[x].text is not None:
                        # set the value of the element
                        default_value = edit_elements[x].text
                # it is an XMl attribute
                elif element_tag == 'attribute':
                    # get the value of the attribute
                    if edit_elements[x] is not None:
                        # set the value of the element
                        if isinstance(edit_elements[x], numbers.Number):
                            default_value = str(edit_elements[x])
                        else:
                            default_value = edit_elements[x]
        elif 'default' in element.attrib:
            # if the default attribute is present
            default_value = element.attrib['default']

        default_value = default_value.strip()

        # if element not removed
        if not removed:
            # if module is present, replace default input by module
            if _has_module:
                module = generate_module(request, element, xsd_xpath, full_path, xml_tree=xml_tree,
                                         edit_data_tree=edit_data_tree)

                form_string += module[0]
                db_elem_iter['children'].append(module[1])
            else:  # generate the type
                if element_type is None:  # no complex/simple type
                    placeholder = app_info['placeholder'] if 'placeholder' in app_info else ''
                    tooltip = _fmt_tooltip(app_info['tooltip']) if 'tooltip' in app_info else ''
                    use = app_info['use'] if 'use' in app_info else ''

                    li_content += ' '
                    li_content += buttons

                    db_child = {
                        'tag': 'input',
                        'options': {
                            'placeholder': placeholder,
                            'tooltip': tooltip,
                            'use': use,
                        },
                        'value': default_value
                    }
                    db_elem_iter['children'].append(db_child)
                else:  # complex/simple type
                    li_content += buttons

                    if element_type.tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):
                        complex_type_result = generate_complex_type(request, element_type, xml_tree,
                                                                    full_path=full_path+'[' + str(x+1) + ']',
                                                                    edit_data_tree=edit_data_tree,
                                                                    default_value=default_value,
                                                                    schema_location=schema_location)

                        li_content += complex_type_result[0]
                        db_elem_iter['children'].append(complex_type_result[1])
                    elif element_type.tag == "{0}simpleType".format(LXML_SCHEMA_NAMESPACE):
                        simple_type_result = generate_simple_type(request, element_type, xml_tree,
                                                                  full_path=full_path+'[' + str(x+1) + ']',
                                                                  edit_data_tree=edit_data_tree,
                                                                  default_value=default_value,
                                                                  schema_location=schema_location)

                        li_content += simple_type_result[0]
                        db_elem_iter['children'].append(simple_type_result[1])
        else:
            li_content += buttons

        # if len(db_elem_iter['children']) > 0:
        db_element['children'].append(db_elem_iter)

    # form_string += render_ul(ul_content, choice_id, chosen)
    return form_string, db_element


def generate_element_absent(request, element_id, config=None):
    """

    Parameters:
        request:
        element_id:
    :return:
    """
    load_config(request, config)

    sub_element = SchemaElement.objects.get(pk=element_id)
    element_list = SchemaElement.objects(children=element_id)

    if len(element_list) == 0:
        raise ValueError("No SchemaElement found")
    elif len(element_list) > 1:
        raise ValueError("More than one SchemaElement found")

    schema_element = element_list[0]

    schema_location = None
    if 'schema_location' in schema_element.options:
        schema_location = schema_element.options['schema_location']

    # if the xml element is from an imported schema
    if schema_location is not None:
        # open the imported file
        ref_xml_schema_file = urllib2.urlopen(schema_element.options['schema_location'])
        # get the content of the file
        ref_xml_schema_content = ref_xml_schema_file.read()
        # build the XML tree
        xml_doc_tree = etree.parse(BytesIO(ref_xml_schema_content.encode('utf-8')))
        # get the namespaces from the imported schema
        namespaces = common.get_namespaces(BytesIO(str(ref_xml_schema_content)))
    else:
        # get the content of the XML tree
        xml_doc_tree_str = request.session['xmlDocTree']
        # # build the XML tree
        xml_doc_tree = etree.ElementTree(etree.fromstring(xml_doc_tree_str))
        # get the namespaces
        namespaces = common.get_namespaces(BytesIO(str(xml_doc_tree_str)))

    # flatten the includes
    flattener = XSDFlattenerURL(etree.tostring(xml_doc_tree))
    xml_doc_tree_str = flattener.get_flat()
    xml_doc_tree = etree.parse(BytesIO(xml_doc_tree_str.encode('utf-8')))

    xpath_element = schema_element.options['xpath']
    xsd_xpath = xpath_element['xsd']

    xml_xpath = None
    if 'xml' in xpath_element:
        xml_xpath = xpath_element['xml']

    xml_element = xml_doc_tree.xpath(xsd_xpath, namespaces=namespaces)[0]

    if 'min' in schema_element.options:
        xml_element.attrib['minOccurs'] = str(schema_element.options['min'])

    if 'max' in schema_element.options:
        if schema_element.options['max'] != -1:
            xml_element.attrib['maxOccurs'] = str(schema_element.options['max'])
        else:
            xml_element.attrib['maxOccurs'] = "unbounded"

    # generating a choice, generate the parent element
    if schema_element.tag == "choice":
        # can use generate_element to generate a choice never generated
        form_string = generate_choice(request, xml_element, xml_doc_tree, full_path=xml_xpath, force_generation=True)
    elif schema_element.tag == 'sequence':
        # form_string = generate_sequence_absent(request, xml_element, xml_doc_tree)
        form_string = generate_sequence(request, xml_element, xml_doc_tree, full_path=xml_xpath, force_generation=True)
    else:
        # can't directly use generate_element because only need the body of the element not its title
        # provide xpath without element name because already generated in generate_element
        form_string = generate_element(request, xml_element, xml_doc_tree, full_path=xml_xpath.rsplit('/', 1)[0],
                                       force_generation=True)

    db_tree = form_string[1]

    # Saving the tree in MongoDB
    tree_root = load_schema_data_in_db(db_tree)
    generated_element = tree_root.children[0]

    # Updating the schema element
    children = schema_element.children
    element_index = children.index(sub_element)

    children.insert(element_index + 1, generated_element)
    schema_element.update(set__children=children)

    if len(sub_element.children) == 0:
        schema_element.update(pull__children=element_id)

    schema_element.reload()
    update_branch_xpath(schema_element)

    tree_root_options = tree_root.options
    tree_root_options['real_root'] = str(schema_element.pk)

    tree_root.update(set__options=tree_root_options)
    tree_root.reload()

    renderer = ListRenderer(tree_root, request)
    html_form = renderer.render(True)

    tree_root.delete()
    return html_form


def generate_sequence(request, element, xml_tree, choice_info=None, full_path="", edit_data_tree=None,
                      schema_location=None, force_generation=False):
    """Generates a section of the form that represents an XML sequence

    Parameters:
        request:
        element: XML element
        xml_tree: XML Tree
        choice_info:
        full_path:
        edit_data_tree:
        schema_location:
        force_generation:

    Returns:       HTML string representing a sequence
    """
    # (annotation?,(element|group|choice|sequence|any)*)
    # FIXME implement group, any
    form_string = ""

    # remove the annotations
    remove_annotations(element)

    min_occurs, max_occurs = manage_occurences(element)

    # XSD xpath
    xsd_xpath = xml_tree.getpath(element)

    db_element = {
        'tag': 'sequence',
        'options': {
            'min': min_occurs,
            'max': max_occurs,
            'xpath': {
                'xsd': xsd_xpath,
                'xml': full_path
            },
            'schema_location': schema_location
        },
        'value': None,
        'children': []
    }

    if min_occurs != 1 or max_occurs != 1:
        text = "Sequence"

        # init variables for buttons management
        nb_occurrences = 1  # nb of occurrences to render (can't be 0 or the user won't see this element at all)
        nb_occurrences_data = min_occurs  # nb of occurrences in loaded data or in form being rendered (can be 0)

        # loading data in the form
        if 'curate_edit' in request.session and request.session['curate_edit']:
            # get the number of occurrences in the data
            elements_found = lookup_occurs(element, xml_tree, full_path, edit_data_tree)
            if max_occurs != 1:
                nb_occurrences_data = len(elements_found)
            else:
                if len(elements_found) > 0:
                    nb_occurrences_data = 1

        if nb_occurrences_data > nb_occurrences:
            nb_occurrences = nb_occurrences_data

        # keeps track of elements to display depending on the selected choice
        if choice_info:
            # chosen = True
            if 'curate_edit' in request.session and request.session['curate_edit']:
                if nb_occurrences == 0:
                    if request.session['PARSER_MIN_TREE']:
                        return form_string, db_element
            else:
                if choice_info.counter > 0:
                    if request.session['PARSER_MIN_TREE']:
                        return form_string, db_element

        if force_generation:
            nb_occurrences = 1

        for x in range(0, int(nb_occurrences)):
            db_elem_iter = {
                'tag': 'sequence-iter',
                'value': None,
                'children': []
            }

            li_content = ''

            if len(list(element)) > 0 and request.session['PARSER_COLLAPSE']:
                li_content += ''

            li_content += text

            # generates the sequence
            for child in element:
                if child.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
                    element_result = generate_element(request, child, xml_tree, choice_info,
                                                      full_path=full_path, edit_data_tree=edit_data_tree,
                                                      schema_location=schema_location)

                    li_content += element_result[0]
                    db_elem_iter['children'].append(element_result[1])
                elif child.tag == "{0}sequence".format(LXML_SCHEMA_NAMESPACE):
                    sequence_result = generate_sequence(request, child, xml_tree, choice_info,
                                                        full_path=full_path, edit_data_tree=edit_data_tree,
                                                        schema_location=schema_location)

                    li_content += sequence_result[0]
                    db_elem_iter['children'].append(sequence_result[1])
                elif child.tag == "{0}choice".format(LXML_SCHEMA_NAMESPACE):
                    choice_result = generate_choice(request, child, xml_tree, choice_info,
                                                    full_path=full_path, edit_data_tree=edit_data_tree,
                                                    schema_location=schema_location)

                    li_content += choice_result[0]
                    db_elem_iter['children'].append(choice_result[1])
                elif child.tag == "{0}any".format(LXML_SCHEMA_NAMESPACE):
                    pass
                elif child.tag == "{0}group".format(LXML_SCHEMA_NAMESPACE):
                    pass

            db_element['children'].append(db_elem_iter)

    else:  # min_occurs == 1 and max_occurs == 1
        db_elem_iter = {
            'tag': 'sequence-iter',
            'value': None,
            'children': []
        }

        # XSD xpath
        # xsd_xpath = xml_tree.getpath(element)

        # init variables for buttons management
        nb_occurrences = 1  # nb of occurrences to render (can't be 0 or the user won't see this element at all)
        # nb_occurrences_data = min_occurs  # nb of occurrences in loaded data or in form being rendered (can be 0)

        if choice_info:
            if 'curate_edit' in request.session and request.session['curate_edit']:
                if nb_occurrences == 0:
                    if request.session['PARSER_MIN_TREE']:
                        # db_element['children'].append(db_elem_iter)
                        return form_string, db_element
                else:
                    pass
            else:
                if choice_info.counter > 0:
                    if request.session['PARSER_MIN_TREE']:
                        # db_element['children'].append(db_elem_iter)
                        return form_string, db_element
                else:
                    pass

        # generates the sequence
        for child in element:
            if child.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
                element_result = generate_element(request, child, xml_tree, choice_info,
                                                  full_path=full_path, edit_data_tree=edit_data_tree,
                                                  schema_location=schema_location)

                form_string += element_result[0]
                db_elem_iter['children'].append(element_result[1])
            elif child.tag == "{0}sequence".format(LXML_SCHEMA_NAMESPACE):
                sequence_result = generate_sequence(request, child, xml_tree, choice_info,
                                                    full_path=full_path, edit_data_tree=edit_data_tree,
                                                    schema_location=schema_location)

                form_string += sequence_result[0]
                db_elem_iter['children'].append(sequence_result[1])
            elif child.tag == "{0}choice".format(LXML_SCHEMA_NAMESPACE):
                choice_result = generate_choice(request, child, xml_tree, choice_info,
                                                full_path=full_path, edit_data_tree=edit_data_tree,
                                                schema_location=schema_location)

                form_string += choice_result[0]
                db_elem_iter['children'].append(choice_result[1])
            elif child.tag == "{0}any".format(LXML_SCHEMA_NAMESPACE):
                pass
            elif child.tag == "{0}group".format(LXML_SCHEMA_NAMESPACE):
                pass

        db_element['children'].append(db_elem_iter)

        # close the list
        if choice_info:
            form_string += "</ul>"

    return form_string, db_element


def generate_sequence_absent(request, element, xml_tree, schema_location=None):
    """Generates a section of the form that represents an XML sequence

    Parameters:
        request:
        element: XML element
        xml_tree: XML Tree
        schema_location:

    Returns:
        HTML string representing a sequence
    """
    # TODO see if it can be merged in generate_sequence
    form_string = ""
    db_element = {
        'tag': 'sequence-iter',
        'value': None,
        'children': []
    }

    # generates the sequence
    for child in element:
        if child.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
            element = generate_element(request, child, xml_tree, schema_location=schema_location)

            form_string += element[0]
            db_element['children'].append(element[1])
        elif child.tag == "{0}sequence".format(LXML_SCHEMA_NAMESPACE):
            sequence = generate_sequence(request, child, xml_tree, schema_location=schema_location)

            form_string += sequence[0]
            db_element['children'].append(sequence[1])
        elif child.tag == "{0}choice".format(LXML_SCHEMA_NAMESPACE):
            choice = generate_choice(request, child, xml_tree, schema_location=schema_location)

            form_string += choice[0]
            db_element['children'].append(choice[1])
        elif child.tag == "{0}any".format(LXML_SCHEMA_NAMESPACE):
            pass
        elif child.tag == "{0}group".format(LXML_SCHEMA_NAMESPACE):
            pass

    # return form_string, db_element
    return form_string, db_element


def generate_choice(request, element, xml_tree, choice_info=None, full_path="", edit_data_tree=None,
                    schema_location=None, force_generation=False):
    """Generates a section of the form that represents an XML choice

    Parameters:
        request:
        element: XML element
        xml_tree: XML Tree
        choice_info: to keep track of branches to display (chosen ones) when going recursively down the tree
        full_path: XML xpath being built
        edit_data_tree: XML tree of data being edited
        schema_location:
        force_generation:

    Returns:       HTML string representing a sequence
    """
    # (annotation?, (element|group|choice|sequence|any)*)
    # FIXME Group not supported
    # FIXME Choice not supported
    form_string = ""
    db_element = {
        'tag': 'choice',
        'options': {
            'xpath': {
                'xsd': None,
                'xml': full_path
            },
            'schema_location': schema_location
        },
        'value': None,
        'children': []
    }

    # remove the annotations
    remove_annotations(element)

    # init variables for buttons management
    nb_occurrences = 1  # nb of occurrences to render (can't be 0 or the user won't see this element at all)

    max_occurs = 1

    elements_found = None
    xml_element = None

    # not multiple roots
    # FIXME process differently this part
    if not isinstance(element, list):
        # XSD xpath: don't need it when multiple root (can't duplicate a root)
        xsd_xpath = xml_tree.getpath(element)

        db_element['options']['xpath']['xsd'] = xsd_xpath

        # get element's min/max occurs attributes
        min_occurs, max_occurs = manage_occurences(element)
        nb_occurrences_data = min_occurs  # nb of occurrences in loaded data or in form being rendered (can be 0)

        # loading data in the form
        if 'curate_edit' in request.session and request.session['curate_edit']:
            # get the number of occurrences in the data
            elements_found = lookup_occurs(element, xml_tree, full_path, edit_data_tree)
            nb_occurrences_data = len(elements_found)
            if max_occurs != 1:
                nb_occurrences_data = len(elements_found)
            else:
                if len(elements_found) > 0:
                    nb_occurrences_data = 1

        if nb_occurrences_data > nb_occurrences:
            nb_occurrences = nb_occurrences_data

        # 'occurs' key contains the tuple (minOccurs, nbOccurs, maxOccurs)
        # db_element['options'] = (min_occurs, nb_occurrences_data, max_occurs)
        db_element['options']['min'] = min_occurs
        db_element['options']['max'] = max_occurs

    # keeps track of elements to display depending on the selected choice
    if choice_info:
        if 'curate_edit' in request.session and request.session['curate_edit']:
            if nb_occurrences == 0:
                # chosen = False

                if request.session['PARSER_MIN_TREE']:
                    return form_string, db_element
        else:
            if choice_info.counter > 0:
                # chosen = False

                if request.session['PARSER_MIN_TREE']:
                    return form_string, db_element

    if force_generation:
        nb_occurrences = 1

    for x in range(0, int(nb_occurrences)):
        db_child = {
            'tag': 'choice-iter',
            'value': None,
            'children': []
        }

        li_content = ''

        element_found = None
        if elements_found is not None:
            try:
                element_found = elements_found[x]
            except:
                pass

        for (counter, choiceChild) in enumerate(list(element)):
            # For unbounded choice, explicitly don't generate the choices not selected
            if choiceChild.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
                # Find the default element
                if choiceChild.attrib.get('name') is not None:
                    opt_label = choiceChild.attrib.get('name')
                else:
                    opt_label = choiceChild.attrib.get('ref')

                    if ':' in choiceChild.attrib.get('ref'):
                        opt_label = opt_label.split(':')[1]

                # get the schema namespaces
                xml_tree_str = etree.tostring(xml_tree)
                namespaces = common.get_namespaces(BytesIO(str(xml_tree_str)))
                # add the XSI prefix used by extensions
                namespaces['xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
                target_namespace, target_namespace_prefix = common.get_target_namespace(namespaces, xml_tree)

                if 'curate_edit' in request.session and request.session['curate_edit']:
                    # TODO: manage unbounded choices for sequences/choices as well
                    if max_occurs != 1:
                        xml_element = False # explicitly don't generate the element
                        element_path = opt_label if target_namespace is None else "{"+target_namespace+"}" + opt_label
                        if element_found is not None and element_found.tag == element_path:
                            xml_element = element_found # explicitly build the element if found
                            db_child['value'] = counter

                    else:
                        # TODO: create prefix if no prefix?
                        ns_prefix = target_namespace_prefix + ":" if target_namespace is not None else ""
                        element_path = '{0}/{1}{2}'.format(full_path, ns_prefix, opt_label)
                        if len(edit_data_tree.xpath(element_path, namespaces=namespaces)) != 0:
                            db_child['value'] = counter
                element_result = generate_element(request, choiceChild, xml_tree,
                                                  common.ChoiceInfo(counter),
                                                  full_path=full_path,
                                                  edit_data_tree=edit_data_tree,
                                                  schema_location=schema_location,
                                                  xml_element=xml_element)

                li_content += element_result[0]
                db_child_0 = element_result[1]
                db_child['children'].append(db_child_0)
            elif choiceChild.tag == "{0}group".format(LXML_SCHEMA_NAMESPACE):
                pass
            elif choiceChild.tag == "{0}choice".format(LXML_SCHEMA_NAMESPACE):
                # if element_found is not None:
                #     subnodes_xpath = get_nodes_xpath(choiceChild, xml_tree)
                #     for subnode_xpath in subnodes_xpath:
                #         if element_found.tag == subnode_xpath['name']:
                #             xml_element = element_found
                #             db_child['value'] = counter
                #             break
                choice = generate_choice(request, choiceChild, xml_tree,
                                         common.ChoiceInfo(counter), full_path=full_path,
                                         edit_data_tree=edit_data_tree, schema_location=schema_location)

                db_child['children'].append(choice[1])
            elif choiceChild.tag == "{0}sequence".format(LXML_SCHEMA_NAMESPACE):
                # if element_found is not None:
                #     subnodes_xpath = get_nodes_xpath(choiceChild, xml_tree)
                #     for subnode_xpath in subnodes_xpath:
                #         if element_found.tag == subnode_xpath['name']:
                #             xml_element = element_found
                #             db_child['value'] = counter
                #             break
                sequence = generate_sequence(request, choiceChild, xml_tree,
                                             common.ChoiceInfo(counter), full_path=full_path,
                                             edit_data_tree=edit_data_tree, schema_location=schema_location)

                li_content += sequence[0]
                db_child_0 = sequence[1]
                db_child['children'].append(db_child_0)
            elif choiceChild.tag == "{0}any".format(LXML_SCHEMA_NAMESPACE):
                pass

        db_element['children'].append(db_child)

    # form_string += render_ul(ul_content, choice_id, chosen)
    return form_string, db_element


def generate_choice_absent(request, element_id, config=None):
    load_config(request, config)

    element = SchemaElement.objects.get(pk=element_id)
    parents = SchemaElement.objects(children=element_id)

    if len(parents) == 0:
        raise ValueError("No SchemaElement found")
    elif len(parents) > 1:
        raise ValueError("More than one SchemaElement found")

    parent = parents[0]

    schema_location = None
    if 'schema_location' in element.options:
        schema_location = element.options['schema_location']

    # if the xml element is from an imported schema
    if schema_location is not None:
        # open the imported file
        ref_xml_schema_file = urllib2.urlopen(element.options['schema_location'])
        # get the content of the file
        ref_xml_schema_content = ref_xml_schema_file.read()
        # build the XML tree
        xml_doc_tree = etree.parse(BytesIO(ref_xml_schema_content.encode('utf-8')))
        # get the namespaces from the imported schema
        namespaces = common.get_namespaces(BytesIO(str(ref_xml_schema_content)))
    else:
        # get the content of the XML tree
        xml_doc_tree_str = request.session['xmlDocTree']
        # # build the XML tree
        xml_doc_tree = etree.ElementTree(etree.fromstring(xml_doc_tree_str))
        # get the namespaces
        namespaces = common.get_namespaces(BytesIO(str(xml_doc_tree_str)))

    # flatten the includes
    flattener = XSDFlattenerURL(etree.tostring(xml_doc_tree))
    xml_doc_tree_str = flattener.get_flat()
    xml_doc_tree = etree.parse(BytesIO(xml_doc_tree_str.encode('utf-8')))

    xpath_element = element.options['xpath']
    xsd_xpath = xpath_element['xsd']

    xml_xpath = None
    if 'xml' in xpath_element:
        xml_xpath = xpath_element['xml']

    xml_element = xml_doc_tree.xpath(xsd_xpath, namespaces=namespaces)[0]

    # FIXME: Support all possibilities
    if element.tag == 'element':
        # provide xpath without element name because already generated in generate_element
        form_string = generate_element(request, xml_element, xml_doc_tree, full_path=xml_xpath.rsplit('/', 1)[0])
    elif element.tag == 'sequence':
        form_string = generate_sequence(request, xml_element, xml_doc_tree, full_path=xml_xpath)
    else:
        raise MDCSError('Element cannot be generated: not implemented.')

    db_tree = form_string[1]

    # Saving the tree in MongoDB
    tree_root = load_schema_data_in_db(db_tree)

    # Replacing the children with the generated branch
    children = parent.children
    element_index = children.index(element)

    children[element_index] = tree_root

    parent.update(set__children=children)
    parent.update(set__value=str(tree_root.pk))

    parent.reload()

    renderer = ListRenderer(tree_root, request)
    html_form = renderer.render(False)

    return html_form


def generate_simple_type(request, element, xml_tree, full_path, edit_data_tree=None,
                         default_value=None, schema_location=None):
    """Generates a section of the form that represents an XML simple type

    Parameters:
        request:
        element:
        xml_tree:
        full_path:
        edit_data_tree:
        default_value:
        schema_location:

    Returns:
        HTML string representing a simple type
    """
    # FIXME implement union, correct list
    form_string = ""
    db_element = {
        'tag': 'simple_type',
        'value': None,
        'children': [],
        'options': {
            'name': element.attrib['name'] if 'name' in element.attrib else '',
            'xmlns': get_element_namespace(element, xml_tree),
        },
    }

    # remove the annotations
    remove_annotations(element)

    # get namespace prefix to reference extension in xsi:type
    xml_tree_str = etree.tostring(xml_tree)
    namespaces = common.get_namespaces(BytesIO(str(xml_tree_str)))
    target_namespace, target_namespace_prefix = common.get_target_namespace(namespaces, xml_tree)
    ns_prefix = None
    if target_namespace is not None:
        for prefix, ns in namespaces.iteritems():
            if ns == target_namespace:
                ns_prefix = prefix
                break
    db_element['options']['ns_prefix'] = ns_prefix

    if has_module(request, element):
        # XSD xpath: /element/complexType/sequence
        xsd_xpath = xml_tree.getpath(element)
        module = generate_module(request, element, xsd_xpath, full_path, xml_tree=xml_tree,
                                 edit_data_tree=edit_data_tree)

        form_string += module[0]
        db_element['children'].append(module[1])
        # db_element['module'] = True

        return form_string, db_element

    # TODO: check that it's not already extending a base
    # check if the type has a name (can be referenced by an extension)
    if 'name' in element.attrib and request.session['implicit_extension']:
        # check if types extend this one
        extensions = get_extensions(xml_tree, element.attrib['name'])

        # the type has some possible extensions
        if len(extensions) > 0:
            # add the base type that can be rendered alone without extensions
            extensions.insert(0, element)
            choice_content = generate_choice_extensions(request, extensions, xml_tree, None, full_path, edit_data_tree,
                                                        schema_location)
            form_string += choice_content[0]
            db_element['children'].append(choice_content[1])
            return form_string, db_element

    if list(element) != 0:
        child = element[0]

        if child.tag == "{0}restriction".format(LXML_SCHEMA_NAMESPACE):
            restriction = generate_restriction(request, child, xml_tree, full_path, edit_data_tree=edit_data_tree,
                                               default_value=default_value, schema_location=schema_location)

            form_string += restriction[0]
            db_child = restriction[1]
        elif child.tag == "{0}list".format(LXML_SCHEMA_NAMESPACE):
            # TODO list can contain a restriction/enumeration
            # FIXME None default value
            if default_value is None:
                default_value = ''

            # form_string += render_input(default_value, '', '')

            db_child = {
                'tag': 'list',
                'value': default_value,
                'children': []
            }
        elif child.tag == "{0}union".format(LXML_SCHEMA_NAMESPACE):
            # TODO: provide UI for unions
            # form_string += render_input(default_value, '', '')

            db_child = {
                'tag': 'union',
                'value': default_value,
                'children': []
            }
        else:
            db_child = {
                'tag': 'error'
            }

        db_element['children'].append(db_child)

    return form_string, db_element
    # return form_string


def generate_complex_type(request, element, xml_tree, full_path, edit_data_tree=None, default_value='',
                          schema_location=None):
    """Generates a section of the form that represents an XML complexType

    Parameters:
        request:
        element: XML element
        xml_tree: XML Tree
        full_path:
        edit_data_tree:
        default_value:
        schema_location:

    Returns:
        HTML string representing a sequence
    """
    # FIXME add support for complexContent, group, attributeGroup, anyAttribute
    # (
    #   annotation?,
    #   (
    #       simpleContent|complexContent|(
    #           (group|all|choice|sequence)?,
    #           (
    #               (attribute|attributeGroup)*,
    #               anyAttribute?
    #           )
    #       )
    #   )
    # )

    form_string = ""
    db_element = {
        'tag': 'complex_type',
        'value': None,
        'children': [],
        'options': {
            'name': element.attrib['name'] if 'name' in element.attrib else '',
            'xmlns': get_element_namespace(element, xml_tree),
        },
    }
    # remove the annotations
    remove_annotations(element)

    # get namespace prefix to reference extension in xsi:type
    xml_tree_str = etree.tostring(xml_tree)
    namespaces = common.get_namespaces(BytesIO(str(xml_tree_str)))
    target_namespace, target_namespace_prefix = common.get_target_namespace(namespaces, xml_tree)
    ns_prefix = None

    if target_namespace is not None:
        for prefix, ns in namespaces.iteritems():
            if ns == target_namespace:
                ns_prefix = prefix
                break

    db_element['options']['ns_prefix'] = ns_prefix

    if has_module(request, element):
        # XSD xpath: /element/complexType/sequence
        xsd_xpath = xml_tree.getpath(element)
        module = generate_module(request, element, xsd_xpath, full_path, xml_tree=xml_tree,
                                 edit_data_tree=edit_data_tree)

        form_string += module[0]
        # db_element['options'] = {
        #     'mod': True
        # }
        db_element['children'].append(module[1])

        return form_string, db_element

    # TODO: check that it's not already extending a base
    # check if the type has a name (can be referenced by an extension)
    if 'name' in element.attrib and request.session['implicit_extension']:
        # check if types extend this one
        extensions = get_extensions(xml_tree, element.attrib['name'])

        # the type has some possible extensions
        if len(extensions) > 0:
            # add the base type that can be rendered alone without extensions
            if request.session['PARSER_IMPLICIT_EXTENSION_BASE']:
                extensions.insert(0, element)

            choice_content = generate_choice_extensions(request, extensions, xml_tree, None, full_path,
                                                        edit_data_tree,
                                                        schema_location)
            form_string += choice_content[0]
            db_element['children'].append(choice_content[1])
            return form_string, db_element

    # is it a simple content?
    complex_type_child = element.find('{0}simpleContent'.format(LXML_SCHEMA_NAMESPACE))
    if complex_type_child is not None:
        result_simple_content = generate_simple_content(request, complex_type_child, xml_tree,
                                                        full_path=full_path,
                                                        edit_data_tree=edit_data_tree,
                                                        default_value=default_value,
                                                        schema_location=schema_location)

        form_string += result_simple_content[0]
        db_element['children'].append(result_simple_content[1])

        return form_string, db_element

    # is it a complex content?
    complex_type_child = element.find('{0}complexContent'.format(LXML_SCHEMA_NAMESPACE))
    if complex_type_child is not None:
        complex_content_result = generate_complex_content(request, complex_type_child, xml_tree,
                                                          full_path=full_path,
                                                          edit_data_tree=edit_data_tree,
                                                          default_value=default_value,
                                                          schema_location=schema_location)
        form_string += complex_content_result[0]
        db_element['children'].append(complex_content_result[1])

        return form_string, db_element

    # does it contain any attributes?
    complex_type_children = element.findall('{0}attribute'.format(LXML_SCHEMA_NAMESPACE))
    if len(complex_type_children) > 0:
        for attribute in complex_type_children:
            element_result = generate_element(request, attribute, xml_tree, full_path=full_path,
                                              edit_data_tree=edit_data_tree, schema_location=schema_location)

            form_string += element_result[0]
            db_element['children'].append(element_result[1])
    # does it contain sequence or all?
    complex_type_child = element.find('{0}sequence'.format(LXML_SCHEMA_NAMESPACE))
    if complex_type_child is not None:
        sequence_result = generate_sequence(request, complex_type_child, xml_tree, full_path=full_path,
                                            edit_data_tree=edit_data_tree, schema_location=schema_location)

        form_string += sequence_result[0]
        db_element['children'].append(sequence_result[1])
    else:
        complex_type_child = element.find('{0}all'.format(LXML_SCHEMA_NAMESPACE))
        if complex_type_child is not None:
            sequence_result = generate_sequence(request, complex_type_child, xml_tree, full_path=full_path,
                                                edit_data_tree=edit_data_tree, schema_location=schema_location)

            form_string += sequence_result[0]
            db_element['children'].append(sequence_result[1])
        else:
            # does it contain choice ?
            complex_type_child = element.find('{0}choice'.format(LXML_SCHEMA_NAMESPACE))
            if complex_type_child is not None:
                choice_result = generate_choice(request, complex_type_child, xml_tree, full_path=full_path,
                                                edit_data_tree=edit_data_tree, schema_location=schema_location)

                form_string += choice_result[0]
                db_element['children'].append(choice_result[1])

    return form_string, db_element


def generate_choice_extensions(request, element, xml_tree, choice_info=None, full_path="",
                               edit_data_tree=None, schema_location=None):
    """Generates a section of the form that represents an implicit extension

    Parameters:
        request:
        element: XML element
        xml_tree: XML Tree
        choice_info: to keep track of branches to display (chosen ones) when going recursively down the tree
        full_path: XML xpath being built
        edit_data_tree: XML tree of data being edited
        schema_location:

    Returns:       HTML string representing a sequence
    """

    form_string = ""
    db_element = {
        'tag': 'choice',
        'options': {
            'xpath': {
                'xsd': None,
                'xml': full_path
            },
            'schema_location': schema_location
        },
        'value': None,
        'children': []
    }

    # remove the annotations
    remove_annotations(element)

    # init variables for buttons management
    nb_occurrences = 1  # nb of occurrences to render (can't be 0 or the user won't see this element at all)

    # keeps track of elements to display depending on the selected choice
    if choice_info:
        if 'curate_edit' in request.session and request.session['curate_edit']:
            if nb_occurrences == 0:
                if request.session['PARSER_MIN_TREE']:
                    return form_string, db_element
        else:
            if choice_info.counter > 0:
                if request.session['PARSER_MIN_TREE']:
                    return form_string, db_element

    for x in range(0, int(nb_occurrences)):
        db_child = {
            'tag': 'choice-iter',
            'value': None,
            'children': [],
            'options': {},
        }

        li_content = ''

        request.session['implicit_extension'] = False
        for (counter, choiceChild) in enumerate(list(element)):
            if choiceChild.tag == "{0}simpleType".format(LXML_SCHEMA_NAMESPACE) or \
               choiceChild.tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):

                if choiceChild.tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):
                    result = generate_complex_type(request, choiceChild, xml_tree,
                                                   full_path=full_path,
                                                   edit_data_tree=edit_data_tree,
                                                   schema_location=schema_location)

                elif choiceChild.tag == "{0}simpleType".format(LXML_SCHEMA_NAMESPACE):
                    result = generate_simple_type(request, choiceChild, xml_tree,
                                                  full_path=full_path,
                                                  edit_data_tree=edit_data_tree,
                                                  schema_location=schema_location)

                # Find the default element
                if choiceChild.attrib.get('name') is not None:
                    opt_label = choiceChild.attrib.get('name')
                else:
                    opt_label = choiceChild.attrib.get('ref')

                    if ':' in choiceChild.attrib.get('ref'):
                        opt_label = opt_label.split(':')[1]

                # look for active choice when editing
                if 'curate_edit' in request.session and request.session['curate_edit']:
                    # get the schema namespaces
                    xml_tree_str = etree.tostring(xml_tree)
                    namespaces = common.get_namespaces(BytesIO(str(xml_tree_str)))
                    # add the XSI prefix used by extensions
                    namespaces['xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
                    target_namespace, target_namespace_prefix = common.get_target_namespace(namespaces, xml_tree)
                    # TODO: create prefix if no prefix?
                    ns_prefix = target_namespace_prefix + ":" if target_namespace is not None else ""
                    ns_element_path = '{0}[@xsi:type="{1}{2}"]'.format(full_path, ns_prefix, opt_label)
                    element_path = '{0}[@xsi:type="{1}"]'.format(full_path, opt_label)

                    ns_elements = edit_data_tree.xpath(ns_element_path, namespaces=namespaces)
                    elements = edit_data_tree.xpath(element_path, namespaces=namespaces)

                    if len(ns_elements) != 0 or len(elements) != 0:
                        db_child['value'] = counter

                li_content += result[0]
                db_child_0 = result[1]
                db_child['children'].append(db_child_0)

        db_element['children'].append(db_child)

    request.session['implicit_extension'] = True
    # form_string += render_ul(ul_content, choice_id, chosen)
    return form_string, db_element


def generate_complex_content(request, element, xml_tree, full_path, edit_data_tree=None, default_value='',
                             schema_location=None):
    """
    Inputs:        request -
                   element - XML element
                   xmlTree - XML Tree
    Outputs:       HTML string representing a sequence
    Exceptions:    None
    Description:   Generates a section of the form that represents an XML complex content

    Parameters:
        request:
        element:
        xml_tree:
        full_path:
        edit_data_tree:
        default_value:
        schema_location:

    :return:
    """
    # (annotation?,(restriction|extension))

    form_string = ""
    db_element = {
        'tag': 'complex_content',
        'value': None,
        'children': []
    }

    # remove the annotations
    remove_annotations(element)

    # generates the content
    if len(list(element)) != 0:
        child = element[0]
        if child.tag == "{0}restriction".format(LXML_SCHEMA_NAMESPACE):
            restriction_result = generate_restriction(request, child, xml_tree, full_path,
                                                      edit_data_tree=edit_data_tree,
                                                      default_value=default_value,
                                                      schema_location=schema_location)

            form_string += restriction_result[0]
            db_element['children'].append(restriction_result[1])
        elif child.tag == "{0}extension".format(LXML_SCHEMA_NAMESPACE):
            extension_result = generate_extension(request, child, xml_tree, full_path,
                                                  edit_data_tree=edit_data_tree,
                                                  default_value=default_value,
                                                  schema_location=schema_location)

            form_string += extension_result[0]
            db_element['children'].append(extension_result[1])

    return form_string, db_element


def generate_module(request, element, xsd_xpath=None, xml_xpath=None, xml_tree=None, edit_data_tree=None):
    """Generate a module to replace an element

    Parameters:
        request:
        element:
        xsd_xpath:
        xml_xpath:
        xml_tree:
        edit_data_tree:

    Returns:
        Module
    """
    db_element = {
        'tag': 'module',
        'value': None,
        'options': {
            'data': None,
            'attributes': None,
            'params': None,
            'multiple': False
        },
        'children': []
    }

    form_string = ""

    # check if a module is set for this element
    if '{http://mdcs.ns}_mod_mdcs_' in element.attrib:
        # get the url of the module
        url = element.attrib['{http://mdcs.ns}_mod_mdcs_']

        parsed_url = urlparse(url)
        url = parsed_url.path

        try:
            module = Module.objects().get(url=url)

            # add extra parameters coming from url parameters
            if parsed_url.query != '':
                db_element['options']['params'] = dict(parse_qsl(parsed_url.query))

            db_element['options']['xpath'] = {
                'xsd': xsd_xpath,
                'xml': xml_xpath
            }

            db_element['options']['multiple'] = module.multiple

            # Get data to reload the module
            reload_data = None
            reload_attrib = None

            if 'curate_edit' in request.session and request.session['curate_edit']:
                # get the schema namespaces
                xml_tree_str = etree.tostring(xml_tree)
                namespaces = common.get_namespaces(BytesIO(str(xml_tree_str)))
                edit_elements = edit_data_tree.xpath(xml_xpath, namespaces=namespaces)

                if module.multiple:
                    reload_data = ""
                    for edit_element in edit_elements:
                        reload_data += etree.tostring(edit_element)
                else:
                    if len(edit_elements) > 0:
                        if len(edit_elements) == 1:
                            edit_element = edit_elements[0]

                            # get attributes
                            if 'attribute' not in xsd_xpath and len(edit_element.attrib) > 0:
                                reload_attrib = dict(edit_element.attrib)

                            reload_data = get_xml_element_data(element, edit_element)
                        else:
                            reload_data = []
                            reload_attrib = []

                            for edit_element in edit_elements:
                                reload_attrib.append(dict(edit_element.attrib))
                                reload_data.append(get_xml_element_data(element, edit_element))

            db_element['options']['url'] = url
            db_element['options']['data'] = reload_data
            db_element['options']['attributes'] = reload_attrib
        except:
            raise MDCSError('Module not found.')

    return form_string, db_element


def generate_simple_content(request, element, xml_tree, full_path='', edit_data_tree=None, default_value='',
                            schema_location=None):
    """Generates a section of the form that represents an XML simple content

    Parameters:
        request:
        element:
        xml_tree:
        full_path:
        edit_data_tree:
        default_value:
        schema_location:

    Returns:
        HTML string representing a simple content
    """
    # (annotation?,(restriction|extension))
    # FIXME better support for extension

    form_string = ""
    db_element = {
        'tag': 'simple_content',
        'value': None,
        'children': []
    }

    # remove the annotations
    remove_annotations(element)

    # generates the content
    if len(list(element)) != 0:
        child = element[0]

        if child.tag == "{0}restriction".format(LXML_SCHEMA_NAMESPACE):
            restriction_result = generate_restriction(request, child, xml_tree, full_path, edit_data_tree=edit_data_tree,
                                                      default_value=default_value, schema_location=schema_location)

            form_string += restriction_result[0]
            db_element['children'].append(restriction_result[1])
        elif child.tag == "{0}extension".format(LXML_SCHEMA_NAMESPACE):
            extension_result = generate_extension(request, child, xml_tree, full_path, edit_data_tree=edit_data_tree,
                                                  default_value=default_value, schema_location=schema_location)

            form_string += extension_result[0]
            db_element['children'].append(extension_result[1])

    return form_string, db_element


def generate_restriction(request, element, xml_tree, full_path="", edit_data_tree=None, default_value=None,
                         schema_location=None):
    """Generates a section of the form that represents an XML restriction

    Parameters:
        request:
        element: XML element
        xml_tree: XML Tree
        full_path:
        edit_data_tree:
        default_value:
        schema_location:

    Returns:
        HTML string representing a sequence
    """
    # FIXME doesn't represent all the possibilities (http://www.w3schools.com/xml/el_restriction.asp)
    # FIXME simpleType is a possible child only if the base attr has not been specified
    form_string = ""
    db_element = {
        'tag': 'restriction',
        'options': {
            'base': element.attrib.get('base')  # TODO Change it to avoid having the namespace with it
        },
        'value': None,
        'children': []
    }

    remove_annotations(element)

    enumeration = element.findall('{0}enumeration'.format(LXML_SCHEMA_NAMESPACE))

    if len(enumeration) > 0:
        option_list = []

        if 'curate_edit' in request.session and request.session['curate_edit']:
            default_value = default_value if default_value is not None else ''

            for enum in enumeration:
                db_child = {
                    'tag': 'enumeration',
                    'value': enum.attrib.get('value')
                }

                if default_value is not None and enum.attrib.get('value') == default_value:
                    entry = (enum.attrib.get('value'), enum.attrib.get('value'), True)
                    db_element['value'] = default_value
                else:
                    entry = (enum.attrib.get('value'), enum.attrib.get('value'), False)

                option_list.append(entry)
                db_element['children'].append(db_child)
        else:
            for enum in enumeration:
                db_child = {
                    'tag': 'enumeration',
                    'value': enum.attrib.get('value')
                }

                entry = (enum.attrib.get('value'), enum.attrib.get('value'), False)
                option_list.append(entry)

                db_element['children'].append(db_child)

            db_element['value'] = db_element['children'][0]['value']
    else:
        simple_type = element.find('{0}simpleType'.format(LXML_SCHEMA_NAMESPACE))
        if simple_type is not None:
            simple_type_result = generate_simple_type(request, simple_type, xml_tree, full_path=full_path,
                                                      edit_data_tree=edit_data_tree, default_value=default_value,
                                                      schema_location=schema_location)

            form_string += simple_type_result[0]
            db_child = simple_type_result[1]
        else:
            # FIXME temp fix default value shouldn't be None
            if default_value is None:
                default_value = ''

            # form_string += render_input(default_value, '', '')
            db_child = {
                'tag': 'input',
                'value': default_value
            }

        db_element['children'].append(db_child)

    return form_string, db_element


def generate_extension(request, element, xml_tree, full_path="", edit_data_tree=None, default_value='',
                       schema_location=None):
    """Generates a section of the form that represents an XML extension

    Parameters:
        request:
        element:
        xml_tree:
        full_path:
        edit_data_tree:
        default_value:
        schema_location:

    Returns:
        HTML string representing an extension
    """
    # FIXME doesn't represent all the possibilities (http://www.w3schools.com/xml/el_extension.asp)
    form_string = ""
    db_element = {
        'tag': 'extension',
        'value': None,
        'children': []
    }

    remove_annotations(element)

    request.session['implicit_extension'] = False

    ##################################################
    # Parsing attributes
    #
    # 'base' (required) is the only attribute to parse
    ##################################################
    if 'base' in element.attrib:
        xml_tree_str = etree.tostring(xml_tree)
        namespaces = common.get_namespaces(BytesIO(str(xml_tree_str)))
        default_prefix = common.get_default_prefix(namespaces)

        target_namespace_prefix = common.get_target_namespace_prefix(namespaces, xml_tree)
        base_type, xml_tree, schema_location = get_element_type(element, xml_tree, namespaces, default_prefix,
                                                                target_namespace_prefix, schema_location, 'base')

        # test if base is a built-in data types
        if base_type is None:
            db_element['children'].append(
                {
                    'tag': 'input',
                    'value': default_value
                }
            )
        else:  # not a built-in data type
            if base_type.tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):
                complex_type_result = generate_complex_type(request, base_type, xml_tree,
                                                            full_path=full_path,
                                                            edit_data_tree=edit_data_tree,
                                                            default_value=default_value,
                                                            schema_location=schema_location)

                form_string += complex_type_result[0]
                db_element['children'].append(complex_type_result[1])
            elif base_type.tag == "{0}simpleType".format(LXML_SCHEMA_NAMESPACE):
                simple_type_result = generate_simple_type(request, base_type, xml_tree,
                                                          full_path=full_path,
                                                          edit_data_tree=edit_data_tree,
                                                          default_value=default_value,
                                                          schema_location=schema_location)

                form_string += simple_type_result[0]
                db_element['children'].append(simple_type_result[1])

    ##################################################
    # Parsing children
    #
    ##################################################
    if 'children' in db_element['children'][0]: # Element extends simple or complex type
        extended_element = db_element['children'][0]['children']
    else:  # Element extends one of the base types
        extended_element = db_element['children']

    # does it contain any attributes?
    complex_type_children = element.findall('{0}attribute'.format(LXML_SCHEMA_NAMESPACE))
    if len(complex_type_children) > 0:
        for attribute in complex_type_children:
            element_result = generate_element(request, attribute, xml_tree, full_path=full_path,
                                              edit_data_tree=edit_data_tree, schema_location=schema_location)

            form_string += element_result[0]

            # Attribute is pushed on top of the list of children
            extended_element.insert(0, element_result[1])

    # does it contain sequence or all?
    complex_type_child = element.find('{0}sequence'.format(LXML_SCHEMA_NAMESPACE))
    if complex_type_child is not None:
        sequence_result = generate_sequence(request, complex_type_child, xml_tree, full_path=full_path,
                                            edit_data_tree=edit_data_tree, schema_location=schema_location)

        form_string += sequence_result[0]
        extended_element.append(sequence_result[1])
    else:
        complex_type_child = element.find('{0}all'.format(LXML_SCHEMA_NAMESPACE))
        if complex_type_child is not None:
            sequence_result = generate_sequence(request, complex_type_child, xml_tree, full_path=full_path,
                                                edit_data_tree=edit_data_tree, schema_location=schema_location)

            form_string += sequence_result[0]
            extended_element.append(sequence_result[1])
        else:
            # does it contain choice ?
            complex_type_child = element.find('{0}choice'.format(LXML_SCHEMA_NAMESPACE))
            if complex_type_child is not None:
                choice_result = generate_choice(request, complex_type_child, xml_tree, full_path=full_path,
                                                edit_data_tree=edit_data_tree, schema_location=schema_location)

                form_string += choice_result[0]
                extended_element.append(choice_result[1])

    request.session['implicit_extension'] = True

    return form_string, db_element
