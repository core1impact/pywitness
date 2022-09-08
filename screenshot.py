#!/usr/bin/python

import sys
import argparse
import time
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

targets = []


def tabs_request(driver, hostname, port):
    main = driver.current_window_handle

    tabs = driver.window_handles
    driver.switchTo().window(tabs[0])


def shooter(hostname, port):
    width = 1440
    height = 900

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--start-fullscreen')

    capabilities = chrome_options.to_capabilities()
    capabilities['acceptInsecureCerts'] = True

    driver = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities,
                              service_log_path='message.log')  # options=chrome_options
    driver.timeouts.page_load = 10000
    driver.set_window_size(width, height)

    try:
        if port == 80:
            driver.get('http://{}:{}'.format(hostname, port))
            driver.save_screenshot('dataset/http_{}_{}.png'.format(hostname, port))
        else:
            driver.get('https://{}:{}'.format(hostname, port))
            driver.save_screenshot('dataset/https_{}_{}.png'.format(hostname, port))
    except:
        pass

def main(argv):
    recovery = 1
    inputfile = ''
    parser = argparse.ArgumentParser(description="screenshot page / core1mpact")
    parser.add_argument('inputfile', help='The nmap result xml file')
    args = parser.parse_args()
    inputfile = args.inputfile
    try:
        tree = ET.parse(inputfile)
        root = tree.getroot()
    except ET.ParseError as e:
        print
        "Parse error({0}): {1}".format(e.errno, e.strerror)
        sys.exit(2)
    except IOError as e:
        print
        "IO error({0}): {1}".format(e.errno, e.strerror)
        sys.exit(2)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit(2)

    for host in root.findall('host'):
        ip = host.find('address').get('addr')
        hostname = ""
        if host.find('hostnames') is not None:
            if host.find('hostnames').find('hostname') is not None:
                hostname = host.find('hostnames').find('hostname').get('name')
        for port in host.find('ports').findall('port'):
            protocol = port.get('protocol')
            if protocol is None:
                protocol = ""
            portnum = port.get('portid')
            if portnum is None:
                portnum = ""
            service = ""
            if port.find('service') is not None:
                if port.find('service').get('name') is not None:
                    service = port.find('service').get('name')
            versioning = ""
            if port.find('service') is not None:
                if port.find('service').get('product') is not None:
                    product = port.find('service').get('product')
                    versioning = product.replace(",", "")
                if port.find('service').get('version') is not None:
                    version = port.find('service').get('version')
                    versioning = versioning + ' (' + version + ')'
                if port.find('service').get('extrainfo') is not None:
                    extrainfo = port.find('service').get('extrainfo')
                    versioning = versioning + ' (' + extrainfo + ')'

            if recovery:
                print("[+] screenshot page {}:{}".format(ip, portnum))
                shooter(ip, portnum)


if __name__ == "__main__":
    main(sys.argv)
