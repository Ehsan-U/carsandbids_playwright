# from time import sleep
# from playwright.sync_api import sync_playwright

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=True,slow_mo=50)
#     context = browser.new_context(user_agent=' ')
#     page = context.new_page()
#     page.goto("https://carsandbids.com/auctions/rkqpPZVO/1984-Porsche-944")
#     sleep(5)
#     resp = page.content()
#     print(resp)
# import re


# import requests

# resp = requests.get(
#     "https://ipv4.webshare.io/",
#     proxies={
#         "http": "149.6.162.2:9999",
#         "https": "149.6.162.2:9999"
#     }
# ).text
# print(resp)