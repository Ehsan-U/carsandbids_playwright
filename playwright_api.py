
import asyncio
import random
from time import sleep
from urllib import response
from flask import Flask, request,jsonify
import json
from playwright.async_api import async_playwright
from rich.console import Console
con = Console()

# proxy setup
# proxy_pool = ['http://yuuvqogr-rotate:9h2mhn3nphde@p.webshare.io:80/','http://bimxecpq-rotate:c1nqqly3v05y@p.webshare.io:80/','http://hjdkysch-rotate:iwfapn45qbcm@p.webshare.io:80/']
# server = random.choice(proxy_pool)

# def handle_route(route):
#     con.print(route.request.post_data)
    
# async def test(playwright):
#     url ='https://httpbin.org/ip'
#     chromium = playwright.chromium
#     browser = await chromium.launch(proxy={
#   "server": "http://p.webshare.io:80",
#   "username": "yuuvqogr-rotate",
#   "password": "9h2mhn3nphde"
# })
#     page = await browser.new_page()  
#     await page.route("**", handle_route)
#     await page.goto(url)
#     data = await page.content() 
#     await browser.close()
#     print(data) 

async def new_interceptor(response):
    api_string = "/v2/autos/auctions?limit"
    if api_string in response.request.url:
        # con.print("url >> ",response.request.url)
        global resp,newapi
        newapi = response.request.url
        resp = await response.json()
# handling new listing
async def new_cars(playwright,url):
    chromium = playwright.chromium
    browser = await chromium.launch(proxy={
  "server": "http://p.webshare.io:80",
  "username": "yuuvqogr-rotate",
  "password": "9h2mhn3nphde"
})  
    context = await browser.new_context()
    page = await context.new_page()
    page.on("response", new_interceptor)
    try:
        await page.goto(url)
        # will raise exception
        await page.check(".paginator")
    except:
        cookies = {}
        cookies_list = await context.cookies(url)
        for cookie in cookies_list:
            cookies[cookie.get("name")] = cookie.get("value")
        await browser.close()
        return {'cookies':cookies,"resp":resp,'newapi':newapi}
    else:
        pass

async def page_interceptor(response):
    api_string = "/v2/autos/auctions/"
    if api_string in response.request.url:
        con.print("url >> ",response.request.url)
        global resp
        resp = await response.json()
async def get_page(playwright,url):
    chromium = playwright.chromium
    browser = await chromium.launch(proxy={
  "server": "http://p.webshare.io:80",
  "username": "yuuvqogr-rotate",
  "password": "9h2mhn3nphde"
})
    context = await browser.new_context()
    page = await context.new_page()
    page.on("response", page_interceptor)
    try:
        await page.goto(url)
        await page.check(".quick-facts")
        # await page.wait_for_selector(".quick-facts")
    except:
        cookies = {}
        cookies_list = await context.cookies(url)
        for cookie in cookies_list:
            cookies[cookie.get("name")] = cookie.get("value")
        await browser.close()
        return jsonify(resp,cookies)
    else:
        pass


async def past_interceptor(response):
    api_string = "/v2/autos/auctions?limit"
    if api_string in response.request.url:
        con.print("url >> ",response.request.url)
        global resp,pastapi
        pastapi = response.request.url
        resp = await response.json()
# handling new listing
async def past_cars(playwright,url):
    chromium = playwright.chromium
    browser = await chromium.launch(proxy={
  "server": "http://p.webshare.io:80",
  "username": "yuuvqogr-rotate",
  "password": "9h2mhn3nphde"
})
    page = await browser.new_page()
    page.on("response",past_interceptor)
    try:
        await page.goto(url)
        await page.check(".paginator")
        # await page.wait_for_selector(".paginator")
    except:
        await browser.close()
        return {"resp":resp,'pastapi':pastapi}
    else:
        pass     



"""Selenium API ENDPOINTS"""
app = Flask(__name__)
# handling new listing
async def main(url,req):
    async with async_playwright() as playwright:
        if req == "new":
            return await new_cars(playwright,url)
        elif req == 'past':
            return await past_cars(playwright,url)
        elif req == "page":
            return await get_page(playwright,url)

@app.route('/new',methods=["POST","GET"])
def new():
    url = str(request.args.get("url"))
    result = asyncio.run(main(url,'new'))
    if result:
        return result
    else:
        con.print('[+]Connection Issue! Trying..new')
        return new()
# handling individual car page
@app.route('/page',methods=["POST","GET"])
def page():
    url = str(request.args.get("url"))
    result = asyncio.run(main(url,'page'))
    if result:
        return result
    else:
        con.print('[+]Connection Issue! Trying..')
        return page()
# handling past listing
@app.route('/past',methods=["POST","GET"])
def past():
    url = str(request.args.get("url"))
    result = asyncio.run(main(url,'past'))
    if result:
        return result
    else:
        con.print('[+]Connection Issue! Trying..')
        return past()


if __name__=="__main__":
    app.run(debug=True,port=8081)
# async def main():
#     async with async_playwright() as playwright:
#         await test(playwright)
# asyncio.run(main())
