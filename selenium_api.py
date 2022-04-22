import random
from time import sleep
from flask import Flask, request,jsonify
import json
import selenium
from seleniumwire.utils import decode 
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from rich.console import Console
con = Console()

# proxy setup
proxy_pool = ['http://yuuvqogr-rotate:9h2mhn3nphde@p.webshare.io:80/','http://bimxecpq-rotate:c1nqqly3v05y@p.webshare.io:80/','http://hjdkysch-rotate:iwfapn45qbcm@p.webshare.io:80/']
proxy = random.choice(proxy_pool)
ch_options = Options()
ch_options.add_argument("--headless")
options = {
    'proxy': {
        'https': f'{proxy}',
        'http': f'{proxy}',
    }
}

def new_interceptor(request):
    api = "/v2/autos/auctions?limit"
    if api in request.url:
        request.url = request.url.replace("limit=12",'limit=100')

def past_interceptor(request):
    api = "/v2/autos/auctions?limit"
    if api in request.url:
        request.url = request.url.replace("offset=50",'offset=0')
        

# handling individual car page
def get_page(url):
    driver = webdriver.Chrome(executable_path="/home/lubuntu/cars_project/chromedriver",options=ch_options,seleniumwire_options=options)
    driver.get(url)
    try:
        element = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.CLASS_NAME,"quick-facts")))
    except:
        pass
    api = '/v2/autos/auctions/'
    for req in driver.requests:
        if req.response:
            if api in req.url:
                body = req.response.body
                resp = decode(body, req.response.headers.get('Content-Encoding', 'identity'))
                resp = json.loads(resp)
                return jsonify(resp)

# handling new listing
def get_new_api(url):
    driver = webdriver.Chrome(executable_path="/home/lubuntu/cars_project/chromedriver",options=ch_options,seleniumwire_options=options)
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

# handling past listing
def get_past_api(url):
    url = "https://carsandbids.com/past-auctions/?page=2"
    driver = webdriver.Chrome(executable_path="/home/lubuntu/cars_project/chromedriver",options=ch_options,seleniumwire_options=options)
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

"""Selenium API ENDPOINTS"""
app = Flask(__name__)
# handling new listing
@app.route('/new',methods=["POST","GET"])
def new():
    url = str(request.args.get("url"))
    while True:
        try:
            result = get_new_api(url)
            if result == None:
                con.print(f"[bold][+]Connection Issue! Trying Again..")
                continue
        except Exception:
            con.print(f"[bold][+]Connection Issue! Trying Again..")
            continue
        else:
            break
    return result

# handling individual car page
@app.route('/page',methods=["POST","GET"])
def page():
    url = str(request.args.get("url"))
    while True:
        try:
            result = get_page(url)
            if result == None:
                con.print(f"[bold][+]Connection Issue! Trying Again..")
                continue
        except Exception:
            con.print(f"[bold][+]Connection Issue! Trying Again..")
            continue
        else:
            break
    return result

# handling past listing
@app.route('/past',methods=["POST","GET"])
def past():
    url = str(request.args.get("url"))
    while True:
        try:
            result = get_past_api(url)
            if result == None:
                con.print(f"[bold][+]Connection Issue! Trying Again..")
                continue
        except TypeError:
            con.print(f"[bold][+]Connection Issue! Trying Again..")
            continue
        else:
            break
    return result



if __name__=="__main__":
    app.run(debug=True,port=8081)
# test()
