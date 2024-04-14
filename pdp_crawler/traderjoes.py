from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.keys import Keys
import urllib
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
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

#getting the driver
driver = webdriver.Chrome(executable_path=r'chromedriver.exe')

#website url
url='https://www.traderjoes.com'
driver.get(url)
time.sleep(5)
driver.maximize_window()

#getting a cookie pop up, so using try and except to close that pop up
try:
    driver.find_element_by_xpath(".//button[@class='Button_button__3Me73 Button_button_variant_secondary__RwIii']").click()
except:
    pass


#to crawl the pdp I am using the keywords shirt and pant
keywords=['mochi']
result=[]
for key in keywords:
    key=key.replace(' ','+')
    
    #opening the search page url directly using driver method
    keyword_url=url+'/home/search?q={}&section=products&global=yes'.format(key)
    driver.get(keyword_url)
    time.sleep(7)

    #getting all the product url from the search pge
    html=driver.page_source
    lxml=etree.HTML(html)

    product_elements=lxml.xpath(".//article[@class='SearchResultCard_searchResultCard__3V-_h']/h3/a")
    product_urls=[j.get('href') for j in product_elements]
    
    
    #looping through the product url to crawl the pdp page
    for urls in product_urls:
        #declaring an empty list to store the values
        variations_dict_list=[]

        #opening pdp page with the base url
        driver.get(url+urls)
        time.sleep(4)


        product_name_=driver.find_element(By.XPATH, ".//h1[@class='ProductDetails_main__title__14Cnm']")
        product_name=product_name_.text

        html=driver.page_source
        lxml=etree.HTML(html)
        image_elements=lxml.xpath("//div[@class='slick-track']//div[@class='slide']//img")
        image_urls=["https://www.traderjoes.com/"+j.get('srcoriginal') for j in image_elements]
        if len(image_urls)==0:
            image_elements=lxml.xpath(".//div[@class='slick-track']//div[@class='HeroImage_heroImage__2ugCl Carousel_heroImageWrapper__1SSK6']//img")
            image_urls=["https://www.traderjoes.com/"+j.get('srcoriginal') for j in image_elements]
            

        #using try and except, beacause image_tag is an optional element
        try:
            image_tag_=driver.find_element(By.XPATH, ".//div[@class='Carousel_tape__2ihtf']")
            image_tag=image_tag_.text
        except:
            image_tag=''

            
        weight_=driver.find_element(By.XPATH, ".//div[@class='ProductPrice_productPrice__1Rq1r']//span[@class='ProductPrice_productPrice__unit__2jvkA']")
        weight = weight_.text.replace('/','')
        
        price_=driver.find_element(By.XPATH, ".//div[@class='ProductPrice_productPrice__1Rq1r']//span[@class='ProductPrice_productPrice__price__3-50j']")
        price=price_.text
        
        description_=driver.find_element(By.XPATH, ".//div[@class='Expand_expand__container__3COzO']/div")
        description = '\n'.join([p_element.text for p_element in description_.find_elements(By.XPATH, ".//p")])
        
        tags  = [li.find_element(By.CLASS_NAME, "FunTag_tag__text__1FfQ6").text for li in driver.find_elements(By.CSS_SELECTOR, ".FunTagList_list__2GhdP li")]

        ingredients_ = driver.find_element(By.XPATH, ".//div[@class='Section_section__header__R8aD_']//following-sibling::div | li[@class='IngredientsList_ingredientsList__item__1VrRy']")
        
        ingredients = ingredients_.text.split('MAY')[0].strip()

        try:
            contains_=driver.find_element(By.XPATH, ".//ul[@class='IngredientsSummary_ingredientsSummary__allergensList__1ROpD']")
            contains_elements = contains_.find_elements(By.TAG_NAME, 'li')
            contains = '\n'.join([li.text for li in contains_elements])
        except:contains=''
            

        note_=driver.find_element(By.XPATH, ".//div[@class='NutritionFacts_note__3X1Lo']/p")
        note = note_.text

        serving=driver.find_element(By.XPATH, "(//div[@class='Item_characteristics__text__dcfEC'])[1]")
        serving_size = serving.text

        _id=urls.split('-')
        product_id=_id[len(_id)-1]

        category_ = driver.find_elements(By.CSS_SELECTOR, "[class*='Nav_nav__1fRnP']")
        category=[cat.text for cat in category_]

        #getting all the category variations
        for variant in category:
            #swtiching to each category in a loop to crawl the variations
            driver.find_element(By.XPATH, "//button[contains(text(), '{}')]".format(variant)).click()
            time.sleep(5)

            #getting the element to crawl and transform the table in pdp page
            table_div = driver.find_elements_by_xpath('//div[@style="display: block;"]')

            #declaring the pattern to extract the data from string
            name_pattern=r'^([ a-zA-Z]+)\s*\d'
            amount_pattern = r'\b\d[.\d\s\w]+g+'

            
            skip_first = True

            #deaclring list and dictionary to stroe the crawled result
            data_dict = {}
            table_list=[]

            #looping through the table and row element
            for  div in table_div:
                tr_elements = div.find_elements_by_xpath('.//table//tr[@class="Item_table__row__3Wdx2"]')                
                for  tr in tr_elements:
                    #need to skip the 1st value which is crawled from the table because its a heading, here we declare the heading manually, so omiting that
                    if skip_first:
                        skip_first = False
                        continue  
                    row_text = tr.text

                    #alterting the crawled data to make it in a proper form using regex
                    name_match = re.search(name_pattern, row_text)
                    if name_match:
                        name=name_match.group(1)
                        
                    amount = "".join(re.findall(amount_pattern, row_text.replace('Added Sugars','')))
                    
                    drv_=row_text.split('g')
                    drv=drv_[len(drv_)-1]
                    
                    data_dict[name] = {'amount': amount, 'drv%': drv.strip()}
                table_list.append(data_dict)
                    

            #storing the variation in a dictionary
            variations_dict = {'category':variant,
                   'Nutrition Facts':table_list}
            variations_dict_list.append(variations_dict)

        if len(category)==0:

            #getting the element to crawl and transform the table in pdp page
            table_div = driver.find_elements_by_xpath(".//div[@class='NutritionFacts_nutritionFacts__1Nvz0']")

            #declaring the pattern to extract the data from string
            name_pattern=r'^([ a-zA-Z]+)\s*\d'
            amount_pattern = r'\b\d[.\d\s\w]+g+'

            
            skip_first = True

            #deaclring list and dictionary to stroe the crawled result
            data_dict = {}
            table_list=[]

            #looping through the table and row element
            for  div in table_div:
                tr_elements = div.find_elements_by_xpath('.//table//tr[@class="Item_table__row__3Wdx2"]')                
                for  tr in tr_elements:
                    #need to skip the 1st value which is crawled from the table because its a heading, here we declare the heading manually, so omiting that
                    if skip_first:
                        skip_first = False
                        continue  
                    row_text = tr.text

                    #alterting the crawled data to make it in a proper form using regex
                    name_match = re.search(name_pattern, row_text)
                    if name_match:
                        name=name_match.group(1)

                    amaount_match = re.findall(amount_pattern, row_text)
                    if amaount_match:
                        amount="".join(amaount_match)
                    
                    
                    drv_=row_text.split('g')
                    drv=drv_[len(drv_)-1]
                    
                    data_dict[name] = {'amount': amount, 'drv%': drv.strip()}
                table_list.append(data_dict)
                    

            #storing the variation in a dictionary
            variations_dict = {'category':'',
                   'Nutrition Facts':table_list}
            variations_dict_list.append(variations_dict)

            

        product_dict = {
                   'product_name': product_name,
                   'product_id':product_id,
                   'product_url':url+urls,
                   'product_image':image_urls,
                   'image_tag':image_tag,
                   'weight': weight,
                   'selling_price': price,
                    'description':description,
                    'tags':tags,
                   'ingredients': ingredients,
                    'contains':contains,
                    'note':note,
                   'serving_size':serving_size,
                    'category':category,
                     'nutrition_facts':variations_dict_list
                    }
        result.append(product_dict)
        

                  

#storing the crawled product in dataframe
df = pd.DataFrame(result)
df.to_excel('traderjoes_output.xlsx',index=False)

#storing the crawled product in json
with open('traderjoes_output.json', 'w', encoding='utf-8') as json_file:
    json.dump(result, json_file, ensure_ascii=False, indent=4)

#closing and quiting the driver
driver.close()
driver.quit()

print('traderjoes crawling is done')

