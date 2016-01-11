class MDCSError(Exception):
    """
        Exception raised by the MDCS
    """
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)
