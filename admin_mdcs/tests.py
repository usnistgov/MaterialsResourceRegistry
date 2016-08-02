################################################################################
#
# File Name: tests.py
# Application: admin_mdcs
# Purpose:
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from testing.models import TokenTest
from mgi.models import Instance
from admin_mdcs.views import update_instance, create_instance
from bson.objectid import ObjectId
from datetime import datetime

class tests_token(TokenTest):

    def test_add_repository_get(self):
        r = self.doRequestGetAdminClientLogged(url="/admin/repositories/add-repository")
        self.assertIsNotNone(r.context[1].get('form'))

    def test_create_instance(self):
        self.assertEquals(0, len(Instance.objects()))
        data = {'name': 'test',
                'protocol': 'http',
                'ip_address': '127.0.0.1',
                'port': 8082,
                'username': 'admin',
                'password': 'admin',
                'client_id': 'client_id',
                'client_secret': 'client_secret',
                'timeout': 12,
                'action': 'Ping'
                }
        response = '{"access_token": "token", "token_type": "Bearer", "expires_in": 31536000, "refresh_token": "refresh_token", "scope": "read write"}'
        create_instance(content=response, request=data)
        self.assertEquals(1, len(Instance.objects()))

    def test_add_repository_post_ping(self):
        data = {'name':'test',
                'protocol': 'http',
                'ip_address': '127.0.0.1',
                'port': 8082,
                'username': 'admin',
                'password':'admin',
                'client_id':'client_id',
                'client_secret':'client_secret',
                'timeout':12,
                'action': 'Ping'

                }
        r = self.doRequestPostAdminClientLogged(url="/admin/repositories/add-repository", data=data)
        self.assertIsNotNone(r.context[1].get('form'))
        self.assertEquals('Remote API reached with success.', r.context[1].get('action_result'))

    def test_add_repository_post_ping_exception(self):
        data = {'name': 'testtest',
                'protocol': 'http',
                'ip_address': '0.0.0.1',
                'port': 8082,
                'username': 'admin',
                'password': 'admin',
                'client_id': 'c',
                'client_secret': 'c',
                'timeout': 1,
                'action': 'Ping'

                }
        r = self.doRequestPostAdminClientLogged(url="/admin/repositories/add-repository", data=data)
        self.assertIsNotNone(r.context[1].get('form'))
        self.assertEquals('Error: Unable to reach the remote API.', r.context[1].get('action_result'))

    def test_add_repository_post_ping_error(self):
        data = {'name': 'testtest',
                'protocol': 'http',
                'ip_address': '0.0.0.0',
                'port': 8082,
                'username': 'a',
                'password': 'a',
                'client_id': 'c',
                'client_secret': 'c',
                'timeout': 1,
                'action': 'Ping'
                }
        r = self.doRequestPostAdminClientLogged(url="/admin/repositories/add-repository", data=data)
        self.assertIsNotNone(r.context[1].get('form'))
        self.assertEquals('Error: Invalid username/password', r.context[1].get('action_result'))

    def test_update_instance(self):
        instance = Instance(name='testtest', protocol='h', address='a',
                 port=12, access_token='a',
                 refresh_token='a', expires=datetime.now()).save()
        response = '{"access_token": "token", "token_type": "Bearer", "expires_in": 31536000, "refresh_token": "refresh_token", "scope": "read write"}'
        update_instance(instance=instance, content=response)
        instance_updated = Instance.objects.get(pk=ObjectId(instance.id))
        self.assertIsNotNone(instance_updated)
        self.assertEquals(instance_updated.access_token, "token")
        self.assertEquals(instance_updated.refresh_token, "refresh_token")
        self.assertNotEqual(instance_updated.expires, instance.expires)


