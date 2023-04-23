from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import time
import pickle
import json
import sys
import msvcrt



def read_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if not config_data["username"]:
                print("錯誤:帳號為空\n按任意鍵以繼續...")
                msvcrt.getch().decode()
                sys.exit()
            if not config_data["password"]:
                print("錯誤:密碼為空\n按任意鍵以繼續...")
                msvcrt.getch().decode()
                sys.exit()
            if not config_data["url"]:
                print("錯誤:未輸入網址\n按任意鍵以繼續...")
                msvcrt.getch().decode()
                sys.exit()
            return config_data["username"], config_data["password"], config_data["url"]      
    except KeyError as e:
        print(f"錯誤: 找不到 {e}\n按任意鍵以繼續...")
        msvcrt.getch().decode()
        sys.exit()
    except FileNotFoundError:
        print("錯誤:找不到config檔案\n按任意鍵以繼續...")
        msvcrt.getch().decode()
        sys.exit()

def save_cookies(driver, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)

def load_cookies(driver, file_path):
    with open(file_path, 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

# 點擊"看廣告"函數
def click_ad_button():
    try:
        ad_button = wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "btn-base c-accent-o") and contains(@onclick, "window.FuliAd.checkAd")]')))
        ad_button.click()
        # 等待跳出確認視窗，並點擊確定按鈕
        confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and contains(@class, "btn btn-insert btn-primary")]')))
        confirm_button.click()
    except TimeoutException:
        try:
            # 如果跳出"廣告能量不足"則重試
            ad_error_close_button = wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(@class, "btn btn-insert btn-danger") and text()="關閉"]')))
            ad_error_close_button.click()
        except:
            # 如果是已經看完廣告的情況
            try:
                #如果廣告次數已經用完(按鈕不可點選)
                ad_button = browser.find_element(By.XPATH,'//a[contains(@class, "btn-base c-accent-o is-disable") and @onclick="javascript:void(0);"]')
                print("廣告已經全部看完了。")
                return False
            except:
                browser.get(url)
        time.sleep(2)
        click_ad_button()

cookie_file_path = 'cookies.pkl'
# 使用者代理
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.3"

chrome_options = Options()
chrome_options.add_argument(f"user-agent={USER_AGENT}")
chrome_options.add_argument("--mute-audio")
browser = webdriver.Chrome(options=chrome_options)

# 讀取配置檔
USERNAME, PASSWORD, url_list = read_config()
browser.get(url)

# 嘗試載入cookie
try:
    load_cookies(browser, cookie_file_path)
    browser.get(url)
except FileNotFoundError:
    pass


#等待秒數設定
wait = WebDriverWait(browser, 5)

#登入嘗試
try:
    #點擊登入
    login_button = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="BH-top-data"]//a[contains(@href, "https://user.gamer.com.tw/login.php") and text()="我要登入"]')))
    login_button.click()

    # 輸入帳密
    username_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="text" and @name="userid"]')))
    password_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password" and @name="password"]')))
    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)

    # 提交登入
    submit_button = wait.until(EC.presence_of_element_located((By.XPATH, '//a[@id="btn-login" and not(@style="display:none;margin-right:2px;")]')))
    time.sleep(2)
    submit_button.click()

    # 保存cookie
    save_cookies(browser, cookie_file_path)
except (EC.NoSuchElementException, TimeoutException):
    pass  # 已經登入的狀況


ad_watched_count = 0



while True:
    result = click_ad_button()
    if result is False:
        break

    # 切换到iframe
    iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[id*="google_ads_iframe_"]')))
    browser.switch_to.frame(iframe)

    #如果出現有聲廣告提醒，則自動按下
    try:
        confirm_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'rewardResumebutton')))
        # 使用JS模擬按下
        browser.execute_script("arguments[0].click();", confirm_button)
    except (EC.NoSuchElementException,TimeoutException):
        pass

    #等待廣告結束
    time.sleep(30)
    close_button_selector = 'img[src="https://googleads.g.doubleclick.net/pagead/images/gmob/close-circle-30x30.png"], div#close_button > div#close_button_icon'
    close_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, close_button_selector)))
    # 使用JS模擬按下
    browser.execute_script("arguments[0].click();", close_button)

    # 在關閉按鈕後進行廣告計數
    ad_watched_count += 1
    print(f"已看完{ad_watched_count}次廣告。")

    # 切換回主畫面
    browser.switch_to.default_content()
    time.sleep(3)
    browser.get(url)
