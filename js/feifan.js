import { Crypto, load, _, jinja2 } from 'assets://js/lib/cat.js';

let key = 'ff';
let HOST = 'https://ffzy5.tv';
let siteKey = '';
let siteType = 0;

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

async function request(reqUrl, agentSp) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: {
            'User-Agent': agentSp || UA,
            'Referer': HOST
        },
    });
    return res.content;
}

async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

async function home(filter) {
    let classes = [{"type_id":1,"type_name":"\u7535\u5f71"},{"type_id":2,"type_name":"\u8fde\u7eed\u5267"},{"type_id":3,"type_name":"\u7efc\u827a"},{"type_id":4,"type_name":"\u52a8\u6f2b"}];
    let filterObj = {
        "2":[{"key":"cateId","name":"\u7c7b\u578b","value":[{"n":"\u5168\u90e8","v":"2"},{"n":"\u77ed\u5267","v":"36"},{"n":"\u9646\u5267","v":"13"},{"n":"\u97e9\u5267","v":"15"},{"n":"\u6b27\u7f8e\u5267","v":"16"},{"n":"\u6e2f\u5267","v":"14"},{"n":"\u53f0\u5267","v":"21"},{"n":"\u65e5\u5267","v":"22"},{"n":"\u6d77\u5916\u5267","v":"23"},{"n":"\u6cf0\u5267","v":"24"},{"n":"\u7eaa\u5f55\u7247","v":"20"}]}],
        "1":[{"key":"cateId","name":"\u7c7b\u578b","value":[{"n":"\u5168\u90e8","v":"1"},{"n":"\u52a8\u4f5c\u7247","v":"6"},{"n":"\u559c\u5267\u7247","v":"7"},{"n":"\u7231\u60c5\u7247","v":"8"},{"n":"\u79d1\u5e7b\u7247","v":"9"},{"n":"\u6050\u6016\u7247","v":"10"},{"n":"\u5267\u60c5\u7247","v":"11"},{"n":"\u6218\u4e89\u7247","v":"12"}]}],
        "3":[{"key":"cateId","name":"\u7c7b\u578b","value":[{"n":"\u5168\u90e8","v":"3"},{"n":"\u56fd\u7efc","v":"25"},{"n":"\u6e2f\u7efc","v":"26"},{"n":"\u97e9\u65e5\u7efc","v":"27"},{"n":"\u6b27\u7f8e\u7efc","v":"28"}]}],
        "4":[{"key":"cateId","name":"\u7c7b\u578b","value":[{"n":"\u5168\u90e8","v":"4"},{"n":"\u56fd\u6f2b","v":"29"},{"n":"\u65e5\u97e9\u52a8\u6f2b","v":"30"},{"n":"\u6b27\u7f8e\u52a8\u6f2b","v":"31"},{"n":"\u6e2f\u6f2b","v":"32"},{"n":"\u6d77\u5916\u52a8\u6f2b","v":"33"}]}]
    };

    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {}

async function category(tid, pg, filter, extend) {
    if (pg <= 0) pg = 1;
    let data = JSON.parse(await request(HOST + '/index.php/ajax/data?mid=1&tid=' + (extend.cateId || tid) + '&page=' + pg + '&limit=20'));
   
    let videos = [];
    for (const vod of data.list) {
        videos.push({
            vod_id: vod.vod_id,
            vod_name: vod.vod_name,
            vod_pic: vod.vod_pic,
            vod_remarks: '',
        });
    }
    return JSON.stringify({
        page: parseInt(data.page),
        pagecount: data.pagecount,
        limit: 20,
        total: data.total,
        list: videos,
    });
}

async function detail(id) {
    var html = await request(HOST + '/index.php/vod/detail/id/' + id + '.html');
    var $ = load(html);
    let pList = $('.people .right p');
    let getTxt = (label) => {
        let text = '';
        pList.each((idx, el) => {
            let t = $(el).text().trim();
            if (t.startsWith(label)) {
                text = t.replace(label, '').trim();
            }
        });
        return text;
    };

    var vod = {
        vod_id: id,
        vod_name: getTxt('\u7247\u540d\uff1a'),
        vod_type: getTxt('\u7c7b\u578b\uff1a').replace(/&nbsp;/g, ''),
        vod_actor: getTxt('\u6f14\u5458\uff1a'),
        vod_director: getTxt('\u5bfc\u6f14\uff1a'),
        vod_pic: $('.people .left img').attr('src'),
        vod_remarks: getTxt('\u72b6\u6001\uff1a') || '',
        vod_content: $('.vod_content').text().replace(/&nbsp;/g, '').trim(),
    };
    
    const playlist = _.map($('div.ffm3u8 > li > a[target*=_blank]'), (it) => {
        return it.attribs.title + '$' + it.attribs.href;
    });
    
    vod.vod_play_from = "\u975e\u51e1\u76f4\u8fbe";
    vod.vod_play_url = playlist.join('#');
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
    return JSON.stringify({
        parse: 0,
        url: id,
    });
}

async function search(wd, quick, pg) {
    if (pg <= 0) pg = 1;
    let data = JSON.parse(await request(HOST + '/api.php/provide/vod/?wd=' + wd + '&pg=' + pg + '&ac=detail'));

    let videos = [];
    for (const vod of data.list) {
        videos.push({
            vod_id: vod.vod_id,
            vod_name: vod.vod_name,
            vod_pic: vod.vod_pic,
            vod_remarks: '',
        });
    }
    return JSON.stringify({
        page: parseInt(data.page),
        pagecount: data.pagecount,
        limit: 20,
        total: data.total,
        list: videos,
    });
}

export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        detail: detail,
        play: play,
        search: search,
    };
}