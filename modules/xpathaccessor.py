from mgi.models import FormData, FormElement
from abc import ABCMeta, abstractmethod

class XPathAccessor():
    
    __metaclass__ = ABCMeta
    
    def __init__(self, request):
        try:
            # get id of form data
            self._form_data_id = request.session['curateFormData']
            # get the form data
            form_data = FormData.objects().get(pk=self._form_data_id) 
            # get the html id of the module
            html_id = request.POST['htmlId']
            # get the id (mongo) of the form element at this id (html)
            form_element_id = form_data.elements[html_id]
            # get the form element from db
            form_element = FormElement.objects().get(pk=form_element_id)
            # get xml xpath of the element
            self.xpath = form_element.xml_xpath
            self.values = {}
            self.set_XpathAccessor(request)
        except:
            raise XPathAccessorError('Unable to get form data information. Please check session is still valid and that HTTP request is correctly sent to the Siblings Accessor system.')


    def get_xpath(self):
        return self.xpath
        

    def set_xpath_value(self, xpath, value):        
        form_element = self._get_element(xpath)
        html_id = form_element.html_id
        if xpath in self.values.keys():
            raise XPathAccessorError('Same XPath set more than once.')
        else:
            self.values[html_id] = value

    
    def _get_element(self, xpath):
        if self.xpath != xpath:
            # get data about the current form
            form_data = FormData.objects().get(pk=self._form_data_id)
            # get all elements from the current form
            form_elements = FormElement.objects.filter(id__in=form_data.elements.values())          
            # check if the provided xpath is one of an element of the current form
            if xpath in form_elements.values_list('xml_xpath'):
                return form_elements.get(xml_xpath=xpath)
            else:
                raise XPathAccessorError('No element found for the given xpath.')
        else:
            raise XPathAccessorError('Xpath provided is the same as reference element.')
    
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
