import selenium
import os
import time
import sys
from http.cookies import SimpleCookie
import pickle
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import bs4

checkout_promo_code = None
user_password = "testing123"
price_threshold = 2


def create_link(_id):
    return f"https://amazon.com/dp/{_id}"


def get_url():
    url = None
    while 1:
        url = input("Please enter url of amazon page: ")
        if "amazon" not in url:
            print(
                "You have entered invalid url. Please try again (url must have amazon)"
            )
        else:
            return url


def get_info(filename="products.txt"):
    info = {}
    if not os.path.exists(filename):
        return info
    with open(filename, "r+") as f:
        for i in f:
            link, code = i.split(",")
            if link and code:
                info[link] = code
    return info


# url = get_url()
# checkout_promo_code = input("Please enter promo code: ")

# driver = webdriver.Chrome(r"C:\Users\user\Downloads\chromedriver.exe", options=options)


def search_text(source, text):
    soup = bs4.BeautifulSoup(source, "lxml")
    if text in soup.text:
        return True
    else:
        return False


def has_coupon(source):
    return search_text(source, "with coupon")


def is_coupon_already_applied(source):
    return search_text(source, "coupon applied")


def buy_products(driver):
    print(">>> Looking...")
    info = get_info()
    print("Running on: ")
    for link, checkout_promo_code in info.items():
        print("Buying product at: ", link)
        # Proceed to buy now page if coupon is already applied or is available
        driver.get(link)
        source = driver.page_source
        coupon_applied = is_coupon_already_applied(source)

        if not has_coupon(source) and not coupon_applied:  # Coupon not found; exiting
            print("Unable to find coupon at first page. Coupon not applied.")

        if not coupon_applied and has_coupon(source):  # Coupon is not already applied
            print("Applying Coupon...")
            driver.find_element_by_xpath(
                '//*[@id="checkBox"]/div/label/i'
            ).click()  # Apply coupon by ticking

        try:
            for i in driver.find_elements_by_id("add-to-cart-button"):
                i.click()

        except selenium.common.exceptions.ElementNotInteractableException:  # Freaking lightning deal at amazon; https://www.amazon.com/Vitamin-Hyaluronic-Wrinkles-Glowing-Younger/dp/B00KOUALMS
            for i in driver.find_elements_by_id("a-autoid-0-announce"):
                try:
                    i.click()
                except Exception as e:
                    continue

        driver.get("https://www.amazon.com/gp/cart/view.html?ref_=nav_cart")

        for i in driver.find_elements_by_name("proceedToRetailCheckout"):
            i.click()
            time.sleep(1)

        if "signin" in driver.current_url:  # Amazon verification check
            driver.find_element_by_id("ap_password").send_keys(user_password)
            driver.find_element_by_id("signInSubmit").click()

        time.sleep(2)
        soup = bs4.BeautifulSoup(driver.page_source, "lxml")
        price = soup.find(
            "td",
            class_="a-color-price a-size-medium a-text-right grand-total-price aok-nowrap a-text-bold a-nowrap",
        )

        time.sleep(2)
        old_price = ""
        if price:
            price = float(price.text.strip().replace("$", ""))
            old_price = price
        if checkout_promo_code:
            try:
                driver.find_element_by_id("spc-gcpromoinput").send_keys(
                    checkout_promo_code
                )
            except Exception as e:
                pass

        price = soup.find(
            "td",
            class_="a-color-price a-size-medium a-text-right grand-total-price aok-nowrap a-text-bold a-nowrap",
        )
        if price:
            price = float(price.text.strip().replace("$", ""))

        print(f"Should blacklist {price} == {old_price}: {price == old_price}")
        if price == old_price:

            with open("expired.txt", "a+") as f:
                f.seek(0)
                promos = set()
                for i in f:
                    link, code = i.split(",")
                    promos.add(code)
                if checkout_promo_code not in promos:
                    f.write(link + "," + checkout_promo_code)

        if price:
            print(f"Comparing threshold {price_threshold} with price {price}.")
            if price < price_threshold:
                time.sleep(2)
                try:
                    driver.find_element_by_name("placeYourOrder1").click()
                except selenium.common.exceptions.ElementClickInterceptedException:
                    return
        else:
            print("nothing")

        # Clearing cart
        driver.get(
            "https://www.amazon.com/gp/cart/view.html/ref=chk_cart_link_return_to_cart"
        )
        soup = bs4.BeautifulSoup(driver.page_source, "lxml")
        menu = soup.find(
            "div", class_="a-row a-spacing-mini sc-list-body sc-java-remote-feature"
        )

        if not menu:
            print("Continuing")
            continue

        for i in menu.findAll("span", class_="a-declarative"):
            if i.find("input"):
                if i.find("input").get("name"):
                    object_id = i.find("input").get("name")
                    if "delete" in object_id:
                        driver.find_element_by_name(object_id).click()
