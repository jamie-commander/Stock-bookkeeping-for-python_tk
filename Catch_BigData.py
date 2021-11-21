import requests
import urllib.request
import os
import re
import random
import json
import time
import sys
#import proxy
import socket
import socks #pip install PySocks
#from stem import Signal
#from stem.control import Controller
#from tkinter import *
#from tkinter import ttk
#from lxml import html
#from threading import Timer
from bs4 import BeautifulSoup
#from openpyxl import Workbook
#from openpyxl import load_workbook
#from openpyxl.styles import colors, Font, Fill, NamedStyle
#from openpyxl.styles import PatternFill, Border, Side, Alignment
#print("hello world")
#global fu
#fu=0
class Catch_Stocks_BigData:
    def __init__(self):
        self.head = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36"
        }
        self.filepath = os.path.join(os.getcwd(),"BigData")
        self.filepath_tse = os.path.join(self.filepath,"tse")
        self.filepath_otc = os.path.join(self.filepath,"otc")
        self.filepath_tse_stocks = os.path.join(self.filepath,"tse_stocks")
        self.filepath_otc_stocks = os.path.join(self.filepath,"otc_stocks")
        self.Simple_Data_filename = 'Simple_Data'
        self.time_start = int(time.mktime(time.strptime('2011/08/01', "%Y/%m/%d")))
        self.filepath_Stocks = os.path.join(self.filepath,"Stocks")
        if(os.path.isdir(self.filepath) == False):
            os.mkdir(self.filepath)
        if(os.path.isdir(self.filepath_tse) == False):
            os.mkdir(self.filepath_tse)
        if(os.path.isdir(self.filepath_otc) == False):
            os.mkdir(self.filepath_otc)
        try:
            with open(os.path.join(self.filepath,self.Simple_Data_filename+".json"),'r') as f:
                self.Stocks_Simple_Data =json.load(f)
                #self.Stocks_Simple_Data['上市']['最近更新日期'] = 'test'
            if(self.Stocks_Simple_Data["上市"]["最近更新日期"] != time.strftime("最近更新日期:%Y/%m/%d",time.localtime())):
                self.Time_Simple_Data_updata()
        except:
            self.Time_Simple_Data_updata()
        #self.proxy_data = proxy.proxy().get_proxy()
        #self.filepath = os.path.join(self.filepath,"上市")
        #self.Initial_Opening()
        #print(len(self.Stocks_Simple_Data['上市']['股票']))
        #print(len(self.Stocks_Simple_Data['上櫃']['股票']))
        #print(len(self.Stocks_Simple_Data['興櫃']['股票']))
        #self.Make_Stocks_Data()
    def Initial_Simple_Data_update(self):#取得所有上市上櫃興櫃股票簡化資料
        HTML_DATA ={'上市' : '2', '上櫃' : '4', '興櫃' : '5' }
        Stocks_Simple_Data = dict()
        for HTML_DATA_Str in HTML_DATA:
            rs=requests.session()#建立一個session
            url="https://isin.twse.com.tw/isin/C_public.jsp?strMode=" + HTML_DATA[HTML_DATA_Str]#HTML_DATA
            time_out = 3
            while True:
                try:
                    if(time_out != 0):
                        Listed_Stocks_Html = rs.get(url, headers = self.head, timeout = 3)#對伺服器發出get
                        break
                    else:
                        print('伺服器維護中或是無網際網路連線。')
                        return False
                except:
                    time.sleep(random.randint(1,3)/10)
                    time_out = time_out - 1
                    continue
            #print(Listed_Stocks_Html)#確認是否請求成功 200
            #Listed_Stocks_Html.encoding = "UTF8"#編碼成Big5
            Listed_Stocks_Soup = BeautifulSoup(Listed_Stocks_Html.text, 'html.parser')#解析。
            #print(Listed_Stocks_Soup)#查看解析後內容
            Listed_Stocks_table = Listed_Stocks_Soup.find_all("table")[1].select('tr')#取得表單資料
            #print(Listed_Stocks_table[2])
            Listed_Stocks_updata_time = Listed_Stocks_Soup.find("body").select('h2')[1]#取得更新日期
            Listed_Stocks_updata_time = ((Listed_Stocks_updata_time.text).split(' '))[0]
            #print(Listed_Stocks_updata_time)
            #print("　")
            #print(" ")
            Stocks_Simple_type = list()
            Stocks_Simple_type_Data = dict()
            Stocks_Simple_type_Data.setdefault("最近更新日期", Listed_Stocks_updata_time)
            Listed_Stocks_table = reversed(Listed_Stocks_table[1:len(Listed_Stocks_table)])
            for Listed_Stocks_tr in Listed_Stocks_table:
                Listed_Stocks_td = Listed_Stocks_tr.select("td")
                if(len(Listed_Stocks_td) == 1):
                    bufstr = (Listed_Stocks_td[0].text).split(' ')
                    for i in bufstr:
                        if(i != ''):
                            bufstr = i
                            break
                    if(bufstr != '上市認購(售)權證' and bufstr != '上櫃認購(售)權證'):
                        Stocks_Simple_type.reverse()
                        Stocks_Simple_type_Data.setdefault(bufstr, Stocks_Simple_type)
                    Stocks_Simple_type = []
                else:
                    Listed_Stocks_td[0] = (Listed_Stocks_td[0].text).split("　")
                    Listed_Stocks_td[0][0] = Listed_Stocks_td[0][0].split(' ')
                    Listed_Stocks_td[0][0] = ''.join(Listed_Stocks_td[0][0])
                    data = {
                        '證券代號' : Listed_Stocks_td[0][0] if Listed_Stocks_td[0] else '',
                        '證券名稱' : Listed_Stocks_td[0][1] if Listed_Stocks_td[0] else '',
                        '國際證券辨識號碼' : Listed_Stocks_td[1].text if Listed_Stocks_td[1].text else '',
                        '上市日' : Listed_Stocks_td[2].text if Listed_Stocks_td[2].text else '',
                        '市場別' : Listed_Stocks_td[3].text if Listed_Stocks_td[3].text else '',
                        '產業別' : Listed_Stocks_td[4].text if Listed_Stocks_td[4].text else '',
                        'CFICode' : Listed_Stocks_td[5].text if Listed_Stocks_td[5].text else ''
                        }
                    Stocks_Simple_type.append(data)
            Stocks_Simple_Data.setdefault(HTML_DATA_Str, Stocks_Simple_type_Data)#HTML_DATA_Str
            Stocks_Simple_type_Data = {}
        #print(Stocks_Simple_Data['上市']['股票'][0])
        #print(Stocks_Simple_Data['上櫃']['股票'][0])
        #print(Stocks_Simple_Data['興櫃']['股票'][0])
        return Stocks_Simple_Data
    def Initial_Opening(self):#抓取讀取資料主程式
        try:
            self.ALL_Data_main()#爬蟲抓資料主程式
            self.Make_Stocks_Data()#建立個股資訊主程式
            return True
        except:
            return False
    def Time_Simple_Data_updata(self):#資料更新資料
        Stocks_Simple_Data_buf = self.Initial_Simple_Data_update()
        if(Stocks_Simple_Data_buf):
            self.Stocks_Simple_Data = Stocks_Simple_Data_buf
            with open(os.path.join(self.filepath,self.Simple_Data_filename+".json"),"w") as f:
                json.dump(self.Stocks_Simple_Data,f)
        return True
    def ALL_Data_main(self):#上櫃市場日期格式 民國/月/日 上市市場日期格式 西元月日
        self.path_data = {
            'tse' : {'Stocks': os.path.join(self.filepath_tse,"Stocks"),#https://www.twse.com.tw and https://www.tpex.org.tw 歷史股價，交易日所有證券成交資訊儲存為一個檔案，檔案名稱定義為該交易日日期名稱的json檔
                     'com_info': os.path.join(self.filepath_tse,"com_info"),#https://mops.twse.com.tw 僅有一個檔案，抓取所有個股公司資訊，檔案名稱為com_info的json檔。
                     'dividend': os.path.join(self.filepath_tse,"dividend"),#https://mops.twse.com.tw 股利分派情形，一檔個股歷史配息資訊儲存為一個檔案，檔案名稱定義為該個股證券代號的json檔。
                     'Ex_Dividends_Right_Notice_date': os.path.join(self.filepath_tse,"Ex_Dividends_Right_Notice_date"),#https://www.twse.com.tw and https://www.tpex.org.tw 除權息預告日
                     'Ex_Dividends_Right_Calculate': os.path.join(self.filepath_tse,"Ex_Dividends_Right_Calculate"),#https://www.twse.com.tw and https://www.tpex.org.tw 除權息計算表，避免資料過大以一年一年區分
                   },
            'otc' : {'Stocks': os.path.join(self.filepath_otc,"Stocks"),
                     'com_info': os.path.join(self.filepath_otc,"com_info"),
                     'dividend': os.path.join(self.filepath_otc,"dividend"),
                     'Ex_Dividends_Right_Notice_date': os.path.join(self.filepath_otc,"Ex_Dividends_Right_Notice_date"),
                     'Ex_Dividends_Right_Calculate': os.path.join(self.filepath_otc,"Ex_Dividends_Right_Calculate"),
                   },
            }
        #-------------------------------------------爬取網站https://www.twse.com.tw 與 https://www.tpex.org.tw  path:Stocks 證券歷史成交資訊
        self.path_data_url_Stocks_list = {
            'tse' : {self.path_data['tse']['Stocks'] : ['https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date=','&type=ALL'],#網址+日期
                    },
            'otc' : {self.path_data['otc']['Stocks'] : ['https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&d=',''],
                    },
            }
        for market in self.path_data_url_Stocks_list:
            for path in self.path_data_url_Stocks_list[market]:
                #True
                #print(market)
                #print(path)
                #print(path_data_url_list[i][j])
                self.Time_ALL_Data_Stocks_updata(market,path,self.path_data_url_Stocks_list[market][path])#該函示適用爬每日資料頁面，不適用一次爬整個月資料的頁面。
        #Catch_BigData.Time_ALL_Data_updata(self)
        #-----------------------------------------------------爬取網站https://mops.twse.com.tw com_info path:com_info公司基本資料-----------------------------------------------------------------
        self.path_data_url_com_info_list = {
            'tse' : {self.path_data['tse']['com_info'] : {'url':'https://mops.twse.com.tw/mops/web/ajax_t51sb01', 'data':{'encodeURIComponent': '1','step':'1','firstin':'1','TYPEK':'sii','code':''},},#網址+head資訊
                    },
            'otc' : {self.path_data['otc']['com_info'] : {'url':'https://mops.twse.com.tw/mops/web/ajax_t51sb01', 'data':{'encodeURIComponent': '1','step':'1','firstin':'1','TYPEK':'otc','code':''},},
                    },
            }
        for market in self.path_data_url_com_info_list:
            for path in self.path_data_url_com_info_list[market]:
                True
                #print(market)
                #print(path)
                #print(path_data_url_list[i][j])
                #self.Time_ALL_Data_com_info_updata(market,path,self.path_data_url_com_info_list[market][path])#公司基本資料僅需爬一次
        #self.Time_ALL_Data_com_info_updata('tse',self.path_data['tse']['com_info'],self.path_data_url_com_info_list['tse'][self.path_data['tse']['com_info']])
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------爬取網站https://mops.twse.com.tw path:dividend股利分派情形----------------------------------------------------
        self.path_data_url_dividend_list = {
            'tse' : {self.path_data['tse']['dividend'] : {'url':'https://mops.twse.com.tw/mops/web/ajax_t05st09_2', 'data':{'encodeURIComponent': '1',
                                                                                                                            'step': '1',
                                                                                                                            'firstin': '1',
                                                                                                                            'off': '1',
                                                                                                                            'keyword4': '',
                                                                                                                            'code1': '',
                                                                                                                            'TYPEK2': '',
                                                                                                                            'checkbtn':'', 
                                                                                                                            'queryName': 'co_id',
                                                                                                                            'inpuType': 'co_id',
                                                                                                                            'TYPEK': 'all',
                                                                                                                            'isnew': 'false',
                                                                                                                            'co_id': '2330',#證券代號
                                                                                                                            'date1': '70',#查詢起始年份
                                                                                                                            'date2': str((int(time.strftime("%Y",time.localtime()))-1911)),#查詢終末年份
                                                                                                                            'qryType': '1'
                                                                                                                            },},#網址+head資訊
                    },
            'otc' : {self.path_data['otc']['dividend'] : {'url':'https://mops.twse.com.tw/mops/web/ajax_t05st09_2', 'data':{'encodeURIComponent': '1',
                                                                                                                            'step': '1',
                                                                                                                            'firstin': '1',
                                                                                                                            'off': '1',
                                                                                                                            'keyword4': '',
                                                                                                                            'code1': '',
                                                                                                                            'TYPEK2': '',
                                                                                                                            'checkbtn':'', 
                                                                                                                            'queryName': 'co_id',
                                                                                                                            'inpuType': 'co_id',
                                                                                                                            'TYPEK': 'all',
                                                                                                                            'isnew': 'false',
                                                                                                                            'co_id': '2330',#證券代號
                                                                                                                            'date1': '70',#查詢起始年份
                                                                                                                            'date2': str((int(time.strftime("%Y",time.localtime()))-1911)),#查詢終末年份
                                                                                                                            'qryType': '1'
                                                                                                                            },},
                    },
            }
        for market in self.path_data_url_dividend_list:
            for path in self.path_data_url_dividend_list[market]:
                True
                #print(market)
                #print(path)
                #print(path_data_url_list[i][j])
                #self.Time_ALL_Data_dividend_updata(market,path,self.path_data_url_dividend_list[market][path])
        #------------------------------------------------------------https://www.twse.com.tw and https://www.tpex.org.tw 除權息預告日--------------------------------------
        self.path_data_url_Ex_Dividends_Right_Notice_date_list = {
            'tse' : {self.path_data['tse']['Ex_Dividends_Right_Notice_date'] : ['https://www.twse.com.tw/exchangeReport/TWT48U?response=json'],#網址+日期
                    },
            'otc' : {self.path_data['otc']['Ex_Dividends_Right_Notice_date'] : ['https://www.tpex.org.tw/web/stock/exright/preAnnounce/PrePost_result.php?l=zh-tw'],
                    },
            }
        for market in self.path_data_url_Ex_Dividends_Right_Notice_date_list:
            for path in self.path_data_url_Ex_Dividends_Right_Notice_date_list[market]:
                True
                #print(market)
                #print(path)
                #print(path_data_url_list[i][j])
                #self.Time_ALL_Data_Ex_Dividends_Right_Notice_date_updata(market,path,self.path_data_url_Ex_Dividends_Right_Notice_date_list[market][path])#該函示適用爬每日資料頁面，不適用一次爬整個月資料的頁面。
        #-------------------------------------------------------------https://www.twse.com.tw and https://www.tpex.org.tw 除權息計算表---------------------------------------
        self.path_data_url_Ex_Dividends_Right_Calculate_list = {
            'tse' : {self.path_data['tse']['Ex_Dividends_Right_Calculate'] : ['https://www.twse.com.tw/exchangeReport/TWT49U?response=json&strDate=','&endDate=',''],#網址+日期20030505
                    },
            'otc' : {self.path_data['otc']['Ex_Dividends_Right_Calculate'] : ['https://www.tpex.org.tw/web/stock/exright/dailyquo/exDailyQ_result.php?l=zh-tw&d=','&ed=',''],#97/01/02
                    },
            }
        for market in self.path_data_url_Ex_Dividends_Right_Calculate_list:
            for path in self.path_data_url_Ex_Dividends_Right_Calculate_list[market]:
                True
                #print(market)
                #print(path)
                #print(path_data_url_list[i][j])
                #self.Time_ALL_Data_Ex_Dividends_Right_Calculate_updata(market,path,self.path_data_url_Ex_Dividends_Right_Calculate_list[market][path])#該函示適用爬每日資料頁面，不適用一次爬整個月資料的頁面。
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def Time_ALL_Data_Stocks_updata(self,Stock_market,path,url):#抓取上市上櫃市場證券歷史成交資訊主程式
        #global fu
        date = time.strftime("%Y%m%d",time.localtime(int(time.mktime(time.strptime(time.strftime("%Y%m%d",time.localtime()), "%Y%m%d")))-86400*3))
        delay_parameter = 0
        if(os.path.isdir(path) == False):
            os.mkdir(path)
        path_list = os.listdir(path)
        if(len(path_list) == 0):
            date = date
        else:
            for i in range(0,len(path_list)):
                path_list[i] = int(path_list[i][0:(len(path_list[i]) - 5)])
            date =str(max(path_list))
        #print(date)
        time_start = int(time.mktime(time.strptime(date, "%Y%m%d")))
        today = time.strftime("%Y%m%d",time.localtime())
        total_time = 0
        if(Stock_market == 'tse'):
            delay_parameter = 2.5
        elif(Stock_market == 'otc'):
            delay_parameter = 0.5
        #start = 0
        try_out = 10
        while True:
            start_time = time.time()
            url_str = ''
            if(Stock_market == 'tse'):
                date = time.strftime("%Y%m%d",time.localtime(time_start))
                url_str = url[0] + date + url[1]
            elif(Stock_market == 'otc'):
                date = time.strftime("%Y/%m/%d",time.localtime(time_start))
                date = date.split('/')
                date[0] = str(int(date[0]) - 1911)
                date = '/'.join(date)
                url_str = url[0] + date + url[1]
                date = time.strftime("%Y%m%d",time.localtime(time_start))
            wake = time.strftime("%w",time.localtime(time_start))
            #time_start = time_start + 86400
            #print(date)
            if(wake != '0'):
                Stocks_ALL_Data = self.Initial_ALL_Data_Stocks_update(url_str,Stock_market)
                end_time = time.time()
                total_time = total_time + end_time - start_time
                #start = start+(end_time - start_time)
                #print('平均:',start/fu,' 次:'+str(fu))
                if(total_time < delay_parameter):
                    time.sleep(delay_parameter - total_time)#+ random.randint(0,5)/10
                    total_time = 0
                else:
                    #total_time = 0
                    total_time = total_time - delay_parameter
                if(total_time > delay_parameter):
                    total_time = delay_parameter
                if(Stocks_ALL_Data == 'error'):
                    try_out = try_out - 10
                    if(try_out == 0):
                        return False
                    print(date)
                    continue
                if(Stock_market == 'tse'):
                    if(Stocks_ALL_Data):
                        with open(os.path.join(path,date+".json"),"w") as f:
                            json.dump(Stocks_ALL_Data,f)
                elif(Stock_market == 'otc'):
                    if(Stocks_ALL_Data):
                        with open(os.path.join(path,date+".json"),"w") as f:
                            json.dump(Stocks_ALL_Data,f)
            time_start = time_start + 86400
            if(today == date):
                break
        return True
    def Initial_ALL_Data_Stocks_update(self,url,Stock_market):#取得盤後資料解析程式
        #global fu
        #rs=requests.session()#建立一個session
        #time_out = 3
        user_agent = [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        ]
        head = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',#
            'Accept-Encoding': 'gzip, deflate, br',#
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',#
            'Cookie': '_gid=GA1.3.431524711.1630199773; _ga=GA1.3.1108908718.1596788564; _ga_F4L5BYPQDJ=GS1.1.1630204727.1.0.1630204730.0; JSESSIONID=7DB3169AADAB847E102B3948FE58E4D5; _gat=1',
            'Host': 'www.twse.com.tw',
            'Referer': 'https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            "User-Agent" : random.choice(user_agent),#
            'X-Requested-With': 'XMLHttpRequest'
            }
        #rs.headers = head
        ALL_Data_Html = self.try_requests(api='get',url = url, headers = head)
        '''while True:
            try:
                if(time_out != 0):
                    #fu = fu + 1
                    ALL_Data_Html = rs.get(url, timeout = 5)#對伺服器發出get
                    break
                else:
                    print('伺服器維護中或是無網際網路連線。')
                    return False
            except:
                time.sleep(random.randint(1,3)/10)
                time_out = time_out - 1
                continue'''
        #print(ALL_Data_Html)
        if(ALL_Data_Html != False and ALL_Data_Html != None and ALL_Data_Html != 'error'):
            ALL_Data = json.loads(ALL_Data_Html.text)
        elif(ALL_Data_Html == 'error'):
            return 'error'
        else:
            return False
        ALL_Data_buf = dict()
        if(ALL_Data != False):
            title_name = ['證券代號','證券名稱','成交股數','成交筆數','成交金額','開盤價','最高價','最低價','收盤價','漲跌','最後買價','最後買量','最後賣價','最後賣量']
            ALL_Data_buf.setdefault('title_name',title_name)
            Stocks_data = dict()
            if(Stock_market == 'tse'):
                if(ALL_Data['stat'] == 'OK'):
                    for i in ALL_Data['data9']:
                        data_buf = dict()
                        for j in range(0,len(i)):
                            if(j==0):
                                data_buf.setdefault('證券代號',i[j])
                            elif(j==1):
                                data_buf.setdefault('證券名稱',i[j])
                            elif(j==2):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                data_buf.setdefault('成交股數',str_buf)
                            elif(j==3):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                data_buf.setdefault('成交筆數',str_buf)
                            elif(j==4):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                data_buf.setdefault('成交金額',str_buf)
                            elif(j==5):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '--'):
                                    data_buf.setdefault('開盤價','X')
                                else:
                                    data_buf.setdefault('開盤價',str_buf)
                            elif(j==6):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '--'):
                                    data_buf.setdefault('最高價','X')
                                else:
                                    data_buf.setdefault('最高價',str_buf)
                            elif(j==7):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '--'):
                                    data_buf.setdefault('最低價','X')
                                else:
                                    data_buf.setdefault('最低價',str_buf)
                            elif(j==8):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '--'):
                                    data_buf.setdefault('收盤價','X')
                                else:
                                    data_buf.setdefault('收盤價',str_buf)
                            elif(j==9):
                                if(i[j] == '<p style= color:red>+</p>'):
                                    data_buf.setdefault('漲跌','+'+i[j+1])
                                elif(i[j] == '<p style= color:green>-</p>'):
                                    data_buf.setdefault('漲跌','-'+i[j+1])
                                elif(i[j] == '<p>X</p>'):
                                    data_buf.setdefault('漲跌','X')
                                elif(i[j] == '<p> </p>'):
                                    data_buf.setdefault('漲跌','X')
                            elif(j==11):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '--'):
                                    data_buf.setdefault('最後買價','X')
                                else:
                                    data_buf.setdefault('最後買價',str_buf)
                            elif(j==12):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '--'):
                                    data_buf.setdefault('最後買量','X')
                                else:
                                    data_buf.setdefault('最後買量',str_buf)
                            elif(j==13):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '--'):
                                    data_buf.setdefault('最後賣價','X')
                                else:
                                    data_buf.setdefault('最後賣價',str_buf)
                            elif(j==14):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '--'):
                                    data_buf.setdefault('最後賣量','X')
                                else:
                                    data_buf.setdefault('最後賣量',str_buf)
                        data_list = list()
                        for i in title_name:
                            data_list.append(data_buf[i])
                        Stocks_data.setdefault(data_buf['證券代號'],data_list)
                    ALL_Data_buf.setdefault('Stocks_data',Stocks_data)
                else:
                    return False
            elif(Stock_market == 'otc'):
                if(ALL_Data['iTotalRecords'] != 0):
                    for i in ALL_Data['aaData']:
                        data_buf = dict()
                        for j in range(0,len(i)):
                            if(j==0):
                                data_buf.setdefault('證券代號',i[j])
                            elif(j==1):
                                data_buf.setdefault('證券名稱',i[j])
                            elif(j==2):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '---'):
                                    data_buf.setdefault('收盤價','X')
                                else:
                                    data_buf.setdefault('收盤價',str_buf)
                            elif(j==3):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '---'):
                                    data_buf.setdefault('漲跌','X')
                                else:
                                    data_buf.setdefault('漲跌',str_buf)
                            elif(j==4):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '---'):
                                    data_buf.setdefault('開盤價','X')
                                else:
                                    data_buf.setdefault('開盤價',str_buf)
                            elif(j==5):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '---'):
                                    data_buf.setdefault('最高價','X')
                                else:
                                    data_buf.setdefault('最高價',str_buf)
                            elif(j==6):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '---'):
                                    data_buf.setdefault('最低價','X')
                                else:
                                    data_buf.setdefault('最低價',str_buf)
                            #j==7 均價
                            elif(j==8):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                data_buf.setdefault('成交股數',str_buf)
                            elif(j==9):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                data_buf.setdefault('成交金額',str_buf)
                            elif(j==10):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                data_buf.setdefault('成交筆數',str_buf)
                            elif(j==11):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '--'):
                                    data_buf.setdefault('最後買價','X')
                                else:
                                    data_buf.setdefault('最後買價',str_buf)
                            elif(j==12):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '--'):
                                    data_buf.setdefault('最後買量','X')
                                else:
                                    data_buf.setdefault('最後買量',str_buf)
                            elif(j==13):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '--'):
                                    data_buf.setdefault('最後賣價','X')
                                else:
                                    data_buf.setdefault('最後賣價',str_buf)
                            elif(j==14):
                                str_buf = i[j].split(',')
                                str_buf = ''.join(str_buf)
                                str_buf = str_buf.split(' ')
                                str_buf = ''.join(str_buf)
                                if(str_buf == '--'):
                                    data_buf.setdefault('最後賣量','X')
                                else:
                                    data_buf.setdefault('最後賣量',str_buf)
                        data_list = list()
                        for i in title_name:
                            data_list.append(data_buf[i])
                        Stocks_data.setdefault(data_buf['證券代號'],data_list)
                    ALL_Data_buf.setdefault('Stocks_data',Stocks_data)
                else:
                    return False
        else:
            return False
        return  ALL_Data_buf
    def Time_ALL_Data_com_info_updata(self,Stock_market,path,rq_data):#抓取公司基本資料主程式
        if(os.path.isdir(path) == False):
            os.mkdir(path)
        try_out = 5
        while True:
            com_info_ALL_Data = self.Initial_ALL_Data_com_info_update(rq_data)
            if(com_info_ALL_Data ==  False or com_info_ALL_Data == 'error'):
                continue
                try_out = try_out - 1
                if(try_our == 0):
                    return False
            else:
                break
        if(Stock_market == 'tse'):
            if(com_info_ALL_Data):
                with open(os.path.join(path,"com_info.json"),"w") as f:
                    json.dump(com_info_ALL_Data,f)
        elif(Stock_market == 'otc'):
            if(com_info_ALL_Data):
                with open(os.path.join(path,"com_info.json"),"w") as f:
                    json.dump(com_info_ALL_Data,f)
        return True
    def Initial_ALL_Data_com_info_update(self,rq_data):#
        #global fu
        #rs=requests.session()#建立一個session
        #time_out = 3
        #print(rq_data['url'])
        #print(rq_data['data'])
        #rq_data['data']['code'] = '09'
        ALL_Data_Html = self.try_requests(api='post',url = rq_data['url'], data = rq_data['data'])
        if(ALL_Data_Html == False or ALL_Data_Html == None):
            return False
        if(ALL_Data_Html == 'error'):
            return 'error'
        #print(ALL_Data_Html.text)
        ALL_Data = BeautifulSoup(ALL_Data_Html.text, 'html.parser')#解析。
        ALL_Data_table = ALL_Data.find_all('table')
        if(ALL_Data_table == None):
            return False
        if(len(ALL_Data_table)==0):
            return False
        ALL_Data_tr = ALL_Data_table[1].find_all('tr')
        ALL_Data_buf = dict()
        title_name = ['公司代號','公司名稱','公司簡稱','產業類別','外國企業註冊地國','住址','營利事業統一編號','董事長','總經理','發言人','發言人職稱',
                      '代理發言人','總機電話','成立日期','上市日期','普通股每股面額','實收資本額(元)','已發行普通股數或TDR原發行股數','私募普通股(股)',
                      '特別股(股)','編製財務報告類型','普通股盈餘分派或虧損撥補頻率','普通股年度(含第4季或後半年度)現金股息及紅利決議層級','股票過戶機構',
                      '過戶電話','過戶地址','簽證會計師事務所','簽證會計師1','簽證會計師2','英文簡稱','英文通訊地址','傳真機號碼','電子郵件信箱','公司網址',
                      '投資人關係聯絡人','投資人關係聯絡人職稱','投資人關係聯絡電話','投資人關係聯絡電子郵件','公司網站內利害關係人專區網址']
        ALL_Data_buf.setdefault('title_name',title_name)
        com_info_data = dict()
        for td in range(0,len(ALL_Data_tr)):
            data_list = list()
            ALL_Data_tr_td = ALL_Data_tr[td].find_all('td')
            #print(len(ALL_Data_tr_td))#th 0
            if(len(ALL_Data_tr_td) != 0):
                for i in range(0,len(ALL_Data_tr_td)):
                    str_buf = ALL_Data_tr_td[i].text
                    if(title_name[i] == '公司代號' or title_name[i] == '營利事業統一編號' or title_name[i] == '成立日期' or title_name[i] == '上市日期' or title_name[i] == '普通股每股面額'):
                        #print(ALL_Data_tr_td[i].text)
                        str_buf = str_buf.split(' ')
                        str_buf = ''.join(str_buf)
                        str_buf = str_buf.split(' ')#特殊空白???
                        str_buf = ''.join(str_buf)
                        #print(str_buf)
                    elif(title_name[i] == '實收資本額(元)' or title_name[i] == '已發行普通股數或TDR原發行股數' or title_name[i] == '私募普通股(股)' or title_name[i] == '特別股(股)'):
                        str_buf = str_buf.split(' ')
                        str_buf = ''.join(str_buf)
                        str_buf = str_buf.split(',')
                        str_buf = ''.join(str_buf)
                        #print(str_buf)
                    data_list.append(str_buf)
                com_info_data.setdefault(data_list[0],data_list)
        ALL_Data_buf.setdefault('com_info_data',com_info_data)
        return ALL_Data_buf
    def Time_ALL_Data_dividend_updata(self,Stock_market,path,rq_data):#抓取股利分派情形主程式
        if(os.path.isdir(path) == False):
            os.mkdir(path)
        market = {'tse':'上市','otc':'上櫃'}
        delay_parameter = 3.5
        total_time = 0
        for i in self.Stocks_Simple_Data[market[Stock_market]]['股票']:
            rq_data['data']['co_id']=i['證券代號']
            #print(rq_data['data']['co_id'])
            try_out = 5
            while True:
                start_time = time.time()
                dividend_ALL_Data = self.Initial_ALL_Data_dividend_update(rq_data)
                end_time = time.time()
                total_time = total_time + end_time - start_time
                if(total_time < delay_parameter):
                    time.sleep(delay_parameter - total_time + random.randint(0,5)/10)#+ random.randint(0,5)/10
                    total_time = 0
                else:
                    total_time = total_time - delay_parameter
                if(total_time > delay_parameter):
                    total_time = delay_parameter
                if(dividend_ALL_Data ==  False or dividend_ALL_Data == 'error'):
                    try_out = try_out - 1
                    if(try_out == 0):
                        return False
                    continue
                else:
                    break
            if(Stock_market == 'tse'):
                if(dividend_ALL_Data):
                    with open(os.path.join(path,i['證券代號']+".json"),"w") as f:
                        json.dump(dividend_ALL_Data,f)
            elif(Stock_market == 'otc'):
                if(dividend_ALL_Data):
                    with open(os.path.join(path,i['證券代號']+".json"),"w") as f:
                        json.dump(dividend_ALL_Data,f)
        return True
    def Initial_ALL_Data_dividend_update(self,rq_data):#
        ALL_Data_Html = self.try_requests(api='post',url = rq_data['url'], data = rq_data['data'],headers = self.head)
        if(ALL_Data_Html == False or ALL_Data_Html == None):
            return False
        if(ALL_Data_Html == 'error'):
            return 'error'
        ALL_Data = BeautifulSoup(ALL_Data_Html.text, 'html.parser')#解析。
        ALL_Data_table = ALL_Data.find('table',class_='hasBorder')
        #ALL_Data_table = ALL_Data.find_all('table')
        if(ALL_Data_table == None):
            return False
        if(len(ALL_Data_table) == 0):
            return False
        ALL_Data_tr = ALL_Data_table.find_all('tr')
        #print(ALL_Data_tr)
        ALL_Data_buf = dict()
        title_name = ['決議（擬議）進度','股利所屬年(季)度','股利所屬期間','期別','董事會決議(擬議)股利分派日','股東會日期','期初未分配盈餘/待彌補虧損(元)','本期淨利(淨損)(元)'
                      ,'可分配盈餘(元)','分配後期末未分配盈餘(元)','盈餘分配之現金股利(元/股)','法定盈餘公積發放之現金(元/股)','資本公積發放之現金(元/股)','股東配發之現金(股利)總金額(元)'
                      ,'盈餘轉增資配股(元/股)','法定盈餘公積轉增資配股(元/股)','資本公積轉增資配股(元/股)','股東配股總股數(股)','摘錄公司章程-股利分派部分','備註','普通股每股面額']
        ALL_Data_buf.setdefault('title_name',title_name)
        dividend_data = dict()
        for td in range(0,len(ALL_Data_tr)):
            data_list = list()
            ALL_Data_tr_td = ALL_Data_tr[td].find_all('td')
            #print(len(ALL_Data_tr_td))#th 0
            if(len(ALL_Data_tr_td) != 0):
                for i in range(0,len(ALL_Data_tr_td)):
                    str_buf = ALL_Data_tr_td[i].text
                    if(title_name[i] == '摘錄公司章程-股利分派部分'):
                        True
                        #print(str_buf)
                    else:
                        str_buf = str_buf.split(' ')#特殊空白???
                        str_buf = ''.join(str_buf)
                        str_buf = str_buf.split(' ')
                        str_buf = ''.join(str_buf)
                        str_buf = str_buf.split(',')
                        str_buf = ''.join(str_buf)
                    data_list.append(str_buf)
                    #print(str_buf)
                dividend_data.setdefault(data_list[2],data_list)
        ALL_Data_buf.setdefault('dividend_data',dividend_data)
        return ALL_Data_buf
    def Time_ALL_Data_Ex_Dividends_Right_Notice_date_updata(self,Stock_market,path,url):
        if(os.path.isdir(path) == False):
            os.mkdir(path)
        try_out = 5
        while True:
            Ex_Dividends_Right_Notice_date_ALL_Data = self.Initial_ALL_Data_Ex_Dividends_Right_Notice_date_update(url[0],Stock_market)
            if(Ex_Dividends_Right_Notice_date_ALL_Data ==  False or Ex_Dividends_Right_Notice_date_ALL_Data == 'error'):
                continue
                try_out = try_out - 1
                if(try_our == 0):
                    return False
            else:
                break
        if(Stock_market == 'tse'):
            if(Ex_Dividends_Right_Notice_date_ALL_Data):
                with open(os.path.join(path,"Ex_Dividends_Right_Notice_date.json"),"w") as f:
                    json.dump(Ex_Dividends_Right_Notice_date_ALL_Data,f)
        elif(Stock_market == 'otc'):
            if(Ex_Dividends_Right_Notice_date_ALL_Data):
                with open(os.path.join(path,"Ex_Dividends_Right_Notice_date.json"),"w") as f:
                    json.dump(Ex_Dividends_Right_Notice_date_ALL_Data,f)
        return
    def Initial_ALL_Data_Ex_Dividends_Right_Notice_date_update(self,url,Stock_market):#取得盤後資料解析程式
        ALL_Data_Html = self.try_requests(api='post',url = url)
        if(ALL_Data_Html != False and ALL_Data_Html != None and ALL_Data_Html != 'error'):
            ALL_Data = json.loads(ALL_Data_Html.text)
        elif(ALL_Data_Html == 'error'):
            return 'error'
        else:
            return False
        ALL_Data_buf = dict()
        #title_name = ["除權除息日期","股票代號","名稱","除權息","無償配股率","現金增資配股率","現金增資認購價","現金股利"]
        title_name = ["除權除息日期","股票代號","名稱","除權息"]
        ALL_Data_buf.setdefault('title_name',title_name)
        Ex_Dividends_Right_Notice_date_data = dict()
        if(Stock_market == 'tse'):
            if(ALL_Data['stat'] != 'OK'):
                return False
            for data in ALL_Data['data']:
                data_list = list()
                data_buf = dict()
                for i in range(0,len(data)):
                    str_buf = data[i]
                    str_buf = str_buf.split(' ')
                    str_buf = ''.join(str_buf)
                    str_buf = str_buf.split(',')
                    str_buf = ''.join(str_buf)
                    if(i==0):
                        str_buf = str_buf.split('年')
                        str_buf = '/'.join(str_buf)
                        str_buf = str_buf.split('月')
                        str_buf = '/'.join(str_buf)
                        str_buf = str_buf.split('日')
                        str_buf = '/'.join(str_buf)
                        data_buf.setdefault('除權除息日期',str_buf)
                    elif(i==1):
                        data_buf.setdefault('股票代號',str_buf)
                    elif(i==2):
                        data_buf.setdefault('名稱',str_buf)
                    elif(i==3):
                        data_buf.setdefault('除權息','除'+str_buf)
                    '''elif(i==4):
                        data_buf.setdefault('無償配股率',str_buf)
                    elif(i==5):
                        data_buf.setdefault('現金增資配股率',str_buf)
                    elif(i==6):
                        data_buf.setdefault('現金增資認購價',str_buf)
                    elif(i==7):
                        data_buf.setdefault('現金股利',str_buf)'''
                    #data_list.append(str_buf)
                for i in title_name:
                    data_list.append(data_buf[i])
                Ex_Dividends_Right_Notice_date_data.setdefault(data_buf['除權除息日期'] + '&' + data_buf['股票代號'],data_list)
        elif(Stock_market == 'otc'):
            if(ALL_Data["iTotalRecords"] == 0):
                return False
            for data in ALL_Data["aaData"]:
                data_list = list()
                data_buf = dict()
                for i in range(0,len(data)):
                    str_buf = data[i]
                    str_buf = str_buf.split(' ')
                    str_buf = ''.join(str_buf)
                    str_buf = str_buf.split(',')
                    str_buf = ''.join(str_buf)
                    if(i==0):
                        data_buf.setdefault('除權除息日期',str_buf)
                    elif(i==1):
                        data_buf.setdefault('股票代號',str_buf)
                    elif(i==2):
                        data_buf.setdefault('名稱',str_buf)
                    elif(i==3):
                        data_buf.setdefault('除權息',str_buf)
                    '''elif(i==4):
                        data_buf.setdefault('無償配股率',str_buf)
                    elif(i==5):
                        data_buf.setdefault('現金增資配股率',str_buf)
                    elif(i==6):
                        data_buf.setdefault('現金增資認購價',str_buf)
                    elif(i==7):
                        data_buf.setdefault('現金股利',str_buf)'''
                    #data_list.append(str_buf)
                for i in title_name:
                    data_list.append(data_buf[i])
                Ex_Dividends_Right_Notice_date_data.setdefault(data_buf['除權除息日期'] + '&' + data_buf['股票代號'],data_list)
        ALL_Data_buf.setdefault('Ex_Dividends_Right_Notice_date_data',Ex_Dividends_Right_Notice_date_data)
        return ALL_Data_buf
    def Time_ALL_Data_Ex_Dividends_Right_Calculate_updata(self,Stock_market,path,url):
        #https://www.twse.com.tw/exchangeReport/TWT49U?response=json&strDate=20211004&endDate=20211004&_=1633092554806
        #https://www.tpex.org.tw/web/stock/exright/dailyquo/exDailyQ_result.php?l=zh-tw&d=110/10/01&ed=110/10/01&_=1633092613264
        if(os.path.isdir(path) == False):
            os.mkdir(path)
        start_y = 2010
        path_list = os.listdir(path)
        if(len(path_list) == 0):
            start_y = 2010
        else:
            for i in range(0,len(path_list)):
                path_list[i] = int(path_list[i][0:(len(path_list[i]) - 5)])
            start_y =max(path_list)
            
        end_y = int(time.strftime("%Y",time.localtime()))
        if(Stock_market == 'tse'):
            delay_parameter = 2.5
        elif(Stock_market == 'otc'):
            delay_parameter = 0.5
        #start = 0
        total_time = 0
        while True:
            start_time = time.time()
            url_str = ''
            if(Stock_market == 'tse'):
                url_str = url[0] + str(start_y)+'0101' + url[1] + str(start_y) + '1231'
            elif(Stock_market == 'otc'):
                url_str = url[0] + str(start_y-1911) + '/01/01' + url[1] + str(start_y-1911) + '/12/31'
                #print(url_str)
            try_out = 5
            while True:
                Ex_Dividends_Right_Calculate_ALL_Data = self.Initial_ALL_Data_Ex_Dividends_Right_Calculate_update(url_str,Stock_market)
                end_time = time.time()
                total_time = total_time + end_time - start_time
                #start = start+(end_time - start_time)
                #print('平均:',start/fu,' 次:'+str(fu))
                if(total_time < delay_parameter):
                    time.sleep(delay_parameter - total_time)#+ random.randint(0,5)/10
                    total_time = 0
                else:
                    #total_time = 0
                    total_time = total_time - delay_parameter
                if(total_time > delay_parameter):
                    total_time = delay_parameter
                if(Ex_Dividends_Right_Calculate_ALL_Data ==  False or Ex_Dividends_Right_Calculate_ALL_Data == 'error'):
                    continue
                    try_out = try_out - 1
                    if(try_our == 0):
                        return False
                else:
                    break
            if(Stock_market == 'tse'):
                if(Ex_Dividends_Right_Calculate_ALL_Data):
                    with open(os.path.join(path,str(start_y)+".json"),"w") as f:
                        json.dump(Ex_Dividends_Right_Calculate_ALL_Data,f)
            elif(Stock_market == 'otc'):
                if(Ex_Dividends_Right_Calculate_ALL_Data):
                    with open(os.path.join(path,str(start_y)+".json"),"w") as f:
                        json.dump(Ex_Dividends_Right_Calculate_ALL_Data,f)
            if(start_y == end_y):
                break
            start_y = start_y + 1
        return
    def Initial_ALL_Data_Ex_Dividends_Right_Calculate_update(self,url,Stock_market):#取得盤後資料解析程式
        ALL_Data_Html = self.try_requests(api='get',url = url)
        if(ALL_Data_Html != False and ALL_Data_Html != None and ALL_Data_Html != 'error'):
            ALL_Data = json.loads(ALL_Data_Html.text)
        elif(ALL_Data_Html == 'error'):
            return 'error'
        else:
            return False
        ALL_Data_buf = dict()
        title_name = ["除權除息日期","股票代號","名稱","除權息前收盤價"]
        ALL_Data_buf.setdefault('title_name',title_name)
        Ex_Dividends_Right_Calculate_data = dict()
        if(Stock_market == 'tse'):
            if(ALL_Data['stat'] != 'OK'):
                return False
            for data in ALL_Data['data']:
                data_list = list()
                data_buf = dict()
                for i in range(0,len(data)):
                    str_buf = data[i]
                    str_buf = str_buf.split(' ')
                    str_buf = ''.join(str_buf)
                    str_buf = str_buf.split(',')
                    str_buf = ''.join(str_buf)
                    if(i==0):
                        str_buf = str_buf.split('年')
                        str_buf = '/'.join(str_buf)
                        str_buf = str_buf.split('月')
                        str_buf = '/'.join(str_buf)
                        str_buf = str_buf.split('日')
                        str_buf = '/'.join(str_buf)
                        data_buf.setdefault('除權除息日期',str_buf)
                    elif(i==1):
                        data_buf.setdefault('股票代號',str_buf)
                    elif(i==2):
                        data_buf.setdefault('名稱',str_buf)
                    elif(i==3):
                        data_buf.setdefault('除權息前收盤價',str_buf)
                    #data_list.append(str_buf)
                for i in title_name:
                    data_list.append(data_buf[i])
                Ex_Dividends_Right_Calculate_data.setdefault(data_buf['除權除息日期'] + '&' + data_buf['股票代號'],data_list)
        elif(Stock_market == 'otc'):
            if(ALL_Data["iTotalRecords"] == 0):
                return False
            for data in ALL_Data["aaData"]:
                data_list = list()
                data_buf = dict()
                for i in range(0,len(data)):
                    str_buf = data[i]
                    str_buf = str_buf.split(' ')
                    str_buf = ''.join(str_buf)
                    str_buf = str_buf.split(',')
                    str_buf = ''.join(str_buf)
                    if(i==0):
                        data_buf.setdefault('除權除息日期',str_buf)
                    elif(i==1):
                        data_buf.setdefault('股票代號',str_buf)
                    elif(i==2):
                        data_buf.setdefault('名稱',str_buf)
                    elif(i==3):
                        data_buf.setdefault('除權息前收盤價',str_buf)
                    #data_list.append(str_buf)
                for i in title_name:
                    data_list.append(data_buf[i])
                Ex_Dividends_Right_Calculate_data.setdefault(data_buf['除權除息日期'] + '&' + data_buf['股票代號'],data_list)
        ALL_Data_buf.setdefault('Ex_Dividends_Right_Calculate_data',Ex_Dividends_Right_Calculate_data)
        return ALL_Data_buf
    '''def Time_ALL_Data_Stocks_updata(self,Stock_market,path,url):
        if(os.path.isdir(path) == False):
            os.mkdir(path)
        date = '20110801'
        delay_parameter = 0
        if(os.path.isdir(path) == False):
            os.mkdir(path)
        path_list = os.listdir(path)
        if(len(path_list) == 0):
            date = date
        else:
            for i in range(0,len(path_list)):
                path_list[i] = int(path_list[i][0:(len(path_list[i]) - 5)])
            date =str(max(path_list))
        #print(date)
        time_start = int(time.mktime(time.strptime(date, "%Y%m%d")))
        today = time.strftime("%Y%m%d",time.localtime())
        total_time = 0
        if(Stock_market == 'tse'):
            delay_parameter = 2.5
        elif(Stock_market == 'otc'):
            delay_parameter = 0.5
        #start = 0
        try_out = 10
        while True:
            start_time = time.time()
            url_str = ''
            if(Stock_market == 'tse'):
                date = time.strftime("%Y%m%d",time.localtime(time_start))
                url_str = url[0] + date + url[1]
            elif(Stock_market == 'otc'):
                date = time.strftime("%Y/%m/%d",time.localtime(time_start))
                date = date.split('/')
                date[0] = str(int(date[0]) - 1911)
                date = '/'.join(date)
                url_str = url[0] + date + url[1]
                date = time.strftime("%Y%m%d",time.localtime(time_start))
            wake = time.strftime("%w",time.localtime(time_start))
            #time_start = time_start + 86400
        return 
    def Initial_ALL_Data_Stocks_update(self,url,Stock_market):#取得盤後資料解析程式
        return'''
    def Make_Stocks_Data(self):#建立個股分析需要的資料主程式
        #self.path_data_url_list['tse'].keys()取得所有key值,型態為dict_keys(),再用list()轉換成list型態在取得key值
        if(os.path.isdir(self.filepath_Stocks) == False):
            os.mkdir(self.filepath_Stocks)
        #print(self.path_data['tse']['Stocks'])
        market_list = {'上市':'tse','上櫃':'otc'}
        for market in market_list:
            for Stock in self.Stocks_Simple_Data[market]['股票']:
                try_out = 5
                while True:
                    Stock_Data = dict()
                    try:
                        with open(os.path.join(self.filepath_Stocks, Stock['證券代號']+".json"),'r') as f:
                            Stock_Data =json.load(f)
                            #print("ok")
                    except:
                        Stock_Data.setdefault('證券基本資料', Stock)
                        Stock_Data.setdefault('歷史成交資訊', dict())
                        Stock_Data['歷史成交資訊'].setdefault('Open', list())
                        Stock_Data['歷史成交資訊'].setdefault('High', list())
                        Stock_Data['歷史成交資訊'].setdefault('Low', list())
                        Stock_Data['歷史成交資訊'].setdefault('Close', list())
                        Stock_Data['歷史成交資訊'].setdefault('UpDown', list())
                        Stock_Data['歷史成交資訊'].setdefault('Volume', list())
                        Stock_Data['歷史成交資訊'].setdefault('Amount', list())
                        Stock_Data['歷史成交資訊'].setdefault('Date', list())
                    if(try_out == 0):
                        print('建立資料錯誤')
                        break
                    '''try:'''
                    #print(Stock['證券代號'])
                    #Stock = self.find_Individual_Stocks(Stock['證券代號'])
                    #total_time = 0
                    #delay_parameter = 0
                    if(Stock):
                        Stock_Data['證券基本資料'] = Stock
                        #----------------------------建立個股成交資料--------------------
                        #start_time = time.time()
                        path_list = os.listdir(self.path_data[market_list[market]]['Stocks'])
                        if(Stock_Data['歷史成交資訊']['Date'] != []):
                            e_date = Stock_Data['歷史成交資訊']['Date'][-1]
                            e_date = e_date.split('-')
                            e_date = ''.join(e_date)
                            e_date = int(e_date)
                        else:
                            #e_date = 0
                            e_date = Stock['上市日']
                            e_date = e_date.split('/')
                            e_date = ''.join(e_date)
                            e_date = int(e_date) - 1
                        for i in path_list:
                            if(e_date >= int(i[0:(len(i) - 5)])):
                                continue
                            with open(os.path.join(self.path_data[market_list[market]]['Stocks'], i),'r') as f:
                                Stocks_Date_Data_buf =json.load(f)
                            if((Stock['證券代號'] in list(Stocks_Date_Data_buf['Stocks_data'].keys())) == False):
                                continue
                            s_key_list = {'Open':5 ,'High':6 ,'Low':7 ,'Close':8 ,'UpDown':9 ,'Volume':2 ,'Amount':4 ,'Date': time.strftime("%Y-%m-%d",time.strptime(i[0:(len(i) - 5)], "%Y%m%d"))}
                            flag = True
                            for s_key in s_key_list:
                                str_buf=''
                                if(s_key == 'Date'):
                                    str_buf =  s_key_list[s_key]
                                else:
                                    str_buf = Stocks_Date_Data_buf['Stocks_data'][Stock['證券代號']][s_key_list[s_key]]
                                if(s_key == 'Open' or s_key == 'High' or s_key == 'Low' or s_key == 'Close'):
                                    if(str_buf=='X' or str_buf=='----'):
                                        flag = False
                                    elif(float(str_buf)==0):
                                        flag = False
                                    else:
                                        #print(Stock['證券代號'],i)
                                        str_buf = round(float(str_buf),2)
                                elif(s_key == 'UpDown' or s_key == 'Volume' or s_key == 'Amount'):
                                    if(str_buf=='X' or str_buf=='除權息' or str_buf=='除息' or str_buf=='除權' or str_buf=='+######'):
                                        str_buf = 0.00
                                    else:
                                        #print(Stock['證券代號'],i,'-')
                                        str_buf = round(float(str_buf),2)
                                if(flag):
                                    Stock_Data['歷史成交資訊'][s_key].append(str_buf)
                        '''if(len(path_list) == 0):
                            date = date
                        else:
                            for i in range(0,len(path_list)):
                                path_list[i] = int(path_list[i][0:(len(path_list[i]) - 5)])
                            date =str(max(path_list))'''
                        #---------------------main------------------------------------------
                        '''basic_com_info = self.Make_Stocks_Data_basic_com_info(Stock['證券代號'])
                        basic_com_info_try_out = 3
                        while(basic_com_info == False):
                            if(basic_com_info_try_out == 0):
                                break
                            basic_com_info = self.Make_Stocks_Data_basic_com_info(Stock['證券代號'])
                            basic_com_info_try_out = basic_com_info_try_out - 1
                        if(basic_com_info != False):
                            Stock_Data.setdefault('公司基本資料', basic_com_info)
                        else:
                            continue'''
                        #------------------------------------------------------------------
                        '''end_time = time.time()
                        total_time = total_time + end_time - start_time
                        if(total_time < delay_parameter):
                            time.sleep(delay_parameter - total_time)
                            total_time = 0
                        else:
                            total_time = total_time - delay_parameter
                        if(total_time > delay_parameter):
                            total_time = delay_parameter'''
                        #------------------------------------------------------------
                        #----------------------------每日成交資訊--------------------
                        #Stock_Data.setdefault('每日成交資訊', list())
                        #Stock_Data['成交資料'] = Catch_BigData.Catch_Stocks_all_deal_data(self,Stock)
                        #print(Stock)
                        with open(os.path.join(self.filepath_Stocks,Stock['證券代號']+".json"),"w") as f:
                            json.dump(Stock_Data,f)
                        break
                    else:
                        print('查無此個股')
                        break
                    '''except:
                        try_out = try_out - 1
                        time.sleep(1)
                        continue'''
        return True
    '''def Make_Stocks_Data_basic_com_info(self,Stocks_Nunber):#這函示沒用了
        data = {
            'encodeURIComponent': '1',
            'step': '1',
            'firstin': '1',
            'off': '1',
            'keyword4': '',
            'code1': '',
            'TYPEK2': '',
            'checkbtn':'',
            'queryName': 'co_id',
            'inpuType': 'co_id',
            'TYPEK': 'all',
            'co_id': Stocks_Nunber
            }
        url="https://mops.twse.com.tw/mops/web/t146sb05"
        com_info_html = self.try_requests('post',url,data = data)
        #time.sleep(0.2)
        com_info = BeautifulSoup(com_info_html.text, 'html.parser')#解析。
        com_info_div = com_info.find(id="zoom")
        #print(com_info_div)
        if(com_info_div == None or com_info_div == False):
            #print('失敗')
            return False
        if('查無此公司代號資料' in com_info_div.text):
            #print('失敗')
            return False
        com_info_table = com_info_div.find_all("table")
        #print(com_info.find(id="zoom"))#4 5
        com_info_table_tr = com_info_table[0].find_all('tr')
        data_buf=dict()
        for i in range(0,len(com_info_table_tr)):
            i_buf = com_info_table_tr[i].select('td')
            for j in range(0,len(i_buf)):
                if(i==1 and j==0):
                    data_buf.setdefault('董事長', i_buf[j].text)
                elif(i==1 and j==1):
                    data_buf.setdefault('總經理', i_buf[j].text)
                elif(i==1 and j==2):
                    data_buf.setdefault('發言人', i_buf[j].text)
                elif(i==1 and j==3):
                    data_buf.setdefault('聯絡電話', i_buf[j].text)
                elif(i==1 and j==4):
                    data_buf.setdefault('公司網址', i_buf[j].text)
                elif(i==3 and j==0):
                    data_buf.setdefault('公司地址', i_buf[j].text)
                elif(i==3 and j==1):
                    data_buf.setdefault('主要經營業務', i_buf[j].text)
                elif(i==3 and j==2):
                    str_buf = (i_buf[j].text).split(' ')
                    str_buf = ''.join(str_buf)
                    str_buf = str_buf.split(',')
                    str_buf = ''.join(str_buf)
                    str_buf = int(str_buf)
                    data_buf.setdefault('實收資本額', str_buf)
                #print(i_buf[j].text)
        print(data_buf)
        return data_buf'''
    def try_requests(self,api,url,headers = '',data = ''):
        rs=requests.session()
        time_out = 5
        if(headers!=''):
            rs.headers = headers
        if(data!=''):
            rs.data = data
        while True:
            try:
                if(time_out != 0):
                    if(api=='get'):
                        rs = requests.get(url,timeout=5)
                    elif(api=='post'):
                        rs = requests.post(url,data=data,timeout=5)
                    else:
                        print('錯誤，請檢察參數是否輸入錯誤。')
                        return False
                    break
                else:
                    print('伺服器維護中或是無網際網路連線。')
                    return 'error'
            except:
                time.sleep(random.randint(1,3))
                time_out = time_out - 1
                continue
        if(str(rs) == '<Response [200]>'):
            return rs
        else:
            return False
    '''def Catch_Individual_Stocks_Data(self, Stocks_Number):#建立個股分析需要的資料主程式#這函式沒用了:(
        Stock = Catch_BigData.find_Individual_Stocks(self, Stocks_Number)
        Stock_Data = dict()
        if(Stock):
            #Stock_Data.setdefault('證券基本資料', Stock)
            #Stock_Data.setdefault('每日成交資訊', list())
            #Stock_Data['成交資料'] = Catch_BigData.Catch_Stocks_all_deal_data(self,Stock)
            print(Stock)
        else:
            print('查無此個股')
        return False'''
    '''def Catch_Stocks_all_deal_data(self,Stock):#這函式沒用了:(
        #controller = Controller.from_port(port=9151)
        #controller.authenticate()
        #socks.set_default_proxy(socks.SOCKS5,"127.0.0.1",9050)
        #socket.socket = socks.socksocket
        print(Stock)
        date_list = list()#每個月日期
        rs=requests.session()
        up_date = Stock['上市日'].split('/')
        while(up_date[0] != time.strftime("%Y",time.localtime()) or up_date[1] != time.strftime("%m",time.localtime())):
            up_date[1] = str(int(up_date[1]) + 1)
            if(int(up_date[1]) < 10):
                up_date[1] = '0' + up_date[1]
            if(up_date[1] == '13'):
                up_date[0] = str(int(up_date[0]) + 1)
                up_date[1] = '01'
            if(int(up_date[0]) > 2009):
                date_list.append(up_date[0] + up_date[1] + '01')
        #print(date_list)
        #date_list.reverse()
        #count = 0
        all_deal_data = list()
        fields = ['日期','成交股數','成交金額','開盤價','最高價','最低價','收盤價','漲跌價差','成交筆數']
        for i in date_list:
            #if(count == 20):
            #    count = 0
            #    controller.signal(Signal.NEWNYM)
            #    a = rs.get("https://httpbin.org/get").text#http://www.santostang.com/
            #    print(a)
            #count = count + 1
            time.sleep(random.randint(230,235)/100)#每分鐘請求最多25次，一次2.4秒，超過這個頻率IP會被封鎖。
            print(i)
            url="https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date="+ i + '&stockNo=' + Stock['證券代號']
            time_out = 3
            while True:
                #time_out = time_out - 1
                try:
                    if(time_out != 0):
                        user_agent = [
                            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
                            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
                            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
                            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
                            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
                            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
                            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
                            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
                            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
                            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
                            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
                            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
                            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
                            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
                            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
                            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
                        ]
                        head = {
                            'Accept': 'application/json, text/javascript, */*; q=0.01',#
                            'Accept-Encoding': 'gzip, deflate, br',#
                            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                            'Connection': 'keep-alive',#
                            'Cookie': '_gid=GA1.3.431524711.1630199773; _ga=GA1.3.1108908718.1596788564; _ga_F4L5BYPQDJ=GS1.1.1630204727.1.0.1630204730.0; JSESSIONID=7DB3169AADAB847E102B3948FE58E4D5; _gat=1',
                            'Host': 'www.twse.com.tw',
                            'Referer': 'https://www.twse.com.tw/zh/page/trading/exchange/STOCK_DAY.html',
                            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                            'sec-ch-ua-mobile': '?0',
                            'Sec-Fetch-Dest': 'empty',
                            'Sec-Fetch-Mode': 'cors',
                            'Sec-Fetch-Site': 'same-origin',
                            "User-Agent" : random.choice(user_agent),#
                            'X-Requested-With': 'XMLHttpRequest'
                            }
                        rs.headers = head
                        #, headers = self.head, proxies = http
                        Stocks_Deal_Data_Html = rs.get(url, timeout = 3)#對伺服器發出get
                        Stocks_Deal_Data_buf = json.loads(Stocks_Deal_Data_Html.text)
                        break
                    else:
                        print('伺服器維護中或是無網際網路連線。')
                        return False
                except:
                    time_out = time_out - 1
                    continue
            #print(Stocks_Deal_Data_buf['stat'])#狀態
            if(Stocks_Deal_Data_buf['stat'] == "OK"):
                #print(Stocks_Deal_Data_buf['fields'])#對應資料名稱
                all_data = list()
                for j in Stocks_Deal_Data_buf['data']:
                    one_data = dict()
                    for k in range(0,len(fields)):
                        str_buf = j[k].split(',')
                        str_buf = ''.join(str_buf)
                        one_data.setdefault(fields[k], str_buf)#單日成交資料
                    print(one_data)
                    one_data['成交股數'] = float(one_data['成交股數'])
                    one_data['成交金額'] = float(one_data['成交金額'])
                    if(one_data['開盤價'] == '--'):
                        one_data['開盤價'] = 0.0
                    else:
                        one_data['開盤價'] = float(one_data['開盤價'])
                    if(one_data['最高價'] == '--'):
                        one_data['最高價'] = 0.0
                    else:
                        one_data['最高價'] = float(one_data['最高價'])
                    if(one_data['最低價'] == '--'):
                        one_data['最低價'] = 0.0
                    else:
                        one_data['最低價'] = float(one_data['最低價'])
                    if(one_data['收盤價'] == '--'):
                        one_data['收盤價'] = 0.0
                    else:
                        one_data['收盤價'] = float(one_data['收盤價'])
                    if(one_data['漲跌價差'] == '--' or one_data['漲跌價差'][0] == 'X'):
                        one_data['漲跌價差'] = 0.0
                    else:
                        one_data['漲跌價差'] = float(one_data['漲跌價差'])
                    one_data['成交筆數'] = float(one_data['成交筆數'])
                    #print(one_data)
                    all_data.append(one_data)
                all_deal_data = all_deal_data + all_data
        for i in all_deal_data:
            print(i)
            #Stock_Data[]
        return all_deal_data'''
    def find_Individual_Stocks(self,Number):
        if(self.Stocks_Simple_Data != False):
            for i in self.Stocks_Simple_Data:
                for j in self.Stocks_Simple_Data[i]:
                    if( j != "最近更新日期"):
                        for k in self.Stocks_Simple_Data[i][j]:
                            if(k["證券代號"] == Number):
                                return k
        return False
    def Stocks(self,Number):
        Stock =self.find_Individual_Stocks(Number)
        if(Stock):
            #path_list = os.listdir(self.filepath_Stocks)
            try:
                with open(os.path.join(self.filepath_Stocks, Stock['證券代號']+".json"),'r') as f:
                    Stock = json.load(f)
                return Stock
            except:
                print('錯誤')
                return False
            return
        else:
            return False
if __name__ == '__main__':
    True
    #Start.Catch_Individual_Stocks_Data('2330')
    '''Start = Catch_Stocks_BigData()
    Start.Initial_Opening()
    print(Start.Stocks_Simple_Data['上市']['股票'][0])
    print(Start.Stocks_Simple_Data['上櫃']['股票'][0])
    print(Start.Stocks_Simple_Data['興櫃']['股票'][0])
    print(Start.Stocks_Simple_Data['上市']['最近更新日期'])
    print(Start.Stocks_Simple_Data['上櫃']['最近更新日期'])
    print(Start.Stocks_Simple_Data['興櫃']['最近更新日期'])'''
    '''filepath = os.getcwd()
    rs=requests.session()
    url="https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_"+"3034"+".tw"
    url2="https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=20210601&stockNo=3034"
    rs = requests.get(url2,timeout=1)
    st=json.loads(rs.text)
    print(st['stat'])#狀態
    if(st['stat']!="很抱歉，沒有符合條件的資料!"):
        print(st['date'])#資料日期
        print(st['title'])#標題
        print(st['fields'])#對應資料名稱
        print(st['data'])#資料
        print(st['notes'])#提醒'''
