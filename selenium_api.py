import random
from time import sleep
from playwright.sync_api import sync_playwright
from flask import Flask, request,jsonify
import requests
import json
import selenium
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from rich.console import Console
con = Console()
import requests

# proxy setup
proxiesapi = ['http://yuuvqogr-rotate:9h2mhn3nphde@p.webshare.io:80/','http://bimxecpq-rotate:c1nqqly3v05y@p.webshare.io:80/','http://hjdkysch-rotate:iwfapn45qbcm@p.webshare.io:80/']
proxy = random.choice(proxiesapi)
scraper_apis = ['6842a4d97074c3c28cf112989077aed6','81913f102c92c6844a27d0ef376b7895','00459e3fb04207a181de793696bda959','62a015a1ce2ac6ffefa474eb821e0f96']
ch_options = Options()
ch_options.add_argument("--headless")
options = {
    'proxy': {
        'https': f'{proxy}',
        'http': f'{proxy}',
    }
}

def test():
    url = "https://httpbin.org/ip"
    driver = webdriver.Chrome(executable_path="/home/lubuntu/sublime/chromedriver",options=ch_options,seleniumwire_options=options)
    driver.get(url)
    con.print(driver.page_source)

def new_interceptor(request):
    api = "/v2/autos/auctions?limit"
    if api in request.url:
        request.url = request.url.replace("limit=12",'limit=100')

def past_interceptor(request):
    api = "/v2/autos/auctions?limit"
    if api in request.url:
        request.url = request.url.replace("offset=50",'offset=0')
        
def get_page(url):
    # api_key = random.choice(scraper_apis)
    # api_url = f'http://api.scraperapi.com?api_key={api_key}&url={url}'
    driver = webdriver.Chrome(executable_path="/home/lubuntu/sublime/chromedriver",options=ch_options,seleniumwire_options=options)
    driver.get(url)
    try:
        element = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.CLASS_NAME,"quick-facts")))
    except:
        pass
    resp = driver.page_source
    return jsonify({"resp":resp})

def get_new_api(url):
    # api_key = random.choice(scraper_apis)
    # api_url = f'http://api.scraperapi.com?api_key={api_key}&url={url}'
    driver = webdriver.Chrome(executable_path="/home/lubuntu/sublime/chromedriver",options=ch_options,seleniumwire_options=options)
    driver.request_interceptor = new_interceptor
    driver.get(url)
    try:
        element = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.CLASS_NAME,"paginator")))
    except:
        pass
    api = "/v2/autos/auctions?limit"
    cookies = {}
    for req in driver.requests:
        if api in req.url:
            cookies_list = driver.get_cookies()
            for cookie_dict in cookies_list:
                cookies[cookie_dict.get("name")] = cookie_dict.get("value")
            api_url = req.url
            return {"cookies":cookies,'newapi':api_url}

def get_past_api(url):
    # api_key = random.choice(scraper_apis)
    # api_url = f'http://api.scraperapi.com?api_key={api_key}&url={url}'
    url = "https://carsandbids.com/past-auctions/?page=2"
    driver = webdriver.Chrome(executable_path="/home/lubuntu/sublime/chromedriver",options=ch_options,seleniumwire_options=options)
    driver.request_interceptor = past_interceptor
    driver.get(url)
    try:
        element = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.CLASS_NAME,"paginator")))
    except:
        pass
    api = "/v2/autos/auctions?limit"
    cookies = {}
    for req in driver.requests:
        if api in req.url:
            cookies_list = driver.get_cookies()
            for cookie_dict in cookies_list:
                cookies[cookie_dict.get("name")] = cookie_dict.get("value")
            api_url = req.url
            return {"cookies":cookies,'pastapi':api_url}

app = Flask(__name__)

@app.route('/new',methods=["POST","GET"])
def new():
    url = str(request.args.get("url"))
    return get_new_api(url)

@app.route('/page',methods=["POST","GET"])
def page():
    url = str(request.args.get("url"))
    return get_page(url)

@app.route('/past',methods=["POST","GET"])
def past():
    url = str(request.args.get("url"))
    return get_past_api(url)


if __name__=="__main__":
    app.run(debug=True,port=8081)
# test()