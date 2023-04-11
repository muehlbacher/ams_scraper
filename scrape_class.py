from seleniumwire import webdriver
import zlib
import json
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time


class AMS_JOBS:
    def __init__(self, url: str, filename: str):
        self.actual_page = 1
        # self.results = []
        # self.total_results
        self.total_pages = 0
        self.url = url
        self.data = []
        self.options = webdriver.ChromeOptions()
        # call in background
        self.options.add_argument("--headless")
        self.driver = 0
        self.timeout = 5
        self.filename = filename

    def split_url(self):
        url_split = self.url.split("?")
        self.base_url = url_split[0]
        self.query = url_split[1].split("query")[1]

    def save_data_to_json(self):
        # writing data to json
        file_name = self.filename
        with open(file_name, "w") as f:
            f.write("[")
            f.write(",".join(self.data))
            f.write("]")
            print("PAGE SUCCESSFULLY SCRAPED. DATA CAN BE FOUND IN THE SAME FOLDER.")
            print(f"Data saved in {file_name}...")

    def transform_data_to_json(self, decompressed_data):
        # from b'{...} to {...}
        data = str(decompressed_data, "utf-8")
        # makes an [{..}, {...}] ready to be saved as json
        self.data.append(data)

    def intercept_api_call(self, requests) -> str:
        for request in requests:
            # check if this is the right url (api call)
            if "api/search?" in request.url:

                #print("intercepted call")
                #print(request.url)
                # get the data from the api
                # b'{...} binary data
                #time.sleep(5)

                try: 
                    decompressed_data = zlib.decompress(
                        request.response.body, 16 + zlib.MAX_WBITS
                    )
                except AttributeError:
                    #print(request.response.body)
                    #print("Wait...")
                    #time.sleep(5)
                    #decompressed_data = zlib.decompress(
                    #    request.response.body, 16 + zlib.MAX_WBITS
                    #)
                    pass

                self.transform_data_to_json(decompressed_data)

    def check_for_api_string(self, driver):
        print("Wait for api to be loaded")
        for request in driver.requests:
            if "api/search?" in request.url:
                print("Request URL")
                #print(request.url)
                if not isinstance(request.response, type(None)):
                    return True
        return False

    def create_page_url(self, page_number: int) -> str:
        page_url = self.base_url + "?page=" + str(page_number) + "&query" + self.query
        return page_url

    def create_connection_and_wait_for_load(self, page_url):
        self.driver = webdriver.Chrome(options=self.options)
        driver = self.driver
        # call the driver get and wait for the api to be loaded
        try:
            self.driver.get(page_url)
            WebDriverWait(driver, self.timeout).until(self.check_for_api_string)
            
        except TimeoutException:
            print("Timeout: Page is called again...")
            self.driver.get(page_url)
            WebDriverWait(driver, self.timeout).until(self.check_for_api_string)

        return self.driver

    def get_total_pages(self):
        try:
            # {..} dictionary format -> needd to make dict calls possible
            data_dict = json.loads(self.data[-1])
            self.total_pages = data_dict["totalPages"]
        except:
            print("No Data to get Total Page!")

    def first_call_for_total_pages(self):
        self.create_connection_and_wait_for_load(self.url)
        self.intercept_api_call(self.driver.requests)
        self.get_total_pages()
        self.driver.quit()
        self.data = []

    def scrape(self):
        # Create the webdriver object and pass the arguments
        self.split_url()
        print("URL:")
        print(self.url)

        # first api call, to get the total pages for the loop
        self.first_call_for_total_pages()

        print(f"Total Pages: {self.total_pages}")

        for page in range(1, self.total_pages + 1):
            self.page_url = self.create_page_url(page)
            print(f"Scraping page {page}")

            # create new connection
            driver = self.create_connection_and_wait_for_load(self.page_url)

            self.intercept_api_call(driver.requests)

            # quit after stuff done
            driver.quit()

        self.save_data_to_json()
