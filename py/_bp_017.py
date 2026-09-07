# coding: utf-8
import json
import sys
import os
import re
import urllib.request
import urllib.parse
import ssl

sys.path.append('..')
from base.spider import Spider

VERSION = '2.0.0'

SITE_URL = 'https://newxvideos.pages.dev'
API_URL = 'https://newxvideos.pages.dev/api'

CATEGORIES = [
    {"type_id": "Arab-159", "type_name": "阿拉伯"},
    {"type_id": "Mature-38", "type_name": "成熟"},
    {"type_id": "Cuckold-237", "type_name": "出轨背叛"},
    {"type_id": "Femdom-235", "type_name": "调教"},
    {"type_id": "Anal-12", "type_name": "肛交"},
    {"type_id": "Brunette-25", "type_name": "褐发"},
    {"type_id": "Black_Woman-30", "type_name": "黑人"},
    {"type_id": "Redhead-31", "type_name": "红发"},
    {"type_id": "Fucked_Up_Family-81", "type_name": "家庭乱搞"},
    {"type_id": "Blonde-20", "type_name": "金发"},
    {"type_id": "Big_Cock-34", "type_name": "巨屌"},
    {"type_id": "Big_Tits-23", "type_name": "巨乳"},
    {"type_id": "Big_Ass-24", "type_name": "巨臀"},
    {"type_id": "Blowjob-15", "type_name": "口交"},
    {"type_id": "Latina-16", "type_name": "拉丁裔"},
    {"type_id": "Milf-19", "type_name": "辣妈"},
    {"type_id": "Gapes-167", "type_name": "裂开"},
    {"type_id": "Ass-14", "type_name": "美臀"},
    {"type_id": "Lesbian-26", "type_name": "女同"},
    {"type_id": "bbw-51", "type_name": "胖女"},
    {"type_id": "Squirting-56", "type_name": "喷出"},
