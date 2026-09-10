/*
@header({
  searchable: 1,
  filterable: 1,
  quickSearch: 1,
  title: '\u805a\u5408\u77ed\u5267',
  lang: 'cat'
})
*/


import { Crypto as CryptoJS } from 'assets://js/lib/cat.js';

let shuaCache = [];
let siteName = '\u805a\u5408\u77ed\u5267';
let xingya_headers = {};
let niuniu_headers = {}; 
let niuniu_token = '';
let niuniu_access_token = ''; 
let hema_headers = {};

// \u5206\u7c7b\u6392\u9664\u89c4\u5219
const cate_remove = ['\u5206\u7c7b\u6392\u9664', '\u8f6f\u9e2d','\u788e\u7247', '\u9526\u9ca4', '\u756a\u8304', '\u751c\u5708']; 

const aggConfig = {
  keys: 'd3dGiJc651gSQ8w1',
  charMap: {
    '+': 'P', '/': 'X', '0': 'M', '1': 'U', '2': 'l', '3': 'E', '4': 'r', '5': 'Y', '6': 'W', '7': 'b', '8': 'd', '9': 'J',
    'A': '9', 'B': 's', 'C': 'a', 'D': 'I', 'E': '0', 'F': 'o', 'G': 'y', 'H': '_', 'I': 'H', 'J': 'G', 'K': 'i', 'L': 't',
    'M': 'g', 'N': 'N', 'O': 'A', 'P': '8', 'Q': 'F', 'R': 'k', 'S': '3', 'T': 'h', 'U': 'f', 'V': 'R', 'W': 'q', 'X': 'C',
    'Y': '4', 'Z': 'p', 'a': 'm', 'b': 'B', 'c': 'O', 'd': 'u', 'e': 'c', 'f': '6', 'g': 'K', 'h': 'x', 'i': '5', 'j': 'T',
    'k': '-', 'l': '2', 'm': 'z', 'n': 'S', 'o': 'Z', 'p': '1', 'q': 'V', 'r': 'v', 's': 'j', 't': 'Q', 'u': '7', 'v': 'D',
    'w': 'w', 'x': 'n', 'y': 'L', 'z': 'e'
  },
  headers: {
    default: {
        'User-Agent': 'okhttp/5.1.0',
        'Content-Type': 'application/json'
    },
    niuniu: {'Cache-Control':'no-cache','Content-Type':'application/json;charset=UTF-8','User-Agent':'okhttp/4.12.0'},
    baidu: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; 22081212C Build/PQ3B.190801.002) Talos/1.8.13 SP-engine/3.47.0 bd_dvt/1 baiduboxapp/15.21.0.10 (Baidu; P1 9)'
    },
    hema: {
      'datas': 'e5f22c6e2c82fe001738cb9ce4696eab0556d064a55aef402e0fbe6b29a083f6538e4567de38e67de2071a49d9751526bfba45314e1fd4702b11c76ab9a3b5f873262854ba66e6715ed51364dbc6ee62c7180e047fcbcdbfd49874fc8f28674b16d90ca71a02de76c70598e0b75e647c37c2c19287e49be5f2a259d727dfc4df3d28802388bf3c356576b342e17e30a2ab74859263dba4d1c8eba79990d22d60d60927fdacb2addf2f0eaadd8887585ca2eb87f603faf0c207dda18cf67dc25b2199d303baff9e6605b3314a7d2631f62864f48619daceb9452f2b7b0667773553741856df030cca68af3c57810f983d452bb428ef5fc32206aef4865ae06c629bee7f5135547304acc7ef4e7c6df887308f2e79c493fd2ee03488722861b5bb51b09cb8911dfc92c288d94e601c066d2f9d612ad2c8d4eeb4920b1d44aff3e13fd75229b857f64925df1cf12f75a00d438c422ec1726462b915903f1dd1f4bb7cdf82cc15a6d507f80c789903e710f39a62aef073f3f93a6c681e75d295428aa290d7e98f82e7e9ad6e2b23d9086dfe8c63c5d8550b13fd61a77291473a8bdd43c7c2639f264be69d9d07f0585de4342a399275a64e7d1d4400b8ed4421a2f289f622e40cdd1cfc916a0b9ce747c924ac33e32d24b91ed5d64772d6ad6896412f52724006eabf12aaecfd6e81dad432c7b3800bbf793a1c375e3e7b4fb3b097724b5fc88a8c9bcf3dbc10cbdb252965',
      'content-type': 'text/plain'
    }
  }
};

// ==================== URL\u914d\u7f6e\u96c6\u4e2d\u7ba1\u7406 ====================
const rule = {
  百度: {
    host: 'https://mbd.baidu.com',
    detailHost: 'https://sv.baidu.com',
    list: '/feedapi/v1/videoserver/playlets/list?service=bdbox',
    search: '/feedapi/v1/videoserver/playlets/search?service=bdbox',
    detail: '/haokan/ui-video/playlet/rec/detail?log=vhk&tn=1020970b&ctn=1008350n&blur=1',
    play: '/appui/api?cmd=video/relate&log=vhk&tn=1020970b&ctn=1008350n&blur=1'
  },
  甜圈: {
    host: 'https://mov.cenguigui.cn',
    list: '/duanju/api.php?classname',
    detail: '/duanju/api.php?book_id',
    search: '/duanju/api.php?name'
  },
  锦鲤: {
    host: 'https://api.jinlidj.com',
    search: '/api/search',
    detail: '/api/detail'
  },
  番茄: {
    host: 'https://reading.snssdk.com',
    list: '/reading/bookapi/bookmall/cell/change/v',
    detail: 'https://fqgo.52dns.cc/catalog',
    search: 'https://fqgo.52dns.cc/search'
  },
  星芽: {
    host: 'https://app.whjzjx.cn',
    list: '/cloud/v2/theater/home_page?theater_class_id',
    detail: '/v2/theater_parent/detail',
    search: '/v3/search',
    login: 'https://u.shytkjgs.com/user/v1/account/login'
  },
  西饭: {
    host: 'https://xifan-api-cn.youlishipin.com',
    list: '/xifan/drama/portalPage',
    detail: '/xifan/drama/getDuanjuInfo',
    search: '/xifan/search/getSearchList'
  },
  软鸭: {
    host: 'https://api.xingzhige.com',
    list: '/API/playlet',
    search: '/API/playlet'
  },
  七猫: {
    host: 'https://api-store.qmplaylet.com',
    list: '/api/v1/playlet/index',
    detail: 'https://api-read.qmplaylet.com/player/api/v1/playlet/info',
    search: '/api/v1/playlet/search'
  },
  牛牛: {
    host: 'https://new.tianjinzhitongdaohe.com',
    list: '/api/v1/app/screen/screenMovie',
    detail: '/api/v1/app/play/movieDetails',
    search: '/api/v1/app/search/searchMovie',
    desc: '/api/v1/app/play/movieDesc',
    visitor: '/api/v1/app/user/visitorInfo',
    login: 'https://csj-sp.csjdeveloper.com/csj_sp/api/v1/user/login?siteid=5627189',
    detail2: 'https://csj-sp.csjdeveloper.com/csj_sp/api/v1/shortplay/detail?siteid=5627189',
    unlock: 'https://csj-sp.csjdeveloper.com/csj_sp/api/v1/pay/ad_unlock?siteid=5627189'
  },
  围观: {
    host: 'https://api.drama.9ddm.com',
    list: '/drama/home/shortVideoTags?version_code=1500&os_type=1',
    detail: '/drama/home/shortVideoDetail?version_code=1500&os_type=1',
    search: '/drama/home/search?version_code=1500&os_type=1'
  },
  碎片: {
    host: 'https://free-api.bighotwind.cc',
    list: '/papaya/papaya-api/theater/tags',
    detail: '/papaya/papaya-api/videos/info',
    search: '/papaya/papaya-api/videos/page'
  },
  河马: {
    host: 'https://freevideo.zqqds.cn',
    list: '/free-video-portal/portal/1121',
    detail: '/free-video-portal/portal/1131',
    episode: '/free-video-portal/portal/1132',
    play: '/free-video-portal/portal/1133',
    search: '/free-video-portal/portal/1803'
  }
};

const platformList = [
  { name: '\u9526\u9ca4\u77ed\u5267', id: '\u9526\u9ca4' },
  { name: '\u756a\u8304\u77ed\u5267', id: '\u756a\u8304' },
  { name: '\u661f\u82bd\u77ed\u5267', id: '\u661f\u82bd' },
  { name: '\u897f\u996d\u77ed\u5267', id: '\u897f\u996d' },
  { name: '\u4e03\u732b\u77ed\u5267', id: '\u4e03\u732b' },
  { name: '\u751c\u5708\u77ed\u5267', id: '\u751c\u5708' },
  { name: '\u725b\u725b\u77ed\u5267', id: '\u725b\u725b' },
  { name: '\u767e\u5ea6\u77ed\u5267', id: '\u767e\u5ea6' },
  { name: '\u56f4\u89c2\u77ed\u5267', id: '\u56f4\u89c2' },
  { name: '\u8f6f\u9e2d\u77ed\u5267', id: '\u8f6f\u9e2d' },
  { name: '\u788e\u7247\u5267\u573a', id: '\u788e\u7247' },
  { name: '\u6cb3\u9a6c\u77ed\u5267', id: '\u6cb3\u9a6c' }
];

const ruleFilterDef = {
  百度: { area: '\u65b0\u5267' },
  甜圈: { area: '\u9006\u88ad' },
  锦鲤: { area: '' },
  番茄: { area: 'videoseries_hot' },
  星芽: { area: '1' },
  西饭: { area: '' },
  软鸭: { area: '\u6218\u795e' },
  七猫: { area: '0' },
  牛牛: { area: '\u73b0\u8a00' },
  围观: { area: '' },
  碎片: { area: '' },
  河马: { area: '308' }
};

const filterOptions = {
  "\u751c\u5708": [{
    "key": "area",
    "name": "\u5267\u60c5",
    "value": [
      {"n": "\u9006\u88ad", "v": "\u9006\u88ad"},
      {"n": "\u9738\u603b", "v": "\u9738\u603b"},
      {"n": "\u73b0\u4ee3\u8a00\u60c5", "v": "\u73b0\u4ee3\u8a00\u60c5"},
      {"n": "\u6253\u8138\u8650\u6e23", "v": "\u6253\u8138\u8650\u6e23"},
      {"n": "\u8c6a\u95e8\u6069\u6028", "v": "\u8c6a\u95e8\u6069\u6028"},
      {"n": "\u795e\u8c6a", "v": "\u795e\u8c6a"},
      {"n": "\u9a6c\u7532", "v": "\u9a6c\u7532"},
      {"n": "\u90fd\u5e02\u65e5\u5e38", "v": "\u90fd\u5e02\u65e5\u5e38"},
      {"n": "\u6218\u795e\u5f52\u6765", "v": "\u6218\u795e\u5f52\u6765"},
      {"n": "\u5c0f\u4eba\u7269", "v": "\u5c0f\u4eba\u7269"},
      {"n": "\u5973\u6027\u6210\u957f", "v": "\u5973\u6027\u6210\u957f"},
      {"n": "\u5927\u5973\u4e3b", "v": "\u5927\u5973\u4e3b"},
      {"n": "\u7a7f\u8d8a", "v": "\u7a7f\u8d8a"},
      {"n": "\u90fd\u5e02\u4fee\u4ed9", "v": "\u90fd\u5e02\u4fee\u4ed9"},
      {"n": "\u5f3a\u8005\u56de\u5f52", "v": "\u5f3a\u8005\u56de\u5f52"},
      {"n": "\u4eb2\u60c5", "v": "\u4eb2\u60c5"},
      {"n": "\u53e4\u88c5", "v": "\u53e4\u88c5"},
      {"n": "\u91cd\u751f", "v": "\u91cd\u751f"},
      {"n": "\u95ea\u5a5a", "v": "\u95ea\u5a5a"},
      {"n": "\u8d58\u5a7f\u9006\u88ad", "v": "\u8d58\u5a7f\u9006\u88ad"},
      {"n": "\u8650\u604b", "v": "\u8650\u604b"},
      {"n": "\u8ffd\u59bb", "v": "\u8ffd\u59bb"},
      {"n": "\u5929\u4e0b\u65e0\u654c", "v": "\u5929\u4e0b\u65e0\u654c"},
      {"n": "\u5bb6\u5ead\u4f26\u7406", "v": "\u5bb6\u5ead\u4f26\u7406"},
      {"n": "\u840c\u5b9d", "v": "\u840c\u5b9d"},
      {"n": "\u53e4\u98ce\u6743\u8c0b", "v": "\u53e4\u98ce\u6743\u8c0b"},
      {"n": "\u804c\u573a", "v": "\u804c\u573a"},
      {"n": "\u5947\u5e7b\u8111\u6d1e", "v": "\u5947\u5e7b\u8111\u6d1e"},
      {"n": "\u5f02\u80fd", "v": "\u5f02\u80fd"},
      {"n": "\u65e0\u654c\u795e\u533b", "v": "\u65e0\u654c\u795e\u533b"},
      {"n": "\u53e4\u98ce\u8a00\u60c5", "v": "\u53e4\u98ce\u8a00\u60c5"},
      {"n": "\u4f20\u627f\u89c9\u9192", "v": "\u4f20\u627f\u89c9\u9192"},
      {"n": "\u73b0\u8a00\u751c\u5ba0", "v": "\u73b0\u8a00\u751c\u5ba0"},
      {"n": "\u5947\u5e7b\u7231\u60c5", "v": "\u5947\u5e7b\u7231\u60c5"},
      {"n": "\u4e61\u6751", "v": "\u4e61\u6751"},
      {"n": "\u5386\u53f2\u53e4\u4ee3", "v": "\u5386\u53f2\u53e4\u4ee3"},
      {"n": "\u738b\u5983", "v": "\u738b\u5983"},
      {"n": "\u9ad8\u624b\u4e0b\u5c71", "v": "\u9ad8\u624b\u4e0b\u5c71"},
      {"n": "\u5a31\u4e50\u5708", "v": "\u5a31\u4e50\u5708"},
      {"n": "\u5f3a\u5f3a\u8054\u5408", "v": "\u5f3a\u5f3a\u8054\u5408"},
      {"n": "\u7834\u955c\u91cd\u5706", "v": "\u7834\u955c\u91cd\u5706"},
      {"n": "\u6697\u604b\u6210\u771f", "v": "\u6697\u604b\u6210\u771f"},
      {"n": "\u6c11\u56fd", "v": "\u6c11\u56fd"},
      {"n": "\u6b22\u559c\u51a4\u5bb6", "v": "\u6b22\u559c\u51a4\u5bb6"},
      {"n": "\u7cfb\u7edf", "v": "\u7cfb\u7edf"},
      {"n": "\u771f\u5047\u5343\u91d1", "v": "\u771f\u5047\u5343\u91d1"},
      {"n": "\u9f99\u738b", "v": "\u9f99\u738b"},
      {"n": "\u6821\u56ed", "v": "\u6821\u56ed"},
      {"n": "\u7a7f\u4e66", "v": "\u7a7f\u4e66"},
      {"n": "\u5973\u5e1d", "v": "\u5973\u5e1d"},
      {"n": "\u56e2\u5ba0", "v": "\u56e2\u5ba0"},
      {"n": "\u5e74\u4ee3\u7231\u60c5", "v": "\u5e74\u4ee3\u7231\u60c5"},
      {"n": "\u7384\u5e7b\u4ed9\u4fa0", "v": "\u7384\u5e7b\u4ed9\u4fa0"},
      {"n": "\u9752\u6885\u7af9\u9a6c", "v": "\u9752\u6885\u7af9\u9a6c"},
      {"n": "\u60ac\u7591\u63a8\u7406", "v": "\u60ac\u7591\u63a8\u7406"},
      {"n": "\u7687\u540e", "v": "\u7687\u540e"},
      {"n": "\u66ff\u8eab", "v": "\u66ff\u8eab"},
      {"n": "\u5927\u53d4", "v": "\u5927\u53d4"},
      {"n": "\u559c\u5267", "v": "\u559c\u5267"},
      {"n": "\u5267\u60c5", "v": "\u5267\u60c5"}
    ]
  }],
  "\u9526\u9ca4": [{
    "key": "area",
    "name": "\u5206\u7c7b",
    "value": [
      {"n": "\u5168\u90e8", "v": ""},
      {"n": "\u60c5\u611f\u5173\u7cfb", "v": "1"},
      {"n": "\u6210\u957f\u9006\u88ad", "v": "2"},
      {"n": "\u5947\u5e7b\u5f02\u80fd", "v": "3"},
      {"n": "\u6218\u6597\u70ed\u8840", "v": "4"},
      {"n": "\u4f26\u7406\u73b0\u5b9e", "v": "5"},
      {"n": "\u65f6\u7a7a\u7a7f\u8d8a", "v": "6"},
      {"n": "\u6743\u8c0b\u8eab\u4efd", "v": "7"}
    ]
  }],
  "\u756a\u8304": [{
    "key": "area",
    "name": "\u5206\u7c7b",
    "value": [
      {"n": "\u70ed\u5267", "v": "videoseries_hot"},
      {"n": "\u65b0\u5267", "v": "firstonlinetime_new"},
      {"n": "\u9006\u88ad", "v": "cate_739"},
      {"n": "\u603b\u88c1", "v": "cate_29"},
      {"n": "\u73b0\u8a00", "v": "cate_3"},
      {"n": "\u6253\u8138", "v": "cate_1051"},
      {"n": "\u9a6c\u7532", "v": "cate_266"},
      {"n": "\u8c6a\u95e8", "v": "cate_1053"},
      {"n": "\u90fd\u5e02", "v": "cate_261"},
      {"n": "\u795e\u8c6a", "v": "cate_20"}
    ]
  }],
  "\u661f\u82bd": [{
    "key": "area",
    "name": "\u5206\u7c7b",
    "value": [
      {"n": "\u5267\u573a", "v": "1"},
      {"n": "\u70ed\u64ad\u5267", "v": "2"},
      {"n": "\u4f1a\u5458\u4e13\u4eab", "v": "8"},
      {"n": "\u661f\u9009\u597d\u5267", "v": "7"},
      {"n": "\u65b0\u5267", "v": "3"},
      {"n": "\u9633\u5149\u5267\u573a", "v": "5"}
    ]
  }],
  "\u897f\u996d": [{
    "key": "area",
    "name": "\u5206\u7c7b",
    "value": [
      {"n": "\u5168\u90e8", "v": ""},
      {"n": "\u90fd\u5e02", "v": "68@\u90fd\u5e02"},
      {"n": "\u9752\u6625", "v": "68@\u9752\u6625"},
      {"n": "\u73b0\u4ee3\u8a00\u60c5", "v": "81@\u73b0\u4ee3\u8a00\u60c5"},
      {"n": "\u8c6a\u95e8", "v": "81@\u8c6a\u95e8"},
      {"n": "\u5927\u5973\u4e3b", "v": "80@\u5927\u5973\u4e3b"},
      {"n": "\u9006\u88ad", "v": "79@\u9006\u88ad"},
      {"n": "\u6253\u8138\u8650\u6e23", "v": "79@\u6253\u8138\u8650\u6e23"},
      {"n": "\u7a7f\u8d8a", "v": "81@\u7a7f\u8d8a"}
    ]
  }],
  "\u8f6f\u9e2d": [{
    "key": "area",
    "name": "\u5206\u7c7b",
    "value": [
      {"n": "\u5168\u90e8", "v": ""},
      {"n": "\u6218\u795e", "v": "\u6218\u795e"},
      {"n": "\u9006\u88ad", "v": "\u9006\u88ad"},
      {"n": "\u9738\u603b", "v": "\u9738\u603b"},
      {"n": "\u795e\u8c6a", "v": "\u795e\u8c6a"},
      {"n": "\u90fd\u5e02", "v": "\u90fd\u5e02"},
      {"n": "\u7384\u5e7b", "v": "\u7384\u5e7b"},
      {"n": "\u8a00\u60c5", "v": "\u8a00\u60c5"}
    ]
  }],
  "\u4e03\u732b": [{
    "key": "area",
    "name": "\u5206\u7c7b",
    "value": [
      {"n": "\u5168\u90e8", "v": ""},
      {"n": "\u63a8\u8350", "v": "0"},
      {"n": "\u65b0\u5267", "v": "-1"},
      {"n": "\u90fd\u5e02\u60c5\u611f", "v": "1273"},
      {"n": "\u53e4\u88c5", "v": "1272"},
      {"n": "\u90fd\u5e02", "v": "571"},
      {"n": "\u7384\u5e7b\u4ed9\u4fa0", "v": "1286"},
      {"n": "\u5947\u5e7b", "v": "570"},
      {"n": "\u4e61\u6751", "v": "590"},
      {"n": "\u6c11\u56fd", "v": "573"},
      {"n": "\u5e74\u4ee3", "v": "572"},
      {"n": "\u9752\u6625\u6821\u56ed", "v": "1288"},
      {"n": "\u6b66\u4fa0", "v": "371"},
      {"n": "\u79d1\u5e7b", "v": "594"},
      {"n": "\u672b\u4e16", "v": "556"},
      {"n": "\u4e8c\u6b21\u5143", "v": "1289"},
      {"n": "\u9006\u88ad", "v": "400"},
      {"n": "\u7a7f\u8d8a", "v": "373"},
      {"n": "\u590d\u4ec7", "v": "795"},
      {"n": "\u7cfb\u7edf", "v": "787"},
      {"n": "\u6743\u8c0b", "v": "790"},
      {"n": "\u91cd\u751f", "v": "784"},
      {"n": "\u5973\u6027\u6210\u957f", "v": "1294"},
      {"n": "\u6253\u8138\u8650\u6e23", "v": "716"},
      {"n": "\u95ea\u5a5a", "v": "480"},
      {"n": "\u5f3a\u8005\u56de\u5f52", "v": "402"},
      {"n": "\u8ffd\u59bb\u706b\u846c\u573a", "v": "715"},
      {"n": "\u5bb6\u5ead", "v": "670"},
      {"n": "\u9a6c\u7532", "v": "558"},
      {"n": "\u804c\u573a", "v": "724"},
      {"n": "\u5bab\u6597", "v": "343"},
      {"n": "\u9ad8\u624b\u4e0b\u5c71", "v": "1299"},
      {"n": "\u5a31\u4e50\u660e\u661f", "v": "1295"},
      {"n": "\u5f02\u80fd", "v": "727"},
      {"n": "\u5b85\u6597", "v": "342"},
      {"n": "\u66ff\u8eab", "v": "712"},
      {"n": "\u7a7f\u4e66", "v": "338"},
      {"n": "\u5546\u6218", "v": "723"},
      {"n": "\u79cd\u7530\u7ecf\u5546", "v": "1291"},
      {"n": "\u4f26\u7406", "v": "1293"},
      {"n": "\u793e\u4f1a\u8bdd\u9898", "v": "1290"},
      {"n": "\u81f4\u5bcc", "v": "492"},
      {"n": "\u5077\u542c\u5fc3\u58f0", "v": "1258"},
      {"n": "\u8111\u6d1e", "v": "526"},
      {"n": "\u8c6a\u95e8\u603b\u88c1", "v": "624"},
      {"n": "\u840c\u5b9d", "v": "356"},
      {"n": "\u6218\u795e", "v": "527"},
      {"n": "\u771f\u5047\u5343\u91d1", "v": "812"},
      {"n": "\u8d58\u5a7f", "v": "36"},
      {"n": "\u795e\u533b", "v": "1269"},
      {"n": "\u795e\u8c6a", "v": "37"},
      {"n": "\u5c0f\u4eba\u7269", "v": "1296"},
      {"n": "\u56e2\u5ba0", "v": "545"},
      {"n": "\u6b22\u559c\u51a4\u5bb6", "v": "464"},
      {"n": "\u5973\u5e1d", "v": "617"},
      {"n": "\u94f6\u53d1", "v": "1297"},
      {"n": "\u5175\u738b", "v": "28"},
      {"n": "\u8650\u604b", "v": "16"},
      {"n": "\u751c\u5ba0", "v": "21"},
      {"n": "\u60ac\u7591", "v": "27"},
      {"n": "\u641e\u7b11", "v": "793"},
      {"n": "\u7075\u5f02", "v": "1287"}
    ]
  }],
  "\u725b\u725b": [{
    "key": "area",
    "name": "\u5206\u7c7b",
    "value": [
      {"n": "\u5168\u90e8", "v": ""},
      {"n": "\u73b0\u8a00", "v": "\u73b0\u8a00"},
      {"n": "\u53e4\u8a00", "v": "\u53e4\u8a00"},
      {"n": "\u5386\u53f2", "v": "\u5386\u53f2"},
      {"n": "\u90fd\u5e02", "v": "\u90fd\u5e02"},
      {"n": "\u6d3b\u52a8", "v": "\u6d3b\u52a8"},
      {"n": "\u9006\u88ad", "v": "\u9006\u88ad"},
      {"n": "\u8c6a\u95e8", "v": "\u8c6a\u95e8"},
      {"n": "\u73b0\u4ee3\u8a00\u60c5", "v": "\u73b0\u4ee3\u8a00\u60c5"},
      {"n": "\u6218\u795e", "v": "\u6218\u795e"},
      {"n": "\u751c\u5ba0", "v": "\u751c\u5ba0"},
      {"n": "\u7a7f\u8d8a", "v": "\u7a7f\u8d8a"},
      {"n": "\u53e4\u88c5", "v": "\u53e4\u88c5"},
      {"n": "\u8650\u5fc3", "v": "\u8650\u5fc3"},
      {"n": "\u795e\u533b", "v": "\u795e\u533b"},
      {"n": "\u8d58\u5a7f", "v": "\u8d58\u5a7f"},
      {"n": "\u4eb2\u60c5", "v": "\u4eb2\u60c5"},
      {"n": "\u590d\u4ec7", "v": "\u590d\u4ec7"},
      {"n": "\u7384\u5e7b", "v": "\u7384\u5e7b"},
      {"n": "\u53e4\u4ee3\u8a00\u60c5", "v": "\u53e4\u4ee3\u8a00\u60c5"},
      {"n": "\u70ed\u8840", "v": "\u70ed\u8840"},
      {"n": "\u52a8\u4f5c", "v": "\u52a8\u4f5c"},
      {"n": "\u559c\u5267", "v": "\u559c\u5267"},
      {"n": "\u60ac\u7591", "v": "\u60ac\u7591"},
      {"n": "\u519b\u4e8b", "v": "\u519b\u4e8b"},
      {"n": "\u4e8c\u6b21\u5143", "v": "\u4e8c\u6b21\u5143"},
      {"n": "\u672a\u6765", "v": "\u672a\u6765"},
      {"n": "\u5feb\u901f\u7a7f\u8d8a", "v": "\u5feb\u901f\u7a7f\u8d8a"},
      {"n": "\u70e7\u8111", "v": "\u70e7\u8111"},
      {"n": "\u6cbb\u6108", "v": "\u6cbb\u6108"},
      {"n": "\u5176\u4ed6\u5267\u60c5", "v": "\u5176\u4ed6\u5267\u60c5"}
    ]
  }],
  "\u767e\u5ea6": [{
    "key": "area",
    "name": "\u5206\u7c7b",
    "value": [
      {"n": "\u65b0\u5267", "v": "\u65b0\u5267"},
      {"n": "\u9650\u65f6\u514d\u8d39", "v": "\u9650\u65f6\u514d\u8d39"},
      {"n": "\u7cbe\u9009", "v": "\u7cbe\u9009"},
      {"n": "\u72ec\u64ad", "v": "\u72ec\u64ad"},
      {"n": "\u5168\u90e8", "v": "\u5168\u90e8\u9898\u6750"},
      {"n": "\u795e\u533b", "v": "\u795e\u533b"},
      {"n": "\u8fde\u7eed\u5267", "v": "\u8fde\u7eed\u5267"},
      {"n": "\u90fd\u5e02", "v": "\u90fd\u5e02"},
      {"n": "\u73b0\u4ee3\u8a00\u60c5", "v": "\u73b0\u4ee3\u8a00\u60c5"},
      {"n": "\u5f02\u80fd", "v": "\u5f02\u80fd"},
      {"n": "\u9006\u88ad", "v": "\u9006\u88ad"},
      {"n": "\u751c\u5ba0", "v": "\u751c\u5ba0"},
      {"n": "\u603b\u88c1", "v": "\u603b\u88c1"},
      {"n": "\u840c\u5b9d", "v": "\u840c\u5b9d"},
      {"n": "\u6218\u795e", "v": "\u6218\u795e"},
      {"n": "\u5bab\u6597\u5b85\u6597", "v": "\u5bab\u6597\u5b85\u6597"},
      {"n": "\u795e\u8c6a", "v": "\u795e\u8c6a"},
      {"n": "\u8650\u604b", "v": "\u8650\u604b"},
      {"n": "\u95ea\u5a5a", "v": "\u95ea\u5a5a"},
      {"n": "\u7384\u5e7b", "v": "\u7384\u5e7b"},
      {"n": "\u7a7f\u8d8a\u91cd\u751f", "v": "\u7a7f\u8d8a\u91cd\u751f"},
      {"n": "\u5e74\u4ee3", "v": "\u5e74\u4ee3"},
      {"n": "\u5bb6\u5ead\u4f26\u7406", "v": "\u5bb6\u5ead\u4f26\u7406"},
      {"n": "\u53e4\u4ee3\u8a00\u60c5", "v": "\u53e4\u4ee3\u8a00\u60c5"},
      {"n": "\u6b66\u4fa0\u6b66\u6253", "v": "\u6b66\u4fa0\u6b66\u6253"},
      {"n": "\u8d58\u5a7f", "v": "\u8d58\u5a7f"},
      {"n": "\u5355\u5143\u5267", "v": "\u5355\u5143\u5267"},
      {"n": "\u9752\u6625\u6821\u56ed", "v": "\u9752\u6625\u6821\u56ed"},
      {"n": "\u5386\u53f2\u67b6\u7a7a", "v": "\u5386\u53f2\u67b6\u7a7a"},
      {"n": "\u738b\u5983", "v": "\u738b\u5983"},
      {"n": "\u9274\u5b9d", "v": "\u9274\u5b9d"},
      {"n": "\u79d1\u5e7b", "v": "\u79d1\u5e7b"},
      {"n": "\u519b\u65c5\u6218\u4e89", "v": "\u519b\u65c5\u6218\u4e89"},
      {"n": "\u79cd\u7530", "v": "\u79cd\u7530"}
    ]
  }],
  "\u56f4\u89c2": [{
    "key": "area",
    "name": "\u5206\u7c7b",
    "value": [
      {"n": "\u5168\u90e8", "v": ""}
    ]
  }],
  "\u788e\u7247": [{
    "key": "area",
    "name": "\u5206\u7c7b",
    "value": [
      {"n": "\u5168\u90e8", "v": ""}
    ]
  }],
  "\u6cb3\u9a6c": [{
    "key": "area",
    "name": "\u5206\u7c7b",
    "value": [
      {"n": "\u63a8\u8350", "v": "308"},
      {"n": "\u65b0\u5267", "v": "309"},
      {"n": "\u9006\u88ad", "v": "310"},
      {"n": "\u604b\u7231", "v": "311"},
      {"n": "\u5f3a\u8005\u56de\u5f52", "v": "312"},
      {"n": "\u8c6a\u95e8\u6069\u6028", "v": "313"},
      {"n": "\u53e4\u88c5", "v": "314"},
      {"n": "\u91cd\u751f", "v": "315"},
      {"n": "\u840c\u5b9d", "v": "316"},
      {"n": "\u590d\u4ec7", "v": "317"},
      {"n": "\u795e\u533b", "v": "318"},
      {"n": "\u9ad8\u624b\u4e0b\u5c71", "v": "319"},
      {"n": "\u8d85\u80fd\u60ac\u7591", "v": "320"},
      {"n": "\u4f20\u627f\u89c9\u9192", "v": "321"},
      {"n": "\u795e\u8c6a", "v": "322"},
      {"n": "\u6c11\u56fd", "v": "323"}
    ]
  }]
};

// \u6cb3\u9a6c\u5206\u7c7b\u6807\u7b7e\u6620\u5c04
const hemaTagIds = {
  "308": "",
  "309": "",
  "310": "417,473,474,464",
  "311": "462,466",
  "312": "476",
  "313": "585,616",
  "314": "444,468",
  "315": "417,439,464,465",
  "316": "589",
  "317": "416,439,463,465",
  "318": "438",
  "319": "417,474,464",
  "320": "439,442,443,445,465,470",
  "321": "417,473,474,464",
  "322": "472,475,585",
  "323": "590"
};

// ==================== \u521d\u59cb\u5316 ====================
async function init(cfg) {
  console.log(`\u3010${siteName}\u3011\u521d\u59cb\u5316\u5f00\u59cb`);
  
  // \u661f\u82bd\u767b\u5f55
  try {
    const loginData = { device: '24250683a3bdb3f118dff25ba4b1cba1a' };
    const response = await request(rule.星芽.login, {
      method: 'POST',
      headers: { 'User-Agent': 'okhttp/4.10.0', 'platform': '1', 'Content-Type': 'application/json' },
      data: loginData
    });
    
    const res = JSON.parse(response);
    const token = res?.data?.token || res?.data?.data?.token || res?.token || res?.result?.token || res?.access_token;
    
    if (token) {
      xingya_headers = { ...aggConfig.headers.default, authorization: token };
      console.log(`\u3010${siteName}\u3011\u661f\u82bd\u767b\u5f55\u6210\u529f`);
    } else {
      xingya_headers = aggConfig.headers.default;
    }
  } catch (e) {
    console.log(`\u3010${siteName}\u3011\u661f\u82bd\u767b\u5f55\u5931\u8d25: ${e.message}`);
    xingya_headers = aggConfig.headers.default;
  }
  
  // \u725b\u725b\u767b\u5f55
  try {
    // \u83b7\u53d6visitor token
    let tkhtml = await request(rule.牛牛.host + rule.牛牛.visitor, {
      headers: {
        "deviceid": "aa11fc54-ba9c-3980-add5-447d3fa5b939",
        "token": "",
        "User-Agent": "okhttp/4.12.0",
        "client": "app",
        "devicetype": "Android"
      }
    });

    let tkRes = JSON.parse(tkhtml);
    niuniu_token = tkRes.data.token;
    console.log("\u725b\u725btoken:", niuniu_token);
    
    // \u83b7\u53d6access_token
    let t = String(Math.floor(new Date().getTime() / 1000));
    let body = `ac=wifi&os=Android&vod_version=1.10.21.6-tob&os_version=9&type=1&clientVersion=v5.2.5&uuid=Y4WNZ3SAWK7MAJMH7CXCDHJ4VMPVFRZQTBSIA4XTYO4AWEUHIK6Q01&resolution=1280*2618&openudid=889edced38f1069b&dt=Pixel%204&sha1=46121F77CE2FCAD3DBC3B9EC8A24908C1A8AD6D9&os_api=28&install_id=1549688030634536&device_brand=google&sdk_version=1.1.3.0&package_name=com.niuniu.ztdh.app&siteid=5627189&dev_log_aid=667431&oaid=&timestamp=${t}`;
    
    let nonce = "VX1KKGtoBDCi1fB1";
    let Signature = t + nonce + body;
    let signature = hmacSHA256(Signature, 'aceaa47f96b4875d446b2e1d97e03bbb');
    let encbdoy = aesEncryptECB(body, 'dafdb3d2a5c343d6');
    
    let loginpost = await request(rule.牛牛.login, {
      headers: {
        'X-Salt': '786774955F',
        'X-Nonce': nonce,
        'X-Timestamp': t,
        'X-Signature': signature,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      data: encbdoy,
      method: "POST"
    });
    let logindata = aesDecryptECB(loginpost, 'dafdb3d2a5c343d6');
    let accesstoken = JSON.parse(logindata);
    niuniu_access_token = accesstoken.data.access_token;
    console.log(`\u3010${siteName}\u3011\u725b\u725b\u767b\u5f55\u6210\u529f`);
    
    niuniu_headers = {
      ...aggConfig.headers.niuniu,
      "token": niuniu_token,
      "deviceid": "aa11fc54-ba9c-3980-add5-447d3fa5b939"
    };
    
  } catch (e) {
    console.log(`\u3010${siteName}\u3011\u725b\u725b\u767b\u5f55\u5931\u8d25: ${e.message}`);
    niuniu_headers = aggConfig.headers.niuniu;
  }
  
  // \u6cb3\u9a6c\u521d\u59cb\u5316
  try {
    hema_headers = { ...aggConfig.headers.hema };
    console.log(`\u3010${siteName}\u3011\u6cb3\u9a6c\u521d\u59cb\u5316\u6210\u529f`);
  } catch (e) {
    console.log(`\u3010${siteName}\u3011\u6cb3\u9a6c\u521d\u59cb\u5316\u5931\u8d25: ${e.message}`);
    hema_headers = aggConfig.headers.hema;
  }
  
  return true;
}

// ==================== \u9996\u9875\u5206\u7c7b ====================
function home(filter) {
  const platForms = getPlatList();
  
  const classes = platForms.map(item => ({
    type_name: item.name, 
    type_id: item.id,
    type_flag: '[CFS][SUBSITE2][FILTERBAR]'
  }));
  
  const filters = {};
  platForms.forEach(item => {
    if (filterOptions[item.id]) filters[item.id] = filterOptions[item.id];
  });
  
  return JSON.stringify({ class: classes, filters: filters });
}

// ==================== \u9996\u9875\u63a8\u8350 ====================
async function homeVod() {
  const platForms = getPlatList();
  
  const randomPlat = platForms[Math.floor(Math.random() * platForms.length)];
  const randomArea = ruleFilterDef[randomPlat.id]?.area || '';
  
  const categoryResult = await category(randomPlat.id, 1, { area: randomArea }, {});
  const categoryList = JSON.parse(categoryResult).list || [];  
  
  return JSON.stringify({
    list: categoryList
  });
}

// ==================== \u5206\u7c7b\u5217\u8868 ====================
async function category(tid, pg, filter, extend) {
  const page = pg || 1;
  extend = extend || {};
  
  const platformItem = platformList.find(p => p.id === tid);
  if (platformItem && isSkipPlat(platformItem)) {
    return JSON.stringify({ list: [], page, pagecount: 1, limit: 0, total: 0 });
  }
  
  const searchKeyword = extend?.custom;
  if (searchKeyword) {
    return await cfs(tid, searchKeyword, pg);
  }
  
  const platRule = rule[tid];
  const area = filter?.area || extend?.area || ruleFilterDef[tid]?.area || '';
  const videos = [];
  
  switch (tid) {
    case '\u767e\u5ea6': {
      let sub = ["\u65b0\u5267","\u9650\u65f6\u514d\u8d39","\u7cbe\u9009","\u72ec\u64ad"].includes(area) ? area : "\u65b0\u5267";
      let tcsub = area === "\u5168\u90e8" || area === "\u5168\u90e8\u9898\u6750" ? "" : area;
      let t = Math.floor(Date.now() / 1000);
      let version = await md5(t + "v2");
      
      let postData = {
        'data': {
          "data": {
            "extRequest": { "flow_tabid": "13" },
            "from": "feed",
            "page": "channel_video_landing",
            "pd": "feed",
            "refreshIndex": parseInt(page),
            "cursor": "",
            "theme": "",
            "timestamp": t,
            "version": version,
            "themes": [
              { "kind": "\u7efc\u5408", "names": [sub] },
              { "kind": "\u9898\u6750", "names": [tcsub] }
            ]
          }
        }
      };
      
      let html = await request(`${platRule.host}${platRule.list}`, {
        method: 'POST',
        headers: aggConfig.headers.baidu,
        data: postData
      });
      let res = JSON.parse(html);
      let items = res.data?.items || [];
      items.slice(0, 20).forEach(it => {
        videos.push({
          vod_id: `\u767e\u5ea6@${it.collId}`,
          vod_name: it.title || '\u672a\u77e5\u77ed\u5267',
          vod_pic: it.img || '',
          vod_remarks: '\u767e\u5ea6\u77ed\u5267 | ' + (it.updateStatus || "\u66f4\u65b0\u4e2d"),
          vod_content: it.description || ''
        });
      });
      break;
    }
    
    case '\u751c\u5708': {
      const url = `${platRule.host}${platRule.list}=${area}&offset=${page}`;
      const response = await request(url, { headers: aggConfig.headers.default });
      const res = JSON.parse(response);
      (res.data || []).forEach(it => {
        videos.push({
          vod_id: `\u751c\u5708@${it.book_id}`,
          vod_name: it.title || '\u672a\u77e5\u6807\u9898',
          vod_pic: it.cover || '',
          vod_remarks: '\u751c\u5708\u77ed\u5267 | ' + (it.copyright || ''),
          vod_content: it.desc || ''
        });
      });
      break;
    }
    
    case '\u9526\u9ca4': {
      const postData = { page, limit: 24, type_id: area, year: '', keyword: '' };
      const response = await request(`${platRule.host}${platRule.search}`, {
        method: 'POST',
        data: postData
      });
      const res = JSON.parse(response);
      (res.data?.list || []).forEach(item => {
        videos.push({
          vod_id: `\u9526\u9ca4@${item.vod_id}`,
          vod_name: item.vod_name || '',
          vod_pic: item.vod_pic || '',
          vod_remarks: '\u9526\u9ca4\u77ed\u5267 | ' + (item.vod_total ? `${item.vod_total}\u96c6` : ''),
          vod_content: item.vod_tag || ''
        });
      });
      break;
    }
    
    case '\u756a\u8304': {
      const sessionId = new Date().toISOString().slice(0,16).replace(/-|T:/g,'');
      let url = `${platRule.host}${platRule.list}?change_type=0&selected_items=${area}&tab_type=8&cell_id=6952850996422770718&version_tag=video_feed_refactor&device_id=1423244030195267&aid=1967&app_name=novelapp&ssmix=a&session_id=${sessionId}`;
      if (page > 1) url += `&offset=${(page-1)*12}`;
      
      const response = await request(url, { headers: aggConfig.headers.default });
      const res = JSON.parse(response);
      let items = res?.data?.cell_view?.cell_data || res?.search_tabs?.find(t => t.title === '\u77ed\u5267' && t.data)?.data || res?.data || [];
      
      items.forEach(item => {
        const videoData = item.video_data?.[0] || item;
        videos.push({
          vod_id: `\u756a\u8304@${videoData.series_id || videoData.book_id || videoData.id || ''}`,
          vod_name: videoData.title || '\u672a\u77e5\u77ed\u5267',
          vod_pic: videoData.cover || videoData.horiz_cover || '',
          vod_remarks: '\u756a\u8304\u77ed\u5267 | ' + (videoData.sub_title || videoData.rec_text || ''),
          vod_content: videoData.abstract || ''
        });
      });
      break;
    }
    
    case '\u661f\u82bd': {
      const url = `${platRule.host}${platRule.list}=${area}&type=1&class2_ids=0&page_num=${page}&page_size=24`;
      const response = await request(url, { headers: xingya_headers });
      const res = JSON.parse(response);
      (res.data?.list || []).forEach(it => {
        videos.push({
          vod_id: `\u661f\u82bd@${it.theater.id}`,
          vod_name: it.theater.title || '',
          vod_pic: it.theater.cover_url || '',
          vod_remarks: '\u661f\u82bd\u77ed\u5267 | ' + (it.theater.total ? `${it.theater.total}\u96c6` : ''),
          vod_content: `\u64ad\u653e\u91cf:${it.theater.play_amount_str || 0}`
        });
      });
      break;
    }
    
    case '\u897f\u996d': {
      const [typeId, typeName] = area.split('@');
      const ts = Math.floor(Date.now() / 1000);
      const url = `${platRule.host}${platRule.list}?reqType=aggregationPage&offset=${(page-1)*30}&categoryId=${typeId}&quickEngineVersion=-1&scene=&categoryNames=${encodeURIComponent(typeName)}&categoryVersion=1&density=1.5&pageID=page_theater&version=2001001&androidVersionCode=28&requestId=${ts}aa498144140ef297&appId=drama&teenMode=false&userBaseMode=false&session=eyJpbmZvIjp7InVpZCI6IiIsInJ0IjoiMTc0MDY1ODI5NCIsInVuIjoiT1BHXzFlZGQ5OTZhNjQ3ZTQ1MjU4Nzc1MTE2YzFkNzViN2QwIiwiZnQiOiIxNzQwNjU4Mjk0In19&feedssession=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dHlwIjowLCJidWlkIjoxNjMzOTY4MTI2MTQ4NjQxNTM2LCJhdWQiOiJkcmFtYSIsInZlciI6MiwicmF0IjoxNzQwNjU4Mjk0LCJ1bm0iOiJPUEdfMWVkZDk5NmE2NDdlNDUyNTg3NzUxMTY2YzFkNzViN2QwIiwiZXhwIjoxNzQxMjYzMDk0LCJkYyI6Imd6cXkifQ.JS3QY6ER0P2cQSxAE_OGKSMIWNAMsYUZ3mJTnEpf-Rc`;
      
      const response = await request(url, { headers: aggConfig.headers.default });
      const res = JSON.parse(response);
      
      (res.result?.elements || []).forEach(soup => {
        (soup.contents || []).forEach(vod => {
          const dj = vod.duanjuVo || {};
          videos.push({
            vod_id: `\u897f\u996d@${dj.duanjuId}#${dj.source}`,
            vod_name: dj.title || '',
            vod_pic: dj.coverImageUrl || '',
            vod_remarks: '\u897f\u996d\u77ed\u5267 | ' + (dj.total ? `${dj.total}\u96c6` : ''),
            vod_content: dj.desc || ''
          });
        });
      });
      break;
    }
    
    case '\u8f6f\u9e2d': {
      const url = `${platRule.host}${platRule.list}/?keyword=${encodeURIComponent(area)}&page=${page}`;
      const response = await request(url, { headers: aggConfig.headers.default });
      const res = JSON.parse(response);
      (res.data || []).forEach(item => {
        const purl = `${item.title}@${item.cover}@${item.author}@${item.type}@${item.desc}@${item.book_id}`;
        videos.push({
          vod_id: `\u8f6f\u9e2d@${encodeURIComponent(purl)}`,
          vod_name: item.title || '',
          vod_pic: item.cover || '',
          vod_remarks: '\u8f6f\u9e2d\u77ed\u5267 | ' + (item.type || ''),
          vod_content: item.author || ''
        });
      });
      break;
    }
    
    case '\u4e03\u732b': {
      let signStr = `operation=1playlet_privacy=1tag_id=${area}${aggConfig.keys}`;
      const sign = await md5(signStr);
      const url = `${platRule.host}${platRule.list}?tag_id=${area}&playlet_privacy=1&operation=1&sign=${sign}`;
      const headers = await getQiMaoHeaders();
      
      const response = await request(url, { method: 'GET', headers });
      const res = JSON.parse(response);
      (res.data?.list || []).forEach(item => {
        videos.push({
          vod_id: `\u4e03\u732b@${encodeURIComponent(item.playlet_id)}`,
          vod_name: item.title || '',
          vod_pic: item.image_link || '',
          vod_remarks: '\u4e03\u732b\u77ed\u5267 | ' + (item.total_episode_num ? `${item.total_episode_num}\u96c6` : ''),
          vod_content: item.tags || ''
        });
      });
      break;
    }
    
    case '\u725b\u725b': {
      const postData = {
        condition: { classify: area, typeId: 'S1' },
        pageNum: page,
        pageSize: 24
      };
      const response = await request(`${platRule.host}${platRule.list}`, {
        method: 'POST',
        headers: niuniu_headers,
        data: postData
      });
      const res = JSON.parse(response);
      (res.data?.records || []).forEach(item => {
        videos.push({
          vod_id: `\u725b\u725b@${item.id}`,
          vod_name: item.name || '',
          vod_pic: item.cover || '',
          vod_remarks: '\u725b\u725b\u77ed\u5267 | ' + (item.totalEpisode ? `${item.totalEpisode}\u96c6` : ''),
          vod_content: item.description || ''
        });
      });
      break;
    }
    
    case '\u56f4\u89c2': {
      const postData = {
        audience: "\u5168\u90e8\u53d7\u4f17",
        page: page,
        pageSize: 30,
        searchWord: "",
        subject: "\u5168\u90e8\u4e3b\u9898"
      };
      
      const response = await request(`${platRule.host}${platRule.search}`, {
        method: 'POST',
        headers: aggConfig.headers.default,
        data: postData
      });
      const res = JSON.parse(response);
      if (res.code === 200 && res.data) {
        (res.data || []).forEach(it => {
          videos.push({
            vod_id: `\u56f4\u89c2@${it.oneId}`,
            vod_name: it.title || '\u672a\u77e5\u77ed\u5267',
            vod_pic: it.vertPoster || it.horizonPoster || '',
            vod_remarks: '\u56f4\u89c2\u77ed\u5267 | ' + `\u96c6\u6570:${it.episodeCount || 0}`,
            vod_content: it.description || ''
          });
        });
      }
      break;
    }
    
    case '\u788e\u7247': {
        const token = await getSuiPianToken();
        const headers = { ...aggConfig.headers.default, 'Authorization': token };
        const url = `${platRule.host}${platRule.search}?type=5&tagId=&pageNum=${page}&pageSize=24`;
        
        const response = await request(url, { headers });
        const res = JSON.parse(response);
        
        if (res && res.list && res.list.length > 0) {
          (res.list || []).forEach(it => {
            videos.push({
              vod_id: `\u788e\u7247@${it.itemId}@${it.videoCode}`,
              vod_name: it.title || '\u672a\u77e5\u5267\u540d',
              vod_pic: it.imageKey ? `https://free-api.bighotwind.cc/papaya/papaya-file/files/download/${it.imageKey}/${it.imageName || 'cover.jpg'}` : 'https://t8.baidu.com/it/u=615012979,225344800&fm=193',
              vod_remarks: '\u788e\u7247\u5267\u573a | ' + (it.episodesMax ? `${it.episodesMax}\u96c6` : '') + (it.hitShowNum ? ` \u64ad\u653e:${it.hitShowNum}` : ''),
              vod_content: it.content || it.description || ''
            });
          });
        }
        break; 
    }
    
    case '\u6cb3\u9a6c': {
      try {
        const sub = area || '308';
        const tagIds = hemaTagIds[sub] || '';
        
        const bodys = JSON.stringify({
          "recSwitch": true,
          "channelId": sub,
          "tagIds": tagIds,
          "cnxhFlag": page - 1,
          "playListFlag": true,
          "watchRecords": ["41000103722_572752006"]
        });
        
        const body = hemaEncrypt(bodys);
        
        const response = await request(`${platRule.host}${platRule.list}`, {
          method: 'POST',
          headers: hema_headers,
          data: body
        });
        
        const res = JSON.parse(response);
        const dehtml = res.data;
        
        if (dehtml) {
          const hmdata = hemaDecrypt(dehtml);
          if (hmdata && hmdata !== '{}') {
            const hmlist = JSON.parse(hmdata).columnData || [];
            hmlist.forEach(videoDataArray => {
              (videoDataArray.videoData || []).forEach(video => {
                videos.push({
                  vod_id: `\u6cb3\u9a6c@${video.bookId}`,
                  vod_name: video.bookName || '',
                  vod_pic: video.coverWap || video.coverCutWap,
                  vod_remarks: `\u6cb3\u9a6c\u77ed\u5267 | \u66f4\u65b0${video.updateNum || 0}\u96c6`,
                  vod_content: video.introduction || '',
                  vod_actor: video.author || '',
                  extra: {
                    bookId: video.bookId,
                    chapterId: video.chapterId,
                    chapterMin: video.updateNum,
                    chapterMax: video.chapterIndex
                  }
                });
              });
            });
          }
        }
      } catch (e) {
        console.log(`\u6cb3\u9a6c\u5206\u7c7b\u5931\u8d25: ${e.message}`);
      }
      break;
    }
  }
  
  return JSON.stringify({
    list: videos,
    page: page,
    pagecount: page + 1,
    limit: videos.length,
    total: videos.length * (page + 1)
  });
}

// ==================== \u8be6\u60c5 ====================
async function detail(id) {
  
  const parts = id.split('@');
  const platform = parts[0];
  const did = parts.slice(1).join('@');
  const platRule = rule[platform];
  let vod = {};
  
  switch (platform) {
    case '\u767e\u5ea6': {
      const postData = { playlet_id: did, vid: "undefined" };
      let html = await request(`${platRule.detailHost}${platRule.detail}`, {
        method: 'POST',
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        data: postData
      });
      let res = JSON.parse(html);
      let dthtml = res.data || {};
      let vids = dthtml.vid_list || [];
      let playArr = vids.map((vid, index) => `\u7b2c${index+1}\u96c6$${vid}`);
      
      vod = {
        vod_id: id,
        vod_name: dthtml.playlet_title || '\u672a\u77e5\u77ed\u5267',
        vod_pic: dthtml.playlet_poster || '',
        vod_content: `\u70ed\u5ea6\u503c:${dthtml.hot_value||0}\n\u9898\u6750:${dthtml.tag_text||''}\n\u96c6\u6570:${dthtml.episodes_num||0}\n\u7b80\u4ecb:${dthtml.description||''}`,
        vod_remarks: `\u5171${vids.length||0}\u96c6`,
        vod_director: dthtml.tag_text || '',
        vod_year: dthtml.create_time || '',
        vod_play_from: "\u767e\u5ea6\u77ed\u5267",
        vod_play_url: playArr.join('#')
      };
      break;
    }
    
    case '\u751c\u5708': {
      const response = await request(`${platRule.host}${platRule.detail}=${did}`);
      const res = JSON.parse(response);
      vod = {
        vod_id: id,
        vod_name: res.book_name || '\u672a\u77e5\u6807\u9898',
        vod_type: res.category || '',
        vod_pic: res.book_pic || '',
        vod_remarks: res.duration || '',
        vod_year: `\u66f4\u65b0\u65f6\u95f4:${res.time || '\u672a\u77e5'}`,
        vod_actor: res.author || '',
        vod_content: res.desc || '',
        vod_play_from: '\u751c\u5708\u77ed\u5267',
        vod_play_url: (res.data || []).map(item => `${item.title || '\u7b2c1\u96c6'}$${item.video_id || item.id || ''}`).join('#')
      };
      break;
    }
    
    case '\u9526\u9ca4': {
      const response = await request(`${platRule.host}${platRule.detail}/${did}`);
      const res = JSON.parse(response);
      const list = res.data || {};
      const playUrls = list.player ? Object.keys(list.player).map(key => `${key}$${list.player[key]}`) : [];
      vod = {
        vod_id: list.vod_id || id,
        vod_name: list.vod_name || '\u6682\u65e0\u540d\u79f0',
        vod_type: list.vod_class || '\u6682\u65e0\u7c7b\u578b',
        vod_pic: list.vod_pic || '\u6682\u65e0\u56fe\u7247',
        vod_remarks: list.vod_remarks || '\u6682\u65e0\u5907\u6ce8',
        vod_year: list.vod_year || '\u6682\u65e0\u5e74\u4efd',
        vod_area: list.vod_area || '\u6682\u65e0\u5730\u533a',
        vod_actor: list.vod_actor || '\u6682\u65e0\u6f14\u5458',
        vod_director: list.vod_director || '\u6682\u65e0\u5bfc\u6f14',
        vod_content: list.vod_blurb || '\u6682\u65e0\u5267\u60c5',
        vod_play_from: '\u9526\u9ca4\u77ed\u5267',
        vod_play_url: playUrls.join('#')
      };
      break;
    }
    
    case '\u756a\u8304': {
      const response = await request(`${platRule.detail}?book_id=${did}`);
      const res = JSON.parse(response);
      const bookInfo = res.data?.book_info || {};
      const playList = (res.data?.item_data_list || []).map(item => `${item.title}$${item.item_id}`).join('#');
      vod = {
        vod_id: bookInfo.book_id || id,
        vod_name: bookInfo.book_name || '',
        vod_type: bookInfo.tags || '',
        vod_year: bookInfo.create_time || '',
        vod_pic: bookInfo.thumb_url || bookInfo.audio_thumb_uri || '',
        vod_content: bookInfo.abstract || bookInfo.book_abstract_v2 || '',
        vod_remarks: bookInfo.sub_info || `\u66f4\u65b0\u81f3${res.data?.item_data_list?.length || 0}\u96c6`,
        vod_play_from: '\u756a\u8304\u77ed\u5267',
        vod_play_url: playList
      };
      break;
    }
    
    case '\u661f\u82bd': {
      const detailUrl = `${platRule.host}${platRule.detail}?theater_parent_id=${did}`;
      const response = await request(detailUrl, { headers: xingya_headers });
      const res = JSON.parse(response);
      
      if (res.code === 'ok' && res.data) {
        const data = res.data;
        const playUrls = [];
        if (data.theaters && Array.isArray(data.theaters)) {
          data.theaters.forEach((item) => {
            if (item.son_video_url) {
              const epTitle = `\u7b2c${item.num}\u96c6`;
              playUrls.push(`${epTitle}$${item.son_video_url}`);
            }
          });
        }
        
        vod = {
          vod_id: id,
          vod_name: data.title || '\u672a\u77e5\u5267\u540d',
          vod_type: data.class_two?.map(c => c.class_name).join(',') || '',
          vod_pic: data.cover_url || '',
          vod_area: `\u6536\u85cf${data.collect_number || 0}`,
          vod_actor: `\u70b9\u8d5e${data.like_num || 0}`,
          vod_director: `\u8bc4\u5206${data.score || 0}`,
          vod_remarks: data.is_over === 2 ? '\u8fde\u8f7d\u4e2d' : '\u5df2\u5b8c\u7ed3',
          vod_content: data.introduction || data.desc || '',
          vod_play_from: '\u661f\u82bd\u77ed\u5267',
          vod_play_url: playUrls.length > 0 ? playUrls.join('#') : '\u6682\u65e0\u64ad\u653e\u5730\u5740$0'
        };
      }
      break;
    }
    
    case '\u897f\u996d': {
      const [duanjuId, source] = did.split('#');
      const url = `${platRule.host}${platRule.detail}?duanjuId=${duanjuId}&source=${source}`;
      const response = await request(url, { headers: aggConfig.headers.default });
      const res = JSON.parse(response);
      const data = res.result || {};
      const playUrls = (data.episodeList || []).map(ep => `${ep.index}$${ep.playUrl}`).join('#');
      
      vod = {
        vod_id: id,
        vod_name: data.title || '',
        vod_pic: data.coverImageUrl || '',
        vod_content: data.desc || '\u672a\u77e5',
        vod_remarks: data.updateStatus === 'over' ? `${data.total || 0}\u96c6 \u5df2\u5b8c\u7ed3` : `\u66f4\u65b0${data.total || 0}\u96c6`,
        vod_play_from: '\u897f\u996d\u77ed\u5267',
        vod_play_url: playUrls
      };
      break;
    }
    
    case '\u8f6f\u9e2d': {
      const didDecoded = decodeURIComponent(did);
      const parts = didDecoded.split('@');
      const title = parts[0] || '';
      const img = parts[1] || '';
      const author = parts[2] || '';
      const type = parts[3] || '';
      const desc = parts[4] || '';
      const book_id = parts[5] || did.split('@')[5] || '';
      
      const detailUrl = `${platRule.host}${platRule.list}/?book_id=${book_id}`;
      const response = await request(detailUrl, { headers: aggConfig.headers.default });
      const res = JSON.parse(response);
      const playUrls = (res.data?.video_list || []).map(ep => `${ep.title}$${ep.video_id}`).join('#');
      
      vod = {
        vod_id: id,
        vod_name: title || '',
        vod_pic: img || '',
        vod_actor: author || '',
        vod_remarks: type || '',
        vod_content: desc || '',
        vod_play_from: '\u8f6f\u9e2d\u77ed\u5267',
        vod_play_url: playUrls
      };
      break;
    }
    
    case '\u4e03\u732b': {
      const didDecoded = decodeURIComponent(did);
      const sign = await md5(`playlet_id=${didDecoded}${aggConfig.keys}`);
      const url = `${platRule.detail}?playlet_id=${didDecoded}&sign=${sign}`;
      const headers = await getQiMaoHeaders();
      
      const response = await request(url, { method: 'GET', headers });
      const res = JSON.parse(response);
      const data = res.data || {};
      
      vod = {
        vod_id: id,
        vod_name: data.title || '\u672a\u77e5\u6807\u9898',
        vod_pic: data.image_link || '\u672a\u77e5\u56fe\u7247',
        vod_actor: '',
        vod_remarks: `${data.tags || ''} ${data.total_episode_num || 0}\u96c6`,
        vod_content: data.intro || '\u672a\u77e5\u5267\u60c5',
        vod_play_from: '\u4e03\u732b\u77ed\u5267',
        vod_play_url: (data.play_list || []).map(it => `${it.sort}$${it.video_url}`).join('#')
      };
      break;
    }
    
    case '\u725b\u725b': {
      const descData = await request(`${platRule.host}${platRule.desc}`, {
        method: 'POST',
        headers: niuniu_headers,
        data: { id: did, typeId: 'S1' }
      });
      const descRes = JSON.parse(descData);
      const descInfo = descRes.data || {};
      
      const listData = await request(`${platRule.host}${platRule.detail}`, {
        method: 'POST',
        headers: niuniu_headers,
        data: { id: did, source: 0, typeId: 'S1', userId: '546932' }
      });
      const listRes = JSON.parse(listData);
      const listInfo = listRes.data || {};
      
      let playUrls = '';
      if (listInfo.url && listInfo.episodeList && listInfo.episodeList.length > 0) {
        playUrls = (listInfo.episodeList || []).map(ep => `${ep.episode}$${did}+${ep.id}`).join('#');
      } else if (listInfo.thirdPlayId) {
        let thirdPlayId = listInfo.thirdPlayId;
        
        let data1 = "not_include=0&lock_free=1&type=1&clientVersion=v5.2.5&uuid=6IDYUSASPQY5BBVACWQW3LLTPV4V7DE26UOCX5TZTVUGX4VUJNXQ01&resolution=1080*2320&openudid=82f4175d577a2939&dt=22021211RC&os_api=31&install_id=1496879012031075&sdk_version=1.1.3.0&siteid=5627189&dev_log_aid=667431&oaid=abec0dfff623201b&timestamp=1752498494&direction=0&ac=mobile&os=Android&vod_version=1.10.21.6-tob&os_version=12&count=1&index=1&shortplay_id="+thirdPlayId+"&sha1=46121F77CE2FCAD3DBC3B9EC8A24908C1A8AD6D9&device_brand=Redmi&package_name=com.niuniu.ztdh.app";
        
        try {
          let html1 = await niuniuPost(rule.牛牛.detail2, data1, "1");
          if (html1 && html1.data && html1.data.episode_right_list) {
            playUrls = html1.data.episode_right_list.map(it => {
              let lockType = it.lock_type || 'free';
              return `\u7b2c${it.index}\u96c6$${it.index}+${lockType}+${thirdPlayId}`;
            }).join('#');
          }
        } catch (e) {
          console.log("\u83b7\u53d6\u52a0\u5bc6\u5267\u96c6\u5931\u8d25:", e.message);
        }
      }
      
      vod = {
        vod_id: id,
        vod_name: descInfo.name || listInfo.name || '\u672a\u77e5\u540d\u79f0',
        vod_pic: descInfo.cover || listInfo.cover || '',
        vod_content: `\u7c7b\u578b\uff1a${descInfo.classify || ''}\n\u8bc4\u5206\uff1a${descInfo.score || ''}\n\u7b80\u4ecb\uff1a${descInfo.introduce || ''}`,
        vod_remarks: `\u5171${descInfo.totalEpisode || listInfo.totalEpisode || 0}\u96c6`,
        vod_play_from: '\u725b\u725b\u77ed\u5267',
        vod_play_url: playUrls || '\u6682\u65e0\u64ad\u653e\u5730\u5740$0'
      };
      break;
    }
    
    case '\u56f4\u89c2': {
      const response = await request(`${platRule.host}${platRule.detail}&oneId=${did}&page=1&pageSize=1000`, {
        headers: aggConfig.headers.default
      });
      const res = JSON.parse(response);
      if (res.code === 200 && res.data) {
        const data = res.data || [];
        const firstEpisode = data[0] || {};
        
        vod = {
          vod_id: id,
          vod_name: firstEpisode.title || '',
          vod_pic: firstEpisode.vertPoster || firstEpisode.horizonPoster || '',
          vod_remarks: `\u5171${data.length || 0}\u96c6`,
          vod_content: `\u64ad\u653e\u91cf:${firstEpisode.viewCount || 0} \u6536\u85cf:${firstEpisode.collectionCount || 0} \u8bc4\u8bba:${firstEpisode.commentCount || 0}`,
          vod_play_from: '\u56f4\u89c2\u77ed\u5267',
          vod_play_url: data.map(ep => {
          let playSetting = ep.playSetting || ep.videoClarityList || [];
          try {
            if (typeof playSetting === 'string') {
              playSetting = JSON.parse(playSetting);
            }
          } catch (e) {}
        
          // \u786e\u4fdd\u662f\u6570\u7ec4
          if (!Array.isArray(playSetting)) playSetting = [];
        
          // \u6e05\u6670\u5ea6\u4f18\u5148\u7ea7\uff1a1080P > 720P > 480P
          const url = (
            playSetting.find(item => item.name === '1080P')?.url ||
            playSetting.find(item => item.name === '720P')?.url ||
            playSetting.find(item => item.name === '480P')?.url ||
            ''
          );
        
          const title = `\u7b2c${ep.playOrder || 1}\u96c6`;
          return `${title}$${url}`;
        }).filter(ep => ep.split('$')[1]).join('#')
        };
      }
      break;
    }
    
    case '\u788e\u7247': {
      const [itemId, videoCode] = did.split('@');
      const token = await getSuiPianToken();
      const headers = { ...aggConfig.headers.default, 'Authorization': token };
      const url = `${platRule.host}${platRule.detail}?videoCode=${videoCode}&itemId=${itemId}`;
      
      const response = await request(url, { headers });
      const res = JSON.parse(response);
      const data = res.data || res;
      const playUrls = (data.episodesList || []).map(episode => {
        let title = `\u7b2c${episode.episodes || 1}\u96c6`;
        if (episode.resolutionList?.length) {
          episode.resolutionList.sort((a, b) => b.resolution - a.resolution);
          let best = episode.resolutionList[0];
          return `${title}$${`https://free-api.bighotwind.cc/papaya/papaya-file/files/download/${best.fileKey}/${best.fileName}`}`;
        }
        return null;
      }).filter(item => item).join('#');
      
      vod = {
        vod_id: id,
        vod_name: data.title || '',
        vod_pic: `https://free-api.bighotwind.cc/papaya/papaya-file/files/download/${data.imageKey || ''}/${data.imageName || ''}`,
        vod_remarks: `\u5171${data.episodesMax || 0}\u96c6`,
        vod_content: data.content || data.description || `\u64ad\u653e\u91cf:${data.hitShowNum || 0} \u70b9\u8d5e:${data.likeNum || 0}`,
        vod_play_from: '\u788e\u7247\u5267\u573a',
        vod_play_url: playUrls
      };
      break;
    }
    
    case '\u6cb3\u9a6c': {
      const bookId = did;
      
      // \u83b7\u53d6\u8be6\u60c5
      const body = hemaEncrypt(JSON.stringify({ "bookId": bookId }));
      const detailResponse = await request(`${platRule.host}${platRule.detail}`, {
        method: 'POST',
        headers: hema_headers,
        data: body
      });
      
      const detailRes = JSON.parse(detailResponse);
      const detailHtml = detailRes.data;
      const postdata = hemaDecrypt(detailHtml);
      const videoInfo = JSON.parse(postdata).videoInfo || {};
      
      // \u83b7\u53d6\u5267\u96c6
      const episodeBody = hemaEncrypt(JSON.stringify({
        "bookId": bookId,
        "chapterMin": videoInfo.updateNum || 0,
        "chapterMax": videoInfo.chapterIndex || 0
      }));
      
      const episodeResponse = await request(`${platRule.host}${platRule.episode}`, {
        method: 'POST',
        headers: hema_headers,
        data: episodeBody
      });
      
      const episodeRes = JSON.parse(episodeResponse);
      const episodeHtml = episodeRes.data;
      const playdata = hemaDecrypt(episodeHtml);
      const chapterList = JSON.parse(playdata).chapterList || [];
      // \u6784\u5efa\u64ad\u653e\u5217\u8868
      const playUrls = chapterList.map(item => 
        `${item.chapterName}$${item.chapterId}++${item.chapterIndex}++${bookId}`
      ).join('#');
      
      // \u5904\u7406\u6570\u7ec4\u5b57\u6bb5
      const vodType = Array.isArray(videoInfo.bookTags) ? videoInfo.bookTags.join(',') : (videoInfo.bookTags || '');
      const vodActor = Array.isArray(videoInfo.protagonist) ? videoInfo.protagonist.join(',') : (videoInfo.protagonist || '');
      
      vod = {
        vod_id: id,
        vod_name: videoInfo.bookName || '\u672a\u77e5\u5267\u540d',
        vod_type: vodType,
        vod_pic: videoInfo.coverWap,
        vod_remarks: videoInfo.finishStatusCn || `\u66f4\u65b0\u81f3${videoInfo.updateNum || 0}\u96c6`,
        vod_content: videoInfo.introduction || '\u6682\u65e0\u7b80\u4ecb',
        vod_actor: vodActor,
        vod_director: videoInfo.author || '',
        vod_year: videoInfo.updateTime || '',
        vod_play_from: '\u6cb3\u9a6c\u77ed\u5267',
        vod_play_url: playUrls || '\u6682\u65e0\u64ad\u653e\u5730\u5740$0'
      };
      break;
    }
  }
  
  return JSON.stringify({ list: [vod] });
}

// ==================== \u64ad\u653e ====================
async function play(flag, id, flags) {
  if (/百度/.test(flag)) {
    const postData = { method: "post", vid: id };
    let html = await request(`${rule.\u767e\u5ea6.detailHost}${rule.\u767e\u5ea6.play}`, {
      method: 'POST',
      headers: aggConfig.headers.baidu,
      data: postData
    });
    
    let res = JSON.parse(html);
    let json = res["video/relate"]?.data?.cur_video;
    
    if (!json?.clarityUrl) {
      return JSON.stringify({ parse: 0, url: id });
    }
    
    let urls = json.clarityUrl
      .filter(item => item.url && item.title)
      .map(item => ({
        title: item.title,
        url: item.url,
        order: { '\u84dd\u5149': 1, '\u8d85\u6e05': 2, '\u6807\u6e05': 3 }[item.title] || 999
      }))
      .sort((a, b) => a.order - b.order)
      .flatMap(item => [item.title, item.url]);
    
    return JSON.stringify({
      parse: urls.length > 0 ? 0 : 1,
      url: urls.length > 0 ? urls : id,
      header: { 
        'User-Agent': aggConfig.headers.baidu['User-Agent'],
        'Referer': 'https://mbd.baidu.com/'
      }
    });
  }
  
  if (/甜圈/.test(flag)) {
    return JSON.stringify({ parse: 0, url: `https://mov.cenguigui.cn/duanju/api.php?video_id=${id}&type=mp4` });
  }
  
  if (/锦鲤/.test(flag)) {
    try {
      const response = await request(`${id}&auto=1`);
      const match = response.match(/let data\s*=\s*({[^;]*});/);
      if (match) {
        const data = JSON.parse(match[1]);
        return JSON.stringify({ parse: 0, url: data.url });
      }
    } catch (error) {}
  }
  
  if (/番茄/.test(flag)) {
    const response = await request(`https://fqgo.52dns.cc/video?item_ids=${id}`, {
      headers: aggConfig.headers.default
    });
    const res = JSON.parse(response);
    if (res.data?.[id]) {
      const videoModel = JSON.parse(res.data[id].video_model);
      const url = videoModel?.video_list?.video_1 ? base64Decode(videoModel.video_list.video_1.main_url) : '';
      return JSON.stringify({ parse: 0, url });
    }
  }
  
  if (/软鸭/.test(flag)) {
    const response = await request(`${rule.\u8f6f\u9e2d.host}/API/playlet/?video_id=${id}&quality=original`, {
      headers: aggConfig.headers.default
    });
    const res = JSON.parse(response);
    return JSON.stringify({ parse: 0, url: res.data?.video?.url || '' });
  }
  
  if (/牛牛/.test(flag)) {
    const inputArr = id.split('+');
    
    if (inputArr.length === 2) {
      var match = inputArr[0].match(/\d+/);
      var ep = match ? match[0] : "";
      var videoId = inputArr[1];
      
      var postData = {
        id: videoId,
        source: 0,
        typeId: "S1",
        userId: "546932",
        episodeId: ep
      };
      
      var response = await request(`${rule.\u725b\u725b.host}/api/v1/app/play/movieDetails`, {
        method: 'POST',
        headers: niuniu_headers,
        data: postData
      });
      
      var result = JSON.parse(response);
      if (result.code == 200 && result.data && result.data.url) {
        return JSON.stringify({ parse: 0, url: result.data.url });
      } else {
        return JSON.stringify({ parse: 0, url: id });
      }
    }
    else if (inputArr.length === 3) {
      var index = inputArr[0];
      var lock_type = inputArr[1];
      var thirdPlayId = inputArr[2];
      
      if (lock_type === "free") {
        let frdata = "not_include=0&lock_free=1&type=1&clientVersion=v5.2.5&uuid=6IDYUSASPQY5BBVACWQW3LLTPV4V7DE26UOCX5TZTVUGX4VUJNXQ01&resolution=1080*2320&openudid=82f4175d577a2939&dt=22021211RC&os_api=31&install_id=1496879012031075&sdk_version=1.1.3.0&siteid=5627189&dev_log_aid=667431&oaid=abec0dfff623201b&timestamp=1752498494&direction=0&ac=mobile&os=Android&vod_version=1.10.21.6-tob&os_version=12&count=1&index=1&shortplay_id="+thirdPlayId+"&sha1=46121F77CE2FCAD3DBC3B9EC8A24908C1A8AD6D9&device_brand=Redmi&package_name=com.niuniu.ztdh.app";
        let frhtml = await niuniuPost(rule.牛牛.detail2, frdata, index);
        if (frhtml && frhtml.data && frhtml.data.list && frhtml.data.list[0]) {
          let url = base64Decode(frhtml.data.list[0].video_model.video_list.video_1.main_url);
          return JSON.stringify({ parse: 0, url });
        }
      } else {
        let unlockData = "ac=mobile&os=Android&vod_version=1.10.21.6-tob&os_version=12&lock_ad=3&lock_free=3&type=1&clientVersion=v5.2.5&uuid=6IDYUSASPQY5BBVACWQW3LLTPV4V7DE26UOCX5TZTVUGX4VUJNXQ01&resolution=1080*2320&openudid=82f4175d577a2939&shortplay_id=" + thirdPlayId + "&dt=22021211RC&sha1=46121F77CE2FCAD3DBC3B9EC8A24908C1A8AD6D9&lock_index=21&os_api=31&install_id=1496879012031075&device_brand=Redmi&sdk_version=1.1.3.0&package_name=com.niuniu.ztdh.app&siteid=5627189&dev_log_aid=667431&oaid=abec0dfff623201b&timestamp=1752498493";
        
        await niuniuPost(rule.牛牛.unlock, unlockData, index);
        
        let udata = "not_include=0&lock_free=1&type=1&clientVersion=v5.2.5&uuid=6IDYUSASPQY5BBVACWQW3LLTPV4V7DE26UOCX5TZTVUGX4VUJNXQ01&resolution=1080*2320&openudid=82f4175d577a2939&dt=22021211RC&os_api=31&install_id=1496879012031075&sdk_version=1.1.3.0&siteid=5627189&dev_log_aid=667431&oaid=abec0dfff623201b&timestamp=1752498494&direction=0&ac=mobile&os=Android&vod_version=1.10.21.6-tob&os_version=12&count=1&index=1&shortplay_id="+thirdPlayId+"&sha1=46121F77CE2FCAD3DBC3B9EC8A24908C1A8AD6D9&device_brand=Redmi&package_name=com.niuniu.ztdh.app";
        let unhtml = await niuniuPost(rule.牛牛.detail2, udata, index);
        if (unhtml && unhtml.data && unhtml.data.list && unhtml.data.list[0]) {
          let url = base64Decode(unhtml.data.list[0].video_model.video_list.video_1.main_url);
          return JSON.stringify({ parse: 0, url });
        }
      }
    }
    
    return JSON.stringify({ parse: 0, url: id });
  }
  
  if (/围观/.test(flag)) {
    try {
      let playSetting = typeof id === 'string' ? JSON.parse(id) : id;
      let urls = [];
      if (playSetting.super) urls.push("\u8d85\u6e05", playSetting.super);
      if (playSetting.high) urls.push("\u9ad8\u6e05", playSetting.high);
      if (playSetting.normal) urls.push("\u6d41\u7545", playSetting.normal);
      return JSON.stringify({ parse: 0, url: urls.length ? urls : id });
    } catch (e) {
      return JSON.stringify({ parse: 0, url: id });
    }
  }
  
  if (/星芽/.test(flag)) {
    return JSON.stringify({ parse: 0, url: id });
  }
  
  if (/河马/.test(flag)) {
    try {
      let arr = id.split("++");
      let chapterId = arr[0];
      let index = arr[1];
      let bookId = arr[2];
      
      let fsbody = JSON.stringify({
        "bookId": bookId,
        "chapterId": chapterId,
        "unClockType": "pay",
        "confirmPay": 2,
        "autoPayFlag": true,
        "omap": {
          "channelName": "\u7cbe\u9009",
          "logId": "17a6500357709bb2547e1e122b438cfc",
          "originName": "\u4e66\u57ce",
          "recId": "bigdata_rec",
          "scene": "nsc_727",
          "sceneId": "dzmf_video_sc_reco",
          "strategyId": "g6y6b5sq"
        }
      });
      
      let fsbodyEnc = hemaEncrypt(fsbody);
      
      let response = await request(rule.河马.host + rule.河马.play, {
        method: 'POST',
        headers: hema_headers,
        data: fsbodyEnc
      });
      
      let res = JSON.parse(response);
      let fshtml = res.data;
      if (fshtml) {
        let fsdata = hemaDecrypt(fshtml);
        if (fsdata && fsdata !== '{}') {
          let parsed = JSON.parse(fsdata);
          let type = parsed.chaptersPayType;
          
          if (type == '\u514d\u8d39') {
            let data = parsed.chapterInfo || [];
            let url = data[0].content.m3u8720p || [];
            if (data.length > 0 && data[0].content.m3u8720p) {
              return JSON.stringify({ parse: 0, url: url });
            }
          }
        }
      }
      
      let playurl = "https://api.cenguigui.cn/api/duanju/hema.php?book_id=" + bookId + "&video_id=" + chapterId + "&type=mp4";
      return JSON.stringify({ parse: 0, url: playurl + '#isVideo=true#' });
      
    } catch (e) {
      console.log(`\u6cb3\u9a6c\u64ad\u653e\u5931\u8d25: ${e.message}`);
      return JSON.stringify({ parse: 0, url: id });
    }
  }
  
  return JSON.stringify({ parse: 0, url: id });
}

// ==================== \u641c\u7d22 ====================
async function cfs(siteId, wd, pg) {
  const page = pg || 1;
  const searchLimit = 20;
  const searchTimeout = 6000;
  let results = [];
  
  const platformItem = platformList.find(p => p.id === siteId);
  if (platformItem && isSkipPlat(platformItem)) {
    return JSON.stringify({ list: [], page, pagecount: page + 1, limit: 0, total: 0 });
  }
  
  const platRule = rule[siteId];
  
  switch (siteId) {
    case '\u767e\u5ea6': {
      let innerData = {
        query: wd,
        page: page,
        attribute: ["title"],
        fe_page_type: "search",
        extra: {
          tab_id: "216",
          flow_tabid: "13",
          shortplay_source: "feed",
          from: "feed",
          tab_type: "\u641c\u7d22",
          sub_template: "playlet_search_result"
        }
      };
      
      let postData = { 'data': { "data": innerData } };
      let html = await request(`${platRule.host}${platRule.search}`, {
        method: 'POST',
        headers: aggConfig.headers.baidu,
        data: postData,
        timeout: searchTimeout
      });
      
      let res = JSON.parse(html);
      let data = res.data?.itemList || [];
      results = data.map(it => ({
        vod_id: `\u767e\u5ea6@${it.nid?.split("_")[1] || ''}`,
        vod_name: it.title || '\u672a\u77e5\u77ed\u5267',
        vod_pic: it.img || '',
        vod_remarks: '\u767e\u5ea6\u77ed\u5267 | ' + (it.collNum || "\u641c\u7d22\u77ed\u5267"),
        vod_content: it.description || ''
      }));
      break;
    }
    
    case '\u751c\u5708': {
      const url = `${platRule.host}${platRule.search}=${encodeURIComponent(wd)}&offset=${page}`;
      const response = await request(url, { headers: aggConfig.headers.default, timeout: searchTimeout });
      const res = JSON.parse(response);
      results = (res.data || []).map(item => ({
        vod_id: `\u751c\u5708@${item.book_id}`,
        vod_name: item.title || '\u672a\u77e5\u6807\u9898',
        vod_pic: item.cover || '',
        vod_remarks: '\u751c\u5708\u77ed\u5267 | ' + (item.copyright || ''),
        vod_content: item.desc || ''
      }));
      break;
    }
    
    case '\u9526\u9ca4': {
      const postData = { page, limit: searchLimit, type_id: '', year: '', keyword: wd };
      const response = await request(`${platRule.host}${platRule.search}`, {
        method: 'POST',
        data: postData,
        timeout: searchTimeout
      });
      const res = JSON.parse(response);
      results = (res.data?.list || []).map(item => ({
        vod_id: `\u9526\u9ca4@${item.vod_id}`,
        vod_name: item.vod_name || '\u672a\u77e5\u77ed\u5267',
        vod_pic: item.vod_pic || '',
        vod_remarks: '\u9526\u9ca4\u77ed\u5267 | ' + (item.vod_total ? `${item.vod_total}\u96c6` : ''),
        vod_content: ''
      }));
      break;
    }
    
    case '\u756a\u8304': {
      const url = `${platRule.search}?keyword=${encodeURIComponent(wd)}&page=${page}`;
      const response = await request(url, { headers: aggConfig.headers.default, timeout: searchTimeout });
      const res = JSON.parse(response);
      results = (res.data || []).map(item => ({
        vod_id: `\u756a\u8304@${item.series_id || ''}`,
        vod_name: item.title || '\u672a\u77e5\u6807\u9898',
        vod_pic: item.cover || '',
        vod_remarks: '\u756a\u8304\u77ed\u5267 | ' + (item.sub_title || ''),
        vod_content: ''
      }));
      break;
    }
    
    case '\u661f\u82bd': {
      const postData = { text: wd };
      const response = await request(`${platRule.host}${platRule.search}`, {
        method: 'POST',
        headers: xingya_headers,
        data: postData,
        timeout: searchTimeout
      });
      const res = JSON.parse(response);
      results = (res.data?.theater?.search_data || []).map(item => ({
        vod_id: `\u661f\u82bd@${item.id}`,
        vod_name: item.title || '',
        vod_pic: item.cover_url || '',
        vod_remarks: '\u661f\u82bd\u77ed\u5267 | ' + (item.total ? `${item.total}\u96c6` : ''),
        vod_content: item.introduction || ''
      }));
      break;
    }
    
    case '\u897f\u996d': {
      const ts = Math.floor(Date.now() / 1000);
      const url = `${platRule.host}${platRule.search}?reqType=search&offset=${(page-1)*searchLimit}&keyword=${encodeURIComponent(wd)}&quickEngineVersion=-1&scene=&categoryVersion=1&density=1.5&pageID=page_theater&version=2001001&androidVersionCode=28&requestId=${ts}aa498144140ef297&appId=drama&teenMode=false&userBaseMode=false&session=eyJpbmZvIjp7InVpZCI6IiIsInJ0IjoiMTc0MDY1ODI5NCIsInVuIjoiT1BHXzFlZGQ5OTZhNjQ3ZTQ1MjU4Nzc1MTE2YzFkNzViN2QwIiwiZnQiOiIxNzQwNjU4Mjk0In19&feedssession=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dHlwIjowLCJidWlkIjoxNjMzOTY4MTI2MTQ4NjQxNTM2LCJhdWQiOiJkcmFtYSIsInZlciI6MiwicmF0IjoxNzQwNjU4Mjk0LCJ1bm0iOiJPUEdfMWVkZDk5NmE2NDdlNDUyNTg3NzUxMTZjMWQ3NWI3ZDAiLCJpZCI6IjNiMzViZmYzYWE0OTgxNDQxNDBlZjI5N2JkMDY5NGNhIiwiZXhwIjoxNzQxMjYzMDk0LCJkYyI6Imd6cXkifQ.JS3QY6ER0P2cQSxAE_OGKSMIWNAMsYUZ3mJTnEpf-Rc`;
      
      const response = await request(url, { headers: aggConfig.headers.default, timeout: searchTimeout });
      const res = JSON.parse(response);
      results = (res.result?.elements || []).map(vod => {
        const dj = vod.duanjuVo || {};
        return {
          vod_id: `\u897f\u996d@${dj.duanjuId || ''}#${dj.source || ''}`,
          vod_name: dj.title || '\u672a\u77e5\u6807\u9898',
          vod_pic: dj.coverImageUrl || '',
          vod_remarks: '\u897f\u996d\u77ed\u5267 | ' + (dj.total ? `${dj.total}\u96c6` : ''),
          vod_content: ''
        };
      });
      break;
    }
    
    case '\u8f6f\u9e2d': {
      const url = `${platRule.host}${platRule.search}/?keyword=${encodeURIComponent(wd)}&page=${page}`;
      const response = await request(url, { headers: aggConfig.headers.default, timeout: searchTimeout });
      const res = JSON.parse(response);
      results = (res.data || []).map(item => {
        const purl = `${item.title}@${item.cover}@${item.author}@${item.type}@${item.desc}@${item.book_id}`;
        return {
          vod_id: `\u8f6f\u9e2d@${encodeURIComponent(purl)}`,
          vod_name: item.title || '',
          vod_pic: item.cover || '',
          vod_remarks: '\u8f6f\u9e2d\u77ed\u5267 | ' + (item.type || ''),
          vod_content: ''
        };
      });
      break;
    }
    
    case '\u4e03\u732b': {
      let signStr = `operation=2playlet_privacy=1search_word=${wd}${aggConfig.keys}`;
      const sign = await md5(signStr);
      const url = `${platRule.host}${platRule.search}?search_word=${encodeURIComponent(wd)}&playlet_privacy=1&operation=2&sign=${sign}`;
      const headers = await getQiMaoHeaders();
      
      const response = await request(url, { method: 'GET', headers, timeout: searchTimeout });
      const res = JSON.parse(response);
      results = (res.data?.list || []).map(item => ({
        vod_id: `\u4e03\u732b@${encodeURIComponent(item.playlet_id)}`,
        vod_name: item.title || '\u672a\u77e5\u6807\u9898',
        vod_pic: item.image_link || '',
        vod_remarks: '\u4e03\u732b\u77ed\u5267 | ' + (item.tags || '') + ' ' + (item.total_episode_num ? `${item.total_episode_num}\u96c6` : ''),
        vod_content: ''
      }));
      break;
    }
    
    case '\u725b\u725b': {
      const postData = {
        condition: { typeId: "S1", value: wd },
        pageNum: page,
        pageSize: searchLimit
      };
      const response = await request(`${platRule.host}${platRule.search}`, {
        method: 'POST',
        headers: niuniu_headers,
        data: postData,
        timeout: searchTimeout
      });
      const res = JSON.parse(response);
      results = (res.data?.records || []).map(item => ({
        vod_id: `\u725b\u725b@${item.id}`,
        vod_name: item.name || '',
        vod_pic: item.cover || '',
        vod_remarks: '\u725b\u725b\u77ed\u5267 | ' + (item.totalEpisode ? `${item.totalEpisode}\u96c6` : ''),
        vod_content: ''
      }));
      break;
    }
    
    case '\u56f4\u89c2': {
      const postData = {
        audience: "",
        page: page,
        pageSize: searchLimit,
        searchWord: wd,
        subject: ""
      };
      const response = await request(`${platRule.host}${platRule.search}`, {
        method: 'POST',
        data: postData,
        timeout: searchTimeout
      });
      const res = JSON.parse(response);
      
      if (res.code === 200 && res.data) {
        results = (res.data || []).map(it => ({
          vod_id: `\u56f4\u89c2@${it.oneId || ''}`,
          vod_name: it.title || '\u672a\u77e5\u6807\u9898',
          vod_pic: it.vertPoster || it.horizonPoster || '',
          vod_remarks: '\u56f4\u89c2\u77ed\u5267 | ' + `\u96c6\u6570:${it.episodeCount || 0}`,
          vod_content: it.description || ''
        }));
      }
      break;
    }
    
    case '\u788e\u7247': {
      try {
        const token = await getSuiPianToken();
        const headers = { ...aggConfig.headers.default, 'Authorization': token };
        const url = `${platRule.host}${platRule.search}?type=5&tagId=&pageNum=${page}&pageSize=${searchLimit}&title=${encodeURIComponent(wd)}`;
        
        const response = await request(url, { headers, timeout: searchTimeout });
        const res = JSON.parse(response);
        
        results = (res.list || []).map(it => ({
          vod_id: `\u788e\u7247@${it.itemId || ''}@${it.videoCode || ''}`,
          vod_name: it.title || '',
          vod_pic: `https://free-api.bighotwind.cc/papaya/papaya-file/files/download/${it.imageKey || ''}/${it.imageName || ''}`,
          vod_remarks: '\u788e\u7247\u5267\u573a | ' + (it.episodesMax ? `${it.episodesMax}\u96c6` : '') + (it.hitShowNum ? ` \u64ad\u653e:${it.hitShowNum}` : ''),
          vod_content: it.content || it.description || ''
        }));
      } catch (e) {
        console.log(`\u3010\u788e\u7247\u641c\u7d22\u3011\u5931\u8d25: ${e.message}`);
      }
      break;
    }
    
    case '\u6cb3\u9a6c': {
      try {
        const hmbody = JSON.stringify({
          "keyword": wd,
          "page": page,
          "size": searchLimit
        });
        
        const response = await request(`${platRule.host}${platRule.search}`, {
          method: 'POST',
          headers: hema_headers,
          data: hemaEncrypt(hmbody),
          timeout: searchTimeout
        });
        
        const res = JSON.parse(response);
        const xmres = res.data;
        
        if (xmres) {
          const dexmres = hemaDecrypt(xmres);
          if (dexmres && dexmres !== '{}') {
            const xmlist = JSON.parse(dexmres).searchVos || [];
            
            results = xmlist.map(video => ({
              vod_id: `\u6cb3\u9a6c@${video.bookId}`,
              vod_name: video.bookName || '',
              vod_pic: (video.coverWap || '') + '@Referer=',
              vod_remarks: `\u6cb3\u9a6c\u77ed\u5267 | \u5171${video.updateNum || 0}\u96c6`,
              vod_content: video.introduction || '',
              extra: {
                bookId: video.bookId,
                chapterId: video.chapterId,
                chapterMin: video.updateNum,
                chapterMax: video.chapterIndex
              }
            }));
          }
        }
      } catch (e) {
        console.log(`\u6cb3\u9a6c\u641c\u7d22\u5931\u8d25: ${e.message}`);
      }
      break;
    }
  }
  
  return JSON.stringify({
    list: results,
    page: page,
    pagecount: page + 1,
    limit: results.length,
    total: results.length * (page + 1)
  });
}

async function search(wd, quick, pg) {
  const videos = [];
  const page = pg || 1;
  
  const platForms = getPlatList();
  
  const searchPromises = platForms.map(async (platform) => {
    const result = await cfs(platform.id, wd, page);
    return JSON.parse(result).list || [];
  });
  
  const searchResults = await Promise.all(searchPromises);
  searchResults.forEach(list => videos.push(...list));
  
  const filteredResults = videos.filter(item => 
    (item.vod_name || '').toLowerCase().includes(wd.toLowerCase())
  );
  
  return JSON.stringify({
    list: filteredResults,
    page: page,
    pagecount: page + 1,
    limit: filteredResults.length,
    total: filteredResults.length * (page + 1)
  });
}

async function action(action, value) {
  if (action === 'shuaPlay') {
    return JSON.stringify({
      action: {
        actionId: '__detail__',
        ids: value,
        keep: true,
      }
    });
  }
}
// ==================== \u6cb3\u9a6c\u8f85\u52a9\u51fd\u6570 ====================
function hemaEncrypt(plaintext) {
  var keyBytes = CryptoJS.enc.Hex.parse("647a6b6a67667978677368796c677a6d");
  var ivBytes = CryptoJS.enc.Hex.parse("6170697570646f776e65646372797074");
  var encrypted = CryptoJS.AES.encrypt(plaintext, keyBytes, {
    iv: ivBytes,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  });
  var ciphertext = encrypted.ciphertext.toString(CryptoJS.enc.Hex);
  return ciphertext.toUpperCase();
}

function hemaDecrypt(word) {
  try {
    var key = CryptoJS.enc.Hex.parse("647a6b6a67667978677368796c677a6d");
    var iv = CryptoJS.enc.Hex.parse("6170697570646f776e65646372797074");
    let encryptedHexStr = CryptoJS.enc.Hex.parse(word);
    let srcs = CryptoJS.enc.Base64.stringify(encryptedHexStr);
    let decrypt = CryptoJS.AES.decrypt(srcs, key, {
      iv: iv,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7,
    });
    let decryptedStr = decrypt.toString(CryptoJS.enc.Utf8);
    return decryptedStr;
  } catch (e) {
    console.log(`\u6cb3\u9a6c\u89e3\u5bc6\u5931\u8d25: ${e.message}`);
    return '{}';
  }
}

// ==================== \u5de5\u5177\u51fd\u6570 ====================
function isSkipPlat(platformItem) {
  return cate_remove.some(word => 
    new RegExp(word, 'i').test(platformItem.name) || new RegExp(word, 'i').test(platformItem.id)
  );
}

function getPlatList() {
  return platformList.filter(item => !isSkipPlat(item));
}

function getRnd(min, max, hexNum, isUpper) {
  let r = Math.floor(Math.random() * (max - min + 1)) + min;
  if (hexNum) {
    r = isUpper ? r.toString(hexNum).toUpperCase() : r.toString(hexNum);
  }
  return r;
}

async function md5(str) {
  return CryptoJS.MD5(str).toString(CryptoJS.enc.Hex).toLowerCase();
}

function base64Encode(text) {
  return CryptoJS.enc.Base64.stringify(CryptoJS.enc.Utf8.parse(text));
}

function base64Decode(text) {
  return CryptoJS.enc.Utf8.stringify(CryptoJS.enc.Base64.parse(text));
}

function encHex(txt) {
  const key = CryptoJS.enc.Utf8.parse("p0sfjw@k&qmewu#w");
  const encrypted = CryptoJS.AES.encrypt(CryptoJS.enc.Utf8.parse(txt), key, {
    mode: CryptoJS.mode.ECB,
    padding: CryptoJS.pad.Pkcs7
  });
  return encrypted.ciphertext.toString(CryptoJS.enc.Hex);
}

function guid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    let r = Math.random() * 16 | 0;
    let v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

async function getAndSign() {
  const sessionId = Math.floor(Date.now()).toString();
  let data = {
    "static_score": "0.8",
    "uuid": "00000000-7fc7-08dc-0000-000000000000",
    "device-id": "20250220125449b9b8cac84c2dd3d035c9052a2572f7dd0122edde3cc42a70",
    "mac": "",
    "sourceuid": "aa7de295aad621a6",
    "refresh-type": "0",
    "model": "22021211RC",
    "wlb-imei": "",
    "client-id": "aa7de295aad621a6",
    "brand": "Redmi",
    "oaid": "",
    "oaid-no-cache": "",
    "sys-ver": "12",
    "trusted-id": "",
    "phone-level": "H",
    "imei": "",
    "wlb-uid": "aa7de295aad621a6",
    "session-id": sessionId
  };
  
  const jsonStr = JSON.stringify(data);
  const base64Str = base64Encode(unescape(encodeURIComponent(jsonStr)));
  let qmParams = '';
  for (const c of base64Str) qmParams += aggConfig.charMap[c] || c;
  const paramsStr = `AUTHORIZATION=app-version=10001application-id=com.duoduo.readchannel=unknownis-white=net-env=5platform=androidqm-params=${qmParams}reg=${aggConfig.keys}`;
  const sign = await md5(paramsStr);
  return { qmParams, sign };
}

async function getHeaderX() {
  const { qmParams, sign } = await getAndSign();
  return {
    'net-env': '5',
    'reg': '',
    'channel': 'unknown',
    'is-white': '',
    'platform': 'android',
    'application-id': 'com.duoduo.read',
    'authorization': '',
    'app-version': '10001',
    'user-agent': 'webviewversion/0',
    'qm-params': qmParams,
    'sign': sign
  };
}

async function getSuiPianToken() {
  let openId = (await md5(guid())).substring(0,16);
  let api = "https://free-api.bighotwind.cc/papaya/papaya-api/oauth2/uuid";
  let key = encHex(Date.now().toString());
  
  const tokenResponse = await request(api, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', "key": key },
    data: { "openId": openId }
  });
  
  const tokenRes = JSON.parse(tokenResponse);
  return tokenRes.data?.token;
}

async function getQiMaoHeaders() {
  const { qmParams, sign } = await getAndSign();
  return {
    'net-env': '5',
    'reg': '',
    'channel': 'unknown',
    'is-white': '',
    'platform': 'android',
    'application-id': 'com.duoduo.read',
    'authorization': '',
    'app-version': '10001',
    'user-agent': 'webviewversion/0',
    'qm-params': qmParams,
    'sign': sign,
    ...aggConfig.headers.default
  };
}

// ==================== \u52a0\u5bc6\u5de5\u5177\u51fd\u6570 ====================
function aesEncryptECB(decrypteddata, key) {
  let keyCrypto = CryptoJS.enc.Utf8.parse(key);
  let dataCrypto = CryptoJS.enc.Utf8.parse(decrypteddata);
  let encrypted = CryptoJS.AES.encrypt(dataCrypto, keyCrypto, {
    mode: CryptoJS.mode.ECB,
    padding: CryptoJS.pad.Pkcs7
  });
  return encrypted.toString();
}


function aesDecryptECB(encryptedData, key) {
  try {
    let keyCrypto = CryptoJS.enc.Utf8.parse(key);
    let encryptedCrypto = CryptoJS.enc.Base64.parse(encryptedData);
    let decrypted = CryptoJS.AES.decrypt({
      ciphertext: encryptedCrypto
    }, keyCrypto, {
      mode: CryptoJS.mode.ECB,
      padding: CryptoJS.pad.Pkcs7
    });
    return decrypted.toString(CryptoJS.enc.Utf8);
  } catch (e) {
    console.log(`ECB\u89e3\u5bc6\u5931\u8d25: ${e.message}`);
    return '';
  }
}

function hmacSHA256(message, secretKey) {
  let hash = CryptoJS.HmacSHA256(message, secretKey);
  return hash.toString(CryptoJS.enc.Hex);
}

async function niuniuPost(url1, data1, index) {
  let t10 = String(Math.floor(new Date().getTime() / 1000));
  let X_Nonce = "X9UknYKtLa3DmtjC";
  let body1 = data1.replace(/&lock_free=\d+/, "&lock_free=1")
                   .replace(/&timestamp=\d+/, "&timestamp="+t10)
                   .replace(/&count=\d+/, "&count=1")
                   .replace(/&index=\d+/, "&index="+index)
                   .replace(/&lock_ad=\d+/, "&lock_ad=1")
                   .replace(/&lock_index=\d+/, "&lock_index="+index);
  
  let body2 = aesEncryptECB(body1, 'ce49b18dd4e0a4d8');
  let body3 = t10 + X_Nonce + body1;
  let signature = hmacSHA256(body3, 'aceaa47f96b4875d446b2e1d97e03bbb');
  
  let html1 = await request(url1, {
    headers: {
      'X-Salt': 'FD8188A8D5',
      'X-Nonce': X_Nonce,
      'X-Timestamp': t10,
      'X-Access-Token': niuniu_access_token,
      'X-Signature': signature,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    data: body2,
    method: "POST"
  });
  
  html1 = aesDecryptECB(html1, 'ce49b18dd4e0a4d8');
  return JSON.parse(html1);
}

// ==================== \u7edf\u4e00\u8bf7\u6c42\u51fd\u6570 ====================

async function request(url, options = {}) {
  try {
    console.log(`\u3010${siteName}\u3011${options.method || 'GET'} ${url.split('?')[0]}`);
    
    let requestConfig = {
      method: options.method || 'GET',
      headers: { ...aggConfig.headers.default, ...options.headers },
      timeout: options.timeout || 5000
    };
    
    if (options.data) {
      if (typeof options.data === 'string') {
        requestConfig.body = options.data;
      } else {
        let contentType = requestConfig.headers['Content-Type'] || '';
        
        if (contentType.includes('json')) {
          requestConfig.body = JSON.stringify(options.data);
        } else {
          const parts = [];
          for (let key in options.data) {
            let value = options.data[key];
            if (typeof value === 'object' && value !== null) {
              value = JSON.stringify(value);
            }
            parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(value));
          }
          requestConfig.body = parts.join('&');
        }
      }
    }
    
    const res = await req(url, requestConfig);
    return res.content || '';
  } catch (e) {
    console.log(`\u3010${siteName}\u3011\u8bf7\u6c42\u5931\u8d25: ${e.message}`);
    return '';
  }
}

export function __jsEvalReturn() {
  return {
    init: init,
    home: home,
    homeVod: homeVod,
    category: category,
    detail: detail,
    play: play,
    search: search
  };
}