/**
 * \u5938\u514b\u7f51\u76d8\u5904\u7406\u5de5\u5177
 * 
 * \u63d0\u4f9b\u5938\u514b\u7f51\u76d8\u5206\u4eab\u94fe\u63a5\u89e3\u6790\u3001\u6587\u4ef6\u4e0b\u8f7d\u3001\u6d41\u5a92\u4f53\u64ad\u653e\u7b49\u529f\u80fd\u3002
 * 
 * @module QuarkPanHandler
 * @author \u4f18\u96c5
 * @since 1.0.0
 */

// \u5168\u5c40\u8c03\u8bd5\u5f00\u5173
let DEBUG = globalThis.quark_debug || 0;

/**
 * \u65e5\u5fd7\u8f93\u51fa
 */
function log(tag, message) {
    if (!DEBUG) return;
    console.log(`\u3010\u5938\u514b-${tag}\u3011 ${message}`);
}

// \u9519\u8bef\u7801\u5b9a\u4e49
const ERROR_CODES = {
    // \u7a7a\u95f4\u76f8\u5173
    32003: { message: "\u7f51\u76d8\u7a7a\u95f4\u4e0d\u8db3\uff0c\u8bf7\u6e05\u7406\u7a7a\u95f4\u6216\u5f00\u901a\u4f1a\u5458" },
    32008: { message: "\u5b58\u50a8\u914d\u989d\u5df2\u7528\u5b8c" },
    
    // \u8ba4\u8bc1\u76f8\u5173
    31001: { message: "\u672a\u767b\u5f55\u6216Cookie\u5df2\u5931\u6548\uff0c\u8bf7\u91cd\u65b0\u83b7\u53d6Cookie" },
    31002: { message: "\u767b\u5f55\u6001\u5df2\u8fc7\u671f\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55" },
    32004: { message: "Cookie\u5df2\u5931\u6548\uff0c\u8bf7\u91cd\u65b0\u83b7\u53d6" },
    32011: { message: "\u767b\u5f55\u6001\u5df2\u8fc7\u671f" },
    32012: { message: "\u8ba4\u8bc1\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5Cookie" },
    32014: { message: "\u8d26\u53f7\u5f02\u5e38\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55" },
    
    // \u9650\u6d41\u76f8\u5173
    32001: { message: "\u8bf7\u6c42\u8fc7\u4e8e\u9891\u7e41\uff0c\u8bf7\u7a0d\u540e\u518d\u8bd5" },
    32002: { message: "\u64cd\u4f5c\u9891\u7387\u8fc7\u9ad8" },
    
    // \u6587\u4ef6\u76f8\u5173
    32005: { message: "\u6587\u4ef6\u4e0d\u5b58\u5728" },
    32006: { message: "\u6587\u4ef6\u5df2\u88ab\u5220\u9664" },
    32007: { message: "\u6587\u4ef6\u683c\u5f0f\u4e0d\u652f\u6301" },
    
    // \u5206\u4eab\u76f8\u5173
    32009: { message: "\u5206\u4eab\u94fe\u63a5\u5df2\u5931\u6548" },
    32010: { message: "\u63d0\u53d6\u7801\u9519\u8bef" },
    32013: { message: "\u5206\u4eab\u6587\u4ef6\u5df2\u88ab\u5220\u9664" }
};

/**
 * \u5938\u514b\u7f51\u76d8\u5904\u7406\u7c7b
 */
class QuarkHandler {
    constructor() {
        // \u5938\u514b\u5206\u4eab\u94fe\u63a5\u6b63\u5219\u8868\u8fbe\u5f0f - \u5339\u914d\u6807\u51c6\u5206\u4eab\u94fe\u63a5\u548c\u63d0\u53d6\u5bc6\u7801
        this.regex = /https:\/\/pan\.quark\.cn\/s\/([^?&#]+)(?:\?.*?pwd=([^&]+))?/;
        // \u8bf7\u6c42\u53c2\u6570
        this.pr = 'pr=ucpro&fr=pc';
        // \u57fa\u7840\u8bf7\u6c42\u5934
        this.baseHeader = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/2.5.20 Chrome/100.0.4896.160 Electron/18.3.5.4-b478491100 Safari/537.36 Channel/pckk_other_ch',
            'Referer': 'https://pan.quark.cn',
            'Content-Type': 'application/json'
        };
        // API\u57fa\u7840URL
        this.apiUrl = 'https://drive.quark.cn/1/clouddrive/';
        // \u5206\u4eab\u4ee4\u724c\u7f13\u5b58
        this.shareTokenCache = {};
        // \u4fdd\u5b58\u76ee\u5f55\u540d\u79f0
        this.saveDirName = 'drpy';
        // \u4fdd\u5b58\u76ee\u5f55ID
        this.saveDirId = null;
        // \u5b57\u5e55\u6587\u4ef6\u6269\u5c55\u540d
        this.subtitleExts = ['.srt', '.ass', '.scc', '.stl', '.ttml'];
        // \u89c6\u9891\u6587\u4ef6\u6269\u5c55\u540d
        this.videoExts = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.ts', '.m3u8'];
        // \u89c6\u9891\u6269\u5c55\u540d\u5f00\u5173\uff081=\u542f\u7528\u5224\u65ad\uff0c0=\u7981\u7528\uff09
        this.videoExtsEnabled = 0;
        
        // Cookie\u5b58\u50a8
        this._cookie = '';
        
        // \u4e0a\u6b21\u5237\u65b0\u65f6\u95f4
        this.lastRefreshTime = 0;
        this.refreshInterval = 1 * 24 * 60 * 60 * 1000;
        
        // \u5237\u65b0\u9501
        this._isRefreshing = false;
        this._refreshPromise = null;
        
        // \u64ad\u653e\u5730\u5740\u4e34\u65f6\u7f13\u5b58\uff0820\u5206\u949f\uff09
        this.urlCache = {};
        this.cacheTTL = 20 * 60 * 1000;
    }

    /**
     * \u83b7\u53d6Cookie
     */
    get cookie() {
        if (this._cookie) return this._cookie;
        if (globalThis.quark_cookie) this._cookie = globalThis.quark_cookie;
        return this._cookie;
    }

    /**
     * \u8bbe\u7f6eCookie
     */
    set cookie(value) {
        this._cookie = value || '';
        if (value) globalThis.quark_cookie = value;
    }

    /**
     * \u83b7\u53d6\u8bf7\u6c42\u5934
     */
    getHeaders() {
        return { ...this.baseHeader, Cookie: this.cookie };
    }
    
    /**
     * \u5ef6\u65f6\u51fd\u6570
     */
    delay(ms) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }

    /**
     * \u83b7\u53d6\u7f13\u5b58\u7684\u64ad\u653e\u5730\u5740
     */
    getCachedUrl(shareId, fileId) {
        const cacheKey = `${shareId}_${fileId}`;
        const cached = this.urlCache[cacheKey];
        if (cached && (Date.now() - cached.timestamp) < this.cacheTTL) {
            return cached.urls;
        }
        if (cached) delete this.urlCache[cacheKey];
        return null;
    }

    /**
     * \u8bbe\u7f6e\u7f13\u5b58\u7684\u64ad\u653e\u5730\u5740
     */
    setCachedUrl(shareId, fileId, urls) {
        const cacheKey = `${shareId}_${fileId}`;
        this.urlCache[cacheKey] = { urls: urls, timestamp: Date.now() };
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
                        code: 31001, 
                        message: ERROR_CODES[31001]?.message || '\u672a\u767b\u5f55\u6216Cookie\u5df2\u5931\u6548\uff0c\u8bf7\u91cd\u65b0\u83b7\u53d6Cookie' 
                    };
                }
                await this.delay(100);
            }
        }
    }

    /**
     * \u786e\u4fddCookie\u6709\u6548
     */
    async ensureValidCookie() {
        const CACHE_TIME = 1 * 24 * 60 * 60 * 1000;
        const now = Date.now();
        const timeSinceLastRefresh = now - this.lastRefreshTime;
        
        const needRefresh = () => {
            if (this.lastRefreshTime === 0) return true;
            if (timeSinceLastRefresh >= CACHE_TIME) return true;
            if (!this.cookie || !this.cookie.includes('__puus=')) return true;
            return false;
        };
        
        if (!needRefresh()) {
            return true;
        }
        
        log('Cookie', `\u5f00\u59cb\u5237\u65b0...`);
        const originalCookie = this.cookie;
        const success = await this.refreshQuarkCookie();
        
        if (success && this.cookie && this.cookie.includes('__puus=')) {
            this.lastRefreshTime = now;
            log('Cookie', `\u5237\u65b0\u6210\u529f`);
            return true;
        }
        
        this.cookie = originalCookie;
        if (originalCookie && originalCookie.includes('__puus=')) {
            return true;
        }
        
        log('Cookie', `\u65e0\u6548`);
        return false;
    }

    /**
     * \u5237\u65b0\u5938\u514bCookie
     */
    async refreshQuarkCookie() {
        if (this._isRefreshing) return await this._refreshPromise;
        
        this._isRefreshing = true;
        this._refreshPromise = (async () => {
            if (!this.cookie) return false;
            
            try {
                const url = `${this.apiUrl}file/sort?pr=ucpro&fr=pc&uc_param_str=&pdir_fid=0&_page=1&_size=50&_fetch_total=1&_fetch_sub_dirs=0&_sort=file_type:asc,updated_at:desc`;
                const resp = await req(url, {
                    method: "GET",
                    headers: {
                        "User-Agent": this.baseHeader['User-Agent'],
                        Origin: 'https://pan.quark.cn',
                        Referer: 'https://pan.quark.cn/',
                        Cookie: this.cookie
                    }
                });
                
                const setCookie = resp.headers?.['set-cookie'] || resp.headers?.['Set-Cookie'];
                if (setCookie) {
                    this.cookie = this.mergeCookies(this.cookie, setCookie);
                    return true;
                }
                return false;
            } catch (error) {
                return false;
            }
        })();
        
        try {
            return await this._refreshPromise;
        } finally {
            this._isRefreshing = false;
            this._refreshPromise = null;
        }
    }

    /**
     * \u5408\u5e76Cookie
     */
    mergeCookies(oldCookie, setCookie) {
        const oldCookies = {};
        if (oldCookie) {
            oldCookie.split(';').forEach(part => {
                const trimmed = part.trim();
                if (trimmed) {
                    const eqIndex = trimmed.indexOf('=');
                    if (eqIndex > 0) {
                        oldCookies[trimmed.substring(0, eqIndex)] = trimmed.substring(eqIndex + 1);
                    }
                }
            });
        }
        
        const cookieArray = Array.isArray(setCookie) ? setCookie : [setCookie];
        for (const item of cookieArray) {
            const cookiePart = item.split(';')[0].trim();
            const eqIndex = cookiePart.indexOf('=');
            if (eqIndex > 0) {
                oldCookies[cookiePart.substring(0, eqIndex)] = cookiePart.substring(eqIndex + 1);
            }
        }
        
        return Object.entries(oldCookies).map(([key, value]) => `${key}=${value}`).join('; ');
    }

    /**
     * \u89e3\u6790\u5206\u4eab\u94fe\u63a5
     * \u4ece\u5206\u4eabURL\u4e2d\u63d0\u53d6shareId\u548c\u5bc6\u7801
     * @param {string} url - \u5938\u514b\u5206\u4eab\u94fe\u63a5
     * @returns {Object|null} \u5305\u542bshareId\u3001folderId\u3001sharePwd\u7684\u5bf9\u8c61\uff0c\u89e3\u6790\u5931\u8d25\u8fd4\u56denull
     */
    getShareData(url) {
        const matches = this.regex.exec(url);
        if (!matches || !matches[1]) return null;
        
        let shareId = matches[1];
        if (shareId.indexOf("?") > 0) shareId = shareId.split('?')[0];
        const passCode = matches[2] || '';
        
        return { shareId: shareId, folderId: '0', sharePwd: passCode };
    }

    /**
     * \u521d\u59cb\u5316\u5938\u514b
     */
    async initQuark(db, cfg) {
        if (cfg?.quark_cookie) this.cookie = cfg.quark_cookie;
        if (cfg?.quark_videoExtsEnabled !== undefined) this.videoExtsEnabled = cfg.quark_videoExtsEnabled;
        if (this.lastRefreshTime === 0) this.lastRefreshTime = Date.now();
        await this.ensureValidCookie();
        log('\u521d\u59cb\u5316', `\u5b8c\u6210, videoExtsEnabled=${this.videoExtsEnabled}`);
    }

    /**
     * \u6700\u957f\u516c\u5171\u5b50\u5e8f\u5217
     */
    lcs(str1, str2) {
        if (!str1 || !str2) return { length: 0, sequence: '', offset: 0 };
        let sequence = '';
        const str1Length = str1.length, str2Length = str2.length;
        const num = Array(str1Length).fill().map(() => Array(str2Length).fill(0));
        let maxlen = 0, lastSubsBegin = 0, thisSubsBegin = null;
        for (let i = 0; i < str1Length; i++) {
            for (let j = 0; j < str2Length; j++) {
                if (str1[i] === str2[j]) {
                    num[i][j] = (i === 0 || j === 0) ? 1 : 1 + num[i - 1][j - 1];
                    if (num[i][j] > maxlen) {
                        maxlen = num[i][j];
                        thisSubsBegin = i - num[i][j] + 1;
                        if (lastSubsBegin === thisSubsBegin) {
                            sequence += str1[i];
                        } else {
                            lastSubsBegin = thisSubsBegin;
                            sequence = str1.substr(lastSubsBegin, i + 1 - lastSubsBegin);
                        }
                    }
                }
            }
        }
        return { length: maxlen, sequence: sequence, offset: thisSubsBegin };
    }

    /**
     * \u67e5\u627e\u6700\u4f73\u5339\u914d
     */
    findBestLCS(mainItem, targetItems) {
        const results = [];
        let bestMatchIndex = 0;
        for (let i = 0; i < targetItems.length; i++) {
            const currentLCS = this.lcs(mainItem.name || mainItem.file_name, targetItems[i].name || targetItems[i].file_name);
            results.push({ target: targetItems[i], lcs: currentLCS });
            if (currentLCS.length > results[bestMatchIndex].lcs.length) bestMatchIndex = i;
        }
        return { allLCS: results, bestMatch: results[bestMatchIndex], bestMatchIndex: bestMatchIndex };
    }

    /**
     * \u683c\u5f0f\u5316\u6587\u4ef6\u5927\u5c0f
     */
    formatFileSize(bytes) {
        if (!bytes || bytes == 0) return '0 B';
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let i = 0, size = bytes;
        while (size >= 1024 && i < units.length - 1) { size /= 1024; i++; }
        return size.toFixed(2) + ' ' + units[i];
    }

    /**
     * \u6e05\u7406\u4fdd\u5b58\u76ee\u5f55
     */
    async clearSaveDir() {
        if (!this.saveDirId) return { success: true };
        
        const url = `${this.apiUrl}file/sort?pdir_fid=${this.saveDirId}&_page=1&_size=200&_sort=file_type:asc,updated_at:desc&${this.pr}`;
        const listData = await this.request(url, { method: 'GET', headers: this.getHeaders() }, 3, '\u6e05\u7406\u76ee\u5f55-\u83b7\u53d6\u5217\u8868');
        
        if (listData.code && listData.code !== 200 && listData.code !== 0) {
            log('\u6e05\u7406\u76ee\u5f55', `\u5931\u8d25: code=${listData.code}`);
            return { error: true, code: listData.code, message: ERROR_CODES[listData.code]?.message || '\u83b7\u53d6\u76ee\u5f55\u6587\u4ef6\u5217\u8868\u5931\u8d25' };
        }
        
        if (listData.data?.list?.length > 0) {
            const deleteUrl = `${this.apiUrl}file/delete?${this.pr}`;
            const deleteResult = await this.request(deleteUrl, {
                method: 'POST',
                data: { action_type: 2, filelist: listData.data.list.map(v => v.fid), exclude_fids: [] },
                headers: this.getHeaders()
            }, 3, '\u6e05\u7406\u76ee\u5f55-\u5220\u9664\u6587\u4ef6');
            
            if (deleteResult.code && deleteResult.code !== 200 && deleteResult.code !== 0) {
                log('\u6e05\u7406\u76ee\u5f55', `\u5220\u9664\u5931\u8d25: code=${deleteResult.code}`);
                return { error: true, code: deleteResult.code, message: ERROR_CODES[deleteResult.code]?.message || '\u6e05\u7406\u76ee\u5f55\u5931\u8d25' };
            }
        }
        
        return { success: true };
    }

    /**
     * \u521b\u5efa\u4fdd\u5b58\u76ee\u5f55
     */
    async createSaveDir(clean) {
        if (this.saveDirId) {
            if (clean) {
                const clearResult = await this.clearSaveDir();
                if (clearResult && clearResult.error) return clearResult;
            }
            return { success: true, dirId: this.saveDirId };
        }
        
        const url = `${this.apiUrl}file/sort?pdir_fid=0&_page=1&_size=200&_sort=file_type:asc,updated_at:desc&${this.pr}`;
        const listData = await this.request(url, { method: 'GET', headers: this.getHeaders() }, 3, '\u521b\u5efa\u76ee\u5f55-\u83b7\u53d6\u6839\u76ee\u5f55');
        
        if (listData.code && listData.code !== 200 && listData.code !== 0) {
            const errorMsg = ERROR_CODES[listData.code]?.message || listData.message || '\u83b7\u53d6\u76ee\u5f55\u5217\u8868\u5931\u8d25';
            log('\u76ee\u5f55', `\u83b7\u53d6\u5931\u8d25: code=${listData.code}`);
            return { error: true, code: listData.code, message: errorMsg };
        }
        
        if (listData.message && listData.code !== 200 && listData.code !== 0) {
            return { error: true, code: listData.code || -1, message: listData.message };
        }
        
        if (listData.data?.list) {
            for (const item of listData.data.list) {
                if (item.file_name === this.saveDirName && item.dir === true) {
                    this.saveDirId = item.fid;
                    if (clean) {
                        const clearResult = await this.clearSaveDir();
                        if (clearResult && clearResult.error) return clearResult;
                    }
                    return { success: true, dirId: this.saveDirId };
                }
            }
        }
    
        if (!this.saveDirId) {
            const createUrl = `${this.apiUrl}file?${this.pr}`;
            const create = await this.request(createUrl, {
                method: 'POST',
                data: { pdir_fid: '0', file_name: this.saveDirName, dir_path: '', dir_init_lock: false },
                headers: this.getHeaders()
            }, 3, '\u521b\u5efa\u76ee\u5f55-\u65b0\u5efa\u76ee\u5f55');
            
            if (create.code && create.code !== 200 && create.code !== 0) {
                const errorMsg = ERROR_CODES[create.code]?.message || create.message || '\u521b\u5efa\u76ee\u5f55\u5931\u8d25';
                log('\u76ee\u5f55', `\u521b\u5efa\u5931\u8d25: code=${create.code}`);
                return { error: true, code: create.code, message: errorMsg };
            }
            
            if (create.data?.fid) {
                this.saveDirId = create.data.fid;
                log('\u76ee\u5f55', `\u521b\u5efa\u6210\u529f\uff0cID: ${this.saveDirId}`);
                return { success: true, dirId: this.saveDirId };
            }
        }
        
        return { error: true, code: -1, message: '\u521b\u5efa\u4fdd\u5b58\u76ee\u5f55\u5931\u8d25' };
    }

    /**
     * \u83b7\u53d6\u5206\u4eab\u4ee4\u724c
     */
    async getShareToken(shareData) {
        if (!this.shareTokenCache[shareData.shareId]) {
            const url = `${this.apiUrl}share/sharepage/token?${this.pr}`;
            const result = await this.request(url, {
                method: 'POST',
                data: { pwd_id: shareData.shareId, passcode: shareData.sharePwd || '' },
                headers: this.getHeaders()
            }, 3, '\u83b7\u53d6\u5206\u4eab\u4ee4\u724c');
            if (result.data?.stoken) {
                this.shareTokenCache[shareData.shareId] = result.data;
            } else {
                log('\u5206\u4eab\u4ee4\u724c', `\u83b7\u53d6\u5931\u8d25: ${shareData.shareId}`);
            }
        }
    }

    /**
     * \u901a\u8fc7\u5206\u4eab\u94fe\u63a5\u83b7\u53d6\u6587\u4ef6\u5217\u8868
     */
    async getFilesByShareUrl(shareInfo) {
        log('\u6587\u4ef6\u5217\u8868', `\u5f00\u59cb\u83b7\u53d6`);
        await this.ensureValidCookie();
        
        const shareData = typeof shareInfo === 'string' ? this.getShareData(shareInfo) : shareInfo;
        if (!shareData) return [];
        
        await this.getShareToken(shareData);
        if (!this.shareTokenCache[shareData.shareId]) return [];
        
        const videos = [];
        const subtitles = [];
        
        const listFile = async (shareId, folderId, page = 1) => {
            const prePage = 200;
            const url = `${this.apiUrl}share/sharepage/detail?pwd_id=${shareId}&stoken=${encodeURIComponent(this.shareTokenCache[shareId].stoken)}&pdir_fid=${folderId}&force=0&_page=${page}&_size=${prePage}&_sort=file_type:asc,file_name:asc&${this.pr}`;
            const listData = await this.request(url, { method: 'GET', headers: this.getHeaders() }, 3, `\u83b7\u53d6\u6587\u4ef6\u5217\u8868-${folderId}-p${page}`);
            
            if (!listData.data?.list) return;
            
            const items = listData.data.list;
            const subDir = [];
            
            for (const item of items) {
                const fileName = item.file_name || '';
                if (item.dir === true) {
                    subDir.push(item);
                } else if (item.file === true && item.size >= 1024 * 1024 * 5) {
                    // \u5224\u65ad\u662f\u5426\u4e3a\u89c6\u9891\u6587\u4ef6
                    let isVideo = false;
                    
                    // \u5982\u679c\u542f\u7528\u89c6\u9891\u6269\u5c55\u540d\u5224\u65ad
                    if (this.videoExtsEnabled === 1) {
                        const isVideoExt = this.videoExts.some(ext => fileName.toLowerCase().endsWith(ext));
                        isVideo = item.obj_category === 'video' || isVideoExt;
                    } else {
                        // \u7981\u7528\u6269\u5c55\u540d\u5224\u65ad\uff0c\u53ea\u4f9d\u8d56\u5938\u514b\u5206\u7c7b
                        isVideo = item.obj_category === 'video';
                    }
                    
                    if (isVideo) {
                        item.stoken = this.shareTokenCache[shareData.shareId].stoken;
                        item.formatted_size = this.formatFileSize(item.size);
                        item.thumbnail = item.thumbnail || item.big_thumbnail || '';
                        item.file_type = 'video';
                        videos.push(item);
                    }
                } else if (item.type === 'file' && this.subtitleExts.some(x => fileName.endsWith(x))) {
                    subtitles.push(item);
                }
            }
            
            if (page < Math.ceil(listData.metadata?._total / prePage)) {
                await listFile(shareId, folderId, page + 1);
            }
            for (const dir of subDir) {
                await listFile(shareId, dir.fid);
            }
        };
        
        await listFile(shareData.shareId, shareData.folderId);
        
        if (subtitles.length > 0) {
            videos.forEach(item => {
                const matchSubtitle = this.findBestLCS(item, subtitles);
                if (matchSubtitle.bestMatch) item.subtitle = matchSubtitle.bestMatch.target;
            });
        }
        
        log('\u6587\u4ef6\u5217\u8868', `\u627e\u5230 ${videos.length} \u4e2a\u89c6\u9891`);
        return videos;
    }

    /**
     * \u4fdd\u5b58\u6587\u4ef6\u5230\u4e2a\u4eba\u7f51\u76d8
     */
    async saveDirect(shareId, stoken, fileId, fileToken) {
        const dirResult = await this.createSaveDir(false);
        if (dirResult.error) {
            return { error: true, code: dirResult.code, message: dirResult.message };
        }
        
        if (!stoken) {
            await this.getShareToken({ shareId });
            if (!this.shareTokenCache[shareId]) {
                return { error: true, code: -2, message: '\u83b7\u53d6\u5206\u4eab\u4ee4\u724c\u5931\u8d25' };
            }
            stoken = this.shareTokenCache[shareId].stoken;
        }
        
        const saveUrl = `${this.apiUrl}share/sharepage/save?${this.pr}`;
        const saveResult = await this.request(saveUrl, {
            method: 'POST',
            data: {
                fid_list: [fileId],
                fid_token_list: [fileToken],
                to_pdir_fid: this.saveDirId,
                pwd_id: shareId,
                stoken: stoken,
                pdir_fid: '0',
                scene: 'link'
            },
            headers: this.getHeaders()
        }, 3, '\u4fdd\u5b58\u6587\u4ef6');
        
        // \u68c0\u67e5\u9519\u8bef
        if (saveResult.code && saveResult.code !== 200 && saveResult.code !== 0) {
            log('\u4fdd\u5b58', `\u5931\u8d25: code=${saveResult.code}`);
            return { error: true, code: saveResult.code, message: ERROR_CODES[saveResult.code]?.message || '\u4fdd\u5b58\u6587\u4ef6\u5931\u8d25' };
        }
        
        if (saveResult.data?.task_resp?.code) {
            return { error: true, code: saveResult.data.task_resp.code, message: saveResult.data.task_resp.message || '\u4fdd\u5b58\u6587\u4ef6\u5931\u8d25' };
        }
        
        if (saveResult.data?.task_id) {
            if (saveResult.data.task_resp?.data?.save_as?.save_as_top_fids?.length > 0) {
                return saveResult.data.task_resp.data.save_as.save_as_top_fids[0];
            }
            for (let retry = 0; retry < 10; retry++) {
                await this.delay(1000);
                const taskUrl = `${this.apiUrl}task?task_id=${saveResult.data.task_id}&retry_index=${retry}&${this.pr}`;
                const taskResult = await this.request(taskUrl, { method: 'GET', headers: this.getHeaders() }, 3, `\u67e5\u8be2\u4fdd\u5b58\u4efb\u52a1-${retry+1}`);
                if (taskResult.code && taskResult.code !== 200 && taskResult.code !== 0) {
                    return { error: true, code: taskResult.code, message: ERROR_CODES[taskResult.code]?.message || '\u67e5\u8be2\u4efb\u52a1\u72b6\u6001\u5931\u8d25' };
                }
                if (taskResult.data?.save_as?.save_as_top_fids?.length > 0) {
                    return taskResult.data.save_as.save_as_top_fids[0];
                }
            }
        }
        
        return { error: true, code: -3, message: '\u4fdd\u5b58\u6587\u4ef6\u8d85\u65f6\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5' };
    }

    /**
     * \u83b7\u53d6\u76f4\u64ad\u8f6c\u7801\u64ad\u653e\u5730\u5740
     */
    async getLiveTranscoding(shareId, stoken, fileId, fileToken) {
        // \u5148\u68c0\u67e5\u7f13\u5b58
        const cacheKey = `${shareId}_${fileId}_transcoding`;
        const cachedResult = this.urlCache[cacheKey];
        if (cachedResult && (Date.now() - cachedResult.timestamp) < this.cacheTTL) {
            return cachedResult.urls;
        }
        
        try {
            // \u8f6c\u5b58\u6587\u4ef6
            const saveFileId = await this.saveDirect(shareId, stoken, fileId, fileToken);
            if (!saveFileId || saveFileId.error) {
                log('\u8f6c\u7801', `\u8f6c\u5b58\u5931\u8d25: ${saveFileId?.message || '\u672a\u77e5\u9519\u8bef'}`);
                return null;
            }
            
            // \u8bf7\u6c42\u8f6c\u7801\u753b\u8d28
            const url = `${this.apiUrl}file/v2/play?${this.pr}`;
            const result = await this.request(url, {
                method: 'POST',
                data: {
                    fid: saveFileId,
                    resolutions: 'normal,low,high,super,2k,4k',
                    supports: 'fmp4'
                },
                headers: this.getHeaders()
            }, 3, '\u83b7\u53d6\u8f6c\u7801\u5730\u5740');
            
            const videoList = result.data?.video_list || null;
            if (videoList && videoList.length > 0) {
                // \u7f13\u5b58\u64ad\u653e\u5730\u5740
                this.urlCache[cacheKey] = { urls: videoList, timestamp: Date.now() };
                
                // \u5f02\u6b65\u5220\u9664\u4e34\u65f6\u6587\u4ef6
                this.delay(3000).then(() => {
                    this.deleteFile(saveFileId).catch(e => {});
                });
                
                return videoList;
            } else {
                return null;
            }
        } catch (error) {
            log('\u8f6c\u7801', `\u5f02\u5e38: ${error.message}`);
            return null;
        }
    }

    /**
     * \u5220\u9664\u6587\u4ef6
     */
    async deleteFile(fileId) {
        if (!fileId) return;
        const deleteUrl = `${this.apiUrl}file/delete?${this.pr}`;
        await this.request(deleteUrl, {
            method: 'POST',
            data: { action_type: 2, filelist: [fileId], exclude_fids: [] },
            headers: this.getHeaders()
        }, 3, '\u5220\u9664\u4e34\u65f6\u6587\u4ef6');
    }

    /**
     * \u83b7\u53d6\u4e0b\u8f7d\u4ee4\u724c
     */
    async getToken() {
        let t = Math.floor(Date.now() / 1e3);
        let data = {
            "conversation_id": "300000" + t,
            "conversation_type": 3,
            "msg_id": t + "000"
        };
        
        const headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/3.23.2 Chrome/112.0.5615.165 Electron/24.1.3.8 Safari/537.36 Channel/pckk_other_ch',
            'Content-Type': 'application/json',
            'origin': 'https://pan.quark.cn',
            'referer': 'https://pan.quark.cn/'
        };
        
        const response = await req('https://drive-social-api.quark.cn/1/clouddrive/chat/conv/file/acquire_dl_token?pr=ucpro&fr=pc&sys=darwin&ve=3.19', {
            method: 'POST',
            headers: { ...headers, 'Cookie': this.cookie },
            data: data
        });
        if (response.code == 200 && response.content) {
            const result = JSON.parse(response.content);
            return result.data?.token;
        }
        return null;
    }

    /**
     * \u83b7\u53d6\u65e0\u9650\u753b\u8d28\u94fe\u63a5
     */
    async getUrl(shareId, stoken, fileId, fileToken) {
        const token = await this.getToken();
        if (!token) return null;
        
        let data = {
            "fids": [fileId],
            "fids_token": [fileToken],
            "pwd_id": shareId,
            "stoken": stoken,
            "speedup_session": "",
            "token": token
        };
        
        const headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/3.20.0 Chrome/112.0.5615.165 Electron/24.1.3.8 Safari/537.36 Channel/pckk_other_ch',
            'Content-Type': 'application/json'
        };
        
        const response = await req('https://drive-pc.quark.cn/1/clouddrive/file/download?pr=ucpro&fr=pc', {
            method: 'POST',
            headers: { ...headers, 'Cookie': this.cookie },
            data: data
        });
        
        if (response.code == 200 && response.content) {
            const result = JSON.parse(response.content);
            if (result.data && Array.isArray(result.data)) {
                return result.data.map(item => ({
                    name: item.video_max_resolution || '\u539f\u753b',
                    url: item.download_url
                }));
            }
        }
        return null;
    }

    /**
     * \u83b7\u53d6\u4e0b\u8f7d\u94fe\u63a5
     */
    async getDownload(shareId, stoken, fileId, fileToken, clean = false) {
        // \u5148\u68c0\u67e5\u7f13\u5b58
        const cachedResult = this.getCachedUrl(shareId, fileId);
        if (cachedResult) return cachedResult;
        
        await this.ensureValidCookie();
        
        const dirResult = await this.createSaveDir(clean);
        if (dirResult.error) {
            return { error: true, code: dirResult.code, message: dirResult.message };
        }
        
        const saveFileId = await this.saveDirect(shareId, stoken, fileId, fileToken);
        
        // \u68c0\u67e5\u4fdd\u5b58\u662f\u5426\u5931\u8d25\uff0c\u76f4\u63a5\u8fd4\u56de saveDirect \u7684\u9519\u8bef\u4fe1\u606f
        if (saveFileId && saveFileId.error) {
            return saveFileId;
        }
        
        if (!saveFileId) {
            return {
                error: true,
                code: -1,
                message: '\u6587\u4ef6\u8f6c\u5b58\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5\u5206\u4eab\u94fe\u63a5\u662f\u5426\u6709\u6548'
            };
        }
        
        const url = `${this.apiUrl}file/download?${this.pr}`;
        const result = await this.request(url, {
            method: 'POST',
            data: { fids: [saveFileId] },
            headers: this.getHeaders()
        }, 3, '\u83b7\u53d6\u4e0b\u8f7d\u94fe\u63a5');
        
        // \u68c0\u67e5\u9519\u8bef\u7801
        if (result.code && result.code !== 200 && result.code !== 0) {
            log('\u4e0b\u8f7d', `\u5931\u8d25: code=${result.code}`);
            return {
                error: true,
                code: result.code,
                message: ERROR_CODES[result.code]?.message || '\u83b7\u53d6\u4e0b\u8f7d\u94fe\u63a5\u5931\u8d25'
            };
        }
        
        if (result.data?.task_resp?.code) {
            return {
                error: true,
                code: result.data.task_resp.code,
                message: result.data.task_resp.message || '\u83b7\u53d6\u4e0b\u8f7d\u94fe\u63a5\u5931\u8d25'
            };
        }
        
        const downloadResult = result.data?.[0] || null;
        
        if (downloadResult) {
            this.setCachedUrl(shareId, fileId, downloadResult);
            return downloadResult;
        }
        
        return {
            error: true,
            code: -2,
            message: '\u83b7\u53d6\u4e0b\u8f7d\u94fe\u63a5\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5'
        };
    }

    /**
     * \u6d4b\u8bd5URL\u652f\u6301\u6027
     */
    async testSupport(url, headers) {
        try {
            const resp = await req(url, {
                method: 'GET',
                headers: { ...this.baseHeader, ...headers, 'Range': 'bytes=0-0' }
            });
            
            if (resp.code === 206 || resp.code === 200) {
                const isAccept = resp.headers?.['accept-ranges'] === 'bytes';
                const contentRange = resp.headers?.['content-range'];
                const contentLength = parseInt(resp.headers?.['content-length'] || '0');
                const isSupport = isAccept || !!contentRange || contentLength === 1 || resp.status === 200;
                return [isSupport, resp.headers || {}];
            }
            return [false, null];
        } catch {
            return [false, null];
        }
    }
}

export const Quark = new QuarkHandler();