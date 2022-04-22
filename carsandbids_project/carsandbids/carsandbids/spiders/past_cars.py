import json
import re
from socket import timeout
from urllib.parse import urljoin
import scrapy
from scrapy_splash import SplashRequest
from scrapy.selector import Selector
from rich.console import Console
from scrapy.loader import ItemLoader
from ..items import CarsandbidsItem
from bs4 import BeautifulSoup
from scrapy_playwright.page import PageMethod 

class CarsSpider(scrapy.Spider):
    data = {}
    not_required = ['seller','bodystyle','sellertype','drivetrain']
    cookies = ''
    name = 'pastcars'
    ids = {}
    counter = 0
    offset = 0
    allowed_domains = ['carsandbids.com','127.0.0.1']
    con = Console()
    def start_requests(self):
        url = "http://127.0.0.1:8081/past?url=https://carsandbids.com/past-auctions/"
        yield scrapy.Request(url,callback=self.temp_parse)

    def temp_parse(self, response):
        body = response.body
        data = json.loads(body)  
        self.cookies = data.get("cookies")
        self.past_api = data.get("pastapi")
        yield scrapy.Request(url=self.past_api,callback=self.parse,cookies=self.cookies)

    def parse(self,response):    
        body = response.body
        data = json.loads(body)
        self.data = data
        r = int(data.get("count"))
        for i in range(r):
            self.ids[data["auctions"][i].get("id")] = data["auctions"][i].get("title")
        # build urls
        for key,val,i in zip(self.ids.keys(),self.ids.values(),range(r)):
            val = val.replace(' ','-')
            each_car = f'https://carsandbids.com/auctions/{key}/{val}'
            url = f'http://127.0.0.1:8081/page?url={each_car}'
            yield scrapy.Request(url,callback=self.custom_parse,meta={'i':i,'data':data,'source':each_car})
        self.past_api = self.past_api.replace(f"offset={self.offset}",f"offset={self.offset+50}")
        if data['count'] != data['total']:
            self.offset+=50
            yield scrapy.Request(url=self.past_api,callback=self.parse,cookies=self.cookies)
    
    def custom_parse(self,response):
        resp = response
        response = response.text.replace("\\",'')
        response = Selector(text=response)
        loader = ItemLoader(item=CarsandbidsItem(),response=resp,selector=response)
        # self.con.print(response.url)
        quick_facts = response.xpath("//div[@class='quick-facts']")
        # self.con.print(quick_facts.xpath(".//dd/a").get())
        year = response.xpath("//div[@class='auction-title']/h1/text()").get()[:4]
        loader.add_value("Year",year)
        for dt,dd in zip(quick_facts.xpath("//div[@class='quick-facts']//dt"),quick_facts.xpath("//div[@class='quick-facts']//dd")):
            if dd.xpath(".//a").get():
                # self.con.print("a true")
                val_xpath = ".//a/text()"
            else:
                # self.con.print("dd true")
                val_xpath = ".//text()"
            p_name = dt.xpath(".//text()").get() 
            p_val = dd.xpath(val_xpath).get()
            if p_name.lower().replace(' ','') in self.not_required:
                pass
            else:
                if "Mileage" in p_name:
                    tmu = p_val.find("TMU")
                    if tmu == -1:
                        tmu = 'False'
                    else:
                        tmu = 'True'
                elif "Title Status" in p_name:
                    p_name = 'Title_Status'
                    loader.add_value(p_name,p_val)
                elif "Color" in p_name:
                    p_name = p_name.replace(" ",'')
                    loader.add_value(p_name,p_val)
                else:
                    loader.add_value(p_name,p_val)
                # self.con.print(f"[bold green]{p_name,p_val}")
        url_source = resp.request.meta.get("source")
        images = ''
        for img in response.xpath("//div[@class='images']//div[@class='preload-wrap  loaded']"):
            images+=f'{img.xpath(".//img/@src").get()},'
        kilometers = resp.text.lower().find("kilometer")
        if kilometers == -1:
            kilometers = "False"
        else:
            kilometers = "True"
        
        self.data['Kilometers'] = kilometers
        self.data['TMU'] = tmu
        i = resp.request.meta.get("i")
        data = resp.request.meta.get("data")
        url = resp.request.meta.get("url")
        price = response.xpath("//span[@class='bid-value']/text()").get()
        no_reserver = str(data["auctions"][i].get('no_reserve'))
        raw_title = data['auctions'][i].get("title")
        raw_subtitle = data['auctions'][i].get("sub_title")
        raw_miles = data['auctions'][i].get("mileage")
        base_url = f'https://{data["auctions"][i].get("main_photo").get("base_url")}'
        rel_path = data['auctions'][i].get("main_photo").get("path")
        main_photo = urljoin(base_url,rel_path)

        loader.add_value("Price",price)
        loader.add_value("Kilometers",kilometers)
        loader.add_value("TMU",tmu)
        loader.add_value("No_Reserver",no_reserver)
        loader.add_value("URL",url_source)
        loader.add_value("Raw_Title",raw_title)
        loader.add_value("Raw_Subtitle",raw_subtitle)
        loader.add_value("Raw_Miles",raw_miles)
        loader.add_value("Source",url_source)
        loader.add_value("Main_Image",main_photo)
        loader.add_value("All_Images",images)
        yield loader.load_item()
        self.counter +=1
        self.con.print("[bold green]Processed Items: ",self.counter,f", [bold green]Remaining Items: {self.data['total']-self.counter}")
            # self.con.print(urljoin(base_url,rel_path))
