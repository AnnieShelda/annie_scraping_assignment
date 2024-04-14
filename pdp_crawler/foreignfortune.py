#importing the neccesary libraries
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import urllib
import time
import urllib
import requests
import re
import random
import json
import sys
from lxml import html
from lxml import etree
import warnings
warnings.filterwarnings("ignore")

#setting up the driver
driver = webdriver.Chrome(executable_path=r'chromedriver.exe')

#website url
url='https://foreignfortune.com/'

#opening the website using driver
driver.get(url)
time.sleep(5)
driver.maximize_window()

#getting a discount pop up, so using try and except to close that pop up window
try:
    driver.find_element_by_xpath(".//button[@aria-label='Close dialog 1']").click()
except:
    pass


#to crawl the pdp I am using some keywords 
keywords=['shirts','shirts and pant']

#declaring the list to store the results
result=[]

#looping the keywords to crawl
for key in keywords:
    key=key.replace(' ','+')
    
    #opening the search page url directly using driver method
    keyword_url=url+'/search?q={}'.format(key)
    driver.get(keyword_url)
    time.sleep(2)

    html=driver.page_source
    lxml=etree.HTML(html)

    #getting all the product links from the search page so that we can loop the products and crawl
    product_elements=lxml.xpath(".//li[@class='list-view-item']/a")
    product_urls=[j.get('href') for j in product_elements]
    
        
    for urls in product_urls:

        #decalring a list to store all the variations of the product
        variations_dict_list=[]
        
        #opening the pdp page using driver
        driver.get(url+urls)
        time.sleep(2)

        #since all the values are not visible in driver, switching to html source method using beautiful soup
        #taking the webpage source
        html_content = driver.page_source        
        soup = BeautifulSoup(html_content, 'html.parser')

        #taking the script with the particular id where all the variations are present and converting into string
        script_tag = soup.find('script', id='web-pixels-manager-setup')
        js_snippet = script_tag.string

        #doing some alterations to get the product variations in json format
        init_data_index = js_snippet.find("initData:")
        if init_data_index == -1:
            print('no products')
        init_data_section = js_snippet[init_data_index + len("initData:"):]

        split_1=init_data_section.split('},},function pageEvents(webPixelsManagerAPI')[0]
        split_2=split_1.split('"productVariants":')[1]

        data = json.loads(split_2)

        #looping all the variations and storing in a dictionary
        for variant in data:
            product_id=variant["id"]
            currency_code=variant["price"]["currencyCode"]
            selling_price=variant["price"]["amount"]
            product_url=variant["product"]["url"]
            product_url='https://foreignfortune.com//'+product_url
            vendor_name=variant["product"]["vendor"]
            three_category = variant["title"]
            size_color_material = re.split(r' / ', three_category)
            try:
                size = size_color_material[0]
            except:
                size=''
            try:
                color = size_color_material[1]
            except:
                color=''

            try:
                material = size_color_material[2]
            except:
                material=''
            
            
            #storing all the variation data in dictionary
            variations_dict = {'product_id':product_id,
                               'product_url':product_url,
                               'price': selling_price,
                               'currency':currency_code,
                               'size': size,
                               'color':color,
                               'material': material}

            variations_dict_list.append(variations_dict)

        #getting the non variant details like product name image urls
        product_name=variant["product"]["title"]
        
        img_tags = soup.find_all('div', attrs={'data-zoom': True})
        image_url_ = [str(img['data-zoom']) for img in img_tags]
        image_urls = [f"https:{url}" if url.startswith('//') else url for url in image_url_]
                                                     
        product_dict = {'product_name': product_name,
                        'image_url': image_urls,
                        'brand':vendor_name,
                        'variations': variations_dict_list}
        
        result.append(product_dict)

#storing the crawled product in dataframe
df = pd.DataFrame(result)
df.to_excel('foreignfortune_output.xlsx',index=False)

#storing the crawled product in json
with open('foreignfortune_output.json', 'w', encoding='utf-8') as json_file:
    json.dump(result, json_file, ensure_ascii=False, indent=4)

#closing and quiting the driver
driver.close()
driver.quit()

print('foreignfortune crawling is done')


