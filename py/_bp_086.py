    BASE_URL = 'https://www.yasetube.com'
    HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8','Referer':'https://www.yasetube.com/'}
    CATS = {'nvce':'女厕偷拍','fc2-ppv':'FC2 PPV','me':'Mesubuta系列','milf':'MILF人妻无码','dalu':'自拍偷拍','madou':'品牌传媒'}

    def __init__(self):
        self.session = requests.Session()
