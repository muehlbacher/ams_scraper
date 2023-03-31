from seleniumwire import webdriver
import zlib
import json
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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
            print(f"Data saved in {file_name}...")

    def transform_data_to_json(self):
        # from b'{...} to {...}
        data = str(self.decompressed_data, "utf-8")
        # makes an [{..}, {...}] ready to be saved as json
        self.data.append(data)

    def intercept_api_call(self, requests) -> str:
        for request in requests:
            # check if this is the right url (api call)
            if "api/search?" in request.url:
                print("intercepted call")
                print(request.url)
                # get the data from the api
                # b'{...} binary data
                self.decompressed_data = zlib.decompress(
                    request.response.body, 16 + zlib.MAX_WBITS
                )
                self.transform_data_to_json()

    def check_for_api_string(self, driver):
        print("Wait for api to be loaded")
        for request in driver.requests:
            if "api/search?" in request.url:
                return True
        return False

    def create_page_url(self, page_number: int) -> str:
        page_url = self.base_url + "?page=" + str(page_number) + "&query" + self.query
        return page_url

    def create_connection_and_wait_for_load(self, page_url):
        self.driver = webdriver.Chrome(options=self.options)

        # call the driver get and wait for the api to be loaded
        self.driver.get(page_url)
        WebDriverWait(self.driver, self.timeout).until(self.check_for_api_string)

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
            print(f"Scraping page {page}")

            # create new connection
            self.create_connection_and_wait_for_load(self.create_page_url(page))

            self.intercept_api_call(self.driver.requests)

            # quit after stuff done
            self.driver.quit()

        self.save_data_to_json()
