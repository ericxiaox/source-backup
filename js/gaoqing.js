// \u672c\u8d44\u6e90\u6765\u6e90\u4e8e\u4e92\u8054\u7f51\u516c\u5f00\u6e20\u9053\uff0c\u4ec5\u53ef\u7528\u4e8e\u4e2a\u4eba\u5b66\u4e60\u722c\u866b\u6280\u672f\u3002
// \u4e25\u7981\u5c06\u5176\u7528\u4e8e\u4efb\u4f55\u5546\u4e1a\u7528\u9014\uff0c\u4e0b\u8f7d\u540e\u8bf7\u4e8e 24 \u5c0f\u65f6\u5185\u5220\u9664\uff0c\u641c\u7d22\u7ed3\u679c\u5747\u6765\u81ea\u6e90\u7ad9\uff0c\u672c\u4eba\u4e0d\u627f\u62c5\u4efb\u4f55\u8d23\u4efb\u3002
import {
    Crypto as e
} from "assets://js/lib/cat.js";
let t, n = "https://web.88spa-03.com:8443",
    r = "https://88api.omwjhz.com:18888";
const o = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        Accept: "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        Origin: n,
        Pragma: "no-cache",
        Referer: `${n}`,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="143", "Google Chrome";v="143"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"'
    },
    a = "function" == typeof js2Proxy && "function" == typeof desX && "function" != typeof getProxy;
async function s(e) {}
async function i(e) {
    let n = [{
        type_id: "1",
        type_name: "\u7535\u5f71"
    }, {
        type_id: "2",
        type_name: "\u8fde\u7eed\u5267"
    }, {
        type_id: "3",
        type_name: "\u7efc\u827a"
    }, {
        type_id: "4",
        type_name: "\u52a8\u6f2b"
    }];
    a && n.unshift({
        type_id: "home",
        type_name: "\u9996\u9875"
    });
    try {
        if (!e) return JSON.stringify({
            class: n,
            filters: {}
        });
        if (t) return JSON.stringify({
            class: n,
            filters: t
        });
        const a = `${r}/v1/vod-list-options`,
            s = await req(a, {
                headers: o,
                timeout: 8e3
            });
        let i = {};
        if (s && s.content) {
            let e = "string" == typeof s.content ? JSON.parse(s.content) : s.content;
            const n = e.areas || {},
                r = e.types || {},
                o = e.languages || [];
            let a = [{
                n: "\u5168\u90e8",
                v: "\u5168\u90e8"
            }];
            Array.isArray(o) && o.forEach(e => {
                "\u5168\u90e8" !== e.name && a.push({
                    n: e.name,
                    v: e.name
                })
            });
            let c = [{
                n: "\u5168\u90e8",
                v: ""
            }];
            ["2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012", "2011", "2010"].forEach(e => {
                c.push({
                    n: e,
                    v: e
                })
            });
            let p = [{
                n: "\u5168\u90e8",
                v: "\u5168\u90e8"
            }];
            for (let e = 65; e <= 90; e++) p.push({
                n: String.fromCharCode(e),
                v: String.fromCharCode(e)
            });
            for (let e = 0; e <= 9; e++) p.push({
                n: e.toString(),
                v: e.toString()
            });
            let l = [{
                n: "\u6700\u65b0",
                v: "time"
            }, {
                n: "\u6700\u70ed",
                v: "hot"
            }, {
                n: "\u8bc4\u5206",
                v: "score"
            }];
            const d = {
                1: "\u7535\u5f71",
                2: "\u8fde\u7eed\u5267",
                3: "\u7efc\u827a",
                4: "\u52a8\u6f2b"
            };
            for (const e in d) {
                const t = d[e];
                let o = [],
                    s = [{
                        n: "\u5168\u90e8",
                        v: e
                    }];
                Array.isArray(r[t]) && r[t].forEach(e => {
                    "\u5168\u90e8" !== e.name && s.push({
                        n: e.name,
                        v: e.id.toString()
                    })
                }), o.push({
                    key: "cateId",
                    name: "\u7c7b\u578b",
                    init: e,
                    value: s
                });
                let u = [{
                    n: "\u5168\u90e8",
                    v: "\u5168\u90e8"
                }];
                Array.isArray(n[t]) && n[t].forEach(e => {
                    "\u5168\u90e8" !== e.name && u.push({
                        n: e.name,
                        v: e.name
                    })
                }), o.push({
                    key: "area",
                    name: "\u5730\u533a",
                    init: "\u5168\u90e8",
                    value: u
                }), o.push({
                    key: "lang",
                    name: "\u8bed\u8a00",
                    init: "\u5168\u90e8",
                    value: a
                }), o.push({
                    key: "year",
                    name: "\u5e74\u4efd",
                    init: "",
                    value: c
                }), o.push({
                    key: "letter",
                    name: "\u5b57\u6bcd",
                    init: "\u5168\u90e8",
                    value: p
                }), o.push({
                    key: "orderBy",
                    name: "\u6392\u5e8f",
                    init: "time",
                    value: l
                }), i[e] = o
            }
            t = i
        }
        return JSON.stringify({
            class: n,
            filters: t || {}
        })
    } catch (e) {
        return JSON.stringify({
            class: n,
            filters: {}
        })
    }
}
async function c() {
    try {
        const e = `${r}/v1/home-list`,
            t = await req(e, {
                headers: o,
                timeout: 8e3
            });
        if (!t || !t.content) return JSON.stringify({
            list: []
        });
        let n = "string" == typeof t.content ? JSON.parse(t.content) : t.content,
            a = new Map;
        for (const e in n) Array.isArray(n[e]) && n[e].forEach(e => {
            if (e && e.VodID) {
                const t = e.VodID.toString();
                a.has(t) || a.set(t, {
                    vod_id: t,
                    vod_name: e.VodName,
                    vod_pic: e.VodPic,
                    vod_remarks: e.VodRemarks
                })
            }
        });
        const s = Array.from(a.values());
        return JSON.stringify({
            list: s
        })
    } catch (e) {
        return JSON.stringify({
            list: []
        })
    }
}
async function p(e, t, n, a) {
    try {
        if ("home" === e) {
            let e = JSON.parse(await c());
            return JSON.stringify({
                list: e.list || [],
                page: 1,
                pagecount: 1
            })
        }
        const n = a.cateId ? encodeURIComponent(a.cateId) : e,
            s = "\u5168\u90e8",
            i = a.area ? encodeURIComponent(a.area) : "\u5168\u90e8",
            p = a.lang ? encodeURIComponent(a.lang) : "\u5168\u90e8",
            l = a.year ? encodeURIComponent(a.year) : "",
            d = a.letter ? encodeURIComponent(a.letter) : "\u5168\u90e8",
            u = a.orderBy ? encodeURIComponent(a.orderBy) : "time",
            g = `${r}/v1/vod-list?orderBy=${u}&type=${n}&class=${s}&area=${i}&year=${l}&lang=${p}&letter=${d}&page=${t}`,
            f = await req(g, {
                headers: o,
                timeout: 8e3
            });
        if (!f || !f.content) return JSON.stringify({
            list: [],
            page: parseInt(t),
            pagecount: parseInt(t)
        });
        let y = "string" == typeof f.content ? JSON.parse(f.content) : f.content;
        if (0 !== y.status || !y.data) return JSON.stringify({
            list: [],
            page: parseInt(t),
            pagecount: parseInt(t)
        });
        const m = y.data.map(e => ({
                vod_id: e.VodID.toString(),
                vod_name: e.VodName,
                vod_pic: e.VodPic,
                vod_remarks: e.VodRemarks
            })),
            h = y.qty || 0,
            v = h > 0 ? Math.ceil(h / 60) : parseInt(t);
        return JSON.stringify({
            list: m,
            page: parseInt(t),
            pagecount: v
        })
    } catch (e) {
        return JSON.stringify({
            list: [],
            page: parseInt(t),
            pagecount: parseInt(t)
        })
    }
}
async function l(e, t, n = 1) {
    try {
        const t = encodeURIComponent(e),
            a = `${r}/v1/search?keyword=${t}&cate=undefined&page=${n}`,
            s = await req(a, {
                headers: o,
                timeout: 8e3
            });
        if (!s || !s.content) return JSON.stringify({
            list: [],
            page: parseInt(n),
            pagecount: parseInt(n)
        });
        let i = "string" == typeof s.content ? JSON.parse(s.content) : s.content;
        if (0 !== i.status || !i.data) return JSON.stringify({
            list: [],
            page: parseInt(n),
            pagecount: parseInt(n)
        });
        const c = i.data.map(e => ({
                vod_id: e.VodID.toString(),
                vod_name: e.VodName,
                vod_pic: e.VodPic,
                vod_remarks: e.VodRemarks
            })),
            p = i.qty || 0,
            l = p > 0 ? Math.ceil(p / 60) : parseInt(n);
        return JSON.stringify({
            list: c,
            page: parseInt(n),
            pagecount: l
        })
    } catch (e) {
        return JSON.stringify({
            list: [],
            page: parseInt(n),
            pagecount: parseInt(n)
        })
    }
}
async function d(e) {
    try {
        const t = `${r}/v1/vod-details?id=${e}`,
            n = await req(t, {
                headers: o,
                timeout: 8e3
            });
        if (!n || !n.content) return JSON.stringify({
            list: []
        });
        let a = "string" == typeof n.content ? JSON.parse(n.content) : n.content;
        if (0 !== a.status || !a.vod) return JSON.stringify({
            list: []
        });
        const s = a.vod,
            i = s.VodPlayServer || [],
            c = s.VodPlayUrls || {};
        let p = [],
            l = [];
        i.forEach(e => {
            if (1 === e.Status) {
                const t = e.From,
                    n = e.Show,
                    r = c[t] || [];
                if (r.length > 0) {
                    const e = r.map(e => `${e[0]}$${e[1]}`).join("#");
                    p.push(n), l.push(e)
                }
            }
        });
        const d = p.join("$$$"),
            u = l.join("$$$"),
            g = {
                vod_id: s.VodID.toString(),
                vod_name: s.VodName,
                vod_pic: s.VodPic,
                type_name: a.VodClass ? a.VodClass.TypeName : "",
                vod_year: s.VodYear || "",
                vod_area: s.VodArea || "",
                vod_remarks: s.VodRemarks || "",
                vod_actor: s.VodActor || "",
                vod_director: s.VodDirector || "",
                vod_content: s.VodContent ? s.VodContent.replace(/<\/?[^>]+(>|$)/g, "") : "",
                vod_play_from: d,
                vod_play_url: u
            };
        return JSON.stringify({
            list: [g]
        })
    } catch (e) {
        return JSON.stringify({
            list: []
        })
    }
}
async function u(t, r, a) {
    try {
        const t = /^(https?:)?\/\//i.test(r) ? r : `https://vip.jsjinfu.com:8443/?url=${r}`;
        let a = await async function(t, n) {
            let r = {
                "User-Agent": o["User-Agent"],
                Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "zh-CN,zh;q=0.9",
                "cache-control": "no-cache",
                pragma: "no-cache",
                referer: n,
                "upgrade-insecure-requests": "1"
            };
            try {
                const n = (await req(t, {
                        headers: r
                    })).content,
                    a = h(n, "video_url");
                if (a) return a;
                const s = h(n, "Domain"),
                    i = h(n, "Time"),
                    c = h(n, "Version"),
                    p = h(n, "Vurl"),
                    l = h(n, "Vkey"),
                    d = h(n, "Key"),
                    u = h(n, "Ref"),
                    S = s || "vip.jsjinfu.com";
                if (!(i && p && l && d)) return null;
                const $ = md5X(l);
                let _ = y(d, $),
                    N = g.encryptToBase64(d, _);
                const k = s + S + i + p + d + _;
                let O = m(md5X(k)),
                    C = f.encode(O, "971a0e7224fecb61b1868f1211a6360d"),
                    A = y(C, $),
                    I = g.encryptToBase64(C, A),
                    V = m(md5X(k + C + A)),
                    b = f.encode(V, i + "52bc46dec47a199abc82793bfabe56f6"),
                    J = y(b, $),
                    w = g.encryptToBase64(b, J),
                    U = `${l}-${d}-${C}-${b}`,
                    E = `${_}-${A}-${J}`;
                const D = U + E;
                let R = g.encryptToBase64(D + N + I + w, S + s + i),
                    B = {
                        url: p,
                        wap: "0",
                        ios: "0",
                        host: S,
                        referer: u,
                        time: i,
                        key: d,
                        key1: _,
                        sign: C,
                        sign1: A,
                        token: b,
                        token1: J
                    },
                    X = function(t, n) {
                        let r = e.enc.Latin1.parse(n.substring(0, 16)),
                            o = e.enc.Latin1.parse(n.substring(16, 32));
                        return e.AES.encrypt(e.enc.Base64.stringify(e.enc.Utf8.parse(t)), r, {
                            iv: o,
                            mode: e.mode.CBC,
                            padding: e.pad.Pkcs7
                        }).toString()
                    }(JSON.stringify(B), md5X(R));
                B.ckey = "110#" + e.enc.Base64.stringify(e.enc.Latin1.parse(X));
                let q = function(e) {
                        let t = String(e.time),
                            n = e.key,
                            r = e.key1,
                            o = e.sign1,
                            a = e.token1,
                            s = ["2", "6", "2", "4"],
                            i = t.split("")[s[0]] || "e",
                            c = n.split("")[s[1]] || "t",
                            p = r.split("")[s[2]] || "c",
                            l = o.split("")[o.split("").length - s[3]] || "n",
                            d = a.split(""),
                            u = [];
                        for (let e = 0; 2 * e < d.length; e++) switch (u.push(d[d.length - e - 1]), e < d.length - e - 1 && u.push(a[e]), e) {
                            case 1:
                                u.push(i);
                                break;
                            case 2:
                                u.push(c);
                                break;
                            case 3:
                                u.push(p);
                                break;
                            case 4:
                                u.push(l)
                        }
                        return u.join("")
                    }(B),
                    T = 1024 * i,
                    j = `https://${s}:8443/Api.php?ver=${c}&timestamp=${T}&appkey=${md5X(S+T+c)}`,
                    x = {
                        "User-Agent": o["User-Agent"],
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        Vkey: l,
                        Md5: md5X(D + R + q),
                        Version: c,
                        "Access-Token0": U,
                        "Access-Token1": E,
                        "Access-Token2": R,
                        "Access-Token3": q,
                        Origin: `https://${S}:8443`,
                        Referer: t
                    };
                const M = await req(j, {
                    method: "post",
                    headers: x,
                    data: v(B),
                    postType: "form"
                });
                let P = "string" == typeof M.content ? JSON.parse(M.content) : M.content;
                if (P && 1 === P.Status) {
                    let t = P.Appkey + P.Md5 + P.Version,
                        n = md5X(t),
                        r = e.enc.Latin1.parse(n.substring(0, 16)),
                        o = e.enc.Latin1.parse(n.substring(16, 32)),
                        a = e.AES.decrypt(P.Data, r, {
                            iv: o,
                            mode: e.mode.CBC,
                            padding: e.pad.Pkcs7
                        }),
                        s = JSON.parse(e.enc.Utf8.stringify(a)),
                        i = f.decode(s.url, md5X(S + b));
                    return decodeURIComponent(i)
                }
            } catch (e) {}
            return null
        }(t, `${n}/`);
        if (a) return JSON.stringify({
            parse: 0,
            url: a,
            header: {
                "User-Agent": o["User-Agent"]
            }
        })
    } catch (e) {}
    return JSON.stringify({
        parse: 1,
        url: r,
        header: {}
    })
}
const g = (e => {
        if (!e) throw new Error("");
        const t = (e, t) => {
                const n = e.words,
                    r = e.sigBytes,
                    o = r + 3 >> 2,
                    a = new Array(t ? o + 1 : o);
                for (let e = 0; e < r; e++) a[e >> 2] |= (n[e >> 2] >>> 24 - e % 4 * 8 & 255) << ((3 & e) << 3);
                return t && (a[o] = r), a
            },
            n = (e, t, n, r, o, a) => (n >>> 5 ^ t << 2) + (t >>> 3 ^ n << 4) ^ (e ^ t) + (a[3 & r ^ o] ^ n);
        return {
            encryptToBase64(r, o) {
                if (!r || 0 === r.length) return r;
                const a = t(e.enc.Utf8.parse(r), !0),
                    s = t(e.enc.Utf8.parse(o), !1);
                return e.enc.Base64.stringify((t => {
                    const n = t.length,
                        r = [];
                    for (let e = 0; e < n; e++) {
                        const n = t[e];
                        r[e] = (255 & n) << 24 | (n >>> 8 & 255) << 16 | (n >>> 16 & 255) << 8 | n >>> 24
                    }
                    return e.lib.WordArray.create(r, 4 * n)
                })(((e, t) => {
                    t.length < 4 && (t.length = 4);
                    const r = e.length,
                        o = r - 1;
                    let a, s = e[o],
                        i = 0;
                    for (let c = 0 | Math.floor(6 + 52 / r); c > 0; --c) {
                        i = i + 2654435769 & 4294967295;
                        const r = i >>> 2 & 3;
                        for (let c = 0; c < o; ++c) a = e[c + 1], s = e[c] = e[c] + n(i, a, s, c, r, t) & 4294967295;
                        a = e[0], s = e[o] = e[o] + n(i, a, s, o, r, t) & 4294967295
                    }
                    return e
                })(a, s)))
            }
        }
    })(void 0 !== e ? e : null),
    f = function() {
        const t = () => Math.floor(Date.now() / 1e3),
            n = function(n, r = "DECODE", o = "liangcheng", a = 0) {
                o = md5X(o);
                const s = md5X(o.substring(0, 16)),
                    i = md5X(o.substring(16, 32));
                let c = "";
                if ("DECODE" === r) c = n.substring(0, 4);
                else {
                    const e = md5X((() => {
                        const e = Date.now(),
                            t = Math.floor(e / 1e3);
                        return (e - 1e3 * t) / 1e3 + " " + t
                    })());
                    c = e.substring(e.length - 4)
                }
                const p = e.enc.Utf8.parse(s + md5X(s + c));
                let l = "";
                if ("DECODE" === r) {
                    let r = e.enc.Base64.parse(n.substring(4)),
                        o = e.RC4.decrypt({
                            ciphertext: r
                        }, p);
                    l = e.enc.Latin1.stringify(o);
                    const a = parseInt(l.substring(0, 10), 10),
                        s = 0 === a || a - t() > 0,
                        c = l.substring(10, 26) === md5X(l.substring(26) + i).substring(0, 16);
                    return s && c ? l.substring(26) : ""
                } {
                    a = a ? a + t() : 0;
                    const r = String(a).padStart(10, "0") + md5X(n + i).substring(0, 16) + n;
                    return l = e.RC4.encrypt(e.enc.Latin1.parse(r), p).toString(), c + l.replace(/=/g, "")
                }
            };
        return {
            encode: (e, t, r) => n(e, "ENCODE", t, r).replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "."),
            decode: (e, t) => n(e.replace(/-/g, "+").replace(/_/g, "/").replace(/\./g, "="), "DECODE", t)
        }
    }();

function y(t, n) {
    return e.AES.encrypt(e.enc.Utf8.parse(t), e.enc.Utf8.parse(n), {
        mode: e.mode.ECB
    }).ciphertext.toString()
}

function m(e) {
    return md5X(`17325841932717338791732584194271733878${e}`.replace(/[\-|\,]/g, ""))
}

function h(e, t) {
    const n = e.match(new RegExp(`var\\s+${t}\\s*=\\s*['"]([^'"]+)['"]`));
    return n ? n[1] : null
}

function v(e) {
    let t = {};
    for (let n in e) t[n] = a ? encodeURIComponent(e[n] || "") : e[n];
    return t
}
export function __jsEvalReturn() {
    return {
        init: s,
        home: i,
        homeVod: c,
        category: p,
        search: l,
        detail: d,
        play: u
    }
}