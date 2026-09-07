# coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json
import time
import urllib.parse
import re
import requests
from lxml import etree

class Spider(Spider):
    
    def getName(self):
        return "香蕉视频"
    
    def init(self, extend=""):
        self.host = "https://618013.xyz"
        self.api_host = "https://h5.xxoo168.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': self.host
        }
        self.log(f"香蕉视频爬虫初始化完成，主站: {self.host}")

    def html(self, content):
        """将HTML内容转换为可查询的对象"""
        try:
            return etree.HTML(content)
        except:
            self.log("HTML解析失败")
            return None

    def regStr(self, pattern, string, index=1):
        """正则表达式提取字符串"""
        try:
            match = re.search(pattern, string, re.IGNORECASE)
            if match and len(match.groups()) >= index:
                return match.group(index)
        except:
            pass
        return ""

    def isVideoFormat(self, url):
        pass

