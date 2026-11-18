"""Run with Selenium and Chrome installed: python3 frontend/tests/check_shared_layout.py [origin]."""
import json
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

origin = sys.argv[1] if len(sys.argv) > 1 else 'https://wheyclub.ir'
paths = json.loads((Path(__file__).parents[1] / 'public/public-routes.json').read_text())
paths += ['/cart/', '/checkout/', '/blog/', '/blog/what-is-whey-protein/', '/blog/category/whey-protein/']
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# shortcut: tolerate the local Chrome/driver version mismatch; use matching versions if browser commands fail.
with webdriver.Chrome(options=options, service=Service(service_args=['--disable-build-check'])) as browser:
    baseline = None
    for width in (1440, 390):
        browser.set_window_size(width, 1000)
        for path in paths:
            browser.get(origin + path)
            WebDriverWait(browser, 15).until(lambda d: d.find_elements(By.TAG_NAME, 'header') and 'در حال بارگذاری' not in d.find_element(By.TAG_NAME, 'body').text)
            result = browser.execute_script('''
                const header=document.querySelector('header'), footer=document.querySelector('footer');
                return {headers:document.querySelectorAll('header').length,footers:document.querySelectorAll('footer').length,
                    links:header?[...header.querySelectorAll('a')].map(a=>a.getAttribute('href')):[],
                    footer:footer?footer.innerHTML:null,
                    overflow:document.documentElement.scrollWidth>innerWidth+1};
            ''')
            assert result['headers'] == result['footers'] == 1, (width, path, result)
            assert '/account/' in result['links'], (width, path, 'Account link missing')
            assert '/cart/' in result['links'], (width, path, 'Cart link missing')
            if baseline is None:
                baseline = (result['links'], result['footer'])
            assert (result['links'], result['footer']) == baseline, (width, path, 'Header/footer differ from homepage')
            assert not result['overflow'], (width, path, 'Page overflows viewport')
            print('PASS', width, path, flush=True)

    browser.execute_script('localStorage.setItem("wheyclub-cart", JSON.stringify({1: 2}))')
    for path in ['/blog/', '/shop/whey-protein/']:
        browser.get(origin + path)
        WebDriverWait(browser, 15).until(lambda d: d.execute_script('return document.querySelector("#cartCount")?.textContent') == '۲')
    WebDriverWait(browser, 15).until(lambda d: d.find_elements(By.CSS_SELECTOR, '[data-add="1"]'))
    WebDriverWait(browser, 15).until(lambda d: d.execute_script('return typeof window.updateCart === "function"'))
    button = browser.find_element(By.CSS_SELECTOR, '[data-add="1"]')
    browser.execute_script('arguments[0].scrollIntoView({block: "center", behavior: "instant"})', button)
    button.click()
    WebDriverWait(browser, 5).until(lambda d: d.execute_script('return document.querySelector("#cartCount")?.textContent') == '۳')
    print('PASS: cart count persists across routes and updates after adding a product')
