################################################################################
#
# File Name: tests.py
# Application: compose
# Purpose:
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
import json

import requests
from mgi.models import create_template, XMLdata
from os.path import join
import os
from django.utils.importlib import import_module
from testing.models import RegressionTest

settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)

RESOURCES_PATH = join(settings.BASE_DIR, 'api', 'tests', 'data')
USER = 'admin'
PWD = 'admin'


def load_template(template_path):
    """
    Load the template to search on
    :param template_path:
    :return:
    """
    # Open the the file
    with open(template_path, 'r') as template_file:
        # read the file content
        template_content = template_file.read()
        return create_template(template_content, template_path, template_path)


def load_data(data_path, template_id):
    """
    Load the data to search
    :param data_path:
    :param template_id
    :return:
    """
    # Open the the file
    with open(data_path, 'r') as data_file:
        # read the file content
        data_content = data_file.read()
        # add the type in database
        XMLdata(template_id, xml=data_content).save()


class ApiEvalSuite(RegressionTest):
    """
    Test suite for the Api application
    """

    def setUp(self):
        # call parent setUp
        super(ApiEvalSuite, self).setUp()
        # add a template
        template = load_template(join(RESOURCES_PATH, 'schema.xsd'))
        # load data
        load_data(join(RESOURCES_PATH, '1.xml'), str(template.id))
        load_data(join(RESOURCES_PATH, '2.xml'), str(template.id))
        load_data(join(RESOURCES_PATH, '3.xml'), str(template.id))

    def test_qbe(self):
        payload = {'query': '{"content.root.integer": 1}'}
        response = requests.post(settings.MDCS_URI + "/rest/explore/query-by-example", data=payload, auth=(USER, PWD))
        self.assertTrue(response.status_code == 200)
        payload = {'query': '{"content.root.str": "test1"}'}
        response = requests.post(settings.MDCS_URI + "/rest/explore/query-by-example", data=payload, auth=(USER, PWD))
        self.assertTrue(response.status_code == 200)

    def test_add_template(self):
        with open(join(RESOURCES_PATH, 'schema.xsd'), 'r') as data_file:
            data_content = data_file.read()
            payload = {"title": "title",
                       "filename": "filename",
                       "content": data_content}

        response = requests.post(settings.MDCS_URI + "/rest/templates/add", data=payload, auth=(USER, PWD))
        self.assertTrue(response.status_code == 201)

    def test_add_type(self):
        with open(join(RESOURCES_PATH, 'type.xsd'), 'r') as data_file:
            data_content = data_file.read()
            payload = {"title": "title",
                       "filename": "filename",
                       "content": data_content}

        response = requests.post(settings.MDCS_URI + "/rest/types/add", data=payload, auth=(USER, PWD))
        self.assertTrue(response.status_code == 201)

    def test_add_repo(self):
        response = '{"access_token": "token", "token_type": "Bearer", "expires_in": 31536000, "refresh_token": "refresh_token", "scope": "read write"}'
        access_token = json.loads(response)["access_token"]
        refresh_token = json.loads(response)["refresh_token"]
        seconds = int(json.loads(response)["expires_in"])
