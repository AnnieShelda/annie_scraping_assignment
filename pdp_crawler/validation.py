#!/usr/bin/env python
# coding: utf-8

# In[29]:


import json
import pandas as pd
import re
import warnings
warnings.filterwarnings("ignore")

class Validation:
    
    def __init__(self):
        self.errors = []
    
    def mandatory_column_check(self, mandatory_fields, df):
        #looping through the columns and checking the presence
        for column in mandatory_fields:
            if column not  in df.columns:
                self.errors.append("ERROR: mandatory field '{}' is missing.".format(column))
               
    def empty_value_check(self,mandatory_field_column,df):
        #checking if there is any empty value is present in the field
        for column in mandatory_field_column:
            if df[column].isnull().any():
                self.errors.append("ERROR: some values are missing in the field '{}'.".format(column))
            if (df[column] == '').any():
                self.errors.append("ERROR: some values are missing in the field '{}'.".format(column))
            
    def url_format_check(self,img_url,image_url):
        #checking if url is in correct for by checkking if it has https
        if 'https' not in img_url:
            self.errors.append("ERROR: url is not in the proper format for the field '{}'.".format(column))
            
    def weight_format_check(self,weight_value,weight):
        #checking if weight is in proper format 
        #(keeping only g and oz so that we can see some validation error result), we can add some other weight variations using regex
        valid_suffixes = ['g', 'oz']
        weight_value=weight_value.lower()
        if not any(weight_value.endswith(suffix) for suffix in valid_suffixes):
            self.errors.append("ERROR: weight is not in the proper format for the value '{}' in the column {}.\n".format(weight_value,weight))
 
            
    def price_check(self,df,column):
        #replacing all the string so that we can conver it to float
        df[column] = df[column].astype(str)
        df[column] = df[column].replace({'\$': '', '£': '','':0}, regex=True)
        df[column]=df[column].fillna(0)
        
        #using try and expect so that i can see what other new charaters are there to replace 
        try:
            df[column]=df[column].astype(float)
        except:
            self.errors.append("ERROR: price is not in the proper format for the field '{}'.".format(column))
        
        # Check for negative prices
        negative_prices = df[df[column] < 0][column]
        if not negative_prices.empty:
            self.errors.append("ERROR: price are in negative in the field '{}'.".format(column))
            
                    
    def unique_id_check(self,df,column):
        #checking if id is unique in all variations 
        if df[column].nunique() != df.shape[0]:
            self.errors.append("ERROR: id are not unique in the field '{}'.".format(column))    
            


    def validate_foreign_fortune(self, df):
        print('PERFORMING VALIDATION FOR FOREIGN FORTUNE')
        #empting all the previous errors
        self.errors = []
        
        #1) mandatory field check in main dataframe
        mandatory_fields = ['product_name', 'image_url', 'brand', 'variations']
        self.mandatory_column_check(mandatory_fields, df)
        
                
        #2) mandatory field check in variations
        for var in df['variations']:
            variation_df=pd.DataFrame(var)
            madatory_variation_fields=['product_id','product_url']
            self.mandatory_column_check(madatory_variation_fields, variation_df)
                    
        #3) checking if important fields values are not empty in df
        mandatory_field_column=['product_name','image_url']
        self.empty_value_check(  mandatory_field_column,df)
        
        #4) checking if important fields values are not empty in variations
        mandatory_variation_field_column=['product_id','product_url']
        for var in df['variations']:
            variation_df=pd.DataFrame(var)
            self.empty_value_check(mandatory_variation_field_column, variation_df)
        
        #5) checking the url format for image url in df
        for image_url in df['image_url']:
            for img in image_url:
                self.url_format_check(img,'image_url')
        
        #6) checking the url format for product url in variations
        for var in df['variations']:
            variation_df=pd.DataFrame(var)
            for product_url in variation_df['product_url']:
                self.url_format_check(product_url,'product_url')
        
        #7) checking the price format in variations
        for var in df['variations']:
            variation_df=pd.DataFrame(var)
            self.price_check(variation_df,'price')
            
        #8) checking if all the product id are unique
        for var in df['variations']:
            variation_df=pd.DataFrame(var)
            self.unique_id_check(variation_df,'product_id')
            
        if self.errors:
            print("validation error found:")
            for error in self.errors:
                print(error)
        else:
            print('no validation errors\n')
        
        
    
    
    
    def validate_chocolat(self,df):
        print('PERFORMING VALIDATION FOR CHOCOLAT')
        
        #empting all the previous errors
        self.errors = []
        
        #1) mandatory field check in main dataframe
        mandatory_fields = ['variations', 'description', 'ingredients', 'nutritional_values',
       'allergy_alert', 'vegan', 'price_per_kilo', 'all_images', 'all_videos']
        self.mandatory_column_check(mandatory_fields, df)
        
                
        #2) mandatory field check in variations
        madatory_variation_fields=['product_name', 'product_id', 'product_url', 'product_image']
        for var in df['variations']:
            variation_df=pd.DataFrame(var)
            self.mandatory_column_check(madatory_variation_fields, variation_df)
                    
        #3) checking if important fields values are not empty in df  
        mandatory_field_column=['variations', 'all_images']
        self.empty_value_check(  mandatory_field_column,df)
        
        #4) checking if important fields values are not empty in variations
        mandatory_variation_field_column=['product_name', 'product_id', 'product_url', 'product_image']
        for var in df['variations']:
            variation_df=pd.DataFrame(var)
            self.empty_value_check(mandatory_variation_field_column, variation_df)
            
        #5) checking the url format for image url in df
        for image_url in df['all_images']:
            for img in image_url:
                self.url_format_check(img,'all_images')
        
        #6) checking the url format for product url in variations
        for var in df['variations']:
            variation_df=pd.DataFrame(var)
            for product_url,image_url in zip(variation_df['product_url'],variation_df['product_image']):
                self.url_format_check(product_url,'product_url')
                self.url_format_check(product_url,'product_image')
        
        #7) checking the price format in variations
        for var in df['variations']:
            variation_df=pd.DataFrame(var)
            self.price_check(variation_df,'selling_price')
        
        #8) checking if all the product id are unique
        for lis in df['variations']:
            variation_df=pd.DataFrame(lis)
            self.unique_id_check(variation_df,'product_id')
        
        #7) checking the weight format in variations
        for var in df['variations']:
            variation_df=pd.DataFrame(var)
            for weight_value in variation_df['weight']:
                self.weight_format_check(weight_value,'weight')
                
                
        if self.errors:
            print("validation error found:")
            for error in self.errors:
                print(error)
        else:
            print('no validation errors\n')


        
        
    def validate_tradersjoe(self,df):
        print('PERFORMING VALIDATION FOR TRADERSJOE')
        
        #empting all the previous errors
        self.errors = []
        
        #1) mandatory field check in main dataframe
        mandatory_fields = ['product_name', 'product_id', 'product_url', 'product_image',
           'image_tag', 'weight', 'selling_price', 'description', 'tags',
           'ingredients', 'contains', 'note', 'serving_size', 'category',
           'nutrition_facts']
        self.mandatory_column_check(mandatory_fields, df)

        #2) checking if important fields values are not empty in df  
        mandatory_field_column=['product_name', 'product_id', 'product_url', 'product_image']
        self.empty_value_check(  mandatory_field_column,df)
        
        #3) checking the url format for image url in df
        for image_url in df['product_image']:
            for img in image_url:
                self.url_format_check(img,'product_image')

        #4) checking the price format in variations
        self.price_check(df,'selling_price')

        #5) checking if all the product id are unique
        self.unique_id_check(df,'product_id')

        #6) checking the weight format in df
        for weight_value in df['weight']:
            self.weight_format_check(weight_value,'weight')
            
        if self.errors:
            print("validation error found:")
            for error in self.errors:
                print(error)
        else:
            print('no validation errors\n')

               


# In[30]:




validator = Validation()

with open('foreignfortune_output.json', 'r') as json_file:
    foreignfortune_data = json.load(json_file)
foreignfortune_df = pd.DataFrame(foreignfortune_data)
validator.validate_foreign_fortune(foreignfortune_df)


with open('lechocolat_output.json', 'r', encoding='utf-8') as json_file:
    lechocolat_data = json.load(json_file)
lechocolat_df = pd.DataFrame(lechocolat_data)
validator.validate_chocolat(lechocolat_df)


with open('traderjoes_output.json', 'r', encoding='utf-8') as json_file:
    traderjoes_data = json.load(json_file)
traderjoes_df = pd.DataFrame(traderjoes_data)
validator.validate_tradersjoe(traderjoes_df)


# In[ ]:




