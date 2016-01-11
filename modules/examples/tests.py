import unittest

from modules.examples.models import PositiveIntegerInputModule
from django.http.request import HttpRequest
import json


class TestPositiveInteger(unittest.TestCase):
    def setUp(self):
        pass 
            
    def test(self):     
        module = PositiveIntegerInputModule()
        request = HttpRequest()
        
        request.method = 'GET'
        
        response = module.view(request)
        data = json.loads(response.content)
        self.assertNotEqual(len(data['module']), 0)
        self.assertEqual(data['moduleDisplay'], "1 is a valid positive integer")
        self.assertEqual(data['moduleResult'], 1)
        
        request.method = 'POST'
        request.POST['value'] = '4'
        
        response = module.view(request)  
        data = json.loads(response.content)      
        self.assertEqual(data['moduleDisplay'], "4 is a valid positive integer")
        self.assertEqual(data['moduleResult'], 4)
        
if __name__ == '__main__':
    unittest.main()
