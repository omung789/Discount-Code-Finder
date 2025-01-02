import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip

# Get the company name from the user
confirm = False
while not confirm:
    company_name = input("Enter the company name: ")
    confirm = input(f"Is {company_name} the correct company name? (y/n): ").lower() == 'y'

# Set up the WebDriver (can specify path to chromedriver if not in PATH)

driver = webdriver.Chrome()

# Open the webpage
driver.get('https://www.vouchercodes.co.uk/')

#reject cookies
try:
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
    ).click()
except Exception:
    print("No cookies popup found.")

# type company name into search bar and press enter
input_field = driver.find_element(By.ID, 'appSearchPlaceholderInput')
input_field.send_keys(company_name)
input_field.send_keys(Keys.RETURN)

#wait for all buttons to be loaded then obtain list of all buttons that can be clicked
time.sleep(1)
articles = driver.find_elements(By.CSS_SELECTOR, "article[data-qa]") 

#may change to set if we use multiple websites to avoid duplicates
codes = []
print(f"Found {len(articles)} articles")

for i in range(len(articles)):
    data_qa = articles[i].get_attribute("data-qa")
    
    #only want to click buttons that will give us a discount code
    if "offerType:code" in data_qa:
        print(f"Clicking on article with ID: {articles[i].get_attribute('id')}")
        clickable_element = articles[i].find_element(By.CSS_SELECTOR, "button, a")
        clickable_element.click()
        #change tab
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[1])

        #copy discount code to clipboard
        time.sleep(1)
        button = driver.find_element(By.CSS_SELECTOR, "button[data-qa='el:copyCode copied:false'][aria-disabled='false']")
        button.click()


        codes.append(pyperclip.paste())

        #close tab and go back to original tab
        driver.close()
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[0])
        driver.back()

        #refresh list as when we go back to the page the elements have refreshed
        time.sleep(1)
        articles = driver.find_elements(By.CSS_SELECTOR, "article[data-qa]")
        print(f"Found {len(articles)} articles")

driver.get('https://www.myvouchercodes.co.uk/')

def reject_cookies():
    try:
        iframe = driver.find_element(By.ID, "sp_message_iframe_1182714")
        driver.switch_to.frame(iframe)
    except Exception:
        return

    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='More options']"))
        ).click()
    except Exception:
        print("No cookies popup found.")
        return

    driver.switch_to.default_content()

    iframe = driver.find_element(By.ID, "sp_message_iframe_775038")
    driver.switch_to.frame(iframe)


    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='REJECT ALL']"))
    ).click()


reject_cookies()

driver.switch_to.default_content()
input_field = driver.find_element(By.ID, 'js-home-search-input')
input_field.send_keys(company_name)
input_field.send_keys(Keys.RETURN)

time.sleep(1)
reject_cookies()

buttons = driver.find_elements(By.CLASS_NAME, "Shared_wrapper__N81Gq")
print(f"Found {len(buttons)} buttons on the page.")
# Print and store the buttons
for i in range(len(buttons)):
    button = buttons[i]
    if button.text[0:8] == "Get code":
        #find the button location and scroll to it
        button_location = button.location['y']
        driver.execute_script(f"window.scrollTo(0, {button_location - 200});")
        time.sleep(0.5) #wait for the page to scroll - DO NOT REMOVE
        button.click()

        #change tab
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[1])
    
        time.sleep(1)

        #remove overlay that blocks the copy button
        driver.execute_script("""
            var element = document.querySelector('div.ModalContainer_overlay__cDdHc');
            if (element) {
                element.remove();
            }
        """)

        # need to access the overlay element to click the copy button
        overlay = driver.find_element(By.CLASS_NAME, "ModalContainer_modal__HIQCd")

        WebDriverWait(overlay, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "CopyToClipboardButton_ctaCopy__njuJB"))
        ).click()

        codes.append(pyperclip.paste())

        #close tab and go back to original tab
        driver.close()
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[0])
        driver.back()
        time.sleep(1)

driver.quit()

codes = list(set(codes))
print(codes)
file_name = company_name + "_discount_codes.txt"
with open(file_name, "w") as f:
    for code in codes:
        f.write(code + "\n")
