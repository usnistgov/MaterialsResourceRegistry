import hashlib
from collections import OrderedDict


class TreeInfo:
    title = ""
    key = ""
    key_hash = ""
    selected = False

    def __init__(self, title, key="", key_hash=""):
        self.title = title
        self.key = key
        self.key_hash = key_hash

    def __str__(self):
        return self.title

    def __eq__(self, other):
        return self.title == other.title

    def __hash__(self):
        return hash(self.title)

    def __lt__(self, other):
        return self.title < other.title

    def is_selected(self):
        return "true" if self.selected else ""

    def key_as_category(self):
        return "{0}_{1}".format(self.key, TreeInfo.get_category_label())

    def key_hash_as_category(self):
        return hashlib.sha1(self.key_as_category()).hexdigest()

    @staticmethod
    def get_category_label():
        return "_category"


def build_tree(tree, root, enums, dot_query, category=False):
    for enum in enums:
        t = tree
        t = t.setdefault(TreeInfo(title=root), OrderedDict())
        groups = enum.attrib['value'].split(':')
        split_index = 0
        for part in groups:
            split_index += 1
            key = "{0}=={1}".format(dot_query, ':'.join(groups[:split_index]))
            key_hash = hashlib.sha1(key).hexdigest()
            title = part
            # if category:
            #     title = ':'.join(groups[:split_index])
            g = TreeInfo(title=title, key=key, key_hash=key_hash)
            t = t.setdefault(g, OrderedDict())
    return tree


def print_tree(tree, nb_occurrences_text=False, category=False):
    display = "[\n"
    for key, leaves in tree.iteritems():
        display += _print_leaves(key, leaves, nb_occurrences_text, category)
    display += "]"
    return _remove_last_comma(display)


def _print_leaves(key, leaves, nb_occurrences_text=False, category=False):
    if len(leaves) == 0:
        display = _get_display(key.title, key.key_hash, key.is_selected(), key.key, nb_occurrences_text)
        return display + "},"
    elif len(leaves) > 0:
        if category:
            elt = _get_display("unspecified " + key.title, key.key_hash, key.is_selected(), key.key, nb_occurrences_text)
            display = _get_display(key.title, key.key_hash_as_category(), key.is_selected(), key.key_as_category(),
                                   nb_occurrences_text)
            display += ", \"folder\": true, \"children\": ["
            display += '\n'
            display += elt + "},"
        else:
            elt = _get_display(key.title, key.key_hash, key.is_selected(), key.key, nb_occurrences_text)
            display = elt
            display += ", \"folder\": true, \"children\": ["
            display += '\n'

        for key, value in sorted(leaves.iteritems()):
            display += _print_leaves(key, value, nb_occurrences_text, category=category) + '\n'
        display = _remove_last_comma(display)+"]},\n"

        return display


def _remove_last_comma(s):
    return "".join(s.rsplit(",", 1))


def _get_display(title, hash_, selected, key, nb_occurrences_text=False):
    if nb_occurrences_text:
        display = "{{\"title\": \"{0}&nbsp;" \
                  "(<em class='occurrences' id='{1}'>-</em>)\", " \
                  "\"selected\": \"{2}\", " \
                  "\"key\": \"{3}\"".format(title, hash_, selected, key)
    else:
        display = "{{\"title\": \"{0}\", " \
                  "\"selected\": \"{1}\", " \
                  "\"key\": \"{2}\"".format(title, selected, key)
    return display
