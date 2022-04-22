import json
import re
import random
from urllib.parse import urljoin
import scrapy
from scrapy.selector import Selector
from rich.console import Console
from scrapy.loader import ItemLoader
from ..items import CarsandbidsItem
from bs4 import BeautifulSoup

class CarsSpider(scrapy.Spider):
    data = {}
    not_required = ['seller','bodystyle','sellertype','drivetrain']
    cookies = ''
    name = 'newcarrrs'
    ids = {}
    counter = 0
    allowed_domains = ['carsandbids.com','127.0.0.1']
    con = Console()
    def start_requests(self):
        # request to selenium API endpoint
        url = "http://127.0.0.1:8081/new?url=https://carsandbids.com/"
        yield scrapy.Request(url,callback=self.temp_parse)

    # parsing response from selenium API
    def temp_parse(self, response):
        body = response.body
        data = json.loads(body)  
        # data used in request to carsandbids
        self.cookies = data.get("cookies")
        self.new_api = data.get("newapi")
        # making request to carsandbids API endpoint with cookies
        yield scrapy.Request(url=self.new_api,callback=self.parse,cookies=self.cookies)

    # parsing response from API and build url for each car page
    def parse(self,response):    
        body = response.body
        self.data = json.loads(body)
        count = int(self.data.get("count"))
        for i in range(count):
            self.ids[self.data["auctions"][i].get("id")] = self.data["auctions"][i].get("title")
        # build urls for each car
        # send request to each car url
        for key,val,i in zip(self.ids.keys(),self.ids.values(),range(count)):
            val = val.replace(' ','-')
            car = f'https://carsandbids.com/auctions/{key}/{val}'
            url = f'http://127.0.0.1:8081/page?url={car}'
            yield scrapy.Request(url,callback=self.custom_parse,meta={'i':i,'source':car})
            
    # extracting required fields from response
    def custom_parse(self,response):
        try:
            page_data = json.loads(response.text)
            sel = Selector(text=response.text)
            loader = ItemLoader(item=CarsandbidsItem(),response=response,selector=sel)
            i = response.request.meta.get("i")
            
            Year = self.data['auctions'][i].get("title")[:5]
            Make = page_data.get("listing").get("make")
            Model = page_data.get("listing").get("model")
            Mileage = page_data.get("listing").get("mileage")
            if Mileage:
                Mileage = str(Mileage)
            else:
                Mileage = ''
                raw_miles = self.data['auctions'][i].get("mileage")
                for c in raw_miles:
                    if c.isdigit():
                        Mileage += c
            VIN = page_data.get("listing").get("vin")
            Title_Status = page_data.get("listing").get("title_status")
            Location = page_data.get("listing").get("location")
            Engine = page_data.get("listing").get("engine")
            T_bool = page_data.get("listing").get("transmission")
            if T_bool == 1:
                Transmission = f'Automatic {page_data.get("listing").get("transmission_details")}'
            else:
                Transmission = f'Manual {page_data.get("listing").get("transmission_details")}'
            ExteriorColor = page_data.get("listing").get("exterior_color")
            InteriorColor = page_data.get("listing").get("interior_color")

            
            price = page_data.get("finance").get("disclosure").get("price")
            no_reserver = str(self.data["auctions"][i].get('no_reserve'))
            raw_title = self.data['auctions'][i].get("title")
            raw_subtitle = self.data['auctions'][i].get("sub_title")
            raw_miles = self.data['auctions'][i].get("mileage")
            base_url = f'https://{self.data["auctions"][i].get("main_photo").get("base_url")}'
            rel_path = self.data['auctions'][i].get("main_photo").get("path")
            main_photo = urljoin(base_url,rel_path)        
            url_source = response.request.meta.get("source")
            url = response.request.meta.get("source")
            images = ''
            for ex_image,in_image in zip(page_data.get("listing").get("photos").get("exterior"),page_data.get("listing").get("photos").get("interior")):
                images += f'https://media.carsandbids.com/{ex_image.get("link")},'
                images += f'https://media.carsandbids.com/{in_image.get("link")},'
            km = "kilometer"
            if km in page_data.get("listing").get("sections").get("doug") or km in page_data.get("listing").get("sections").get("equipment") or km in page_data.get("listing").get("sections").get("highlights"):
                kilometers = "True"
            else:
                kilometers = "False"
            raw_Mileage = self.data['auctions'][i].get("mileage")
            if "TMU" in raw_Mileage:
                tmu = 'True'
            else:
                tmu = 'False'
        
            loader.add_value("Year",Year)
            loader.add_value("Make",Make)
            loader.add_value("Model",Model)
            loader.add_value("Mileage",Mileage)
            loader.add_value("VIN",VIN)
            loader.add_value("Title_Status",Title_Status)
            loader.add_value("Location",Location)
            loader.add_value("Engine",Engine)
            loader.add_value("Transmission",Transmission)
            loader.add_value("ExteriorColor",ExteriorColor)
            loader.add_value("InteriorColor",InteriorColor) 
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
            self.counter +=1
            yield loader.load_item()
            self.con.print("[bold green]Processed Items: ",self.counter," Remaining:",self.data['total']-self.counter)
        except:
            self.con.print_exception()