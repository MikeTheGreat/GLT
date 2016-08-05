"""Testing the PyUnit / Selenium (WebDriver for Chrome) integration"""
import unittest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

class TestSelenium(unittest.TestCase):
    """"Apparently PyUnit looks for classes that inherit from TestCase """

    def test_chrome(self):
        """Can I get chrome to work via WebDriver?"""

        # Create a new instance of the Chrome driver
        driver = webdriver.Chrome()

        # go to the google home page
        driver.get("http://www.google.com")

        # the page is ajaxy so the title is originally this:
        print driver.title

        # find the element that's name attribute is q (the google search box)
        input_element = driver.find_element_by_name("q")

        # type in the search
        input_element.send_keys("cheese!")

        # submit the form (although google automatically searches now without submitting)
        input_element.submit()

        try:
            # we have to wait for the page to refresh, the last thing that seems
            # to be updated is the title
            WebDriverWait(driver, 10).until(EC.title_contains("cheese!"))

            # You should see "cheese! - Google Search"
            print driver.title

            if driver.title != "cheese! - Google Search":
                self.fail()

        finally:
            driver.quit()

if __name__ == '__main__':
    unittest.main()
