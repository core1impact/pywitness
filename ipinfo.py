import sys

from selenium import webdriver
from selenium.webdriver.common.by import By

urls = []

def set_proxy(driver, http_addr='', http_port=0, ssl_addr='', ssl_port=0, socks_addr='', socks_port=0):
    driver.execute("SET_CONTEXT", {"context": "chrome"})

    try:
        driver.execute_script("""
          Services.prefs.setIntPref('network.proxy.type', 1);
          Services.prefs.setCharPref("network.proxy.http", arguments[0]);
          Services.prefs.setIntPref("network.proxy.http_port", arguments[1]);
          Services.prefs.setCharPref("network.proxy.ssl", arguments[2]);
          Services.prefs.setIntPref("network.proxy.ssl_port", arguments[3]);
          Services.prefs.setCharPref('network.proxy.socks', arguments[4]);
          Services.prefs.setIntPref('network.proxy.socks_port', arguments[5]);
          """, http_addr, http_port, ssl_addr, ssl_port, socks_addr, socks_port)

    finally:
        driver.execute("SET_CONTEXT", {"context": "content"})


def get_range_by_asn(driver, url):
    driver.get('https://ipinfo.io/{}'.format(url))
    # try:
    if driver.title.__contains__('Too Many Requests'):
        print("[*] change proxy")
        set_proxy(driver, http_addr="127.0.0.1", http_port=8082) # socks5 service 
        driver.get('https://ipinfo.io/{}'.format(url))
    try:
        driver.find_element(By.XPATH, '//*[@id="ipv4-data"]/div/a').click()
    except:
        pass

    range_list = driver.find_elements(By.XPATH, '//*[@id="ipv4-data"]')
    for ip in range_list:
        print(ip.text)  # save data to neo4j

    file = open('ra-{}-ip.txt'.format(url), 'w')
    for ip in range_list:
        file.write(ip.text + '\n')
    file.close()

def get_asn_by_country(driver):
    driver.get('https://ipinfo.io/countries/gb') # change country code
    try:
        next = driver.find_elements(By.XPATH, "//td[@class='p-3']")
        for i in next:
            if (i.text.find('AS')) == 0 and len(i.text) <= 9:
                urls.append(i.text)
                print('[+] ASN: {}'.format(i.text)) # save asn to neo4j

    except:
        pass


if __name__ == "__main__":
    # proxy = "127.0.0.1:8082"
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--proxy-server=%s' % proxy)
    driver = webdriver.Chrome(service_log_path='message.log')  # options=chrome_options

    get_asn_by_country(driver)

    file = open('at-asn.txt', 'w')
    for url in urls:
        file.write(url + '\n')
    file.close()

    for url in urls:
        get_range_by_asn(driver, url)

    driver.close()
