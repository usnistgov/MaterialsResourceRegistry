class ModuleError(Exception):
    """
        Exception raised by module system
    """
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)
