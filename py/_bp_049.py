# -*- coding: utf-8 -*-

import sys
import urllib.parse
import re
from lxml import etree

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "禁片天堂"

    def init(self, extend):
        pass

    def homeContent(self, filter):
