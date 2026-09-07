#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import requests
from urllib.parse import quote, urljoin
try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None
try:
