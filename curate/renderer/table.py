"""
"""
from os.path import join
from django.template import loader

from curate.renderer import DefaultRenderer


# def render_table(content):
#     data = {
#         'content': content
#     }
#
#     return load_template('table.html', data, 'table')
#
#
# def render_tr(name, content):
#     data = {
#         'name': name,
#         'content': content
#     }
#
#     return load_template('tr.html', data, 'table')
#
#
# def render_top(title, content):
#     data = {
#         'title': title,
#         'content': content
#     }
#
#     return load_template('wrap.html', data, 'table')


class AbstractTableRenderer(DefaultRenderer):

    def __init__(self, xsd_data):
        table_renderer_path = join('renderer', 'table')
        table_templates = {
            'top': loader.get_template(join(table_renderer_path, 'wrap.html')),
            'table': loader.get_template(join(table_renderer_path, 'table.html')),
            'tr': loader.get_template(join(table_renderer_path, 'tr.html')),
        }

        super(AbstractTableRenderer, self).__init__(xsd_data, table_templates)

    def _render_table(self, content):
        data = {
            'content': content
        }

        return self._load_template('table', data)

    def _render_tr(self, name, content):
        data = {
            'name': name,
            'content': content
        }

        return self._load_template('tr', data)

    def _render_top(self, title, content):
        data = {
            'title': title,
            'content': content
        }

        return self._load_template('top', data)


class TableRenderer(AbstractTableRenderer):
    """
    """

    def __init__(self, xsd_data):
        super(TableRenderer, self).__init__(xsd_data)

    def render(self):
        html_content = ''

        if self.data.tag == 'element':
            html_content += self.render_element(self.data, no_name=True)
        else:
            message = 'render_data: ' + self.data.tag + ' not handled'
            self.warnings.append(message)

        return self._render_top(self.data.options['name'], html_content)

    def render_element(self, element, no_name=False):
        children = {}
        child_keys = []
        children_number = 0

        for child in element.children:
            if child.tag == 'elem-iter':
                children[child.pk] = child.children
                child_keys.append(child.pk)

                if len(child.children) > 0:
                    children_number += 1
            else:
                message = 'render_element (iteration): ' + child.tag + ' not handled'
                self.warnings.append(message)

        final_html = ''

        # Buttons generation (render once, reused many times)
        add_button = False
        del_button = False

        if 'max' in element.options:
            if children_number < element.options["max"] or element.options["max"] == -1:
                add_button = True

        if 'min' in element.options:
            if children_number > element.options["min"]:
                del_button = True

        buttons = self._render_buttons(add_button, del_button)

        for child_key in child_keys:
            # FIXME Use tuples instead
            sub_elements = []
            sub_inputs = []

            for child in children[child_key]:
                if child.tag == 'complex_type':
                    sub_elements.append(self.render_complex_type(child))
                    sub_inputs.append(False)
                elif child.tag == 'simple_type':
                    sub_elements.append(self.render_simple_type(child))
                    sub_inputs.append(False)
                elif child.tag == 'input':
                    sub_elements.append(self._render_input(child.pk))
                    sub_inputs.append(True)
                elif child.tag == 'module':
                    sub_elements.append(self.render_module(child))
                    sub_inputs.append(False)
                else:
                    message = 'render_element: ' + child.tag + ' not handled'
                    self.warnings.append(message)

            if children_number == 0:
                # FIXME Find a way to make the label grey
                html_content = ''
                # li_class = 'removed'
            else:
                html_content = ''
                for child_index in xrange(len(sub_elements)):
                    if sub_inputs[child_index]:  # Element is an input
                        html_content += element.options["name"] + sub_elements[child_index] + buttons
                    else:  # Element is not an input
                        html_content += self._render_collapse_button() + element.options["name"] + buttons
                        # html_content += self._render_ul(sub_elements[child_index], None)

            final_html += self._render_tr(element["options"]["name"] + buttons, html_content)

        # if len(children) > 1 or (len(children) == 1 and children[0]['tag'] != 'input'):
        #     html_content += self._render_table(subhtml)
        # else:
        #     # html_content += subhtml + buttons
        #     html_content += subhtml
        #
        # # return render_li(html_content, '', '', None, element["options"]["name"])
        # if no_name:
        #     return html_content

        return final_html

    def render_complex_type(self, element):
        print "ct"
        html_content = ''

        for child in element['children']:
            if child['tag'] == 'sequence':
                html_content += self.render_sequence(child)
            elif child['tag'] == 'simple_content':
                html_content += self.render_simple_content(child)
            elif child['tag'] == 'attribute':
                html_content += self.render_attribute(child)
            else:
                print child['tag'] + ' not handled (rend_ct)'

        return html_content

    def render_attribute(self, element):
        print "attr"
        # html_content = element["options"]["name"]
        html_content = ''
        children = []

        for child in element['children']:
            if child['tag'] == 'elem-iter':
                children += child['children']
            else:
                print child['tag'] + 'not handled (rend_attr base)'

        for child in children:
            if child['tag'] == 'simple_type':
                html_content += self.render_simple_type(child)
            elif child['tag'] == 'input':
                html_content += self._render_input(child)
            else:
                print child['tag'] + ' not handled (rend_attr)'
            # print child['tag'] + ' not handled (rend_attr)'

        # return render_li(html_content, '', '')
        return self._render_tr(element['options']['name'], html_content)

    def render_sequence(self, element):
        print "seq"
        html_content = ''

        for child in element['children']:
            if child['tag'] == 'element':
                html_content += self.render_element(child)
            else:
                print child['tag'] + '  not handled (rend_seq)'

        return html_content

    def render_simple_content(self, element):
        print "sc"
        html_content = ''

        for child in element['children']:
            if child['tag'] == 'element':
                html_content += self.render_element(child)
            elif child['tag'] == 'extension':
                html_content += self.render_extension(child)
            else:
                print child['tag'] + '  not handled (rend_scont)'

        return html_content

    def render_simple_type(self, element):
        print "st"
        html_content = ''

        for child in element['children']:
            # if child['tag'] == 'element':
            #     self._render_element(child)
            if child['tag'] == 'restriction':
                html_content += self.render_restriction(child)
            else:
                print child['tag'] + '  not handled (rend_stype)'

        return html_content

    def render_extension(self, element):
        print "ext"
        html_content = ''

        for child in element['children']:
            if child['tag'] == 'input':
                html_content += self._render_input(child)
            elif child['tag'] == 'attribute':
                html_content += self.render_attribute(child)
            else:
                print child['tag'] + ' not handled (rend_ext)'
            # print child['tag'] + '  not handled (rend_ext)'

        return html_content

    def render_restriction(self, element):
        print "rest"
        options = []
        subhtml = ''

        for child in element['children']:
            if child['tag'] == 'enumeration':
                options.append((child['value'], child['value'], False))
            elif child['tag'] == 'input':
                subhtml += self._render_input(child)
            else:
                print child['tag'] + ' not handled (rend_ext)'

        if subhtml == '' or len(options) != 0:
            return self._render_select(str(element.pk), 'restriction', options)
        else:
            return subhtml

    def render_module(self, element):
        return ''
