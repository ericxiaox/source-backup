/*
@header({
  searchable: 1,
  filterable: 1,
  quickSearch: 1,
  title: '\u9ebb\u8c46HD',
  lang: 'cat'
})
*/

import { load } from 'assets://js/lib/cat.js';

let host = 'https://www.madouhd.com';
let headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 16; 23078RKD5C) AppleWebKit/537.36',
    'Referer': host
};

async function request(url, options = {}) {
    try {
        let res = await req(url, { headers: { ...headers, ...options.headers }, ...options });
        return res.content || '';
    } catch (e) {
        console.log('[\u8bf7\u6c42\u5931\u8d25] ' + url);
        return '';
    }
}

function buildCategoryUrl(tid, page, extend) {
    let cls = (extend.class || '').trim();
    let year = (extend.year || '').trim();
    let hasFilter = cls || year;

    if (!hasFilter) {
        return `${host}/vodtype/${tid}-${page}.html`;
    }

    let clsPart = cls ? encodeURIComponent(cls) : '';
    let yearPart = year ? year : '';

    let base = `${host}/vodshow/${tid}---${clsPart}-----${page}`;
    if (yearPart) {
        base += `---${yearPart}`;
    }
    return base + '.html';
}

function yearOptions() {
    let arr = [{ n: '\u5168\u90e8', v: '' }];
    for (let y = 2026; y >= 2004; y--) arr.push({ n: y.toString(), v: y.toString() });
    return arr;
}

function home(filter) {
    const classes = [
        { type_id: '1', type_name: '\u7535\u5f71' },
        { type_id: '2', type_name: '\u7535\u89c6\u5267' },
        { type_id: '3', type_name: '\u7efc\u827a' },
        { type_id: '4', type_name: '\u52a8\u6f2b' },
        { type_id: '24', type_name: '\u7eaa\u5f55\u7247' }
    ];

    const filters = {
        '1': [
            { key: 'class', name: '\u5267\u60c5', value: [
                { n: '\u5168\u90e8', v: '' }, { n: '\u52a8\u4f5c', v: '\u52a8\u4f5c' }, { n: '\u559c\u5267', v: '\u559c\u5267' },
                { n: '\u7231\u60c5', v: '\u7231\u60c5' }, { n: '\u79d1\u5e7b', v: '\u79d1\u5e7b' }, { n: '\u6050\u6016', v: '\u6050\u6016' },
                { n: '\u5267\u60c5', v: '\u5267\u60c5' }, { n: '\u6218\u4e89', v: '\u6218\u4e89' }, { n: '\u72af\u7f6a', v: '\u72af\u7f6a' }
            ]},
            { key: 'year', name: '\u5e74\u4efd', value: yearOptions() }
        ],
        '2': [
            { key: 'class', name: '\u5267\u60c5', value: [
                { n: '\u5168\u90e8', v: '' }, { n: '\u53e4\u88c5', v: '\u53e4\u88c5' }, { n: '\u7231\u60c5', v: '\u7231\u60c5' },
                { n: '\u5947\u5e7b', v: '\u5947\u5e7b' }, { n: '\u559c\u5267', v: '\u559c\u5267' }, { n: '\u5bb6\u5ead', v: '\u5bb6\u5ead' }
            ]},
            { key: 'year', name: '\u5e74\u4efd', value: yearOptions() }
        ],
        '3': [{ key: 'year', name: '\u5e74\u4efd', value: yearOptions() }],
        '4': [{ key: 'year', name: '\u5e74\u4efd', value: yearOptions() }],
        '24': [{ key: 'year', name: '\u5e74\u4efd', value: yearOptions() }]
    };
    return JSON.stringify({ class: classes, filters: filters });
}

async function homeVod() {
    return JSON.stringify({ list: [] });
}

async function category(tid, pg, filter, extend) {
    let page = parseInt(pg) || 1;
    let url = buildCategoryUrl(tid, page, extend || {});
    console.log('[\u5206\u7c7b] ' + url);

    let html = await request(url);
    if (!html) return JSON.stringify({ list: [], page, pagecount: 1 });

    const $ = load(html);
    const list = [];

    $('.stui-vodlist li').each((i, el) => {
        let a = $(el).find('a.stui-vodlist__thumb');
        let href = a.attr('href') || '';
        let title = a.attr('title') || '';
        let pic = a.attr('data-original') || a.find('img').attr('src') || '';
        let remarks = a.find('.pic-text').text().trim();
        let vid = (href.match(/\/(\d+)\.html$/) || [])[1] || href;

        if (title && vid) {
            list.push({
                vod_id: vid,
                vod_name: title,
                vod_pic: pic,
                vod_remarks: remarks
            });
        }
    });

    let totalPage = 1;
    $('a').each((i, el) => {
        let href = $(el).attr('href') || '';
        let m = href.match(/\/(\d+)(?:-(\d+)|-----(\d+)---\d+)?\.html$/);
        if (m) {
            let p = parseInt(m[2] || m[3] || m[1]); 
            if (p > totalPage) totalPage = p;
        }
    });
    if (totalPage < page && list.length > 0) totalPage = page + 1;

    return JSON.stringify({
        list,
        page: page,
        pagecount: totalPage,
        limit: list.length,
        total: totalPage * list.length
    });
}

async function detail(id) {
    let url = `${host}/dy/${id}.html`;
    let html = await request(url);
    if (!html) return JSON.stringify({ list: [] });

    const $ = load(html);
    let vod = {
        vod_id: id,
        vod_name: $('h1.title').text().trim(),
        vod_pic: $('.stui-content__thumb img').attr('data-original') || $('.stui-content__thumb img').attr('src') || '',
        vod_content: '',
        vod_play_from: '',
        vod_play_url: '',
        vod_director: '',
        vod_actor: '',
        type_name: '',
        vod_area: '',
        vod_year: '',
        vod_remarks: ''
    };

    let dataText = $('.stui-content__detail .data').first().text() || '';
    let typeMatch = dataText.match(/类型：(.+?)(?=\s*(?:地区|年份|$))/);
    if (typeMatch) vod.type_name = typeMatch[1].replace(/\s+/g, ' ').trim();
    let areaMatch = dataText.match(/地区：(.+?)(?=\s*(?:年份|$))/);
    if (areaMatch) vod.vod_area = areaMatch[1].trim();
    let yearMatch = dataText.match(/年份：(\d{4})/);
    if (yearMatch) vod.vod_year = yearMatch[1];
    $('.stui-content__detail .data').each((i, el) => {
        let text = $(el).text();
        if (text.includes('\u5bfc\u6f14\uff1a'))
            vod.vod_director = $(el).find('a').map((j, a) => $(a).text()).get().join(',');
        if (text.includes('\u4e3b\u6f14\uff1a'))
            vod.vod_actor = $(el).find('a').map((j, a) => $(a).text()).get().join(',');
    });

    vod.vod_content = $('.detail-content').text().trim() || $('.detail-sketch').text().trim();

    let updateMatch = $('.stui-content__detail').text().match(/更新：(\d{4}-\d{2}-\d{2})/);
    if (updateMatch) vod.vod_remarks = updateMatch[1];

    let sources = [];
    $('.stui-pannel-box.b.playlist.mb').each((i, panel) => {
        let name = $(panel).find('h3.title').text().trim();
        let urls = [];
        $(panel).find('.stui-content__playlist a').each((j, a) => {
            let href = $(a).attr('href') || '';
            let text = $(a).text().trim();
            if (!href.startsWith('http')) href = host + href;
            urls.push(text + '$' + href);
        });
        if (urls.length) sources.push({ name, urls: urls.join('#') });
    });

    if (sources.length) {
        vod.vod_play_from = sources.map(s => s.name).join('$$$');
        vod.vod_play_url = sources.map(s => s.urls).join('$$$');
    } else {
        let btn = $('.play-btn .btn-primary').attr('href');
        if (btn) {
            if (!btn.startsWith('http')) btn = host + btn;
            vod.vod_play_from = '\u64ad\u653e';
            vod.vod_play_url = '\u7acb\u5373\u89c2\u770b$' + btn;
        }
    }

    return JSON.stringify({ list: [vod] });
}

async function search(wd, quick, pg) {
    let page = pg || 1;
    let url = `${host}/vodsearch/-------------.html?wd=${encodeURIComponent(wd)}&submit=`;
    let html = await request(url);
    if (!html) return JSON.stringify({ list: [] });

    const $ = load(html);
    const list = [];
    $('.stui-vodlist li').each((i, el) => {
        let a = $(el).find('a.stui-vodlist__thumb');
        let href = a.attr('href') || '';
        let title = a.attr('title') || '';
        let pic = a.attr('data-original') || a.find('img').attr('src') || '';
        let remarks = a.find('.pic-text').text().trim();
        let vid = (href.match(/\/(\d+)\.html$/) || [])[1] || href;
        if (title && vid) list.push({ vod_id: vid, vod_name: title, vod_pic: pic, vod_remarks: remarks });
    });
    return JSON.stringify({ list });
}

async function play(flag, id, flags) {
    let url = id.startsWith('http') ? id : host + id;
    let html = await request(url);
    if (!html) return JSON.stringify({ parse: 0, url: url });

    let match = html.match(/player_aaaa\s*=\s*(\{[\s\S]*?\});/);
    if (match) {
        try {
            let cfg = JSON.parse(match[1]);
            if (cfg.url) return JSON.stringify({ parse: 1, url: cfg.url, header: JSON.stringify({ Referer: url }) });
        } catch (e) {}    
        let urlMatch = match[1].match(/"url":"([^"]+)"/);
        if (urlMatch) {
            let realUrl = urlMatch[1].replace(/\\\//g, '/');
            return JSON.stringify({ parse: 1, url: realUrl, header: JSON.stringify({ Referer: url }) });
        }
    }
    return JSON.stringify({ parse: 0, url: url });
}

export function __jsEvalReturn() {
    return { init: () => {}, home, homeVod, category, detail, play, search };
}