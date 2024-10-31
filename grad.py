import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import zipfile
import os
import re


def unzip_crx(crx_path, extract_to_folder):
    with zipfile.ZipFile(crx_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_folder)


crx_path = os.path.join(os.getcwd(), '1.0.1_0.crx')
extract_to_folder = os.path.join(os.getcwd(), 'folder_ekstensi')

if not os.path.exists(extract_to_folder):
    os.makedirs(extract_to_folder)

unzip_crx(crx_path, extract_to_folder)


def create_extension_folder(proxy_host, proxy_port, proxy_user, proxy_pass):
    folder_ekstensi1 = os.path.join(os.getcwd(), 'folder_ekstensi1')

    if not os.path.exists(folder_ekstensi1):
        os.makedirs(folder_ekstensi1)

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxy Chrome",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (proxy_host, proxy_port, proxy_user, proxy_pass)

    with open(os.path.join(folder_ekstensi1, 'manifest.json'), 'w') as f:
        f.write(manifest_json)

    with open(os.path.join(folder_ekstensi1, 'background.js'), 'w') as f:
        f.write(background_js)

    return folder_ekstensi1


def launch_browser_with_proxy(proxy_host, proxy_port, proxy_user, proxy_pass, username, password):
    options = Options()
    folder_ekstensi_path = os.path.join(os.getcwd(), 'folder_ekstensi')
    folder_ekstensi_path1 = create_extension_folder(proxy_host, proxy_port, proxy_user, proxy_pass)
    
    if use_proxy == '1':
        extensions = f"{folder_ekstensi_path},{folder_ekstensi_path1}"
    else:
        extensions = f"{folder_ekstensi_path}"

    options.add_argument(f'--load-extension={extensions}')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-notifications")
    options.add_argument('--headless')
    
    driver = uc.Chrome(options=options)
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(5)
    driver.get("https://app.gradient.network/dashboard")
    main_tab = driver.current_window_handle

    for handle in driver.window_handles:
        if handle != main_tab:
            driver.switch_to.window(handle)
            driver.close()

    driver.switch_to.window(main_tab)
    wait = WebDriverWait(driver, 10)

    # Menggunakan username dan password dari input pengguna
    email_input = wait.until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div[2]/div[1]/input')))
    email_input.send_keys(username)

    password_input = wait.until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div[2]/div[2]/span/input')))
    password_input.send_keys(password)

    login_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div[4]/button[1]')))
    login_button.click()
    print("Farming dimulai")
    return driver


num_browsers = int(input("Berapa banyak browser yang akan dibuka?\n"))
use_proxy = input("Gunakan proxy? (1 - Ya, 2 - Tidak)\n")

# Mengambil username dan password
username = input("Masukkan username: ")
password = input("Masukkan password: ")

with open('proxies.txt', 'r') as proxy_file:
    proxies = proxy_file.read().strip().split('\n')

drivers = []
for i in range(min(num_browsers, len(proxies))):
    proxy = proxies[i]
    match = re.match(r'(.+):(.+)@([\d\.]+):(\d+)', proxy)
    if match:
        proxy_user = match.group(1)
        proxy_pass = match.group(2)
        proxy_host = match.group(3)
        proxy_port = match.group(4)
        driver = launch_browser_with_proxy(proxy_host, proxy_port, proxy_user, proxy_pass, username, password)
        drivers.append(driver)

input("Tekan Enter untuk menutup semua browser")

for driver in drivers:
    driver.quit()
