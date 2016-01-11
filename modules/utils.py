import json
from lxml import etree
from django.utils.html import escape
from lxml.etree import XMLSyntaxError


def sanitize(input_value):
    input_type = type(input_value)

    if input_type == list:
        clean_value = []
        for item in input_value:
            clean_value.append(sanitize(item))

        return clean_value
    elif input_type == dict:
        return {sanitize(key): sanitize(val) for key, val in input_value.items()}
    elif input_type == str or input_type == unicode:
        try:
            # XML cleaning
            xml_cleaner_parser = etree.XMLParser(remove_blank_text=True)
            xml_data = etree.fromstring(input_value, parser=xml_cleaner_parser)

            input_value = etree.tostring(xml_data)
        except XMLSyntaxError, e:
            pass
#             if e is not None and e.message is not None:
#                 print 'Sanitizing XML (' + input_value + '): ' + e.message
#             else:
#                 print 'Sanitizing XML (' + input_value + '): '
        finally:
            try:
                json_value = json.loads(input_value)
                sanitized_value = sanitize(json_value)

                clean_value = json.dumps(sanitized_value)
            except ValueError:
                clean_value = escape(input_value)

        return clean_value
    elif input_type == int or input_type == float:
        return input_value
    else:
        # Default sanitizing
        return escape(str(input_value))

