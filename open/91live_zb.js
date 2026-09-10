/*
@header({
  searchable: 1,
  filterable: 1,
  quickSearch: 1,
  title: '91\u7535\u89c6[\u76f4]',
  lang: 'cat',
})
*/

import { Crypto as CryptoJS } from 'assets://js/lib/cat.js';

let host = 'http://sj.91kds.cn';
let siteName = '91\u7535\u89c6', siteKey = '', siteType = 0;

let UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (Chrome/126.0.0.0 Safari/537.36)";

const headers = {
    'User-Agent': UA,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
};

function init(cfg) {
    siteName = cfg.skey?.split('_')[1] || cfg.skey || '91\u7535\u89c6';
    siteKey = cfg.skey;
    siteType = cfg.stype;
    
    if (cfg && typeof cfg === 'string') {
        host = cfg;
    } else if (cfg && typeof cfg === 'object') {
        let ext = cfg.ext;
        if (ext && typeof ext === 'object' && Object.keys(ext).length) {
            host = ext.host || ext.hosturl || ext.url || ext.site;
        }
    }
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
        return response?.content || response?.data || response;
    } catch {
        return null;
    }
}

async function home(filter) {
    const classes = [
        { type_id: "\u592e\u89c6", type_name: "\u592e\u89c6" }, { type_id: "\u536b\u89c6", type_name: "\u536b\u89c6" },
        { type_id: "\u9ad8\u6e05", type_name: "\u9ad8\u6e05" }, { type_id: "4K", type_name: "4K" },
        { type_id: "\u5f71\u89c6", type_name: "\u5f71\u89c6" }, { type_id: "\u4f53\u80b2", type_name: "\u4f53\u80b2" },
        { type_id: "\u52a8\u6f2b", type_name: "\u52a8\u6f2b" }, { type_id: "\u8d22\u7ecf", type_name: "\u8d22\u7ecf" },
        { type_id: "\u7efc\u827a", type_name: "\u7efc\u827a" }, { type_id: "\u6559\u80b2", type_name: "\u6559\u80b2" },
        { type_id: "\u65b0\u95fb", type_name: "\u65b0\u95fb" }, { type_id: "\u7eaa\u5f55", type_name: "\u7eaa\u5f55" },
        { type_id: "\u56fd\u9645", type_name: "\u56fd\u9645" }, { type_id: "\u7f51\u7edc", type_name: "\u7f51\u7edc" },
        { type_id: "\u8d2d\u7269", type_name: "\u8d2d\u7269" }, { type_id: "\u864e\u7259", type_name: "\u864e\u7259" }
    ];
    
    const filters = {};
    classes.forEach(cls => { filters[cls.type_id] = []; });
    
    return JSON.stringify({ class: classes, filters: filters });
}

async function homeVod() {
    return await category('\u6e56\u5317', 1, null, {});
}

async function category(tid, pg, filter, extend) {
    try {
        const url = `${host}/api/get_channel.php?id=${tid}`;
        const html = await request(url);
        
        if (!html || !html.includes('ename')) {
            return JSON.stringify({ list: [], page: 1, pagecount: 1, limit: 20, total: 0 });
        }
        
        const list = safeJSONParse(html);
        const nwtime = Math.floor(Date.now() / 1000);
        
        const videos = list.map(item => {
            const enamee = item.ename;
            const srcKey = enamee + "com.jiaoxiang.fangnaleahkajfkahlajjaflfakhfakfbuyaozaigaolefuquqikangbuzhu2.3.4fu:ck:92:92:ff" + nwtime + "20240918";
            const sign = CryptoJS.MD5(srcKey).toString();
            const detailUrl = `http://sjapi1.91kds.cn/api/get_source.php?ename=${enamee}&app=com.jiaoxiang.fangnale&version=2.3.4&mac=fu:ck:92:92:ff&nwtime=${nwtime}&sign=${sign}&ev=20240918`;
            
            return {
                vod_id: detailUrl + '@' + item.name,
                vod_name: item.name,
                vod_pic: item.icon,
                vod_remarks: '\u76f4\u64ad'
            };
        });
        
        return JSON.stringify({ list: videos, page: 1, pagecount: 1, limit: 20, total: videos.length });
    } catch (e) {
        return JSON.stringify({ list: [], page: 1, pagecount: 1, limit: 20, total: 0 });
    }
}

async function detail(id) {
    try {
        const [purl, vod_name] = id.split('@');
        const html = await request(purl);
        const data = safeJSONParse(html);
        
        const vod = {
            vod_id: purl,
            vod_name: vod_name || data.name || data.title || "\u76f4\u64ad\u9891\u9053",
            vod_pic: data.icon || "",
            vod_content: data.desc || "\u6682\u65e0\u7b80\u4ecb",
            vod_remarks: "\u76f4\u64ad"
        };
        
        let list = data.liveSource || [];
        let names = data.liveSourceName || [];
        let playFrom = [];
        let playUrl = [];
        let seen = new Set();
        let lineCounter = 1;
        
        list.forEach((item, j) => {
            let rawInput = item;
            let inputUrl = rawInput.replace(/^kdsvod:\/\//, '');
            let urlName = names[j] || '\u7ebf\u8def' + lineCounter;
            
            if (inputUrl.includes('pwd=jsdecode') && inputUrl.includes('id=')) {
                let parts = inputUrl.split('?');
                let baseUrl = parts[0];
                let queryStr = parts[1] || '';
                let queryObj = {};
                queryStr.split('&').forEach(kv => {
                    let t = kv.split('=');
                    if (t[0]) queryObj[t[0]] = decodeURIComponent(t[1] || '');
                });
                
                let id = queryObj['id'];
                let bt = queryObj['bt'] || null;
                let coreKey = (bt || '') + '_' + id;
                
                if (seen.has(coreKey)) return;
                seen.add(coreKey);
                
                let params = {
                    app: 'com.jiaoxiang.fangnale',
                    version: '2.3.4',
                    mac: 'fu:ck:92:92:ff',
                    utk: '',
                    nwtime: Math.floor(Date.now() / 1000),
                    ev: '20250113'
                };
                
                let appendStr = 'ahkajfkahlajjaflfakhfakfbuyaozaigaolefuquqikangbuzhu';
                let signStr = id;
                Object.keys(params).forEach(key => {
                    if (key === 'tmk') return;
                    if (key === 'app') signStr += params[key] + appendStr;
                    else signStr += params[key];
                });
                
                params.sign = CryptoJS.MD5(signStr).toString();
                let finalQuery = [];
                if (bt !== null) finalQuery.push('bt=' + bt);
                finalQuery.push('id=' + id);
                Object.keys(params).forEach(k => {
                    finalQuery.push(k + '=' + encodeURIComponent(params[k]));
                });
                
                let finalUrl = baseUrl + '?' + finalQuery.join('&');
                let lineName = '\u7ebf\u8def' + lineCounter;
                playFrom.push(lineName);
                playUrl.push(urlName + '$' + finalUrl);
                lineCounter++;
            } else {
                let videoUrl;
                if (inputUrl.startsWith('htmlplay://')) {
                    videoUrl = inputUrl.replace('htmlplay://', '').split('#')[0];
                } else {
                    videoUrl = inputUrl;
                }
                
                let urlKey = videoUrl.split('?')[0];
                if (seen.has(urlKey)) return;
                seen.add(urlKey);
                
                let referer = '';
                if (inputUrl.includes('@@referer=')) {
                    let tmp = inputUrl.split('@@referer=');
                    videoUrl = tmp[0];
                    referer = tmp[1] || '';
                }
                
                let lineName = '\u7ebf\u8def' + lineCounter;
                
                if (referer) {
                    let playObj = JSON.stringify({ url: videoUrl, header: { Referer: referer } });
                    playFrom.push(lineName);
                    playUrl.push(urlName + '$' + playObj);
                } else {
                    playFrom.push(lineName);
                    playUrl.push(urlName + '$' + videoUrl);
                }
                lineCounter++;
            }
        });
        
        vod.vod_play_from = playFrom.join('$$$');
        vod.vod_play_url = playUrl.join('$$$');
        
        return JSON.stringify({ list: [vod] });
    } catch (e) {
        return JSON.stringify({ list: [] });
    }
}

async function play(flag, id, flags) {
    return JSON.stringify({ parse: 0, url: id, header: {} });
}

async function search(wd, quick, pg = "1") {
    try {
        const nwtime = Math.floor(Date.now() / 1000);
        const srcKey = "4954af3c86d8bc0b766afee71503d860" + nwtime + "f8dd806a73202456eb6e782c1c4aecfc";
        const sign = CryptoJS.MD5(srcKey).toString();
        
        const searchUrl = `${host}/api/get_search.php?id=${encodeURIComponent(wd)}`;
        const html = await request(searchUrl);
        
        if (!html || !html.includes('ename')) {
            return JSON.stringify({ list: [], page: parseInt(pg), pagecount: 0, limit: 20, total: 0 });
        }
        
        const list = safeJSONParse(html);
        const videos = list.map(item => ({
            vod_id: `${host}/api/get_source.php?ename=${item.ename}@${item.name}`,
            vod_name: item.name,
            vod_pic: item.icon,
            vod_remarks: item.path || ''
        }));
        
        return JSON.stringify({ list: videos, page: parseInt(pg), pagecount: 1, limit: 20, total: videos.length });
    } catch (e) {
        return JSON.stringify({ list: [], page: parseInt(pg), pagecount: 0, limit: 20, total: 0 });
    }
}

export function __jsEvalReturn() {
    return { init, home, homeVod, category, detail, play, search };
}