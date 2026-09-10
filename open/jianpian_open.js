/*
@header({
  searchable: 1,
  filterable: 1,
  quickSearch: 0,
  title: '\u8350\u7247',
  lang: 'cat'
})
*/

let siteName = '\u8350\u7247', siteKey = '', siteType = 0;
let host = 'https://api.ztcgi.com';
let imghost = '';
let maxPages = 5;
let config = {};

let title_remove = ['\u540d\u79f0\u6392\u9664', '\u5e7f\u544a', '\u7834\u89e3', '\u7fa4'];
let line_remove = ['\u7ebf\u8def\u6392\u9664', '\u5e7f\u544a', '666', 'mymv'];
let line_order = ['\u7ebf\u8def\u6392\u5e8f', '\u84dd\u5149', 'ft', '\u5b98', 'ace', '1080p', 'dytt'];
let cate_remove = ['\u5206\u7c7b\u6392\u9664', '\u63a8\u8350', '\u9996\u9875'];

let rule = {
    homeCategory: '/api/v2/settings/homeCategory',
    resourceDomain: '/api/v2/settings/resourceDomainConfig',
    slideList: '/api/slide/list',
    dyTag: '/api/dyTag/tpl2_data',
    crumbList: '/api/crumb/list',
    detail: '/api/video/detailv2',
    search: '/api/v2/search/videoV2'
};

const headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
};

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

async function init(cfg) {
    siteName = cfg.skey?.split('_')[1] || cfg.skey || '\u8350\u7247';
    siteKey = cfg.skey;
    siteType = cfg.stype;
    
    let ext = cfg.ext !== undefined ? cfg.ext : cfg;
    
    if (typeof ext === 'string' && ext.includes('$')) {
        const [url, order] = ext.split('$');
        const response = await req(url, { headers, timeout: 10000 });
        if (response && response.content) {
            config = safeJSONParse(response.content)[order] || {};
            host = config.host || config.hosturl || config.url || config.site;
        }
    } else if (ext && typeof ext === 'object') {
        config = ext;
        host = config.host || config.hosturl || config.url || config.site;
    }
    
    if (!host) {
        host = 'https://api.ztcgi.com';
    }
    
    
    if (config.title_remove !== undefined) title_remove = Array.isArray(config.title_remove) ? config.title_remove : title_remove;
    if (config.line_remove !== undefined) line_remove = Array.isArray(config.line_remove) ? config.line_remove : line_remove;
    if (config.line_order !== undefined) line_order = Array.isArray(config.line_order) ? config.line_order : line_order;
    if (config.cate_remove !== undefined) cate_remove = Array.isArray(config.cate_remove) ? config.cate_remove : cate_remove;
    
    try {
        let res = await req(`${host}${rule.resourceDomain}`, { headers, timeout: 10000 });
        if (res && res.content) {
            let configData = safeJSONParse(res.content);
            if (configData.code === 1 && configData.data && configData.data.imgDomain) {
                const domainList = configData.data.imgDomain.split(',');
                imghost = `https://${domainList[Math.floor(Math.random() * domainList.length)].trim()}`;
            }
        }
    } catch (e) {
        imghost = 'https://img.jgsfnl.com';
    }
}

async function home(filter) {
    let html = await request(`${host}${rule.homeCategory}`);
    if (!html) {
        return JSON.stringify({ class: [], filters: {} });
    }
    
    let parsed = safeJSONParse(html);
    let res = parsed.data;
    
    if (!res || !Array.isArray(res)) {
        return JSON.stringify({ class: [], filters: {} });
    }
    
    let classes = [];
    res.forEach(item => {
        if (item && item.id && item.name) {
            classes.push({ type_id: item.id.toString(), type_name: item.name });
        }
    });
    
    const commonFilter = [{
        "key": "cateId", "name": "\u5206\u7c7b",
        "value": [{"v": "", "n": "\u5168\u90e8"}, {"v": "1", "n": "\u5267\u60c5"}, {"v": "2", "n": "\u7231\u60c5"}, {"v": "3", "n": "\u52a8\u753b"}, {"v": "4", "n": "\u559c\u5267"}, {"v": "5", "n": "\u6218\u4e89"}, {"v": "6", "n": "\u6b4c\u821e"}, {"v": "7", "n": "\u53e4\u88c5"}, {"v": "8", "n": "\u5947\u5e7b"}, {"v": "9", "n": "\u5192\u9669"}, {"v": "10", "n": "\u52a8\u4f5c"}, {"v": "11", "n": "\u79d1\u5e7b"}, {"v": "12", "n": "\u60ac\u7591"}, {"v": "13", "n": "\u72af\u7f6a"}, {"v": "14", "n": "\u5bb6\u5ead"}, {"v": "15", "n": "\u4f20\u8bb0"}, {"v": "16", "n": "\u8fd0\u52a8"}, {"v": "18", "n": "\u60ca\u609a"}, {"v": "20", "n": "\u77ed\u7247"}, {"v": "21", "n": "\u5386\u53f2"}, {"v": "22", "n": "\u97f3\u4e50"}, {"v": "23", "n": "\u897f\u90e8"}, {"v": "24", "n": "\u6b66\u4fa0"}, {"v": "25", "n": "\u6050\u6016"}]
    }, {
        "key": "area", "name": "\u5730\u533a",
        "value": [{"v": "", "n": "\u5168\u90e8"}, {"v": "1", "n": "\u56fd\u4ea7"}, {"v": "3", "n": "\u4e2d\u56fd\u9999\u6e2f"}, {"v": "6", "n": "\u4e2d\u56fd\u53f0\u6e7e"}, {"v": "5", "n": "\u7f8e\u56fd"}, {"v": "18", "n": "\u97e9\u56fd"}, {"v": "2", "n": "\u65e5\u672c"}]
    }, {
        "key": "year", "name": "\u5e74\u4ee3",
        "value": [{"v": "", "n": "\u5168\u90e8"}, {"v": "162", "n": "2026"}, {"v": "107", "n": "2025"}, {"v": "119", "n": "2024"}, {"v": "153", "n": "2023"}, {"v": "101", "n": "2022"}, {"v": "118", "n": "2021"}, {"v": "16", "n": "2020"}, {"v": "7", "n": "2019"}, {"v": "2", "n": "2018"}, {"v": "3", "n": "2017"}, {"v": "22", "n": "2016"}, {"v": "2015", "n": "2015\u4ee5\u524d"}]
    }, {
        "key": "sort", "name": "\u6392\u5e8f",
        "value": [{"v": "update", "n": "\u6700\u65b0"}, {"v": "hot", "n": "\u6700\u70ed"}, {"v": "rating", "n": "\u8bc4\u5206"}]
    }];

    let filterObj = {};
    classes.forEach(item => {
        if (item.type_id !== '88' && item.type_id !== '99') {
            filterObj[item.type_id] = commonFilter;
        }
    });
    
    let i = 0;
    while (i < classes.length) {
        const isBad = cate_remove.some(word => new RegExp(word, 'i').test(classes[i].type_name));
        if (isBad) {
            classes.splice(i, 1);
        } else {
            i++;
        }
    }
    
    return JSON.stringify({ class: classes, filters: filterObj });
}

async function homeVod() {
    let html = await request(`${host}${rule.slideList}?pos_id=88`);
    if (!html) {
        return JSON.stringify({ list: [] });
    }
    
    let parsed = safeJSONParse(html);
    let res = parsed.data;
    
    if (!res || !Array.isArray(res)) {
        return JSON.stringify({ list: [] });
    }
    
    let videos = [];
    res.forEach(item => {
        if (item && item.jump_id) {
            videos.push({
                vod_id: item.jump_id,
                vod_name: item.title || '\u672a\u77e5\u6807\u9898',
                vod_pic: imghost ? `${imghost}${item.thumbnail || ''}` : (item.thumbnail || ''),
                vod_remarks: "",
            });
        }
    });

    let filteredVideos = [];
    videos.forEach(item => {
        const title = item.vod_name;
        const isBadTitle = title_remove.some(word => new RegExp(word, 'i').test(title));
        if (!isBadTitle) {
            filteredVideos.push(item);
        }
    });

    return JSON.stringify({ list: filteredVideos });
}

async function DyTag(id, pg) {
    let url = `${host}${rule.dyTag}?id=${id}&page=${pg}`;
    let html = await request(url);
    if (!html) return [];
    
    let parsed = safeJSONParse(html);
    let res = parsed.data;
    
    if (!res || !Array.isArray(res)) return [];
    
    let videos = [];
    res.forEach(item => {
        if (item) {
            videos.push({
                vod_id: item.id,
                vod_name: item.title || '\u672a\u77e5\u6807\u9898',
                vod_pic: imghost ? `${imghost}${item.path || ''}` : (item.path || ''),
                vod_remarks: item.mask || '',
            });
        }
    });
    return videos;
}

async function category(tid, pg, filter, extend) {
    if (pg <= 0) pg = 1;
    let videos = [];
    
    if (tid === '99' || tid === 99) {
        videos = await DyTag(70, pg);
    } else {
        let extendParams = extend || {};
        let url = `${host}${rule.crumbList}?fcate_pid=${tid}&category_id=&area=${extendParams.area || ''}&year=${extendParams.year || ''}&type=${extendParams.cateId || ''}&sort=${extendParams.sort || ''}&page=${pg}`;
        
        let html = await request(url);
        if (html) {
            let parsed = safeJSONParse(html);
            let res = parsed.data;
            if (res && Array.isArray(res)) {
                res.forEach(item => {
                    if (item) {
                        videos.push({
                            vod_id: item.id,
                            vod_name: item.title || '\u672a\u77e5\u6807\u9898',
                            vod_pic: imghost ? `${imghost}${item.path || ''}` : (item.path || ''),
                            vod_remarks: item.mask || '',
                        });
                    }
                });
            }
        }
    }
    
    let filteredVideos = [];
    videos.forEach(item => {
        if (!item.vod_name) return;
        const title = item.vod_name;
        const isBadTitle = title_remove.some(word => new RegExp(word, 'i').test(title));
        if (!isBadTitle) {
            filteredVideos.push(item);
        }
    });

    return JSON.stringify({
        page: parseInt(pg),
        pagecount: 99999,
        limit: filteredVideos.length,
        total: 99999,
        list: filteredVideos
    });
}

async function detail(id) {
    let html = await request(`${host}${rule.detail}?id=${id}`);
    if (!html) {
        return JSON.stringify({ list: [] });
    }
    
    let parsed = safeJSONParse(html);
    let res = parsed.data;
    if (!res) {
        return JSON.stringify({ list: [] });
    }
    
    let playForm = [];
    let playUrls = [];
    
    if (res.source_list_source && Array.isArray(res.source_list_source)) {
        res.source_list_source.forEach(item => {
            if (!item) return;
            const form = item.name || '\u672a\u77e5\u7ebf\u8def';
            let finalForm = form;
            
            if (item.source_list && item.source_list.length > 0 && item.source_list[0] && item.source_list[0].url) {
                let domain = extractDomain(item.source_list[0].url);
                if (domain.length > 8) domain = domain.substring(0, 8);
                finalForm = `${form}(${domain})`;
            }
            
            const isBadLine = line_remove.some(pattern => finalForm.toLowerCase().includes(pattern.toLowerCase()));
            
            if (!isBadLine) {
                playForm.push(finalForm);
                let urls = [];
                if (item.source_list && Array.isArray(item.source_list)) {
                    item.source_list.forEach(source => {
                        if (source && source.source_name && source.url) {
                            urls.push(`${source.source_name}$${source.url}`);
                        }
                    });
                }
                playUrls.push(urls.join('#'));
            }
        });
    }
    
    let combined = [];
    playForm.forEach((form, i) => {
        if (playUrls[i]) {
            combined.push({ form, url: playUrls[i] });
        }
    });
    
    combined.sort((a, b) => {
        const getPri = name => {
            const idx = line_order.findIndex(k => name.toLowerCase().includes(k.toLowerCase()));
            return idx === -1 ? 999 : idx;
        };
        return getPri(a.form) - getPri(b.form);
    });

    let sortedPlayForm = [];
    let sortedPlayUrls = [];
    combined.forEach(item => {
        sortedPlayForm.push(item.form);
        sortedPlayUrls.push(item.url);
    });
    
    let play_from = [];
    sortedPlayForm.forEach(item => {
        play_from.push(item.replace(/常规线路/g, '\u8fb9\u4e0b\u8fb9\u64ad'));
    });
    
    const vod = {
        "vod_id": id,
        "vod_name": res.title || '\u672a\u77e5\u6807\u9898',
        "vod_year": res.year || '',
        "vod_area": res.area || '',
        "vod_remarks": res.mask || '',
        "vod_content": res.description || '',
        "vod_pic": imghost ? `${imghost}${res.thumbnail || ''}` : (res.thumbnail || ''),
        "vod_play_from": play_from.join('$$$'),
        "vod_play_url": sortedPlayUrls.join('$$$')
    };

    return JSON.stringify({ list: [vod] });
}

async function play(flag, id, flags) {
    if (id && id.indexOf(".m3u8") > -1) {
        return JSON.stringify({ parse: 0, url: id });
    } else if (id) {
        return JSON.stringify({ parse: 0, url: `tvbox-xg:${id}` });
    }
    return JSON.stringify({ parse: 0, url: '', msg: '\u64ad\u653e\u5730\u5740\u4e3a\u7a7a' });
}

async function search(wd, quick, pg) {
    let page = pg || 1;
    
    let promises = [];
    for (let p = page; p < page + maxPages; p++) {
        let url = `${host}${rule.search}?key=${encodeURIComponent(wd)}&category_id=88&page=${p}&pageSize=20`;
        promises.push(request(url, { headers, timeout: 8000 }));
    }
    
    let results = await Promise.all(promises);
    
    let allVideos = [];
    for (let html of results) {
        if (!html) continue;
        let parsed = safeJSONParse(html);
        let res = parsed.data;
        if (res && Array.isArray(res)) {
            res.forEach(item => {
                if (item && item.id) {
                    allVideos.push({
                        vod_id: item.id,
                        vod_name: item.title || '\u672a\u77e5\u6807\u9898',
                        vod_pic: imghost ? `${imghost}${item.thumbnail || ''}` : (item.thumbnail || ''),
                        vod_remarks: item.mask || '',
                    });
                }
            });
        }
    }

    let filteredVideos = [];
    for (let item of allVideos) {
        if (item.vod_name && new RegExp(wd, "i").test(item.vod_name)) {
            filteredVideos.push(item);
        }
    }

    return JSON.stringify({
        page: page,
        pagecount: maxPages,
        limit: filteredVideos.length,
        total: filteredVideos.length,
        list: filteredVideos
    });
}

function extractDomain(url) {
    if (!url) return '';
    const cleanUrl = url.replace(/^(https?:\/\/)?/, '');
    const domainPart = cleanUrl.split('/')[0];
    
    if (domainPart.includes('-')) {
        return domainPart.split('-')[0];
    }
    
    if (domainPart.includes('.')) {
        const dotParts = domainPart.split('.');
        if (dotParts.length > 2) {
            return dotParts[dotParts.length - 2];
        } else if (dotParts.length === 2) {
            return dotParts[0];
        }
    }
    
    return domainPart;
}

export function __jsEvalReturn() {
    return { init, home, homeVod, category, detail, play, search };
}