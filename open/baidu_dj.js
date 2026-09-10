/*
@header({
  searchable: 1,
  filterable: 0,
  quickSearch: 1,
  title: '\u767e\u5ea6\u77ed\u5267',
  lang: 'cat'
})
*/
import { Crypto as CryptoJS } from 'assets://js/lib/cat.js';

let siteName = '\u767e\u5ea6\u77ed\u5267', siteKey = '', siteType = 0;

let UA = "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36";
let clarity_order = { '\u84dd\u5149': 1, '\u8d85\u6e05': 2, '\u6807\u6e05': 3 };

let rule = {
    host: 'https://mbd.baidu.com',
    detailHost: 'https://sv.baidu.com',
    listUrl: '/feedapi/v1/videoserver/playlets/list?service=bdbox',
    searchUrl: '/feedapi/v1/videoserver/playlets/search?service=bdbox',
    detailUrl: '/haokan/ui-video/playlet/rec/detail?log=vhk&tn=1020970b&ctn=1008350n&blur=1',
    playUrl: '/appui/api?cmd=video/relate&log=vhk&tn=1020970b&ctn=1008350n&blur=1',
};

const headers = {
    'User-Agent': UA,
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
};

function init(cfg) {
    siteName = cfg.skey?.split('_')[1] || cfg.skey || '\u767e\u5ea6\u77ed\u5267';
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

function safeJSONParse(str, defaultValue = {}) {
    if (!str || typeof str === 'object') return str || defaultValue;
    try {
        return JSON.parse(str);
    } catch {
        return defaultValue;
    }
}

async function request(url, options = {}) {
    const reqHeaders = { ...headers, ...options.headers };
    let postType = reqHeaders['Content-Type']?.includes('json') ? 'json' :
        reqHeaders['Content-Type']?.includes('form') ? 'form' : '';

    try {
        const response = await req(url, {
            method: options.method || 'GET',
            headers: reqHeaders,
            data: options.data,
            postType: postType,
            timeout: options.timeout || 15000
        });
        const content = response?.content || response?.data || response;
        return typeof content === 'object' ? content : safeJSONParse(content);
    } catch {
        return null;
    }
}

function home(filter) {
    let he = ["\u5168\u90e8", "\u65b0\u5267", "\u9650\u65f6\u514d\u8d39", "\u7cbe\u9009", "\u72ec\u64ad"];
    let ticailist = [
        "\u795e\u533b", "\u8fde\u7eed\u5267", "\u90fd\u5e02", "\u73b0\u4ee3\u8a00\u60c5", "\u5f02\u80fd", "\u9006\u88ad", "\u751c\u5ba0", "\u603b\u88c1", "\u840c\u5b9d", "\u6218\u795e", "\u5bab\u6597\u5b85\u6597", "\u795e\u8c6a",
        "\u8650\u604b", "\u95ea\u5a5a", "\u7384\u5e7b", "\u7a7f\u8d8a\u91cd\u751f", "\u5e74\u4ee3", "\u5bb6\u5ead\u4f26\u7406", "\u53e4\u4ee3\u8a00\u60c5", "\u6b66\u4fa0\u6b66\u6253", "\u8d58\u5a7f", "\u5355\u5143\u5267", "\u9752\u6625\u6821\u56ed",
        "\u5386\u53f2\u67b6\u7a7a", "\u738b\u5983", "\u9274\u5b9d", "\u79d1\u5e7b", "\u519b\u65c5\u6218\u4e89", "\u79cd\u7530"
    ];

    let classes = he.map(name => ({ type_id: name, type_name: name }));
    classes = classes.concat(ticailist.map(name => ({
        type_id: name === "\u5168\u90e8" ? "\u5168\u90e8\u9898\u6750" : name,
        type_name: name
    })));
    return JSON.stringify({ class: classes, filters: {} });
}

async function homeVod() {
    const categoryResult = await category('\u65b0\u5267', 1, {}, {});
    const list = safeJSONParse(categoryResult).list || [];
    return JSON.stringify({ list: list.slice(0, 12) });
}

async function category(tid, pg, filter, extend) {
    pg = pg <= 0 ? 1 : pg;
    let sub = ["\u65b0\u5267", "\u9650\u65f6\u514d\u8d39", "\u7cbe\u9009", "\u72ec\u64ad"].includes(tid) ? tid : "\u65b0\u5267";
    let tcsub = (tid === "\u5168\u90e8" || tid === "\u5168\u90e8\u9898\u6750") ? "" : tid;
    let t = Math.floor(Date.now() / 1000);
    let version = await md5(t + "v2");

    let postData = {
        'data': JSON.stringify({
            "data": {
                "extRequest": { "flow_tabid": "13" },
                "from": "feed",
                "page": "channel_video_landing",
                "pd": "feed",
                "refreshIndex": pg,
                "cursor": "",
                "theme": "",
                "timestamp": t,
                "version": version,
                "themes": [
                    { "kind": "\u7efc\u5408", "names": [sub] },
                    { "kind": "\u9898\u6750", "names": [tcsub] }
                ]
            }
        })
    };

    const res = await request(`${rule.host}${rule.listUrl}`, { method: 'POST', data: postData });
    let videos = (res?.data?.items || []).map(it => ({
        vod_id: it.collId || '',
        vod_name: it.title || '\u672a\u77e5\u6807\u9898',
        vod_pic: it.img || '',
        vod_remarks: it.updateStatus || '',
        vod_content: it.description || ''
    }));

    return JSON.stringify({
        page: pg,
        pagecount: pg + 1,
        limit: videos.length,
        total: videos.length * (pg + 1),
        list: videos
    });
}

async function detail(id) {
    const res = await request(`${rule.detailHost}${rule.detailUrl}`, {
        method: 'POST',
        data: { playlet_id: id, vid: "undefined" }
    });
    const dthtml = res?.data;
    const vids = dthtml?.vid_list || [];
    if (!vids.length) return JSON.stringify({ list: [] });

    const playArr = vids.map((vid, index) => `\u7b2c${index + 1}\u96c6$${vid}`);
    const vod = {
        vod_id: id,
        vod_name: dthtml.playlet_title || '\u672a\u77e5\u5267\u540d',
        vod_pic: dthtml.playlet_poster || '',
        vod_content: dthtml.description || '',
        vod_remarks: `\u5171${vids.length}\u96c6 \u70ed\u5ea6\u503c:${dthtml.hot_value || 0}`,
        vod_director: dthtml.tag_text || '',
        vod_year: dthtml.create_time || '',
        vod_play_from: "\u767e\u5ea6\u77ed\u5267",
        vod_play_url: playArr.join('#')
    };

    return JSON.stringify({ list: [vod] });
}

async function play(flag, id, flags) {
    let res = await request(`${rule.detailHost}${rule.playUrl}`, {
        method: 'POST',
        data: { method: "post", vid: id }
    });
    const video = res?.["video/relate"]?.data?.cur_video;
    if (!video?.clarityUrl) return JSON.stringify({ parse: 0, url: '', msg: '\u83b7\u53d6\u64ad\u653e\u94fe\u63a5\u5931\u8d25' });

    const urls = video.clarityUrl.filter(item => item?.url).map(item => ({
        title: item.title,
        url: item.url,
        order: clarity_order[item.title] || 999
    })).sort((a, b) => a.order - b.order);

    if (!urls.length) return JSON.stringify({ parse: 0, url: '', msg: '\u6682\u65e0\u53ef\u7528\u64ad\u653e\u5730\u5740' });

    const flat = urls.flatMap(item => [item.title, item.url]);
    return JSON.stringify({
        parse: 0,
        url: flat,
        header: { 'User-Agent': UA, 'Referer': rule.host }
    });
}

async function search(wd, quick, pg) {
    pg = pg <= 0 ? 1 : pg;
    let postData = {
        'data': JSON.stringify({
            "query": wd,
            "page": pg,
            "attribute": ["title"],
            "fe_page_type": "search",
            "extra": {
                "tab_id": "216",
                "flow_tabid": "13",
                "shortplay_source": "feed",
                "from": "feed",
                "tab_type": "\u641c\u7d22",
                "sub_template": "playlet_search_result"
            }
        })
    };

    const res = await request(`${rule.host}${rule.searchUrl}`, {
        method: 'POST',
        data: postData
    });
    let videos = (res?.data?.itemList || []).map(it => ({
        vod_id: it.nid?.split("_")[1] || '',
        vod_name: it.title || '\u672a\u77e5\u6807\u9898',
        vod_pic: it.img || '',
        vod_remarks: (it.collNum || '0') + '\u96c6',
        vod_content: it.description || ''
    }));

    return JSON.stringify({
        page: pg,
        pagecount: pg + 1,
        limit: videos.length,
        total: videos.length * (pg + 1),
        list: videos
    });
}

async function md5(str) {
    return CryptoJS.MD5(str).toString(CryptoJS.enc.Hex).toLowerCase();
}

export function __jsEvalReturn() {
    return { init, home, homeVod, category, detail, play, search };
}