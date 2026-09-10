// \u672c\u8d44\u6e90\u6765\u6e90\u4e8e\u4e92\u8054\u7f51\u516c\u5f00\u6e20\u9053\uff0c\u4ec5\u53ef\u7528\u4e8e\u4e2a\u4eba\u5b66\u4e60\u722c\u866b\u6280\u672f\u3002
// \u4e25\u7981\u5c06\u5176\u7528\u4e8e\u4efb\u4f55\u5546\u4e1a\u7528\u9014\uff0c\u4e0b\u8f7d\u540e\u8bf7\u4e8e 24 \u5c0f\u65f6\u5185\u5220\u9664\uff0c\u641c\u7d22\u7ed3\u679c\u5747\u6765\u81ea\u6e90\u7ad9\uff0c\u672c\u4eba\u4e0d\u627f\u62c5\u4efb\u4f55\u8d23\u4efb\u3002
let e = "https://web.agespa-01.com:8443",
    t = "https://ageapi.omwjhz.com:18888";
const a = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        Accept: "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        Origin: e,
        Pragma: "no-cache",
        Referer: `${e}`,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="143", "Google Chrome";v="143"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"'
    },
    r = "function" == typeof js2Proxy && "function" == typeof desX && "function" != typeof getProxy;
async function n(e) {}
async function l(e) {
    let t = [{
        type_id: "1",
        type_name: "\u52a8\u6f2b"
    }];
    void 0 !== r && r && t.unshift({
        type_id: "home",
        type_name: "\u9996\u9875"
    });
    try {
        if (!e) return JSON.stringify({
            class: t,
            filters: {}
        });
        let a = {
            1: [{
                name: "region",
                label: "\u5730\u533a",
                data: [{
                    text: "\u5168\u90e8",
                    value: "all"
                }, {
                    text: "\u65e5\u672c",
                    value: "\u65e5\u672c"
                }, {
                    text: "\u4e2d\u56fd",
                    value: "\u4e2d\u56fd"
                }, {
                    text: "\u6b27\u7f8e",
                    value: "\u6b27\u7f8e"
                }]
            }, {
                name: "genre",
                label: "\u7248\u672c",
                data: [{
                    text: "\u5168\u90e8",
                    value: "all"
                }, {
                    text: "TV",
                    value: "TV"
                }, {
                    text: "\u5267\u573a\u7248",
                    value: "\u5267\u573a\u7248"
                }, {
                    text: "OVA",
                    value: "OVA"
                }]
            }, {
                name: "letter",
                label: "\u9996\u5b57\u6bcd",
                data: [{
                    text: "\u5168\u90e8",
                    value: "all"
                }, {
                    text: "A",
                    value: "A"
                }, {
                    text: "B",
                    value: "B"
                }, {
                    text: "C",
                    value: "C"
                }, {
                    text: "D",
                    value: "D"
                }, {
                    text: "E",
                    value: "E"
                }, {
                    text: "F",
                    value: "F"
                }, {
                    text: "G",
                    value: "G"
                }, {
                    text: "H",
                    value: "H"
                }, {
                    text: "I",
                    value: "I"
                }, {
                    text: "J",
                    value: "J"
                }, {
                    text: "K",
                    value: "K"
                }, {
                    text: "L",
                    value: "L"
                }, {
                    text: "M",
                    value: "M"
                }, {
                    text: "N",
                    value: "N"
                }, {
                    text: "O",
                    value: "O"
                }, {
                    text: "P",
                    value: "P"
                }, {
                    text: "Q",
                    value: "Q"
                }, {
                    text: "R",
                    value: "R"
                }, {
                    text: "S",
                    value: "S"
                }, {
                    text: "T",
                    value: "T"
                }, {
                    text: "U",
                    value: "U"
                }, {
                    text: "V",
                    value: "V"
                }, {
                    text: "W",
                    value: "W"
                }, {
                    text: "X",
                    value: "X"
                }, {
                    text: "Y",
                    value: "Y"
                }, {
                    text: "Z",
                    value: "Z"
                }]
            }, {
                name: "year",
                label: "\u5e74\u4efd",
                data: [{
                    text: "\u5168\u90e8",
                    value: "all"
                }, {
                    text: "2026",
                    value: "2026"
                }, {
                    text: "2025",
                    value: "2025"
                }, {
                    text: "2024",
                    value: "2024"
                }, {
                    text: "2023",
                    value: "2023"
                }, {
                    text: "2022",
                    value: "2022"
                }, {
                    text: "2021",
                    value: "2021"
                }, {
                    text: "2020",
                    value: "2020"
                }, {
                    text: "2019",
                    value: "2019"
                }, {
                    text: "2018",
                    value: "2018"
                }, {
                    text: "2017",
                    value: "2017"
                }, {
                    text: "2016",
                    value: "2016"
                }, {
                    text: "2015",
                    value: "2015"
                }, {
                    text: "2014",
                    value: "2014"
                }, {
                    text: "2013",
                    value: "2013"
                }, {
                    text: "2012",
                    value: "2012"
                }, {
                    text: "2011",
                    value: "2011"
                }, {
                    text: "2010",
                    value: "2010"
                }, {
                    text: "2009",
                    value: "2009"
                }, {
                    text: "2008",
                    value: "2008"
                }, {
                    text: "2007",
                    value: "2007"
                }, {
                    text: "2006",
                    value: "2006"
                }, {
                    text: "2005",
                    value: "2005"
                }, {
                    text: "2004",
                    value: "2004"
                }, {
                    text: "2003",
                    value: "2003"
                }, {
                    text: "2002",
                    value: "2002"
                }, {
                    text: "2001",
                    value: "2001"
                }, {
                    text: "2000\u4ee5\u524d",
                    value: "2000"
                }]
            }, {
                name: "season",
                label: "\u5b63\u5ea6",
                data: [{
                    text: "\u5168\u90e8",
                    value: "all"
                }, {
                    text: "1\u6708",
                    value: "1"
                }, {
                    text: "4\u6708",
                    value: "4"
                }, {
                    text: "7\u6708",
                    value: "7"
                }, {
                    text: "10\u6708",
                    value: "10"
                }]
            }, {
                name: "status",
                label: "\u72b6\u6001",
                data: [{
                    text: "\u5168\u90e8",
                    value: "all"
                }, {
                    text: "\u8fde\u8f7d",
                    value: "\u8fde\u8f7d"
                }, {
                    text: "\u5b8c\u7ed3",
                    value: "\u5b8c\u7ed3"
                }, {
                    text: "\u672a\u64ad\u653e",
                    value: "\u672a\u64ad\u653e"
                }]
            }, {
                name: "label",
                label: "\u7c7b\u578b",
                data: [{
                    text: "\u5168\u90e8",
                    value: "all"
                }, {
                    text: "\u641e\u7b11",
                    value: "\u641e\u7b11"
                }, {
                    text: "\u8fd0\u52a8",
                    value: "\u8fd0\u52a8"
                }, {
                    text: "\u52b1\u5fd7",
                    value: "\u52b1\u5fd7"
                }, {
                    text: "\u70ed\u8840",
                    value: "\u70ed\u8840"
                }, {
                    text: "\u6218\u6597",
                    value: "\u6218\u6597"
                }, {
                    text: "\u7ade\u6280",
                    value: "\u7ade\u6280"
                }, {
                    text: "\u6821\u56ed",
                    value: "\u6821\u56ed"
                }, {
                    text: "\u9752\u6625",
                    value: "\u9752\u6625"
                }, {
                    text: "\u7231\u60c5",
                    value: "\u7231\u60c5"
                }, {
                    text: "\u604b\u7231",
                    value: "\u604b\u7231"
                }, {
                    text: "\u5192\u9669",
                    value: "\u5192\u9669"
                }, {
                    text: "\u540e\u5bab",
                    value: "\u540e\u5bab"
                }, {
                    text: "\u767e\u5408",
                    value: "\u767e\u5408"
                }, {
                    text: "\u6cbb\u6108",
                    value: "\u6cbb\u6108"
                }, {
                    text: "\u841d\u8389",
                    value: "\u841d\u8389"
                }, {
                    text: "\u9b54\u6cd5",
                    value: "\u9b54\u6cd5"
                }, {
                    text: "\u60ac\u7591",
                    value: "\u60ac\u7591"
                }, {
                    text: "\u63a8\u7406",
                    value: "\u63a8\u7406"
                }, {
                    text: "\u5947\u5e7b",
                    value: "\u5947\u5e7b"
                }, {
                    text: "\u79d1\u5e7b",
                    value: "\u79d1\u5e7b"
                }, {
                    text: "\u6e38\u620f",
                    value: "\u6e38\u620f"
                }, {
                    text: "\u795e\u9b54",
                    value: "\u795e\u9b54"
                }, {
                    text: "\u6050\u6016",
                    value: "\u6050\u6016"
                }, {
                    text: "\u8840\u8165",
                    value: "\u8840\u8165"
                }, {
                    text: "\u673a\u6218",
                    value: "\u673a\u6218"
                }, {
                    text: "\u6218\u4e89",
                    value: "\u6218\u4e89"
                }, {
                    text: "\u72af\u7f6a",
                    value: "\u72af\u7f6a"
                }, {
                    text: "\u5386\u53f2",
                    value: "\u5386\u53f2"
                }, {
                    text: "\u793e\u4f1a",
                    value: "\u793e\u4f1a"
                }, {
                    text: "\u804c\u573a",
                    value: "\u804c\u573a"
                }, {
                    text: "\u5267\u60c5",
                    value: "\u5267\u60c5"
                }, {
                    text: "\u4f2a\u5a18",
                    value: "\u4f2a\u5a18"
                }, {
                    text: "\u803d\u7f8e",
                    value: "\u803d\u7f8e"
                }, {
                    text: "\u7ae5\u5e74",
                    value: "\u7ae5\u5e74"
                }, {
                    text: "\u6559\u80b2",
                    value: "\u6559\u80b2"
                }, {
                    text: "\u4eb2\u5b50",
                    value: "\u4eb2\u5b50"
                }, {
                    text: "\u771f\u4eba",
                    value: "\u771f\u4eba"
                }, {
                    text: "\u6b4c\u821e",
                    value: "\u6b4c\u821e"
                }, {
                    text: "\u8089\u756a",
                    value: "\u8089\u756a"
                }, {
                    text: "\u7f8e\u5c11\u5973",
                    value: "\u7f8e\u5c11\u5973"
                }, {
                    text: "\u8f7b\u5c0f\u8bf4",
                    value: "\u8f7b\u5c0f\u8bf4"
                }, {
                    text: "\u5438\u8840\u9b3c",
                    value: "\u5438\u8840\u9b3c"
                }, {
                    text: "\u5973\u6027\u5411",
                    value: "\u5973\u6027\u5411"
                }, {
                    text: "\u6ce1\u9762\u756a",
                    value: "\u6ce1\u9762\u756a"
                }, {
                    text: "\u6b22\u4e50\u5411",
                    value: "\u6b22\u4e50\u5411"
                }]
            }, {
                name: "resource",
                label: "\u8d44\u6e90",
                data: [{
                    text: "\u5168\u90e8",
                    value: "all"
                }, {
                    text: "BDRIP",
                    value: "BDRIP"
                }, {
                    text: "AGERIP",
                    value: "AGERIP"
                }]
            }, {
                name: "order",
                label: "\u6392\u5e8f",
                data: [{
                    text: "\u66f4\u65b0\u65f6\u95f4",
                    value: "time"
                }, {
                    text: "\u540d\u79f0",
                    value: "name"
                }, {
                    text: "\u70b9\u51fb\u91cf",
                    value: "\u70b9\u51fb\u91cf"
                }]
            }].map(e => ({
                key: e.name,
                name: e.label,
                init: e.data[0].value,
                value: e.data.map(e => ({
                    n: e.text,
                    v: e.value
                }))
            }))
        };
        return JSON.stringify({
            class: t,
            filters: a
        })
    } catch (e) {
        return JSON.stringify({
            class: t,
            filters: {}
        })
    }
}
async function o() {
    try {
        const e = `${t}/v2/home-list`,
            r = await req(e, {
                headers: a,
                timeout: 8e3
            });
        if (!r || !r.content) return JSON.stringify({
            list: []
        });
        let n = "string" == typeof r.content ? JSON.parse(r.content) : r.content,
            l = new Map;
        const o = (e, t, a, r) => {
            if (!e) return;
            const n = e.toString().replace(/\/detail\//i, "");
            l.has(n) || l.set(n, {
                vod_id: n,
                vod_name: t || "",
                vod_pic: a || "",
                vod_remarks: r || ""
            })
        };
        if (Array.isArray(n.recommend) && n.recommend.forEach(e => {
                o(e.AID, e.Title, e.PicSmall, e.NewTitle)
            }), Array.isArray(n.latest) && n.latest.forEach(e => {
                o(e.AID, e.Title, e.PicSmall, e.NewTitle)
            }), n.week_list && "object" == typeof n.week_list) {
            ["1", "2", "3", "4", "5", "6", "0"].forEach(e => {
                const t = n.week_list[e];
                Array.isArray(t) && t.forEach(e => {
                    o(e.id, e.name, "", e.namefornew)
                })
            })
        }
        const i = Array.from(l.values());
        return JSON.stringify({
            list: i
        })
    } catch (e) {
        return JSON.stringify({
            list: []
        })
    }
}
async function i(e, r, n, l) {
    try {
        if ("home" === e) {
            let e = JSON.parse(await o());
            return JSON.stringify({
                list: e.list || [],
                page: 1,
                pagecount: 1
            })
        }
        const n = l.genre || "all",
            i = l.label || "all",
            s = l.letter || "all",
            c = l.order || "time",
            u = l.region || "all",
            v = l.resource || "all",
            p = l.season || "all",
            x = l.status || "all",
            d = l.year || "all",
            h = 20,
            m = `${t}/v2/catalog?genre=${encodeURIComponent(n)}&label=${encodeURIComponent(i)}&letter=${encodeURIComponent(s)}&order=${encodeURIComponent(c)}&region=${encodeURIComponent(u)}&resource=${encodeURIComponent(v)}&season=${encodeURIComponent(p)}&status=${encodeURIComponent(x)}&year=${encodeURIComponent(d)}&page=${r}&size=${h}`,
            g = await req(m, {
                headers: a,
                timeout: 8e3
            });
        if (!g || !g.content) return JSON.stringify({
            list: [],
            page: parseInt(r),
            pagecount: parseInt(r)
        });
        let f = "string" == typeof g.content ? JSON.parse(g.content) : g.content;
        if (!f.videos) return JSON.stringify({
            list: [],
            page: parseInt(r),
            pagecount: parseInt(r)
        });
        const y = f.videos.map(e => ({
                vod_id: e.id.toString(),
                vod_name: e.name,
                vod_pic: e.cover,
                vod_remarks: e.uptodate || e.status
            })),
            A = f.total || 0,
            S = A > 0 ? Math.ceil(A / h) : parseInt(r);
        return JSON.stringify({
            list: y,
            page: parseInt(r),
            pagecount: S
        })
    } catch (e) {
        return JSON.stringify({
            list: [],
            page: parseInt(r),
            pagecount: parseInt(r)
        })
    }
}
async function s(e, r, n = 1) {
    try {
        const r = encodeURIComponent(e),
            l = `${t}/v2/search?query=${r}&page=${n}`,
            o = await req(l, {
                headers: a,
                timeout: 8e3
            });
        if (!o || !o.content) return JSON.stringify({
            list: [],
            page: parseInt(n),
            pagecount: parseInt(n)
        });
        let i = "string" == typeof o.content ? JSON.parse(o.content) : o.content;
        if (!i.data || !i.data.videos) return JSON.stringify({
            list: [],
            page: parseInt(n),
            pagecount: parseInt(n)
        });
        const s = i.data.videos.map(e => ({
                vod_id: e.id.toString(),
                vod_name: e.name,
                vod_pic: e.cover,
                vod_remarks: e.uptodate || e.status
            })),
            c = i.data.totalPage || parseInt(n);
        return JSON.stringify({
            list: s,
            page: parseInt(n),
            pagecount: c
        })
    } catch (e) {
        return JSON.stringify({
            list: [],
            page: parseInt(n),
            pagecount: parseInt(n)
        })
    }
}
async function c(e) {
    try {
        const r = `${t}/v2/detail/${e}`,
            n = await req(r, {
                headers: a,
                timeout: 8e3
            });
        if (!n || !n.content) return JSON.stringify({
            list: []
        });
        let l = "string" == typeof n.content ? JSON.parse(n.content) : n.content;
        const o = l.video || {},
            i = o.playlists || {},
            s = l.player_label_arr || {},
            c = (l.player_vip || "").split(","),
            u = l.player_jx || {
                vip: "",
                zj: ""
            };
        let v = [],
            p = [];
        for (const e in i) {
            const t = s[e] || e;
            v.push(`${t}(${e})`);
            const a = c.includes(e) ? u.vip || "" : u.zj || "";
            let r = [];
            (i[e] || []).forEach(e => {
                if (Array.isArray(e) && e.length >= 2) {
                    const t = e[0],
                        n = e[1],
                        l = a ? `${a}${n}` : n;
                    r.push(`${t}$${l}`)
                }
            }), p.push(r.join("#"))
        }
        const x = {
            vod_id: o.id ? o.id.toString() : e.toString(),
            vod_name: o.name || "",
            vod_pic: o.cover || "",
            type_name: o.type || "",
            vod_year: o.year ? o.year.toString() : "",
            vod_area: o.area || "",
            vod_remarks: o.uptodate || o.status || "",
            vod_actor: "",
            vod_director: "",
            vod_content: o.intro_clean || o.intro || "",
            vod_play_from: v.join("$$$"),
            vod_play_url: p.join("$$$")
        };
        return JSON.stringify({
            list: [x]
        })
    } catch (e) {
        return JSON.stringify({
            list: []
        })
    }
}
async function u(e, t, r) {
    try {
        let e = await async function(e) {
            try {
                function t(e) {
                    const t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
                    let a = [];
                    for (let t = 0; t < e.length; t += 2) a.push(parseInt(e.substring(t, t + 2), 16));
                    let r = "",
                        n = 0,
                        l = a.length;
                    for (; n < l;) {
                        let e, o, i = 255 & a[n++];
                        if (n === l) {
                            r += t.charAt(i >> 2) + t.charAt((3 & i) << 4) + "==";
                            break
                        }
                        if (e = a[n++], n === l) {
                            r += t.charAt(i >> 2) + t.charAt((3 & i) << 4 | (240 & e) >> 4) + t.charAt((15 & e) << 2) + "=";
                            break
                        }
                        o = a[n++], r += t.charAt(i >> 2) + t.charAt((3 & i) << 4 | (240 & e) >> 4) + t.charAt((15 & e) << 2 | (192 & o) >> 6) + t.charAt(63 & o)
                    }
                    return r
                }

                function a(e) {
                    const t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
                        a = new Uint8Array(256);
                    for (let e = 0; e < t.length; e++) a[t.charCodeAt(e)] = e;
                    let r = [];
                    for (let t = 0; t < e.length; t += 4) {
                        let n = a[e.charCodeAt(t)] << 18 | a[e.charCodeAt(t + 1)] << 12 | a[e.charCodeAt(t + 2)] << 6 | a[e.charCodeAt(t + 3)];
                        r.push(n >> 16 & 255), "=" !== e[t + 2] && r.push(n >> 8 & 255), "=" !== e[t + 3] && r.push(255 & n)
                    }
                    return r.map(e => ("00" + e.toString(16)).slice(-2)).join("").toUpperCase()
                }

                function r() {
                    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, e => {
                        const t = 16 * Math.random() | 0;
                        return ("x" === e ? t : 3 & t | 8).toString(16)
                    })
                }
                const n = function() {
                        const e = "ni po jie ni ** ",
                            r = "AES/CBC/PKCS7";
                        return {
                            encrypt: t => a(aesX(r, !0, t, !1, e, e, !0)),
                            decrypt: a => aesX(r, !1, t(a), !0, e, e, !1)
                        }
                    }(),
                    l = e.match(/(https?:\/\/[^/]+)/),
                    o = l ? l[1] : "",
                    i = e.match(/https?:\/\/([^/:]+)/),
                    s = i ? i[1] : "",
                    c = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
                        "accept-language": "zh-CN,zh;q=0.9",
                        "cache-control": "no-cache",
                        pragma: "no-cache",
                        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": '"Windows"',
                        "sec-fetch-storage-access": "none"
                    },
                    u = (await req(e, {
                        method: "get",
                        headers: {
                            ...c,
                            Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                            priority: "u=0, i",
                            referer: "https://web.agespa-01.com:8443/",
                            "sec-fetch-dest": "iframe",
                            "sec-fetch-mode": "navigate",
                            "sec-fetch-site": "cross-site",
                            "sec-fetch-user": "?1",
                            "upgrade-insecure-requests": "1"
                        }
                    })).content;
                if (!u) throw new Error("");
                const v = u.match(/var Vurl\s*=\s*['"]([^'"]+)['"]/),
                    p = v ? v[1] : "";
                if (/^(https?:\/\/|\/\/)\S+/i.test(p)) return p.startsWith("//") ? "https:" + p : p;
                const x = u.match(/var Time\s*=\s*"([^"]+)"/),
                    d = u.match(/var Version\s*=\s*"([^"]+)"/),
                    h = u.match(/var Ref\s*=\s*"([^"]+)"/),
                    m = u.match(/var Api\s*=\s*"([^"]+)"/),
                    g = u.match(/<meta\s+http-equiv="Content-Type"[^>]+id="([^"]+)"/i),
                    f = u.match(/<meta\s+name="viewport"[^>]+id="([^"]+)"/i),
                    y = x ? x[1] : Math.floor(Date.now() / 1e3).toString(),
                    A = d ? d[1] : "V3.2",
                    S = h ? h[1] : "aHR0cHM6Ly93ZWIuYWdlc3BhLTAxLmNvbTo4NDQzLw==",
                    C = m ? m[1] : `${o}/vip`,
                    N = g ? g[1] : "",
                    _ = f ? f[1] : "",
                    I = r(),
                    $ = {
                        url: p,
                        wap: "0",
                        ios: "0",
                        host: s,
                        referer: S,
                        time: y
                    },
                    w = n.encrypt(JSON.stringify($)),
                    O = `${s} | ${I} | ${y} | ${A} | ${w}`,
                    J = n.encrypt(O),
                    b = `${C}/Api.php`,
                    R = await req(b, {
                        method: "post",
                        postType: "form",
                        headers: {
                            ...c,
                            Accept: "application/json, text/javascript, */*; q=0.01",
                            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                            origin: o,
                            priority: "u=1, i",
                            "sec-fetch-dest": "empty",
                            "sec-fetch-mode": "cors",
                            "sec-fetch-site": "same-origin",
                            "video-parse-sign": J,
                            "video-parse-time": y,
                            "video-parse-uuid": I,
                            "video-parse-version": A,
                            "x-requested-with": "XMLHttpRequest"
                        },
                        data: {
                            Params: w
                        }
                    });
                let U = {};
                if (U = "string" == typeof R.content ? JSON.parse(R.content) : R.content, 1 !== U.Status) throw new Error("");
                let q = "";
                if (10 === U.Code) {
                    let E = (N + _).replace("viewport", "");
                    q = U.Code + E + U.Appkey + U.Version
                } else q = U.Code + U.Appkey + U.Version;
                let T = md5X(q),
                    k = aesX("AES/CBC/PKCS7", !1, t(U.Data), !0, T.substring(0, 16), T.substring(16, 32), !1),
                    j = JSON.parse(k),
                    P = "";
                return P = 10 === U.Code ? n.decrypt(j.url) : j.url, decodeURIComponent(P)
            } catch (M) {
                return ""
            }
        }(t);
        if (e) return JSON.stringify({
            parse: 0,
            url: e,
            header: {
                "User-Agent": a["User-Agent"]
            }
        })
    } catch (e) {}
    return JSON.stringify({
        parse: 1,
        url: t,
        header: {}
    })
}
export function __jsEvalReturn() {
    return {
        init: n,
        home: l,
        homeVod: o,
        category: i,
        search: s,
        detail: c,
        play: u
    }
}