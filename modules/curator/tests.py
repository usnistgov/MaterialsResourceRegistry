"""
"""
# from unittest import TestCase
import os
from time import sleep

# from os.path import join
# from selenium import webdriver
# from selenium.common.exceptions import NoSuchElementException
# from selenium.common.exceptions import NoAlertPresentException
from mgi.tests import SeleniumTestCase
# from mgi.settings import BASE_DIR
# from modules.discover import discover_modules


class EnumAutoCompleteModuleTestCase(SeleniumTestCase):
    """Test suite for the EnumAutoCompleteModule class
    """

    def setUp(self):
        super(EnumAutoCompleteModuleTestCase, self).setUp()

    def test_not_working_on_not_enum(self):
        """Test if adding the module on not enums is working

        :return:
        """
        pass

    def test_working_on_enum(self):
        """Test if adding the module on enums works

        :return:
        """
        pass

    def test_nothing_in_list(self):
        """Test if proposal is empty when input is not found in list

        :return:
        """
        pass

    def test_correct_list_size(self):
        """Test if list is displayed and of correct size when input is entered

        :return:
        """

        pass

    def test_error_selection_not_found(self):
        """Test validating the document with unexisting input selected

        :return:
        """

        pass

    def test_reload_working(self):
        """Test save and reload a document

        :return:
        """

        pass

    def test_upload_working(self):
        """Test download and upload a document

        :return:
        """

        pass

    def test_choice_switch(self):
        pass

    def test_multiple_autocomplete(self):
        pass

    # def test_excel_uploader(self):
    #     driver = self.driver
    #     select_url = self.base_url + self.pages["select"]
    #
    #     select_template(driver, select_url, self.template)
    #     create_new_document(driver, self.template)
    #
    #     driver.find_element_by_xpath("//li[@id='element1']/div/div/div/div").click()
    #     sleep(0.2)
    #
    #     driver.find_element_by_id("id_file").clear()
    #     driver.find_element_by_id("id_file").send_keys(os.path.join(TESTS_RESOURCES_PATH, "data", "xls",
    #                                                                 "sample_table_module.xlsx"))
    #
    #     driver.find_element_by_xpath("(//button[@type='button'])[2]").click()
    #     sleep(1)
    #
    #     filename = driver.find_element_by_xpath("//li[@id='element1']//div[@class='moduleDisplay']/div[1]/p[1]").text
    #     print filename
    #     self.assertIn("sample_table_module.xlsx", filename)
    #
    #     filehandle = driver.find_element_by_xpath("//li[@id='element1']//div[@class='moduleDisplay']/div[1]/p[2]")
        # .text
    #     print filehandle
    #     self.assertIn("rest/get-blob?id", filehandle)
    #
    #     driver.find_element_by_xpath("(//a[contains(text(),'View Data')])[2]").click()
    #
    #     sleep(5)
    #
    # def is_element_present(self, how, what):
    #     try:
    #         self.driver.find_element(by=how, value=what)
    #     except NoSuchElementException, e:
    #         return False
    #     return True
    #
    # def is_alert_present(self):
    #     try: self.driver.switch_to_alert()
    #     except NoAlertPresentException, e: return False
    #     return True
    #
    # def close_alert_and_get_its_text(self):
    #     try:
    #         alert = self.driver.switch_to_alert()
    #         alert_text = alert.text
    #         if self.accept_next_alert:
    #             alert.accept()
    #         else:
    #             alert.dismiss()
    #         return alert_text
    #     finally: self.accept_next_alert = True
    #
    # def tearDown(self):
    #     self.driver.quit()
    #     self.assertEqual([], self.verificationErrors)
    #
    #     # Clean the database
    #     clean_db()
