# -*- coding: utf-8 -*-

import os
import re
import time
#import json
import random
#import requests
import sqlite3 as lite

from selenium import webdriver
#from bs4 import BeautifulSoup

from .models import Account

from django.http import HttpResponse, JsonResponse


#------------------CONSTANTS----------------------

PATH = os.path.dirname(os.path.abspath(__file__)) 
PATH_CHROMEDRIVER = os.path.join(PATH, "drivers", "chromedriver.exe")

LOGIN = "79192264174"
PASSWORD = "9959095Fg"
EMAIL_PASSWORD = ""
ID = ""
HEADERS = "Mozilla/5.0 (Linux; Android 8.1.0; 1AEC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Safari/537.36"
URL_LOGIN = "https://mbasic.facebook.com/login"

def facebook(request, username):
    start_time = time.time()
    
    if request.method=='GET':
        pass
    else:
        return HttpResponse('Invalid method')

    if os.path.exists(os.path.join(PATH, "account.txt")):
        infile = open(os.path.join(PATH, "account.txt")).readlines()
        
        for line in infile:
            match = re.search(r'(\d+)\:(\S+)', line) 
            
            if match:
                new = Account(login = match[1], password = match[2])
                new.save()
                
            else:
                continue
        
        os.remove(os.path.join(PATH, "account.txt"))


    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    browser = webdriver.Chrome(PATH_CHROMEDRIVER, chrome_options=chrome_options)

    accounts = Account.objects.all()
    try:
        LOGIN = accounts[0].login
        PASSWORD = accounts[0].password
    except:
        return HttpResponse('Error. Contact technical support.')
    #LOGIN = "79192264174"
    #PASSWORD = "9959095Fg"    

    while True:
        browser.get(URL_LOGIN)
        time.sleep(random.randint(3, 5))

        # Ввод логина
        login = browser.find_element_by_name("email")
        login.send_keys(LOGIN)

        # Ввод пароля
        pswd = browser.find_element_by_name("pass")
        pswd.send_keys(PASSWORD)

        # Жмем войти
        browser.find_element_by_name("login").click()

        #Подтверждение

        try:
            browser.find_element_by_xpath('//td[@id="checkpointSubmitButton"]')
            print("OK")
        except:
            break
        else:
            Account.objects.filter(login=LOGIN).delete()
            accounts = Account.objects.all()
            try:
                LOGIN = accounts[0].login
                PASSWORD = accounts[0].password
            except:
                return HttpResponse('Error. Contact technical support.')

    #Смена языка по необходимости
    browser.get(f"https://mbasic.facebook.com/settings/language/")    
    time.sleep(random.randint(3, 5))
    
    language = browser.find_element_by_xpath('//div[@id="objects_container"]/div/div/table[1]/tbody/tr/td/h3/a/span').get_attribute("innerHTML")
    
    if language != "Русский":
        browser.get(f"https://mbasic.facebook.com/language.php")
        time.sleep(random.randint(3, 5))
        
        languages = browser.find_elements_by_xpath('//div[@id="objects_container"]/div/div/div/div/table')
        
        for language in range(len(languages)):
            name = browser.find_elements_by_xpath('//div[@id="objects_container"]/div/div/div/div/table')
            if name == "Русский":
                url_language = browser.find_element_by_xpath(f'//div[@id="objects_container"]/div/div/div/div/table[{language}]/tbody/tr/td[1]/h3/a').get_attribute("href")
                browser.get(url_language)
                time.sleep(random.randint(3, 5))


    # Загрузка профиля
    
    if isinstance(username, int):
        browser.get(f"https://mbasic.facebook.com/profile.php?id={username}")        
    else:
        browser.get(f"https://mbasic.facebook.com/{username}")  
    
    time.sleep(random.randint(3, 5))

    #Парсинг информации
    name = browser.find_element_by_xpath('//div[@id="objects_container"]/div/div/div/div[2]/div/span/div/span/strong').get_attribute("innerHTML")

    result = {
        'name' : name,
        'work' : None,
        'education' : None,
        'place' : None,
        'contact' : None,
        'basic_info' : None,
        'about' : None,
        'events' : None,
        'like' : None
    }

   #Работа - /html/body/div/div/div[2]/div/div/               /html/body/div/div/div[2]/div/div/div[2]/div
    try:
        works = browser.find_elements_by_xpath('//div[@id="work"]/div/div/div')
    except:
        result['work'] = None
    else:    
        result['work'] = list()
        
        for work in range(len(works)):
            try:
                work_name = browser.find_element_by_xpath(f'//div[@id="work"]/div/div/div[{work+1}]/div/div[1]/div[1]/span/a').get_attribute("innerHTML")
            except:
                work_name = browser.find_element_by_xpath(f'//div[@id="work"]/div/div/div[{work+1}]/div/div[1]/div[1]/span').get_attribute("innerHTML")

            work_url = browser.find_element_by_xpath(f'//div[@id="work"]/div/div/div[{work+1}]/div/a').get_attribute('href')
            work_image = browser.find_element_by_xpath(f'//div[@id="work"]/div/div/div[{work+1}]/div/a/img').get_attribute('src')
            result['work'].append({
                'name' : work_name,
                #'position' : work_position,
                #'date' : work_date,
                #'place' : work_place,
                'url' : work_url,
                'image' : work_image,
            })

    #Образование
    try:
        educations = browser.find_elements_by_xpath('//div[@id="education"]/div/div/div')
    except:
        result['education'] = None
    else:    
        result['education'] = list()

        for education in range(len(educations)):
            #education = browser.find_element_by_xpath(f'//div[@id="education"]/div/div/div[{education+1}]/div')
            try:
                education_name = browser.find_element_by_xpath(f'//div[@id="education"]/div/div/div[{education+1}]/div/div/div[1]/div/span/a').get_attribute("innerHTML")
            except:
                education_name = browser.find_element_by_xpath(f'//div[@id="education"]/div/div/div[{education+1}]/div/div/div[1]/div/span').get_attribute("innerHTML")
            #education_type = browser.find_element_by_xpath('//div/div[2]/span').get_attribute("innerHTML")
            #education_date = browser.find_element_by_xpath('//div/div[3]/span').get_attribute("innerHTML")
            try:
                education_url = browser.find_element_by_xpath(f'//div[@id="education"]/div/div/div[{education+1}]/div/div/div[1]/div/span/a').get_attribute('href')
            except:
                education_url = None
            try:
                education_image = browser.find_element_by_xpath(f'//div[@id="education"]/div/div/div[{education+1}]/div/a/img').get_attribute('src')
            except:
                education_image = None


            result['education'].append({
                'name' : f'{education_name}',
                #'type' : education_type,
                #'date' : education_date,
                'url' : f'{education_url}',
                'image' : f'{education_image}',
            })

    
    #Места проживания

    try:
        places = browser.find_elements_by_xpath('//div[@id="living"]/div/div/div')
    except:
        result['place'] = None
    else:    
        result['place'] = {}

        for place in range(len(places)):
            name = browser.find_element_by_xpath(f'//div[@id="living"]/div/div/div[{place+1}]/div/table/tbody/tr/td[1]/div/span').get_attribute("innerHTML")   
            
            place = browser.find_element_by_xpath(f'//div[@id="living"]/div/div/div[{place+1}]/div/table/tbody/tr/td[2]/div/a').get_attribute("innerHTML")
            result['place'].update({f'{name}' : f'{place}'})
            
            
    #Контакты

    try:
        contacts = browser.find_elements_by_xpath('//div[@id="contact-info"]/div/div/div')
    except:
        result['contact'] = None
    else:    
        result['contact'] = {}

        for contact in range(len(contacts)):
            name = browser.find_element_by_xpath(f'//div[@id="contact-info"]/div/div[1]/div[{contact+1}]/table/tbody/tr/td[1]/div/span').get_attribute("innerHTML")     
            try:
                contact = browser.find_element_by_xpath(f'//div[@id="contact-info"]/div/div[1]/div[{contact+1}]/table/tbody/tr/td[2]/div/a').get_attribute("innerHTML")     
            except:
                contact = browser.find_element_by_xpath(f'//div[@id="contact-info"]/div/div[1]/div[{contact+1}]/table/tbody/tr/td[2]/div').get_attribute("innerHTML") 
            
            result['contact'].update({f'{name}' : f'{contact}'})

    
    #Основная информация

    try:
        basic_infos = browser.find_elements_by_xpath('//div[@id="basic-info"]/div/div/div')
    except:
        result['basic_info'] = None
    else:    
        result['basic_info'] = {}

        for basic_info in range(len(basic_infos)):
            name = browser.find_element_by_xpath(f'//div[@id="basic-info"]/div/div[1]/div[{basic_info+1}]/table/tbody/tr/td[1]/div/span').get_attribute("innerHTML")     
            basic_info = browser.find_element_by_xpath(f'//div[@id="basic-info"]/div/div[1]/div[{basic_info+1}]/table/tbody/tr/td[2]/div').get_attribute("innerHTML") 
            
            result['basic_info'].update({f'{name}' : f'{basic_info}'})


    #О пользователе

    try:
        about = browser.find_element_by_xpath('//div[@id="bio"]/div/div/div').get_attribute("innerHTML") 
    
    except:
        pass
    
    else:
        result['about'] = str(about)

    
    #События

    try:
        events = browser.find_elements_by_xpath('//div[@id="year-overviews"]/div/div/div/div')
    except:
        result['events'] = None
    else:    
        result['events'] = {}

        for event in range(len(events)):
            if not browser.find_element_by_xpath(f'//div[@id="year-overviews"]/div/div/div/div[{event+1}]').get_attribute("innerHTML"):
                continue
            
            else:
                records = browser.find_elements_by_xpath(f'//div[@id="year-overviews"]/div/div/div/div[{event+1}]/div/div')

                for record in range(len(records)):
                    if record == 0:
                        count = browser.find_element_by_xpath(f'//div[@id="year-overviews"]/div/div/div/div[{event+1}]/div/div[1]').get_attribute("innerHTML") 
                        result['events'].update({f'{count}' : list()})
                    else:
                        result['events'][f'{count}'].append(browser.find_element_by_xpath(f'//div[@id="year-overviews"]/div/div/div/div[{event+1}]/div/div[{record+1}]/div/a').get_attribute("innerHTML")) 


    #Лайки /html/body/div/div/div[2]/div/div/div/div[4]/a[3]

    try:
        like_urls = browser.find_element_by_xpath('/html/body/div/div/div[2]/div/div/div/div[4]/a[3]').get_attribute("href") 
        
        browser.get(like_urls) 
        time.sleep(random.randint(3, 5))
        
        likes = browser.find_elements_by_xpath('/html/body/div/div/div[2]/div/div[1]/div')
    except:
        result['likes'] = None
    else:    
        result['likes'] = {}

        for like in range(len(likes)):
            if like == 0:
                continue
            
            try:
                header = browser.find_element_by_xpath(f'/html/body/div/div/div[2]/div/div[1]/div[{like+1}]/h4').get_attribute("innerHTML")
                loves = browser.find_elements_by_xpath(f'/html/body/div/div/div[2]/div/div[1]/div[{like+1}]/div/div')
                result_like = {}

                for love in range(len(loves)):
                    like_name = browser.find_element_by_xpath(f'/html/body/div/div/div[2]/div/div[1]/div[{like+1}]/div[{love+1}]/div/div/a/span').get_attribute("innerHTML")
                    like_url = browser.find_element_by_xpath(f'/html/body/div/div/div[2]/div/div[1]/div[{like+1}]/div[{love+1}]/div/div/a').get_attribute("href")
                    result_like.update({f'{like_name}':f'{like_url}'})

                result['likes'].update({f'{header}' : f'{result_like}'})
            
            except:
                
                try:
                    header = browser.find_element_by_xpath(f'/html/body/div/div/div[2]/div/div[1]/div[{like+1}]/div/div/div/div/div/h3').get_attribute("innerHTML")
                    
                    loves = browser.find_elements_by_xpath(f'/html/body/div/div/div[2]/div/div[1]/div[{like+1}]/div/div')
                    
                    for love in range(len(loves)):
                        like_name = browser.find_element_by_xpath(f'/html/body/div/div/div[2]/div/div[1]/div[{like+1}]/div/div/div/div/div/div/div[{love+1}]/div/div/a/span').get_attribute("innerHTML")
                        like_url = browser.find_element_by_xpath(f'/html/body/div/div/div[2]/div/div[1]/div[{like+1}]/div/div/div/div/div/div/div[{love+1}]/div/div/a').get_attribute("href")
                    
                    result_like.update({f'{like_name}':f'{like_url}'})         
                
                
                except:
                    result['likes'] = None

    browser.quit()
    
    print("--- %s seconds ---" % (time.time() - start_time))
    
    return JsonResponse(result, safe=False)

