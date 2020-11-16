import selenium
import time
import re
from selenium import webdriver
import bs4
from selenium.webdriver.chrome.options import Options
import utils
import requests

# import amzn


class Browser:
    def __init__(self, profile_path, driver_path):
        self.profile_path = profile_path
        self.chrome_driver_path = driver_path
        self.options = Options()
        self.options.add_argument(f"user-data-dir={self.profile_path}")
        self.options.add_argument("--start-maximized")
        self.linux_platform = utils.is_linux_platform()

    def mount_browser(self):
        return webdriver.Firefox()

    # def mount_browser(self):
    #     try:
    #         if self.linux_platform:
    #             browser = webdriver.Chrome(options=self.options)
    #         else:
    #             browser = webdriver.Chrome(
    #                 self.chrome_driver_path, options=self.options
    #             )
    #         return browser
    #     except selenium.common.exceptions.InvalidArgumentException:
    #         print("Relaunching")
    #         # Kill the browser and relaunch it.
    #         command = "chrome"
    #         if not self.linux_platform:
    #             command += ".exe"
    #         utils.kill_process(command)
    #         return self.mount_browser()

    def __str__(self):
        return f"Browser at <{self.chrome_driver_path}>"

    __repr__ = __str__


def create_browser():
    browser = Browser(
        profile_path=utils.get_profile_path, driver_path=utils.get_driver_path()
    )
    return browser.mount_browser()  # Launch browser


class Product:
    def __init__(self, link, code):
        self.link = link
        self.code = code

    def get(self):
        if self.link and self.code:
            return f"{self.link}, {self.code}\n"
        return ""

    def __equals__(self, a):
        if self.code == a.code:
            return True
        return False


class FacebookGroupScraper:
    search_keys = (
        "auto",
        "kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql ii04i59q",
        "du4w35lb k4urcfbm l9j0dhe7 sjgh65i0",
        "j83agx80 cbu4d94t",
        "j83agx80 l9j0dhe7 k4urcfbm",
        "rq0escxv l9j0dhe7 du4w35lb",
    )

    def __init__(
        self,
        url="https://facebook.com/groups/kickassdealaddicts/?sorting_setting=CHRONOLOGICAL",
    ):
        self.url = url
        self.browser = create_browser()
        self.products = []
        self.fetch_limit = 2

    def open_url(self):
        self.browser.get(self.url)

    def set_products_limit(self, limit):
        self.fetch_limit = limit

    def scroll_page(self, number_of_times=9, wait=1):
        for _ in range(number_of_times):
            self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(wait)

    def is_product_free(self, text):
        return "free" in text.lower()

    def get_promo_codes(self, only_free=False):
        self.open_url()
        self.scroll_page()
        soup = bs4.BeautifulSoup(self.browser.page_source, "lxml")
        for key in self.search_keys:

            if len(self.products) >= self.fetch_limit:
                print("Products Fetched.")
                break

            for i in soup.findAll("div", class_=key):
                if len(self.products) >= self.fetch_limit:
                    print("Products Fetched.")
                    break

                text = re.sub(" +", " ", i.text.replace("\n", " "))

                if only_free:
                    if not self.is_product_free(text.lower()):
                        print("Found product is not free.")
                        continue

                pattern = re.search(r"(CODE|code|Code):?\s*(?P<promo>\w{8})", text)

                if not pattern:
                    print("Nothing found in", text[:40])

                if pattern:
                    post_link = [
                        i.get("href").split("?")[0]
                        for i in soup.findAll("a")
                        if i.get("href") and "permalink" in i.get("href")
                    ][0]

                    j = i.findAll("a")
                    product_link = ""
                    for elem in j:
                        link = re.sub(" +", " ", elem.text.replace("\n", " "))
                        if link.startswith("http"):
                            product_link = link
                            break

                    if not product_link:
                        link_pattern = re.search(r"https?://amzn.to/\w+", text)
                        if link_pattern:
                            product_link = link_pattern.group()

                    product_link = product_link.strip()

                    try:
                        code = pattern.group("promo")
                        if not bool(re.search(r"\d", code)):
                            return
                        print(f"Found code: {code} at {post_link}")
                    except IndexError:
                        print(pattern.group())

                    if product_link and code:
                        if "bit.ly" in product_link.strip():
                            r = requests.get(product_link.strip())
                            if not "amzn" in r.url or not "amazon" in r.url:
                                print("Skipping ", product_link.strip(), r.url)
                                continue

                        self.products.append(
                            Product(product_link.strip(), code.strip())
                        )
        return self.products


def main():

    fb_fetcher = FacebookGroupScraper()
    for i in fb_fetcher.get_promo_codes():
        print(i.get())

    # products = products[:products_to_fetch]
    # print("Found products: ", len(products))

    # if os.path.exists("products.txt"):
    #     with open("products.txt", "r+") as f:
    #         f.seek(0)
    #         products_cache = []
    #         for i in [i.strip() for i in list(set(f.readlines()))]:
    #             print("Read from file: ", i)
    #             link, code = i.split(",")
    #             products_cache.append(code.strip())

    #         for i in products:
    #             if i.code.strip() not in products_cache:
    #                 f.write(i.get())

    # else:
    #     with open("products.txt", "w+") as f:
    #         _products = [i.code for i in products]
    #         products = [i for i in products if i.code not in _products]
    #         for i in products:
    #             print(i.get())
    #             f.write(i.get())

    # if os.path.exists("expired.txt"):
    #     with open("expired.txt", "r") as f:
    #         f.seek(0)
    #         promos = set()
    #         print("READING EXPIRED FILE...")
    #         for i in f:
    #             link, code = i.split(",")
    #             products = [i for i in products if i.code.strip() != code.strip()]

    # print("Buying products: ", len(products))
    # # amzn.buy_products(browser)
    # print("Waiting")
    # time.sleep(5)


main()
