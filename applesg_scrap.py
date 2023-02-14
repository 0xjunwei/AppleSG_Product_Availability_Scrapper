from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from telegram import Bot
import asyncio


async def main():
    # Slot in ur own BOT API Key
    bot = Bot("<OWN API KEY>")
    # Get ur chatID by going to @RawDataBot and clicking start under the CHAT parameter you will see id
    chat_id = "<CHAT ID>"
    # Example URL BELOW please change accordingly
    url = "https://www.apple.com/sg/shop/buy-mac/macbook-pro/13-inch-space-grey-apple-m2-chip-with-8-core-cpu-and-10-core-gpu-256gb"  # adjust URL as needed
    
    telegram_message_to_send = url + "\n\n"
    driver = webdriver.Firefox()  # adjust to use your preferred web driver
    driver.get(url)

    wait = WebDriverWait(driver, 5)  # adjust wait time as needed
    if "iphone" in url:
        try:
            applecare_option = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "applecareplus_58_noapplecare"))
            )
            driver.execute_script("arguments[0].click();", applecare_option)

            print("No AppleCare+ coverage selected")
        except Exception:
            pass

    pickup_availability = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.rf-pickup-quote-value"))).text
    print(f"Pickup availability: {pickup_availability}")

    if pickup_availability != "Apple Store Pickup is currently unavailable":
        print("Product is available")
        check_availability_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.rf-pickup-quote-overlay-trigger")))
        check_availability_button.click()

        zip_code_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-autom=zipCode]")))
        zip_code_input.clear()
        zip_code_input.send_keys("018972")  # replace with your desired ZIP code
        # Simulate enter key if iphone based search
        if "iphone" in url:
            # simulate pressing the "Enter" key
            zip_code_input.send_keys(Keys.RETURN)
        else:
            search_button = driver.find_element(By.CSS_SELECTOR, "button.rf-storelocator-searchbutton")
            search_button.click()
        
        
        # Get the store location and availability information for each search result

        if "iphone" in url:
            # Wait for the element to be present and displayed
            wait = WebDriverWait(driver, 2)
            store_options = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'li.rf-productlocator-storeoption')))

            for store_option in store_options:
                # Get the store name
                try:
                    # Get the store name
                    store_name = store_option.find_element(By.CSS_SELECTOR, "span.form-selector-title").text

                except:
                    store_name = "N/A"

                # Get the store availability
                try:
                    store_availability = store_option.find_element(By.CSS_SELECTOR, "span.form-selector-right-col > span").text
                except:
                    store_availability = "N/A"
                    
                print(store_name)
                print(store_availability)
                telegram_message_to_send += "Location: " + store_name + " is " + store_availability + " \n"

        else:
            # handle the results in the popup window as needed
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.rf-storelocator-searchresult-list")))
            time.sleep(1)
            search_results = driver.find_elements(By.CSS_SELECTOR, "li.rf-storelocator-storeoption")
            for result in search_results:
                store_location = result.find_element(By.CSS_SELECTOR, "span.form-selector-title").text
                availability_info = result.find_element(By.CSS_SELECTOR, "span.rf-storelocator-storeitem-availabilityinfo span").text
                telegram_message_to_send += "Location: " + store_location + " is " + availability_info + " \n"
                print(store_location, availability_info)
            
        await bot.send_message(chat_id=chat_id, text=telegram_message_to_send)


    else:
        print("Product is unavailable")

    driver.quit()

if __name__ == '__main__':
    asyncio.run(main())
