from comic.items import ComicItem
import scrapy
import time
import logging

from scrapy_splash import SplashRequest
from bs4 import BeautifulSoup

from comic.util.method import creatDir

from opencc import OpenCC

from fake_useragent import UserAgent
import requests
import shutil
import os

class PTTSpider(scrapy.Spider):
    name = 'comic'
    allowed_domains = ['https://www.mhgui.com/']
    start_urls = ['https://www.mhgui.com/comic/'] 
    custom_settings={
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [400, 404, 500, 502, 503, 504, 408],
        "COOKIES_ENABLED": True,



    }

    def __init__(self, *args, **kwargs):
        #turn off annoying logging, set LOG_LEVEL=DEBUG in settings.py to see more logs
        logger = logging.getLogger('scrapy.middleware')
        logger.setLevel(logging.WARNING)

        super().__init__(*args,**kwargs)

        #comicid need to be passed as attributes!
        if 'comicid' not in kwargs :
            raise AttributeError('You need to provide valid comicid :\n'
                                 'scrapy comic -a comicid="EMAIL"   ')
        else:
            self.logger.info('comicid  provided, will be used ')

        self.start_urls = [ ('https://www.mhgui.com/comic/%s/')%(self.comicid)]
        self.URL="https://www.mhgui.com"

        self.cc= OpenCC('s2tw')

        #伪装成浏览器

        #其实很好理解，就是告诉你要下载的那个图片页面，我是从主页面来的，现在把数据给我。
        # headers = {'User-Agent':ua.random,'Referer':'https://www.mhgui.com//comic/31550/435127.html'}
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36','Referer':self.URL}

        self.headers=headers


    def start_requests(self):
        for url in self.start_urls:
            yield  SplashRequest(url=url,dont_filter=True,callback=self.parse, args={"wait": 5})


    def parse(self, response):
        print('--------------------------')
        print('parse posts of Fanpage or Group...')
        print('--------------------------')
        '''
        Handle login with provided credentials
        '''
        print('login by email and password..')
         #log response of parse
        with open("logs/page-parse.html","a") as f:
            f.write(response.text)
            f.write("\n")

        soup = BeautifulSoup(response.body, "lxml") 
        name=self.cc.convert(soup.find('h1').text)
        paths=[ i.find('a')['href']   for i in soup.find_all(id="chapter-list-0")[0].find_all('li')]
        titles=[ i.find('a')['title']   for i in soup.find_all(id="chapter-list-0")[0].find_all('li')]
        # print(paths)
        # print(titles)

        print('first herer')
        

        for st in range(len(titles)):
            if st>1:
                break
            dir_index=-1-st
            creatDir(name,titles[dir_index],st+1)
            newurl=self.URL+paths[dir_index]
            print(newurl)
            yield SplashRequest(url=newurl, dont_filter=True,callback=self.parse_comicpage, 
                args={
                    "wait": 5,
                    'headers': self.headers,
                    'images': 0,
                    'timeout': 90,
                    'http_method': 'GET'
                },
            meta={'newurl':(self.URL+paths[dir_index]),'name':name,'title':titles[dir_index]})

        print('wait QQ')

    def parse_comicpage(self, response):
        print('comic gogogog')
        

        soup2 = BeautifulSoup(response.body, "lxml") 
        indexs=[i["value"] for i in soup2.find(class_="main-btn").find(id="pageSelect").find_all('option')]
        print(indexs)
        name=response.meta['name']
        title=response.meta['title']
        newurl=response.meta['newurl']
        
        for st,page_index in enumerate(indexs):
            url=('%s#p=%s'%(newurl,page_index))
            print(url)
            # 增加判斷是否要爬取
            # t.submit(ComicFun.tagSpider,st,paths[dir_index],page_index,titles[dir_index])
            yield SplashRequest(url=url, callback=self.parse_downcomic,dont_filter=True, 
                args={
                    "wait": 6,
                    'headers': self.headers,
                    'images': 0,
                    'timeout': 90,
                    'http_method': 'GET'
                },
                meta={'url':url,'name':name,'title':title,"index":st+1})

    def parse_downcomic(self, response):
        name=response.meta['name']
        title=response.meta['title']
        index=response.meta['index']
        url=response.meta['url']

        #log response of parse
        with open("logs/parse_downcomic_%s_%s.html"%(title,index),"a") as f:
            f.write(response.text)
            f.write("\n")

        try:
            soup = BeautifulSoup(response.body, "lxml") 
            photourl=soup.find(id="mangaFile")['src']
            print(photourl)
            yield self.downphoto(photourl,name,title,index)
        except:
            print('---------------------------')
            print('error')
            print(title,index)
            print('---------------------------')
            yield SplashRequest(url=url, callback=self.parse_downcomic,dont_filter=True, 
                args={
                    "wait": 6,
                    'headers': self.headers,
                    'images': 0,
                    'timeout': 90,
                    'http_method': 'GET'
                },
                meta={'url':url,'name':name,'title':title,"index":index})




    def downphoto(self,getUrl,name,title,index):
        
        try:
            res=requests.get(getUrl,headers=self.headers, stream=True)
            with open('comic_info/%s/%s/%05d.png'%(name,title,index), 'wb') as out_file:
                shutil.copyfileobj(res.raw, out_file)

            return None
        except:
            print('error')
            print(name,title,index)
            return None