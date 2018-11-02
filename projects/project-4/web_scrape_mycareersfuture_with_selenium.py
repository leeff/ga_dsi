# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 02:15:59 2018

@author: Lee Fung Fung
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0


import os, sys, random
from datetime import datetime
from time import sleep
from scrapy.selector import Selector
import pandas as pd

chromedriver = "c:/Users/mail/Downloads/chromedriver_win32/chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver

# Set up options so that browser will not load images
chromeOptions = webdriver.ChromeOptions()
prefs = {'profile.managed_default_content_settings.images':2}
chromeOptions.add_experimental_option("prefs", prefs)

URL_BASE = 'https://www.mycareersfuture.sg/search?search=<POSITION>&sortBy=new_posting_date'
POSITIONS = [
        #'data%20engineer',
        #'data%20scientist',
        #'machine%20learning',
        #'data%20analyst',
        #'business%20analyst',
        #'business%20intelligence',
        #'big%20data',
        'data%20mining',
        'predictive%20modeling'
        ]

def parse_mycareersfuture_job_details(url, driver):
  
    driver.get(url)
    #sleep(random.randint(2, 10))
    
    try:
        # give up to 10 seconds for the content elements to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "content")))
    except TimeoutException:
        print('Timeout Exception waiting for url %s' % url) 
        return None,None
    except Exception as exception:
        print('Unexpected error %s' % type(exception).__name__) 
        print('Unexpected error class name %s ' % exception.__class__.__name__)
        print('Unexpected error while processing url %s - %s '.format(sys.exc_info()[0],url))
        return None,None

    html = driver.page_source    
    sel = Selector(text=html)  
    
    job_description_list = sel.xpath('//div[@id="job_description"]/div[@id="content"]/child::*').extract()
    job_description = ''.join(job_description_list)
    
    job_requirements_list = sel.xpath('//div[@id="requirements"]/div[@id="content"]/child::*').extract()
    job_requirements = ''.join(job_requirements_list)

    return (job_description, job_requirements)

    

def parse_mycareersfuture_search_page(url, driver, job_details_driver, page_num=0, data=False):
    
    current_page_url = url+'&page='+str(page_num)
    driver.get(current_page_url)

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "card-list")))

    # for first page this Update Search will appear, give up to 5 seconds for it
#    if (type(data)==bool):
#        #element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "basicbutton")))
#        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//button[text()="Update Search"]')))
#        element.click()
#        except TimeoutException:
#           print('Timeout Exception waiting for url %s' % current_page_url) 

    #sleep(random.randint(2, 10))

    # It's always good to check that we have the page we think we do.
    assert "MyCareersFuture" in driver.title, "Wrong website: %s" % driver.title
    
    job_title, job_company = '',''
    
    try:
            
        # Grab the page source.
        html = driver.page_source

        main_sel = Selector(text=html)    

        if page_num==0: print('Number of jobs for url : {} is {}: '.format(url, main_sel.xpath('//*[@id="search-results-message"]/div/text()').extract_first()))

        for job_sel in (main_sel.xpath('//div[@class="card-list"]/div[contains(@id,"job-card")]')):
     
            job_title = job_sel.xpath('.//h1[@name="job_title"]/text()').extract_first()
            job_company = job_sel.xpath('.//p[@name="company"]/text()').extract_first() 
     
                                 
            job_location =  job_sel.xpath('.//p[@name="location"]/text()').extract_first()
            job_seniority = job_sel.xpath('.//p[@name="seniority"]/text()').extract_first()
            job_category = job_sel.xpath('.//p[@name="category"]/text()').extract_first()
            job_employment_type = job_sel.xpath('.//p[@name="employment_type"]/text()').extract_first()
         
            # salary
            job_salary_range = job_sel.xpath('.//span[contains(@class,"salary_range")]/div/span[@class="dib"]/text()').extract()
            job_salary_range_from = None
            job_salary_range_to = None
            job_salary_type = None
            if (len(job_salary_range)>0):
                job_salary_range_from = job_salary_range[0]
                job_salary_range_to = job_salary_range[1] if len(job_salary_range) > 1 else job_salary_range[0]
                job_salary_type = job_sel.xpath('.//span[contains(@class,"salary_type")]/text()').extract_first() 
                
            job_details_path = job_sel.xpath('.//a/@href').extract_first()
            job_details_url  =  "https://www.mycareersfuture.sg" + job_details_path
       
            job_description,job_requirements = parse_mycareersfuture_job_details(job_details_url, job_details_driver)
             
            # If there's data, append them. 
            # If not, it's the first iteration
            scraped = dict(
                job_title   =  job_title, 
                job_company    =  job_company,
                job_location = job_location,
                job_seniority = job_seniority,
                job_category = job_category,
                job_employment_type = job_employment_type,
                job_salary_range_from = job_salary_range_from,
                job_salary_range_to = job_salary_range_to,
                job_salary_type = job_salary_type,
                job_details_url = job_details_url,
                job_description = job_description,
                job_requirements = job_requirements
            )   
     
    
            df = pd.DataFrame(scraped,index=[0])
            if type(data) != bool:
                data = data.append(df)
            else:
                data = df
                 
        # Check if there are more pages than current page
        more_anchor  =  main_sel.xpath('//span[@type="action"]/text()').extract()
        more_pages = False
        for p in more_anchor:
            if p.isdigit() and (int(p) > page_num + 1):
                more_pages = True
                break
        if more_pages: 
            print("Fetching Next Page %s..." % (page_num+1))
            return parse_mycareersfuture_search_page(url, driver, job_details_driver, page_num+1, data)   
 
        if type(data) != bool: data.reset_index()    
    

    except Exception as exception:
        print('Exception while processing url %s' % current_page_url) 
        if (job_title): print('Error while processing job title {} at company {}.'.format(job_title, job_company))
        print('Unexpected error %s' % type(exception).__name__) 
        print('Unexpected error class name %s ' % exception.__class__.__name__)      
        raise exception
    
    return data


for position in POSITIONS:
    driver = webdriver.Chrome(chromedriver, options=chromeOptions) 
    job_details_driver = webdriver.Chrome(chromedriver, options=chromeOptions)                

    df = parse_mycareersfuture_search_page(URL_BASE.replace('<POSITION>',position), driver, job_details_driver)
    filename = position + datetime.now().strftime('%Y%m%d%H%m%S') + '.csv'
    df.to_csv(filename)

    job_details_driver.quit()
    driver.quit()

#test_driver = webdriver.Chrome(chromedriver, options=chromeOptions)
#a,b = parse_mycareersfuture_job_details('https://www.mycareersfuture.sg/job/senior-executive-data-services-singapore-land-authority-1dc412ae4cb015131753c20a17a4ab84', test_driver)    