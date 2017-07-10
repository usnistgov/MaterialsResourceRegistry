class MDCSError(Exception):
    """
        Exception raised by the MDCS
    """
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)


class XMLError(Exception):
    """
        Exception raised by XML validation
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class XSDError(Exception):
    """
        Exception raised by XSD validation
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
