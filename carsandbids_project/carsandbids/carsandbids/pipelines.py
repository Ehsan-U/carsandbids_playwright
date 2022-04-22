# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemloaders import processors
import itemloaders
from .items import CarsandbidsItem
import openpyxl
from openpyxl import Workbook
from openpyxl.styles.fonts import Font
import string


class Excel_Pipeline(object):

    def __init__(self):
        self.cars_obj = CarsandbidsItem()
        self.wb = Workbook()
        self.wb.active.title = 'cars_sheet'
        self.cars_sheet = self.wb.active
        print('\n\nHELLO from init\n\n')

    def open_spider(self,spider):
        # will return the field names that we have defined in items.py
        self.fields = list(self.cars_obj.fields.keys())
        self.fields.reverse()
        
        # will contain A-Z letters
        alphabets = list(string.ascii_uppercase)[0:len(self.fields)]
        for field,letter in zip(self.fields, alphabets):
            self.cars_sheet[f'{letter}1'].value = field
            self.cars_sheet[f'{letter}1'].font = Font(bold=True)

    def close_spider(self,spider):
        self.wb.save('Cars.xlsx')

    def process_item(self, item, spider):
        # phone_obj.fields is dict
        # field is key here
        # item is dict
        row = [item.get(field) for field in self.fields]
        # append accept an iteratble
        self.cars_sheet.append(row)
        return item
