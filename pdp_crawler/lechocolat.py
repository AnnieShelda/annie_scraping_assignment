#importing the neccessary libraries
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import urllib
from lxml import html
from lxml import etree
import pandas as pd
import time
import urllib
import requests
import re
import random
import json
import sys
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

#setting up a driver
driver = webdriver.Chrome(executable_path=r'chromedriver.exe')


#website url
url='https://www.lechocolat-alainducasse.com/uk/'

#opening a website url using driver
driver.get(url)
time.sleep(5)
driver.maximize_window()

#getting pop up to choose cookies, closing that using try and except
try:
    driver.find_element_by_xpath(".//button[@id='axeptio_btn_dismiss']").click()
except:
    pass


#to crawl the pdp I am using the keywords rose chocolate and gelato
keywords=['rose chocolate','truffles']
result=[]
for key in keywords:
    key=key.replace(' ','+')
    
    #opening the search page url directly using driver method
    keyword_url=url+'recherche?controller=search&s={}'.format(key)
    driver.get(keyword_url)
    time.sleep(2)

    #getting all the product links from the search page
    html=driver.page_source
    lxml=etree.HTML(html)

    product_elements=lxml.xpath(".//section[@class='productMiniature__data']/a")
    product_urls=[j.get('href') for j in product_elements]
    
    for urls in product_urls:
        #declaring empty dictionary and list to store the data
        product_dict={}
        variations_dict_list=[]
        
        #opening the search page url using requests method
        driver.get(urls)
        time.sleep(4)

        #checking if the product is available or not, if product is not available skipping to next product
        try:
            notification_=driver.find_element(By.XPATH, ".//article[@class='notification notification--error']")
            notification=notification_.text
        except:
            notification=''            
        if notification.strip()=='':
            
            product_name_=driver.find_element(By.XPATH, ".//h1[@class='productCard__title']")
            product_name=product_name_.text

            image_=driver.find_element(By.XPATH, ".//li[@class='productImages__item keen-slider__slide']/a")
            image = image_.get_attribute('href')

            weight_=driver.find_element(By.XPATH, ".//p[@class='productCard__weight']")
            weight=weight_.text

            #putting this consumer adive in try and expect, so that if there is no consumer advice available it will keep it as empty
            try:
                alert_=driver.find_element(By.XPATH, "//p[@class='consumeAdvices'] | //p[@class='consumeAdvices']/strong")
                alert = alert_.text
            except:
                alert=''

            price_status_=driver.find_element(By.XPATH, "//button[@class='productActions__addToCart button add-to-cart add'] ")
            price_status=price_status_.text
            try:
                price=price_status.split('-')[1].strip()
            except:
                price=''
            try:            
                status=price_status.split('-')[0].strip()
            except:
                status=''                    

            try:
                category_=driver.find_element(By.XPATH, "//p[@class='linkedProducts__title'] ")
                category = category_.text
            except:
                category=''
                

            product_url=driver.current_url
            
            product_id_=product_url.split('/')
            product_id=product_id_[len(product_id_)-1]

            variations_dict = {'product_name': product_name,
                               'product_id': product_id,
                               'product_url':product_url,
                               'product_image': image,
                               'selling_price':price,
                               'weight': weight,
                               'best_before_alert': alert,
                               'available_status':status,
                               'category':category}
            variations_dict_list.append(variations_dict)

            #getting the product variations
            try:
                categories=driver.find_element(By.XPATH, "//ul[@class='linkedProducts__list'] /li/a")
                category_links = [categories.get_attribute('href')]
            except:
                category_links=[]
                
            #looping through the product variations and crawling the details
            for category_link in category_links:
                driver.get(category_link)
                time.sleep(4)

                #checking if the product is available or not
                try:
                    notification_=driver.find_element(By.XPATH, ".//article[@class='notification notification--error']")
                    notification=notification_.text
                except:
                    notification=''                    
                if notification.strip()=='':

                    product_name_=driver.find_element(By.XPATH, ".//h1[@class='productCard__title']")
                    product_name=product_name_.text

                    image_=driver.find_element(By.XPATH, ".//li[@class='productImages__item keen-slider__slide']/a")
                    image = image_.get_attribute('href')

                    weight_=driver.find_element(By.XPATH, ".//p[@class='productCard__weight']")
                    weight=weight_.text

                    alert_=driver.find_element(By.XPATH, "//p[@class='consumeAdvices'] | //p[@class='consumeAdvices']/strong")
                    alert = alert_.text

                    price_status_=driver.find_element(By.XPATH, "//button[@class='productActions__addToCart button add-to-cart add'] ")
                    price_status=price_status_.text
                    try:
                        price=price_status.split('-')[1].strip()
                    except:
                        price=''
                    try:            
                        status=price_status.split('-')[0].strip()
                    except:
                        status=''


                    category_=driver.find_element(By.XPATH, "//p[@class='linkedProducts__title'] ")
                    category = category_.text

                    product_id_=category_link.split('/')
                    product_id=product_id_[len(product_id_)-1]


                    variations_dict = {'product_name': product_name,
                                       'product_id': product_id,
                                       'product_url':category_link,
                                       'product_image': image,
                                       'selling_price':price,
                                       'weight': weight,
                                       'best_before_alert': alert,
                                       'available_status':status,
                                       'category':category}
                    variations_dict_list.append(variations_dict)

            #getting all the non variant details of a product
            description=''
            Ingredients=''
            Nutritional_values=''
            Allergens=''
            Price_per_kilo=''
            image_urls=''
            video_urls=''

            image_urls = [li.get_attribute("href") for li in driver.find_elements(By.XPATH, ".//li[@class='productImages__item keen-slider__slide']/a")]
            try:
                video_urls = ['https://www.lechocolat-alainducasse.com/'+li.get_attribute("data-src") for li in driver.find_elements(By.XPATH, ".//video[@class='lazyloaded']")]
                
            except:
                video_urls=''
                

            
            html_content=driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            h3_tags = soup.find_all('h3', class_='wysiwyg-title-default')
            for h3_tag in h3_tags:
                header=h3_tag.text
                if header=='Ingredients':
                    ingredients=h3_tag.find_next('p').text.strip()
                if header=='Nutritional values':
                    nutritional_values=h3_tag.find_next('p').text.strip()
                if header=='Allergens':
                    allergy=h3_tag.find_next('p').text.strip()
                if header=='Price per kilo':
                    price_per_kilo=h3_tag.find_next('p').text.strip()
                if header=='Vegan':
                    vegan=h3_tag.find_next('p').text.strip()
                    
            description_div = soup.find('div', class_='productAccordion__content js-tab-content')
            description_ = [p.get_text(strip=True) for p in description_div.find_all('p') if not p.find_previous_sibling('h3')]
            description="".join(description_)
            
            product_dict = {
                       'variations': variations_dict_list,
                       'description':description,
                        'ingredients': ingredients,
                        'nutritional_values': nutritional_values,
                        'allergy_alert':allergy,
                        'vegan':vegan,
                        'price_per_kilo':price_per_kilo,
                        'all_images':image_urls,
                        'all_videos':video_urls
                        }
            result.append(product_dict)
            
            

                
                    

#storing the crawled product in dataframe
df = pd.DataFrame(result)
df.to_excel('lechocolat_output.xlsx',index=False)

#storing the crawled product in json
with open('lechocolat_output.json', 'w', encoding='utf-8') as json_file:
    json.dump(result, json_file, ensure_ascii=False, indent=4)


#closing and quiting the driver
driver.close()
driver.quit()

print('lechocolat crawling is done')


