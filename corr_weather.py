#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
import time

import pymysql

from datetime import datetime
import time

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

get_ipython().run_line_magic('matplotlib', 'inline   # 웹 브라우저에 그림 출력 가능')

import matplotlib.font_manager as fm

font_name = fm.FontProperties(fname = 'C:\Windows\Fonts\malgun.ttf').get_name()
plt.rc('font', family = font_name)

mpl.rcParams['axes.unicode_minus'] = False


# # 날씨 크롤링

# In[178]:


driver = webdriver.Chrome('C:\chrome/chromedriver.exe')


# In[2]:


# for 문을 줄이기 위한 노력

year_month_list = []
year_month_2020 = []
for year in range(2015, 2020):
    for month in range(1, 13):
        year_month = (year, month)
        year_month_list.append(year_month)
        
for month in range(1, 6):
    year_month = (2020, month)
    year_month_2020.append(year_month)


# In[4]:


year_month_2020


# In[181]:


#total_temp = pd.DataFrame(columns=['날짜', '평균기온', '최고기온', '최저기온', '평균운량', '강수량'])

for year, month in year_month:
    print(year, month)
    url = 'https://www.weather.go.kr/weather/climate/past_cal.jsp?stn=108&yy=%d&mm=%d' %(year, month)
    driver.get(url)
    time.sleep(2)
    
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find('table', {'class' : 'table_develop'})
    trs = table.findAll('tr')
    
    # 날씨 뽑을 준비
    date_list = []
    mean_tem_list = []
    high_tem_list = []
    low_tem_list = []
    cloud_tem_list = []
    rain_tem_list = []
    
    for i in range(1, len(trs) // 2 + 1):
        # 날짜 뽑기
        tds_date = trs[2*i-1].findAll('td')
        for td in tds_date:
            if td.text == '\xa0':
                continue
            date = str(year) + '-' + str(month).zfill(2) + '-' + td.text.split('일')[0].zfill(2)
            date_list.append(date)
    
        # 날씨 뽑기
        tds_weather = trs[2*i].findAll('td')
        for td in tds_weather:
            if td.text == '\xa0':
                continue
            
            temp = td.text.split(':')
            mean_tem = float(temp[1].split('℃')[0])
            high_tem = float(temp[2].split('℃')[0])
            low_tem = float(temp[3].split('℃')[0])
            cloud_tem = float(temp[4].split('일')[0])
        
            if temp[5] == ' - ':
                rain_tem = 0.0
            else:
                rain_tem = float(temp[5].split('mm')[0])

            mean_tem_list.append(mean_tem)
            high_tem_list.append(high_tem)
            low_tem_list.append(low_tem)
            cloud_tem_list.append(cloud_tem)
            rain_tem_list.append(rain_tem)
            
    new_data = pd.DataFrame(data = {'날짜' : date_list, '평균기온' : mean_tem_list, '최고기온' : high_tem_list,
                                '최저기온' : low_tem_list, '평균운량' : cloud_tem_list, '강수량' : rain_tem_list})
        
    total_temp = pd.concat([total_temp, new_data], ignore_index=True)

driver.close()


# In[233]:


total_temp.head()


# In[228]:


total_temp.to_csv('data/날씨.csv', encoding = 'utf-8')


# # CORRELATION

# In[344]:


# 분석 DB에서 데이터 불러오기
connect = pymysql.connect(host='192.168.0.4', user='NDCOM', password='1111', db='mcrawling',  charset='utf8')
curs = connect.cursor()
sql = "select date, ranking, rank1, rank2 from emoti where ranking >= 50"
curs.execute(sql)
datas = curs.fetchall()
data = pd.DataFrame(datas, columns=['날짜', '순위', '1순위', '2순위'])


# In[345]:


data = pd.DataFrame(datas, columns=['날짜', '순위', '1순위', '2순위'])

index0 = data[data['1순위'] == '0'].index
data.loc[index0, :]

data.drop(index0, axis = 0)


# In[351]:


# 1순위의 감정 빈도 확인
emotion = ['happy', 'enjoy', 'comfort', 'horror', 'angry', 'sad']

for emo in emotion:
    list_em=np.array(data['1순위'].str.contains(emo))
    data[emo] = list_em  

pdf = data.pivot_table(('happy','sad','enjoy','horror','angry','comfort'), 
                             '날짜', aggfunc='sum')
pdf.head()


# In[352]:


pdf = pdf.reset_index()
pdf.head()


# In[353]:


total_temp['날짜'] = pd.to_datetime(total_temp['날짜'])
total_temp = total_temp.set_index('날짜')


# In[354]:


total_temp = total_temp.reset_index()
total_temp.head()


# In[355]:


data_rank1 = pd.merge(pdf, total_temp)
data_rank1.head()


# In[310]:


data_rank1.corr()


# In[342]:


# 1순위 correlation
plt.figure(figsize=(10, 10))
sns.heatmap(data = data_rank1.corr(), annot=True, fmt = '.2f', linewidths=.5, cmap='Blues')


# In[315]:


# 2순위
pdf_rank2 = pdf_rank2.reset_index()
data_rank2 = pd.merge(pdf_rank2, total_temp)
data_rank2.head()


# In[343]:


plt.figure(figsize=(10, 10))
sns.heatmap(data = data_rank2.corr(), annot=True, fmt = '.2f', linewidths=.5, cmap='Blues')


# # The End
