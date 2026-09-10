/**
 * \u767e\u5ea6\u7f51\u76d8\u5904\u7406\u7c7b 
 * \u63d0\u4f9b\u5206\u4eab\u94fe\u63a5\u89e3\u6790\u3001\u6587\u4ef6\u5217\u8868\u83b7\u53d6\u3001\u64ad\u653e\u94fe\u63a5\u751f\u6210\u529f\u80fd
 * 
 * @module BaiduHandler
 * @author \u4f18\u96c5
 * @since 1.0.0
 */

import { Crypto as CryptoJS } from 'assets://js/lib/cat.js';

// \u5168\u5c40\u8c03\u8bd5\u5f00\u5173
let DEBUG = globalThis.baidu_debug || 0;

/**
 * \u65e5\u5fd7\u8f93\u51fa
 */
function log(tag, message) {
    if (!DEBUG) return;
    console.log(`\u3010\u767e\u5ea6-${tag}\u3011 ${message}`);
}

class BaiduHandler {
    /**
     * \u521d\u59cb\u5316\u767e\u5ea6\u7f51\u76d8\u5904\u7406\u5668
     * \u914d\u7f6e\u6b63\u5219\u8868\u8fbe\u5f0f\u3001\u8bf7\u6c42\u5934\u3001API\u5730\u5740\u7b49\u57fa\u7840\u53c2\u6570
     */
    constructor() {
        // \u767e\u5ea6\u5206\u4eab\u94fe\u63a5\u6b63\u5219\u8868\u8fbe\u5f0f - \u5339\u914d\u6807\u51c6\u5206\u4eab\u94fe\u63a5\u548c\u63d0\u53d6\u5bc6\u7801
        this.regex = /https:\/\/pan\.baidu\.com\/s\/([^?&#]+)(?:\?.*?pwd=([^&]+))?/;
        
        // \u57fa\u7840\u8bf7\u6c42\u5934\u914d\u7f6e
        this.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            'Referer': 'https://pan.baidu.com/',
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6"
        };
        
        // \u767e\u5ea6\u7f51\u76d8API\u57fa\u7840\u5730\u5740
        this.api = 'https://pan.baidu.com';
        
        // \u5e94\u7528ID - \u7528\u4e8eAPI\u8bf7\u6c42\u6807\u8bc6
        this.app_id = 250528;
        
        // \u89c6\u56fe\u6a21\u5f0f - 1\u8868\u793a\u5217\u8868\u89c6\u56fe
        this.view_mode = 1;
        
        // \u6e20\u9053\u6807\u8bc6
        this.channel = 'chunlei';
        
        // \u6e05\u6670\u5ea6\u7c7b\u578b\u5b9a\u4e49
        this.type = ["M3U8_AUTO_4K", "M3U8_AUTO_2K", "M3U8_AUTO_1080", "M3U8_AUTO_720", "M3U8_AUTO_480"];
    }

    /**
     * \u83b7\u53d6\u767e\u5ea6Cookie
     * \u4ece\u5168\u5c40\u53d8\u91cf baidu_cookie \u4e2d\u8bfb\u53d6
     * @returns {string} \u767e\u5ea6Cookie\u5b57\u7b26\u4e32
     */
    get cookie() {
        return globalThis.baidu_cookie || '';
    }
    
    /**
     * \u8bbe\u7f6e\u767e\u5ea6Cookie
     * \u5b58\u50a8\u5230\u5168\u5c40\u53d8\u91cf baidu_cookie \u4e2d
     * @param {string} value - Cookie\u5b57\u7b26\u4e32
     */
    set cookie(value) {
        globalThis.baidu_cookie = value;
    }

    /**
     * \u5ef6\u65f6\u51fd\u6570
     */
    delay(ms) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }

    /**
     * \u7edf\u4e00\u8bf7\u6c42\u51fd\u6570
     * @param {string} url - \u8bf7\u6c42\u5730\u5740
     * @param {object} options - \u8bf7\u6c42\u914d\u7f6e
     * @param {number} retries - \u91cd\u8bd5\u6b21\u6570
     * @param {string} requestType - \u8bf7\u6c42\u7c7b\u578b\u6807\u8bc6
     */
    async request(url, options, retries = 2, requestType = '\u672a\u77e5') {
        log('\u8bf7\u6c42', `\u3010${requestType}\u3011 ${options.method || 'GET'} ${url.substring(0, 100)}${url.length > 100 ? '...' : ''}`);
        if (DEBUG && options.data) {
            const dataStr = JSON.stringify(options.data);
            log('\u8bf7\u6c42\u6570\u636e', `\u3010${requestType}\u3011 ${dataStr.substring(0, 300)}`);
        }
        
        for (let i = 0; i <= retries; i++) {
            try {
                const response = await req(url, options);
                log('\u54cd\u5e94', `\u3010${requestType}\u3011 ${response.code || response.status || 'unknown'}`);
                
                if (response.content) {
                    try {
                        return JSON.parse(response.content);
                    } catch {
                        return { content: response.content, status: response.status };
                    }
                }
                return { status: response.status };
            } catch (error) {
                log('\u9519\u8bef', `\u3010${requestType}\u3011 \u5931\u8d25 (${i + 1}/${retries + 1}): ${error?.message || error}`);
                if (i === retries) {
                    return { 
                        error: true, 
                        code: -1, 
                        message: '\u8bf7\u6c42\u5931\u8d25: ' + (error?.message || '\u672a\u77e5\u9519\u8bef')
                    };
                }
                await this.delay(100);
            }
        }
    }

    /**
     * \u683c\u5f0f\u5316\u6587\u4ef6\u5927\u5c0f
     * \u5c06\u5b57\u8282\u6570\u8f6c\u6362\u4e3a\u4eba\u7c7b\u53ef\u8bfb\u7684\u683c\u5f0f (B, KB, MB, GB, TB)
     * @param {number} bytes - \u6587\u4ef6\u5927\u5c0f\uff08\u5b57\u8282\uff09
     * @returns {string} \u683c\u5f0f\u5316\u540e\u7684\u6587\u4ef6\u5927\u5c0f
     */
    formatFileSize(bytes) {
        if (!bytes) return '0 B';
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let i = 0;
        let size = bytes;
        while (size >= 1024 && i < units.length - 1) {
            size /= 1024;
            i++;
        }
        return size.toFixed(2) + ' ' + units[i];
    }

    /**
     * \u5bf9\u8c61\u8f6c\u67e5\u8be2\u5b57\u7b26\u4e32
     * \u5c06\u5bf9\u8c61\u8f6c\u6362\u4e3aURL\u67e5\u8be2\u53c2\u6570\u683c\u5f0f
     * @param {Object} obj - \u8981\u8f6c\u6362\u7684\u5bf9\u8c61
     * @returns {string} URL\u67e5\u8be2\u5b57\u7b26\u4e32
     */
    objectToQuery(obj) {
        return Object.entries(obj)
            .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
            .join('&');
    }

    /**
     * \u89e3\u6790\u5206\u4eab\u94fe\u63a5
     * \u4ece\u5206\u4eabURL\u4e2d\u63d0\u53d6surl\u548c\u5bc6\u7801
     * @param {string} url - \u767e\u5ea6\u5206\u4eab\u94fe\u63a5
     * @returns {Object|null} \u5305\u542bsurl\u548cpwd\u7684\u5bf9\u8c61\uff0c\u89e3\u6790\u5931\u8d25\u8fd4\u56denull
     */
    getShareData(url) {
        const matches = this.regex.exec(url);
        if (!matches || !matches[1]) return null;
        return { surl: matches[1], pwd: matches[2] || '' };
    }
    
    /**
     * \u83b7\u53d6\u968f\u673a\u5bc6\u94a5(randsk)\u5e76\u8fd4\u56de\u72ec\u7acbCookie
     * \u9a8c\u8bc1\u5206\u4eab\u5bc6\u7801\u5e76\u83b7\u53d6\u8bbf\u95ee\u51ed\u8bc1
     * @param {Object} shareData - \u5206\u4eab\u6570\u636e\uff0c\u5305\u542bsurl\u548cpwd
     * @returns {Object|null} \u5305\u542brandsk\u548ccookie\u7684\u5bf9\u8c61\uff0c\u5931\u8d25\u8fd4\u56denull
     */
    async getRandsk(shareData) {
        // \u6ce8\u610f\uff1averify\u63a5\u53e3\u9700\u8981\u53bb\u6389\u5f00\u5934\u76841
        const shorturl = shareData.surl.replace(/^1+/, '');
        const timestamp = Date.now();
        const baseCookie = this.cookie;
        const verUrl = `${this.api}/share/verify?t=${timestamp}&surl=${shorturl}`;
        
        // \u51c6\u5907\u4e24\u79cd\u6570\u636e\u683c\u5f0f
        const formData = { pwd: shareData.pwd || '' };
        const postData = `pwd=${encodeURIComponent(shareData.pwd || '')}`;
        const dataFormats = [
            { data: formData, type: 'object' },
            { data: postData, type: 'string' }
        ];
        
        for (const format of dataFormats) {
            try {
                const result = await this.request(verUrl, {
                    method: 'POST',
                    headers: {
                        ...this.headers,
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Cookie': baseCookie
                    },
                    data: format.data
                }, 3, '\u9a8c\u8bc1\u5206\u4eab\u5bc6\u7801');
                
                if (!result.error && result.errno === 0 && result.randsk) {
                    const randsk = result.randsk;
                    const BDCLND = `BDCLND=${randsk}`;
                    
                    // \u6784\u5efa\u72ec\u7acbCookie\uff0c\u4e0d\u4fee\u6539\u5168\u5c40
                    let independentCookie;
                    if (!baseCookie.includes('BDCLND')) {
                        independentCookie = baseCookie + (baseCookie ? '; ' : '') + BDCLND;
                    } else {
                        independentCookie = baseCookie.replace(/BDCLND=[^;]+/, BDCLND);
                    }
                    
                    return { randsk, cookie: independentCookie };
                }
            } catch (error) {
                log('Randsk', `${format.type}\u683c\u5f0f\u5931\u8d25: ${error.message}`);
            }
        }
        
        log('Randsk', `\u6240\u6709\u6570\u636e\u683c\u5f0f\u90fd\u5931\u8d25`);
        return null;
    }

    /**
     * \u83b7\u53d6\u5206\u4eab\u6587\u4ef6\u5217\u8868
     * \u83b7\u53d6\u5206\u4eab\u94fe\u63a5\u6839\u76ee\u5f55\u7684\u6587\u4ef6\u548c\u76ee\u5f55\u5217\u8868
     * @param {Object} shareData - \u5206\u4eab\u6570\u636e\uff0c\u5305\u542bsurl\u548cpwd
     * @returns {Object|null} \u5305\u542blist\u3001uk\u3001shareid\u3001title\u3001cookie\u7684\u5bf9\u8c61\uff0c\u5931\u8d25\u8fd4\u56denull
     */
    async getShareList(shareData) {
        const shorturl = shareData.surl.replace(/^1+/, '');
        const randskResult = await this.getRandsk(shareData);
        if (!randskResult) return null;
        
        const headers = { ...this.headers, 'Cookie': randskResult.cookie };
        
        const listUrl = `${this.api}/share/list?` + this.objectToQuery({
            web: 5,
            app_id: this.app_id,
            desc: 1,
            showempty: 0,
            page: 1,
            num: 100,
            order: 'time',
            shorturl: shorturl,
            root: 1,
            view_mode: this.view_mode,
            channel: this.channel,
            clienttype: 0
        });
        
        const listResult = await this.request(listUrl, {
            method: 'GET',
            headers: headers
        }, 3, '\u83b7\u53d6\u5206\u4eab\u5217\u8868');
        
        if (listResult.error || listResult.errno !== 0) {
            log('\u5206\u4eab\u5217\u8868', `\u83b7\u53d6\u5931\u8d25: errno=${listResult.errno}`);
            return null;
        }
        
        return {
            list: listResult.list,
            uk: listResult.uk,
            shareid: listResult.share_id,
            title: listResult.title,
            cookie: randskResult.cookie
        };
    }

    /**
     * \u83b7\u53d6\u6307\u5b9a\u8def\u5f84\u4e0b\u7684\u6587\u4ef6\u5217\u8868
     * \u9012\u5f52\u83b7\u53d6\u5b50\u76ee\u5f55\u4e2d\u7684\u6587\u4ef6
     * @param {string} path - \u76ee\u5f55\u8def\u5f84
     * @param {Object} shareInfo - \u5206\u4eab\u4fe1\u606f\uff0c\u5305\u542buk\u548cshareid
     * @param {Object} shareData - \u5206\u4eab\u6570\u636e\uff0c\u5305\u542bsurl\u548cpwd
     * @returns {Array} \u6587\u4ef6\u5217\u8868
     */
    async getSharepath(path, shareInfo, shareData) {
        const randskResult = await this.getRandsk(shareData);
        if (!randskResult) return [];
        
        const headers = { ...this.headers, 'Cookie': randskResult.cookie };
        
        const dirUrl = `${this.api}/share/list?` + this.objectToQuery({
            is_from_web: true,
            uk: shareInfo.uk,
            shareid: shareInfo.shareid,
            order: 'name',
            desc: 0,
            showempty: 0,
            view_mode: this.view_mode,
            page: 1,
            num: 100,
            dir: path,
            channel: this.channel,
            app_id: this.app_id
        });
        
        const dirResult = await this.request(dirUrl, {
            method: 'GET',
            headers: headers
        }, 3, `\u83b7\u53d6\u76ee\u5f55\u5217\u8868-${path}`);
        
        if (dirResult.error || dirResult.errno !== 0) return [];
        return dirResult.list || [];
    }

    /**
     * \u4ece\u6587\u4ef6\u9879\u4e2d\u63d0\u53d6\u89c6\u9891\u4fe1\u606f
     * \u63d0\u53d6\u6587\u4ef6\u540d\u3001\u8def\u5f84\u3001\u7f29\u7565\u56fe\u3001\u5927\u5c0f\u7b49\u4fe1\u606f
     * @param {Object} item - \u6587\u4ef6\u9879
     * @param {Object} shareInfo - \u5206\u4eab\u4fe1\u606f
     * @param {Object} shareData - \u5206\u4eab\u6570\u636e
     * @returns {Object} \u89c6\u9891\u4fe1\u606f\u5bf9\u8c61
     */
    extractVideoInfo(item, shareInfo, shareData) {
        const fileName = item.server_filename || item.path.split('/').pop();
        
        // \u63d0\u53d6\u7f29\u7565\u56fe
        let thumbnail = '';
        if (item.thumbs) {
            thumbnail = item.thumbs.url || item.thumbs.icon || '';
        } else if (item.icon) {
            thumbnail = item.icon;
        }
        
        return {
            name: fileName,
            path: item.path.replaceAll('#', '\0'),
            uk: shareInfo.uk,
            shareid: shareInfo.shareid,
            fsid: item.fs_id || item.fsid,
            surl: shareData.surl,
            size: item.size,
            thumbnail: thumbnail
        };
    }

    /**
     * \u83b7\u53d6\u5206\u4eab\u4e2d\u7684\u89c6\u9891\u6587\u4ef6\u5217\u8868 - \u4e3b\u5165\u53e3\u65b9\u6cd5
     * \u9012\u5f52\u83b7\u53d6\u5206\u4eab\u4e2d\u7684\u6240\u6709\u89c6\u9891\u6587\u4ef6
     * @param {Object} shareData - \u5206\u4eab\u6570\u636e\uff0c\u5305\u542bsurl\u548cpwd
     * @returns {Array} \u89c6\u9891\u6587\u4ef6\u5217\u8868
     */
    async getFilesByShareUrl(shareData) {
        log('\u6587\u4ef6\u5217\u8868', `\u5f00\u59cb\u83b7\u53d6`);
        if (!shareData || !shareData.surl) return [];
        
        const listResult = await this.getShareList(shareData);
        if (!listResult || !listResult.list) return [];
        
        const shareInfo = {
            uk: listResult.uk,
            shareid: listResult.shareid
        };
        
        let dirs = [];
        let videos = [];
        
        // \u5904\u7406\u6839\u76ee\u5f55\u6587\u4ef6
        listResult.list.map(item => {
            if (item.category === '6' || item.category === 6) {
                dirs.push(item.path);
            }
            if (item.category === '1' || item.category === 1) {
                videos.push(this.extractVideoInfo(item, shareInfo, shareData));
            }
        });
        
        // \u5904\u7406\u5b50\u76ee\u5f55
        if (dirs.length > 0) {
            const results = await Promise.all(dirs.map(async (path) => {
                const dirItems = await this.getSharepath(path, shareInfo, shareData);
                if (dirItems.length === 0) return [];
                
                let subDirs = [];
                let subVideos = [];
                
                dirItems.map(item => {
                    if (item.category === '6' || item.category === 6) {
                        subDirs.push(item.path);
                    }
                    if (item.category === '1' || item.category === 1) {
                        subVideos.push(this.extractVideoInfo(item, shareInfo, shareData));
                    }
                });
                
                // \u5904\u7406\u66f4\u6df1\u5c42\u76ee\u5f55
                if (subDirs.length > 0) {
                    const deeperResults = await Promise.all(subDirs.map(subPath => 
                        this.getSharepath(subPath, shareInfo, shareData)
                    ));
                    
                    deeperResults.forEach(deeperItems => {
                        deeperItems.forEach(item => {
                            if (item.category === '1' || item.category === 1) {
                                subVideos.push(this.extractVideoInfo(item, shareInfo, shareData));
                            }
                        });
                    });
                }
                
                return subVideos;
            }));
            
            results.flat().forEach(video => videos.push(video));
        }
        
        log('\u6587\u4ef6\u5217\u8868', `\u627e\u5230 ${videos.length} \u4e2a\u89c6\u9891`);
        return videos;
    }

    /**
     * \u83b7\u53d6\u7528\u6237UID
     * \u901a\u8fc7\u767e\u5ea6MBD\u63a5\u53e3\u83b7\u53d6\u7528\u6237\u552f\u4e00\u6807\u8bc6
     * @returns {string} \u7528\u6237UID
     */
    async getUid() {
        const headers = { ...this.headers, 'Cookie': this.cookie };
        
        const result = await this.request('https://mbd.baidu.com/userx/v1/info/get?appname=baiduboxapp&fields=%20%20%20%20%20%20%20%20%5B%22bg_image%22,%22member%22,%22uid%22,%22avatar%22,%20%22avatar_member%22%5D&client&clientfrom&lang=zh-cn&tpl&ttt', {
            method: 'GET',
            headers: headers
        }, 3, '\u83b7\u53d6\u7528\u6237UID');
        
        return result.data?.fields?.uid || result.data?.uid || result.uid || '';
    }

    /**
     * SHA1\u54c8\u5e0c\u8ba1\u7b97
     * \u4f7f\u7528CryptoJS\u8fdb\u884cSHA1\u52a0\u5bc6
     * @param {string} message - \u5f85\u52a0\u5bc6\u5b57\u7b26\u4e32
     * @returns {string} SHA1\u54c8\u5e0c\u503c\uff08\u5341\u516d\u8fdb\u5236\uff09
     */
    sha1(message) {
        return CryptoJS.SHA1(message).toString(CryptoJS.enc.Hex);
    }

    /**
     * \u83b7\u53d6\u7b7e\u540d
     * \u7528\u4e8eWeb\u7248\u64ad\u653e\u94fe\u63a5\u7684\u7b7e\u540d\u9a8c\u8bc1
     * @param {Object} shareData - \u5206\u4eab\u6570\u636e\uff0c\u5305\u542bsurl\uff08\u5b8c\u6574surl\uff0c\u5e26\u5f00\u5934\u76841\uff09
     * @returns {Promise<string|null>} \u7b7e\u540d\u5b57\u7b26\u4e32\uff0c\u5931\u8d25\u8fd4\u56denull
     */
    async getSign(shareData) {
        // \u6ce8\u610f\uff1atplconfig\u63a5\u53e3\u9700\u8981\u5b8c\u6574\u7684surl\uff08\u5e26\u5f00\u5934\u76841\uff09
        const url = `${this.api}/share/tplconfig?surl=${shareData.surl}&fields=Espace_info,card_info,sign,timestamp&view_mode=${this.view_mode}&channel=${this.channel}&web=1&app_id=${this.app_id}`;
        const headers = { ...this.headers, 'Cookie': this.cookie };
        const data = await this.request(url, { headers }, 3, '\u83b7\u53d6\u7b7e\u540d');
        
        if (data.error || data.errno !== 0 || !data.data) {
            log('\u7b7e\u540d', `\u83b7\u53d6\u5931\u8d25`);
            return null;
        }
        
        return data.data.sign;
    }

    /**
     * \u83b7\u53d6\u6587\u4ef6\u7684\u76f4\u94fe\u5730\u5740\uff08App\u7248\uff09
     * \u751f\u6210\u767e\u5ea6\u7f51\u76d8App\u63a5\u53e3\u7684\u64ad\u653e\u76f4\u94fe
     * @param {string} path - \u6587\u4ef6\u8def\u5f84
     * @param {string} uk - \u7528\u6237uk
     * @param {string} shareid - \u5206\u4eabID
     * @param {string} fsid - \u6587\u4ef6fsid
     * @param {Object} shareData - \u5206\u4eab\u6570\u636e\uff0c\u5305\u542bsurl\u548cpwd
     * @returns {string|null} \u64ad\u653e\u76f4\u94fe\uff0c\u5931\u8d25\u8fd4\u56denull
     */
    async getAppShareUrl(path, uk, shareid, fsid, shareData) {
        path = path.replaceAll('\0', '#');
        
        const randskResult = await this.getRandsk(shareData);
        if (!randskResult) return null;
        
        const uid = await this.getUid();
        if (!uid) return null;

        // \u6784\u5efaApp\u63a5\u53e3\u8bf7\u6c42\u5934
        const headers = { 
            ...this.headers, 
            'Cookie': randskResult.cookie,
            "User-Agent": 'netdisk;P2SP;2.2.91.136;android-android;'
        };
        
        const devuid = "73CED981D0F186D12BC18CAE1684FFD5|VSRCQTF6W";
        const time = String(Date.now());

        const bdussMatch = randskResult.cookie.match(/BDUSS=(.+?);/);
        if (!bdussMatch) return null;
        
        const BDUSS = bdussMatch[1];

        // \u8ba1\u7b97\u7b7e\u540d
        const rand = this.sha1(
            this.sha1(BDUSS) + 
            uid + 
            "ebrcUYiuxaZv2XGu7KIYKxUrqfnOfpDF" + 
            time + 
            devuid + 
            "11.30.2ae5821440fab5e1a61a025f014bd8972"
        );

        const url = this.api + "/share/list?" + this.objectToQuery({
            shareid, 
            uk, 
            fid: fsid,
            sekey: randskResult.randsk,
            origin: 'dlna',
            devuid,
            clienttype: 1,
            channel: 'android_12_zhao_bd-netdisk_1024266h',
            version: '11.30.2',
            time,
            rand
        });
        
        const result = await this.request(url, {
            method: "GET",
            headers: headers
        }, 3, '\u83b7\u53d6App\u76f4\u94fe');
        
        if (result.error || result.errno !== 0 || !result.list?.length) return null;
        return result.list[0].dlink;
    }

    /**
     * \u83b7\u53d6Web\u7248\u64ad\u653e\u94fe\u63a5
     * \u8fd4\u56de\u4e0d\u540c\u6e05\u6670\u5ea6\u7684\u64ad\u653e\u94fe\u63a5\u6570\u7ec4
     * \u4f7f\u7528\u6d41\u7a0b: \u5148\u901a\u8fc7getFilesByShareUrl\u83b7\u53d6\u89c6\u9891\u4fe1\u606f\uff0c\u7136\u540e\u7528\u5176\u4e2d\u7684uk\u3001shareid\u3001fsid\u548cshareData\u8c03\u7528\u6b64\u65b9\u6cd5
     * 
     * @param {string} path - \u6587\u4ef6\u8def\u5f84\uff08\u652f\u6301\0\u8f6c\u4e49\u7684\u8def\u5f84\uff09
     * @param {string} uk - \u7528\u6237UK
     * @param {string} shareid - \u5206\u4eabID
     * @param {string} fsid - \u6587\u4ef6ID
     * @param {Object} shareData - \u5206\u4eab\u6570\u636e\uff0c\u5305\u542bsurl\uff08\u5b8c\u6574surl\uff0c\u5e26\u5f00\u5934\u76841\uff09
     * @returns {Promise<Array>} \u64ad\u653e\u94fe\u63a5\u6570\u7ec4\uff0c\u6bcf\u4e2a\u5143\u7d20\u5305\u542b{name, url}\uff0cname\u4e3a\u6e05\u6670\u5ea6\u540d\u79f0
     */
    async getWebPlayUrls(path, uk, shareid, fsid, shareData) {
        // \u8fd8\u539f\u88ab\u66ff\u6362\u7684#\u5b57\u7b26
        path = path.replace(/\0/g, '#');
        // \u83b7\u53d6\u7b7e\u540d
        const sign = await this.getSign(shareData);
        if (!sign) return [];
        
        const timestamp = Math.floor(Date.now() / 1000);
        const urls = [];
        
        // \u751f\u6210\u4e0d\u540c\u6e05\u6670\u5ea6\u7684\u64ad\u653e\u94fe\u63a5
        this.type.forEach(type => {
            const urlInfo = {
                name: type.replace('M3U8_AUTO_', ''),
                url: `${this.api}/share/streaming?channel=${this.channel}&uk=${uk}&fid=${fsid}&sign=${sign}&timestamp=${timestamp}&shareid=${shareid}&type=${type}&vip=0&jsToken&isplayer=1&check_blue=1&adToken`
            };
            urls.push(urlInfo);
        });
        
        return urls;
    }
}

export const Baidu = new BaiduHandler();