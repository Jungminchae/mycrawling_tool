# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 22:43:23 2019

@author: min
"""
import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.keys import Keys
import time
import re
from bs4 import BeautifulSoup
import urllib
import urllib.parse as rep
import urllib.request as req
from fake_useragent import UserAgent
import os
import sys
import ast
import requests
from tqdm import tqdm_notebook


class mycrawler:

    def __init__(self):
        pass
    
    def browser_open(self,browser_loc):
        '''chrome browser만 열기'''
        self.browser = webdriver.Chrome(browser_loc)
        self.browser.implicitly_wait(3)
        return self.browser
    
    def browser_open_hl(self,browser_loc):
        '''browser headless로 열기'''
        chrome_option = Options()
        chrome_option.add_argument('--headless')
        self.browser = webdriver.Chrome(browser_loc, options=chrome_option)
        self.browser.implicitly_wait(3)
        return self.browser

    def browser_open_with_url(self,browser_loc, url):
        '''browser 열고 url까지 입력'''
        self.browser = webdriver.Chrome(browser_loc)
        self.browser.implicitly_wait(3)
        self.browser.get(url)        
        return self.browser

    def browser_open_with_url_hl(self,browser_loc, url):
        '''browser headless로 열고 
            url까지 입력  '''
        chrome_option = Options()
        chrome_option.add_argument('--headless')
        self.browser = webdriver.Chrome(browser_loc, options=chrome_option)
        self.browser.implicitly_wait(3)
        self.browser.get(url)        
        return self.browser

        
    def pagedownTobottom(self, time_setting =3):        
        scroll_pause_time = time_setting
        last_height = self.browser.execute_script("return document.documentElement.scrollHeight")
        while True:
            # 스크롤 끝까지 내리기
            self.browser.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
            # 로딩 기다리기 // 너무 빨리 돌리면 씹힘
            time.sleep(scroll_pause_time)
            # 새로운 높이와 갱신된 높이를 비교해서 같으면 종료 => 같다는 것은 더 이상 갱신이 안된다는 뜻
            new_height = self.browser.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def pagedown(self, page_down_num = 1):
        body = self.browser.find_element_by_tag_name('body')
        while page_down_num:
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1.5)
            page_down_num -= 1

    def youtube_video_url_crawler(self,limit_num=10):
        html = self.browser.page_source
        src = BeautifulSoup(html,'html.parser')

        video_url = src.find_all('a', attrs={'id':'thumbnail','class':'yt-simple-endpoint inline-block style-scope ytd-thumbnail'})
        urls = []
        length = 0
        for row in video_url:
            if row.get('href') != None:
                address = row.get('href')
                true_address = 'https://www.youtube.com'+ address
                urls.append(true_address)
                length += 1
            if length >=limit_num:
                break
        return urls            

    # 특정 동영상에서 댓글 가져오기        
    def youtube_comment_crawler(self):
        ''' 
        댓글의 댓글은 크롤링 안됨
        '''
        comment_data = pd.DataFrame({'youtube_ID':[],
                                     'cmt' :[],
                                     'like_num' :[]})
        html = self.browser.page_source
        src = BeautifulSoup(html, 'html.parser')
        
        comment = src.find_all('ytd-comment-renderer' , attrs={'class':'style-scope ytd-comment-thread-renderer'})
        
        for i in range(len(comment)):
            #댓글
            comment0 = comment[i].find('yt-formatted-string',{'id':'content-text','class':'style-scope ytd-comment-renderer'}).text
    
            try:
                aa = comment[i].find('span',{'id':'vote-count-left'}).text
        
                like_num = "".join(re.findall('[0-9]',aa))+"개"
            except:
                like_num = 0
    
            bb = comment[i].find('a',{'id':'author-text'}).find('span').text
            youtube_id = ''.join(re.findall('[가-힣0-9a-zA-Z]',bb))
            insert_data = pd.DataFrame({'youtube_ID' : youtube_id,
                               'cmt' : [comment0],
                               'like_num' : [like_num]})
            comment_data = comment_data.append(insert_data)
        comment_data = comment_data.reset_index(drop=True)
        return comment_data
    

    # youtube 댓글 csv 저장    
    def make_csv(self, df, youtube_name = 'no'):
        df.to_csv(youtube_name +'_Youtube_comments.csv', encoding='UTF8')
    
    # 헤더
    def header_set(self):
        # Header 정보 초기화
        opener = req.build_opener()
        # User_Agent 정보
        opener.addheaders = [("user-agent", UserAgent().chrome)]
        # Header 정보 삽입
        req.install_opener(opener)

    # 네이버에서 이미지 다운 받기
    def naver_image_search(self,search_name, PATH ='C:/', num_page_down = 0):
        # selenium 기반
        
        # 네이버 이미지 기본 UR
        base = "https://search.naver.com/search.naver?where=image&sm=tab_jum&query="
        # 검색어
        quote = rep.quote_plus(search_name)
        # URL 완성
        url = base + quote 
        
        # url 요청
        res = self.browser.get(url)
        
        savePath = PATH
        
        try:
            # 기본 폴더가 있는지 체크
            if not (os.path.isdir(savePath)):
                os.makedirs(os.path.join(savePath))
        except OSError as e:
            print("folder creation failed")
            print("folder name : {} ".format(e.filename))
            
            # 런타임 에러
            raise RuntimeError("System Exit!")
        else:
            # 폴더 생성이 되었거나, 존재할 경우
            print("folder is created!")
            
        body = self.browser.find_element_by_tag_name('body')
        # page down
        if num_page_down == 9999:
            self.pagedownTobottom()
        else:
            while num_page_down:
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(1.5)
                num_page_down -= 1
        
        # bs4 초기화
        soup = BeautifulSoup(res, 'html.parser')
        
        # select 로 이미지 선택
        img_list = soup.select('div.img_area > a.thumb._thumb > img')
        
        
        for i, img in enumerate(img_list ,1):
            
            # 저장 파일명 및 경로
            fullFileName = os.path.join(savePath, savePath+ search_name +str(i)+'번 '+ search_name + '.png')
            
            # print(fullFileName)
            
            # 다운로드 요청
            req.urlretrieve(img['data-source'], fullFileName)
        
        print('download succeeded!')



    def naver_news_crawling_with_api(self, searching_keyword = '검색어', id='id',key='key', page_cnt=10, return_type='df'):

        news_data =[]
        page_count = page_cnt

        id_ = id
        key_ = key
        Text = urllib.parse.quote(searching_keyword)

        naver_news_title = []
        naver_news_content = []

        for idx in range(page_count):
            url = "https://openapi.naver.com/v1/search/news?query=" + Text + '&start=' + str(idx * 10 + 1) # json 결과
            # url = "https://openapi.naver.com/v1/search/blog.xml?query=" + Text # xml 결과

            request = req.Request(url)
            request.add_header("X-Naver-Client-Id",id_)
            request.add_header("X-Naver-Client-Secret",key_)
            response = req.urlopen(request)
            rescode = response.getcode()
            if(rescode==200):
                #response_body = response.read()
                result = requests.get(response.geturl(),
                                    headers = {'X-Naver-Client-Id':id_,
                                                'X-Naver-Client-Secret':key_})
                news_data.append(result.json())
                #print(response_body.decode('utf-8'))
            else:
                print("Error Code:" + rescode)
        
        naver_news_link = []

        for page in news_data:
            
            link_01 =[]

            for item in page['items']:
                link = item['link']
                if 'naver' in link:
                    link_01.append(link)
            naver_news_link.append(link_01)



        chrome_option = Options()
        chrome_option.add_argument('--headless')
        driver = webdriver.Chrome('D:/jupyter/chrome_driver/chromedriver.exe',options=chrome_option)
        
        for n in tqdm_notebook(range(len(naver_news_link))):
            
            news_page_title =[]
            news_page_content = []
            
            for idx in tqdm_notebook(range(len(naver_news_link[n]))):
                
                try:
                    driver.get(naver_news_link[n][idx])
                
                except:
                    print('Timeout')
                    continue
                
                try:
                    response = driver.page_source
                    
                except selenium.common.exceptions.UnexpectedAlertPresentException:
                    driver.switch_to_alert().accept()
                    print('게시글이 삭제된 경우입니다.')
                    continue
                
                soup = BeautifulSoup(response, 'html.parser')
                
                # title
                title = None
                
                try:
                    item = soup.find('div', class_ = 'article_info')
                    title = item.find('h3', class_ = 'tts_head').get_text()
                    
                except:
                    title = 'Outlink'
                
                news_page_title.append(title)
                
                # content
                doc = None
                text = ''
                
                data = soup.find_all('div', {'class' : '_article_body_contents'})
                if data:
                    for item in data:
                        
                        text = text + str(item.find_all(text=True)).strip()
                        text = ast.literal_eval(text)
                        doc = ' '.join(text)
                        
                else:
                    doc = 'Outlink'
                    
                news_page_content.append(doc.replace('\n', ' '))
                
            naver_news_title.append(news_page_title)
            naver_news_content.append(news_page_content)
            
            time.sleep(2)

        if return_type =='df':
            df = pd.DataFrame()
            df['title'] = naver_news_title
            df['content'] = naver_news_content
            return df

        elif return_type == 'list' :
            return naver_news_title, naver_news_content     

    def naver_juga_day(self,stock_number='005930', pages=1):
        """
        1 page당 10일의 주가 데이터
        """
        stock_price = pd.DataFrame()
        for page in range(pages):
            url = 'https://finance.naver.com/item/sise_day.nhn?code={}&page={}'.format(stock_number, page+1)
            juga = pd.read_html(url)
            juga = juga[0].dropna()
            stock_price = pd.concat([stock_price,juga], axis=0)
        stock_price.reset_index(drop=True, inplace=True)
        return stock_price







