from flask import Flask, render_template, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Flask app initialization
app = Flask(__name__)

# Chrome options for WebDriver
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument('--allow-insecure-localhost')

# Define the route for the homepage
@app.route('/')
def index():
    return render_template('complete.html')

# Route to handle the form submission
@app.route('/run', methods=['POST'])
def run():
    url = request.form.get('url')
    cycles = int(request.form.get('cycles'))

    # Initialize WebDriver with ChromeDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 10)

    def click_ads():
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframes:
                try:
                    driver.switch_to.frame(iframe)
                    ad = driver.find_element(By.TAG_NAME, 'a')
                    if ad.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView();", ad)
                        driver.execute_script("arguments[0].click();", ad)
                        time.sleep(5)
                except NoSuchElementException:
                    pass
                finally:
                    driver.switch_to.default_content()
        except TimeoutException:
            print("Page load timed out.")

    # Perform the ad-clicking loop
    for i in range(cycles):
        try:
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url)
            click_ads()
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except WebDriverException as e:
            print(f"Error during iteration {i+1}: {e}")
            break

    driver.quit()
    return redirect(url_for('index'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
