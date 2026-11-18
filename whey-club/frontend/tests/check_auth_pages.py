"""Browser check: python3 frontend/tests/check_auth_pages.py [origin]. Requires Selenium/Chrome."""
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

origin=sys.argv[1] if len(sys.argv)>1 else 'https://wheyclub.ir'
options=webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
# shortcut: tolerate the local Chrome/driver mismatch; use matching versions if commands fail.
with webdriver.Chrome(options=options,service=Service(service_args=['--disable-build-check'])) as browser:
 for width in (1440,720,390):
  browser.set_window_size(width,900)
  for mode in ('login','register'):
   browser.get(origin+'/account/'+mode+'/?next=/checkout/')
   WebDriverWait(browser,15).until(lambda d:d.find_elements(By.CSS_SELECTOR,'.account-form input'))
   browser.execute_async_script('document.fonts.ready.then(arguments[0])')
   assert browser.find_elements(By.CSS_SELECTOR,'.auth-layout'), 'New auth layout missing'
   assert not browser.find_elements(By.CSS_SELECTOR,'header, footer'), (width,mode,'Standalone auth has a header/footer')
   assert browser.find_element(By.CSS_SELECTOR,'.auth-back').is_displayed(), (width,mode,'Return link missing')
   assert browser.execute_script('return getComputedStyle(document.querySelector(".auth-page")).getPropertyValue("--ink").trim()===getComputedStyle(document.documentElement).getPropertyValue("--ink").trim()'), 'Account page overrides the site theme'
   if width==1440:
    assert browser.execute_script('return document.querySelector(".auth-submit").getBoundingClientRect().bottom <= innerHeight'), (mode,'Submit requires scrolling')
   elif width<=650:
    assert not browser.find_element(By.CSS_SELECTOR,'.auth-story').is_displayed(), 'Decorative panel adds mobile scrolling'
   assert all(tab.is_displayed() for tab in browser.find_elements(By.CSS_SELECTOR,'.auth-tabs a')), (width,mode,'Auth switch hidden')
   other='register' if mode=='login' else 'login'
   assert browser.find_element(By.CSS_SELECTOR,'.auth-tabs a[href*="/'+other+'/"]').get_attribute('href').endswith('?next=%2Fcheckout%2F')
   assert browser.execute_script('return document.documentElement.scrollWidth<=innerWidth+1'),(width,mode,'horizontal overflow')
   assert browser.find_element(By.NAME,'password').get_attribute('type')=='password'
   browser.execute_script('document.querySelector("form").reportValidity()')
   assert not browser.execute_script('return document.querySelector("form").checkValidity()')
   if mode=='register':
    for name,value in {'name':'تست طراحی','email':'design-check@example.com','password':'Sample-pass-248','confirm':'Different-pass-248'}.items():
     browser.find_element(By.NAME,name).send_keys(value)
    WebDriverWait(browser,15).until(lambda d:d.find_element(By.CSS_SELECTOR,'button[type="submit"]').is_enabled())
    browser.execute_script('document.querySelector("form").requestSubmit()')
    WebDriverWait(browser,5).until(lambda d:d.find_elements(By.CSS_SELECTOR,'[role="alert"]'))
    assert 'تکرار رمز عبور یکسان نیست' in browser.find_element(By.CSS_SELECTOR,'[role="alert"]').text
    assert browser.find_element(By.NAME,'email').get_attribute('value')=='design-check@example.com'
   print('PASS',width,mode,flush=True)

 browser.get(origin+'/account/')
 WebDriverWait(browser,15).until(lambda d:d.find_elements(By.CSS_SELECTOR,'.account-page .account-main'))
 assert not browser.find_elements(By.CSS_SELECTOR,'header, footer'), 'Account has a header/footer'
 assert browser.find_element(By.CSS_SELECTOR,'.auth-back').is_displayed()
 assert browser.execute_script('return document.documentElement.scrollWidth<=innerWidth+1')
 print('PASS standalone account',flush=True)

 browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': """
 const originalFetch=window.fetch;
 window.fetch=(url,options)=>url==='/api/account/session/'
  ? Promise.resolve(new Response(JSON.stringify({user:{id:1,name:'کاربر تست'}})))
  : url==='/api/account/addresses/'
   ? Promise.resolve(new Response(JSON.stringify({results:[]})))
   : originalFetch(url,options);
 """})
 browser.refresh()
 WebDriverWait(browser,15).until(lambda d:d.find_elements(By.CSS_SELECTOR,'.account-welcome'))
 assert not browser.find_elements(By.CSS_SELECTOR,'header, footer')
 assert browser.find_elements(By.CSS_SELECTOR,'.address-form')
 assert browser.execute_script('return document.documentElement.scrollWidth<=innerWidth+1')
 browser.save_screenshot('/tmp/whey-account-mobile.png')
 print('PASS signed-in account with simulated session',flush=True)
