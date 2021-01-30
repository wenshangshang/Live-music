import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from transCoordinateSystem import bd09_to_wgs84

def band_infor(link,headers):
    band = requests.get(link,headers=headers)
    if band.status_code == 200:
        htmls = band.text
        soups = BeautifulSoup(htmls,"lxml")
        try:
            name = soups.find_all(name='div',attrs={"class": "name"})[0].text
        except:
            name = "未知姓名"
        try:
            city = soups.find_all(name="ol",attrs={"class":"dec"})[0].li.text.replace("地区：","").replace(" ","")
        except:
            city = "未知城市"
        try:
            style = soups.find_all(name="ol",attrs={"class":"dec"})[0].find_all(name='li')[1].text.replace(" ","").replace("\n","").replace("风格：","").replace("\t","")
        except:
            style = "未知风格"
        infor = {"乐队名称":name,"乐队城市":city,"乐队风格":style}
    return infor

def web_analysis(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"}
    b = requests.get(url,headers=headers)
    data = []
    if b.status_code == 200:
        html = b.text
        soup = BeautifulSoup(html, 'lxml')
        
        #基础信息检索
        name = soup.find_all(name='h1',attrs={"class": "goods-name"})[0].text
        name = name.replace("\n","").replace("\t","").replace(" ","")
        all_data = soup.find_all(name='ul',attrs={"class": "items-list"})[0].find_all(name='li')
        time = all_data[0].text.replace("\n","").replace("\t","").replace(" ","").replace("演出时间：","")
        livehouse = all_data[2].text.replace("\n","").replace("\t","").replace(" ","").replace("场地：","")
        locat = all_data[3].a["locate"].split(",")
        coord_wgs84 = bd09_to_wgs84(float(locat[0]), float(locat[1]))
        lng = coord_wgs84[0]
        lat = coord_wgs84[1]
        types = soup.find_all(name='div',attrs={"class": "goods-type"})[0].text
        piece = soup.find_all(name='ul',attrs={"class": "ticket MT30"})[0].find_all(name='li')[0].attrs["sellingprice"]
        paizi = soup.find_all(name='div',attrs={"class": "activity-hoster ll"})
        if str(paizi) != "[]":
            paizi = paizi[0].text.replace("\n","").replace("\t","").replace(" ","").replace("演出主办方","")
        information = {"演出名称":name,"演出时间":time,"演出场所":livehouse,"lng":lng,"lat":lat,"演出类型":types,"价格":int(piece),"厂牌":paizi,"url":url}
        
        #乐队信息分条
        star = all_data[1].find_all(name='a')
        band = []
        for i in star:
            link = i.attrs["href"]
            a = band_infor(link,headers)
            a.update(information)
            band.append(a)
        return band

df = pd.DataFrame(columns=["乐队名称","乐队城市","乐队风格","演出名称","演出时间","演出场所","lng","lat","演出类型","价格",
                           "厂牌","链接"])  #构建一个空表
data = []
number = 0

file_df = pd.read_excel("/Users/creative/OneDrive - stu.hit.edu.cn/课程资料/2020秋 音乐消费论文/数据收集/总表/数据总表.xlsx",sheet_name='January')
for i in range(len(file_df)):
    number += 1
    if number/100 % 1 == 0:
        time.sleep(10)
    link = file_df.loc[i,"标题链接"]
    print("任务正在抓取第{}个链接{}，还剩余{}个链接未完成".format(number,link,len(file_df)-number))


    try:
        web_data = web_analysis(link)
        for i in web_data:
            data.append(i)
    except:
        try:
            time.sleep(5)
            web_data = web_analysis(link)
            for i in web_data:
                data.append(i)
        except:
            try:
                time.sleep(5)
                web_data = web_analysis(link) 
                for i in web_data:
                    data.append(i)
            except:
                pass
                
    

df = df.append(data,ignore_index=True)
df.to_excel("/Users/creative/OneDrive - stu.hit.edu.cn/课程资料/2020秋 音乐消费论文/数据收集/处理数据/2021January.xlsx") 
