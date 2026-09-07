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
