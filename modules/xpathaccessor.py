from curate.models import SchemaElement
from abc import ABCMeta, abstractmethod


class XPathAccessor(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, request):
        try:
            self._form_data_id = request.session['curateFormData']
            element = SchemaElement.objects.get(pk=request.POST['module_id'])

            # get xml xpath of the element
            # self.xpath = form_element.xml_xpath
            self.xpath = element.options['xpath']['xml']
            self.values = {}
            self.set_XpathAccessor(request)
        except:
            message = 'Unable to get form data information. Please check session is still valid and that HTTP request'
            message += ' is correctly sent to the Siblings Accessor system.'
            raise XPathAccessorError(message)

    def get_xpath(self):
        return self.xpath

    def set_xpath_value(self, form_id, xpath, value):
        form_element = self._get_element(form_id, xpath)
        input_element = self.get_input(form_element)

        if input_element.tag != 'module':
            input_element.update(set__value=value)
        else:  # Element is a module
            options = input_element.options

            if 'data' in value:
                options['data'] = value['data']

            if 'attriubtes' in value:
                options['attributes'] = value['attributes']

            input_element.update(set__options=options)

        input_element.reload()

    def get_input(self, element):
        input_elements = ['input', 'restriction', 'choice', 'module']

        if element.tag in input_elements:
            return element

        for child in element.children:
            return self.get_input(child)

    def _get_element(self, form_id, xpath):
        form_root = SchemaElement.objects.get(pk=form_id)

        if self.element_has_xpath(form_root, xpath):
            return form_root

        if len(form_root.children) == 0:
            return None

        for child in form_root.children:
            element = self._get_element(child.pk, xpath)

            if element is not None:
                return element


    @staticmethod
    def element_has_xpath(element, xpath):
        return 'xpath' in element.options and element.options['xpath']['xml'] == xpath
    
    @abstractmethod
    def set_XpathAccessor(self, request):
        """
            Method:
                Set values of siblings
            Input:
                http request
        """
        raise NotImplementedError("This method is not implemented.")  
    
    def get_XpathAccessor(self):
        return {'xpath_accessor': self.values}


class XPathAccessorError(Exception):
    """
        Exception raised by the siblings accessor system
    """
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)
