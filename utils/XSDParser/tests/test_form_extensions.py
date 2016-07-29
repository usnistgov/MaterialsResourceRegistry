from selenium import webdriver
import time
from mgi.tests import SeleniumTestCase

from mgi.settings import BASE_DIR
from os.path import join
from os import listdir, remove
import os

from mgi.models import create_template
from lxml import etree
from mgi.tests import are_equals
from pymongo import MongoClient
from mgi.settings import MONGODB_URI
from pymongo.errors import OperationFailure

RESOURCES_PATH = join(BASE_DIR, 'utils', 'XSDParser', 'tests', 'data', 'parser', 'extension', 'explicit-implicit')
USER = "admin"
PASSWORD = "admin"
BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 5


def clean_db():
    # create a connection
    client = MongoClient(MONGODB_URI)
    # connect to the db 'mgi'
    db = client['mgi_test']
    # clear all collections
    for collection in db.collection_names():
        try:
            if collection != 'system.indexes':
                db.drop_collection(collection)
        except OperationFailure:
            pass


def login(driver, base_url, user, password):
    driver.get("{0}/{1}".format(base_url, "login"))
    driver.find_element_by_id("id_username").clear()
    driver.find_element_by_id("id_username").send_keys(user)
    driver.find_element_by_id("id_password").clear()
    driver.find_element_by_id("id_password").send_keys(password)
    driver.find_element_by_css_selector("button.btn").click()
    time.sleep(TIMEOUT)


def load_new_form(driver, base_url, form_name):
    driver.get("{0}/{1}".format(base_url, "curate"))
    driver.find_element_by_css_selector("button.btn.set-template").click()
    time.sleep(TIMEOUT)
    driver.find_element_by_name("curate_form").click()
    driver.find_element_by_id("id_document_name").clear()
    driver.find_element_by_id("id_document_name").send_keys(form_name)
    time.sleep(TIMEOUT)
    driver.find_element_by_xpath("(//button[@type='button'])[2]").click()


def upload_xml_form(driver, base_url, form_path):
    driver.get("{0}/{1}".format(base_url, "curate"))
    driver.find_element_by_css_selector("button.btn.set-template").click()
    time.sleep(TIMEOUT)
    driver.find_element_by_xpath("(//input[@name='curate_form'])[3]").click()
    driver.find_element_by_id("id_file").clear()
    driver.find_element_by_id("id_file").send_keys(form_path)
    time.sleep(TIMEOUT)
    driver.find_element_by_xpath("(//button[@type='button'])[2]").click()


class LoadExtensionToXML(SeleniumTestCase):
    """
    """
    def setUp(self):
        # clean mongo db collections
        clean_db()

        self.resources_path = RESOURCES_PATH
        self.results_path = join(RESOURCES_PATH, 'results')

        try:
            # remove all result files if there are some
            for filename in listdir(self.results_path):
                remove(join(self.results_path, filename))
        except:
            pass

        # setup Selenium

        # define profile for custom download
        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.dir', self.results_path)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/xml')

        # define Firefox web driver
        self.driver = webdriver.Firefox(profile)
        self.driver.implicitly_wait(10)
        self.base_url = BASE_URL
        self.verificationErrors = []
        self.accept_next_alert = True

        # login to MDCS
        login(self.driver, self.base_url, USER, PASSWORD)

    def test(self):
        errors = []
        try:
            # get all the files in the directory
            for filename in listdir(self.resources_path):
                # clean mongo db collections
                clean_db()
                if filename.endswith('.xsd'):
                    # print 'TESTING: {}'.format(filename)
                    file_id = filename.split('.')[0]
                    try:
                        self.add_template(file_id)
                        self.blank(file_id)
                    except Exception, e:
                        print e
                        errors.append(str(e.message))
                    i = 1
                    while i <= 2:
                        try:
                            self.reload(file_id, str(i))
                        except Exception, e:
                            print e
                            errors.append(str(e.message))
                        i += 1

        except Exception, e:
            errors.append(str(e.message))

        if len(errors) > 0:
            self.fail()

    def add_template(self, file_id):
        filename = '{}.xsd'.format(file_id)

        # load XSD
        xsd_file_path = join(self.resources_path, filename)
        xsd_file = open(xsd_file_path, 'r')
        xsd_file_content = xsd_file.read()

        # create template
        template = create_template(xsd_file_content, filename, filename)

    def blank(self, file_id):
        # load the form
        load_new_form(self.driver, self.base_url, file_id)
        time.sleep(TIMEOUT)
        # download XML
        self.driver.execute_script("downloadCurrentXML();")

        # wait a bit more to let time to save the file
        time.sleep(TIMEOUT * 5)

        # load expected result
        exp_result_path = join(self.resources_path, "{0}.xml".format(file_id))
        exp_result_file = open(exp_result_path, 'r')
        exp_result_content = exp_result_file.read()

        # load result generated by the form
        result_path = join(self.results_path, "{0}.xml".format(file_id))
        result_file = open(result_path, 'r')
        result_content = result_file.read()

        expected = etree.fromstring(exp_result_content)
        result = etree.fromstring(result_content)

        if not are_equals(expected, result):
            raise Exception(str(file_id))

    def reload(self, file_id, reload_id):
        file_name = '{0}-reload{1}.xml'.format(file_id, str(reload_id))
        file_path = os.path.join(RESOURCES_PATH, file_name)
        if os.path.exists(file_path):
            # load the form
            upload_xml_form(self.driver, self.base_url, file_path)
            time.sleep(TIMEOUT)
            # download XML
            self.driver.execute_script("downloadCurrentXML();")

            # wait a bit more to let time to save the file
            time.sleep(TIMEOUT * 5)

            # load expected result
            exp_result_path = join(self.resources_path, file_name)
            exp_result_file = open(exp_result_path, 'r')
            exp_result_content = exp_result_file.read()

            # load result generated by the form
            result_path = join(self.results_path, "{}.xml".format(file_name))
            result_file = open(result_path, 'r')
            result_content = result_file.read()

            expected = etree.fromstring(exp_result_content)
            result = etree.fromstring(result_content)

            if not are_equals(expected, result):
                raise Exception(file_name)
