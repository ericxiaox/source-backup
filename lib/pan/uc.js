/**
 * UC\u7f51\u76d8\u5904\u7406\u5de5\u5177
 * 
 * \u63d0\u4f9bUC\u7f51\u76d8\u5206\u4eab\u94fe\u63a5\u89e3\u6790\u3001\u6587\u4ef6\u4e0b\u8f7d\u7b49\u529f\u80fd\u3002
 * 
 * @module UCPanHandler
 * @author \u4f18\u96c5
 * @since 1.0.0
 */

import { Crypto as CryptoJS } from 'assets://js/lib/cat.js';

// \u5168\u5c40\u8c03\u8bd5\u5f00\u5173
let DEBUG = globalThis.uc_debug || 0;

/**
 * \u65e5\u5fd7\u8f93\u51fa
 */
function log(tag, message) {
    if (!DEBUG) return;
    console.log(`\u3010UC-${tag}\u3011 ${message}`);
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
 * UC\u7f51\u76d8\u5904\u7406\u7c7b
 */
class UCHandler {
    constructor() {
        // UC\u5206\u4eab\u94fe\u63a5\u6b63\u5219\u8868\u8fbe\u5f0f - \u5339\u914d\u6807\u51c6\u5206\u4eab\u94fe\u63a5\u548c\u63d0\u53d6\u5bc6\u7801
        this.regex = /https:\/\/drive\.uc\.cn\/s\/([^?&#]+)(?:\?.*?pwd=([^&]+))?/;
        // \u8bf7\u6c42\u53c2\u6570
        this.pr = 'pr=UCBrowser&fr=pc';
        // \u57fa\u7840\u8bf7\u6c42\u5934
        this.baseHeader = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) uc-cloud-drive/1.8.5 Chrome/100.0.4896.160 Electron/18.3.5.16-b62cf9c50d Safari/537.36 Channel/ucpan_other_ch',
            'Referer': 'https://drive.uc.cn/',
            'Origin': 'https://drive.uc.cn',
           'Content-Type': 'application/json'
        };
        // API\u57fa\u7840URL
        this.apiUrl = 'https://pc-api.uc.cn/1/clouddrive';
        // \u5206\u4eab\u4ee4\u724c\u7f13\u5b58
        this.shareTokenCache = {};
        // \u4fdd\u5b58\u76ee\u5f55\u540d\u79f0
        this.saveDirName = 'drpy';
        // \u4fdd\u5b58\u76ee\u5f55ID
        this.saveDirId = null;
        // \u4fdd\u5b58\u6587\u4ef6ID\u7f13\u5b58
        this.saveFileIdCaches = {};
        // \u5b57\u5e55\u6587\u4ef6\u6269\u5c55\u540d
        this.subtitleExts = ['.srt', '.ass', '.scc', '.stl', '.ttml'];
        // \u89c6\u9891\u6587\u4ef6\u6269\u5c55\u540d
        this.videoExts = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.ts', '.m3u8'];
        // \u89c6\u9891\u6269\u5c55\u540d\u5f00\u5173\uff081=\u542f\u7528\u5224\u65ad\uff0c0=\u7981\u7528\uff09
        this.videoExtsEnabled = 0;
        
        // Cookie\u548cToken\u5b58\u50a8
        this._cookie = "";
        this._token = "";
        
        // Token\u548cCookie\u6709\u6548\u671f\u8bb0\u5f55
        this.tokenExpireTime = 0;
        this.cookieExpireTime = 0;
        
        // \u64ad\u653e\u5730\u5740\u4e34\u65f6\u7f13\u5b58\uff0820\u5206\u949f\uff09
        this.urlCache = {};
        this.cacheTTL = 20 * 60 * 1000;
        
        // \u4e0a\u6b21\u5237\u65b0\u65f6\u95f4
        this.lastRefreshTime = 0;
        this.refreshInterval = 4 * 24 * 60 * 60 * 1000;
        
        // UC TV\u914d\u7f6e
        this.ucConfig = {
            api: "https://open-api-drive.uc.cn",
            clientID: "5acf882d27b74502b7040b0c65519aa7",
            signKey: "l3srvtd7p42l0d0x1u8d7yc8ye9kki4d",
            appVer: "1.6.8",
            channel: "UCTVOFFICIALWEB",
            deviceID: "07b48aaba8a739356ab8107b5e230ad4"
        }
        
        // \u5237\u65b0\u9501
        this._isRefreshing = false;
        this._refreshPromise = null;
    }

    /**
     * \u83b7\u53d6Cookie
     */
    get cookie() {
        if (this._cookie && this.cookieExpireTime > Date.now()) {
            return this._cookie;
        }
        if (globalThis.uc_cookie) {
            this._cookie = globalThis.uc_cookie;
            this.cookieExpireTime = Date.now() + 7 * 24 * 60 * 60 * 1000;
        }
        return this._cookie;
    }

    /**
     * \u8bbe\u7f6eCookie
     */
    set cookie(value) {
        this._cookie = value || '';
        if (value) {
            this.cookieExpireTime = Date.now() + 7 * 24 * 60 * 60 * 1000;
            globalThis.uc_cookie = value;
        }
    }

    /**
     * \u83b7\u53d6Token
     */
    get token() {
        if (this._token && this.tokenExpireTime > Date.now()) {
            return this._token;
        }
        if (globalThis.uc_token) {
            this._token = globalThis.uc_token;
            try {
                const parts = this._token.split('.');
                if (parts.length >= 2) {
                    const payload = JSON.parse(CryptoJS.enc.Base64.parse(parts[1]).toString(CryptoJS.enc.Utf8));
                    this.tokenExpireTime = payload.exp * 1000;
                }
            } catch (e) {}
        }
        return this._token;
    }

    /**
     * \u8bbe\u7f6eToken
     */
    set token(value) {
        this._token = value || '';
        if (value) {
            try {
                const parts = value.split('.');
                if (parts.length >= 2) {
                    const payload = JSON.parse(CryptoJS.enc.Base64.parse(parts[1]).toString(CryptoJS.enc.Utf8));
                    this.tokenExpireTime = payload.exp * 1000;
                }
            } catch (e) {}
            globalThis.uc_token = value;
        }
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
     * \u521d\u59cb\u5316UC
     */
    async initUC(db, cfg) {
        if (cfg?.uc_cookie) this.cookie = cfg.uc_cookie;
        if (cfg?.uc_token) this.token = cfg.uc_token;
        if (cfg?.uc_videoExtsEnabled !== undefined) this.videoExtsEnabled = cfg.uc_videoExtsEnabled;
        if (this.lastRefreshTime === 0) this.lastRefreshTime = Date.now();
        await this.ensureTokenAndCookie();
        log('\u521d\u59cb\u5316', `\u5b8c\u6210, videoExtsEnabled=${this.videoExtsEnabled}`);
    }

    /**
     * \u89e3\u6790\u5206\u4eab\u94fe\u63a5
     * \u4ece\u5206\u4eabURL\u4e2d\u63d0\u53d6shareId\u548c\u5bc6\u7801
     * @param {string} url - UC\u5206\u4eab\u94fe\u63a5
     * @returns {Object|null} \u5305\u542bshareId\u3001folderId\u3001passCode\u7684\u5bf9\u8c61\uff0c\u89e3\u6790\u5931\u8d25\u8fd4\u56denull
     */
    getShareData(url) {
        const matches = this.regex.exec(url);
        if (!matches || !matches[1]) return null;
        
        let shareId = matches[1];
        if (shareId.indexOf("?") > 0) shareId = shareId.split('?')[0];
        // public=1 \u8868\u793a\u65e0\u5bc6\u7801\uff0c\u5426\u5219\u4f7f\u7528\u6b63\u5219\u6355\u83b7\u7684\u5bc6\u7801
        let passCode = matches[2] || '';
        // \u5982\u679cURL\u4e2d\u6709public=1\u53c2\u6570\uff0c\u5219\u5bc6\u7801\u4e3a\u7a7a
        if (url.includes('public=1')) {
            passCode = '';
        }
        
        return { shareId: shareId, folderId: '0', passCode: passCode };
    }

    /**
     * \u83b7\u53d6\u5206\u4eab\u4ee4\u724c
     */
    async getShareToken(shareData) {
        if (!this.shareTokenCache[shareData.shareId]) {
            const url = `${this.apiUrl}/share/sharepage/token?${this.pr}`;
            const result = await this.request(url, {
                method: 'POST',
                data: { pwd_id: shareData.shareId, passcode: shareData.passCode || '' },
                headers: this.baseHeader
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
        const shareData = typeof shareInfo === 'string' ? this.getShareData(shareInfo) : shareInfo;
        if (!shareData) return [];
        
        await this.getShareToken(shareData);
        if (!this.shareTokenCache[shareData.shareId]) return [];
        
        const videos = [];
        const subtitles = [];
        
        const listFile = async (shareId, folderId, page = 1) => {
            const prePage = 200;
            const url = `${this.apiUrl}/share/sharepage/detail?pwd_id=${shareId}&stoken=${encodeURIComponent(this.shareTokenCache[shareId].stoken)}&pdir_fid=${folderId}&force=0&_page=${page}&_size=${prePage}&_sort=file_type:asc,file_name:asc&${this.pr}`;
            const listData = await this.request(url, { method: 'GET', headers: this.baseHeader }, 3, `\u83b7\u53d6\u6587\u4ef6\u5217\u8868-${folderId}-p${page}`);
            
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
                        // \u7981\u7528\u6269\u5c55\u540d\u5224\u65ad\uff0c\u53ea\u4f9d\u8d56UC\u5206\u7c7b
                        isVideo = item.obj_category === 'video';
                    }
                    
                    if (isVideo) {
                        item.stoken = this.shareTokenCache[shareData.shareId].stoken;
                        item.formatted_size = this.formatFileSize(item.size);
                        if (!item.share_fid_token && item.fid_token) item.share_fid_token = item.fid_token;
                        if (!item.share_fid_token) item.share_fid_token = item.fid;
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
        
        const url = `${this.apiUrl}/file/sort?pdir_fid=${this.saveDirId}&_page=1&_size=200&_sort=file_type:asc,updated_at:desc&${this.pr}`;
        const listData = await this.request(url, { method: 'GET', headers: this.getHeaders() }, 3, '\u6e05\u7406\u76ee\u5f55-\u83b7\u53d6\u5217\u8868');
        
        if (listData.code && listData.code !== 200 && listData.code !== 0) {
            return { error: true, code: listData.code, message: ERROR_CODES[listData.code]?.message || '\u83b7\u53d6\u76ee\u5f55\u6587\u4ef6\u5217\u8868\u5931\u8d25' };
        }
        
        if (listData.data?.list?.length > 0) {
            const deleteUrl = `${this.apiUrl}/file/delete?${this.pr}`;
            const deleteResult = await this.request(deleteUrl, {
                method: 'POST',
                data: { action_type: 2, filelist: listData.data.list.map(v => v.fid), exclude_fids: [] },
                headers: this.getHeaders()
            }, 3, '\u6e05\u7406\u76ee\u5f55-\u5220\u9664\u6587\u4ef6');
            
            if (deleteResult.code && deleteResult.code !== 200 && deleteResult.code !== 0) {
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
        
        const url = `${this.apiUrl}/file/sort?pdir_fid=0&_page=1&_size=200&_sort=file_type:asc,updated_at:desc&${this.pr}`;
        const listData = await this.request(url, { method: 'GET', headers: this.getHeaders() }, 3, '\u521b\u5efa\u76ee\u5f55-\u83b7\u53d6\u6839\u76ee\u5f55');
        
        if (!listData.code && !listData.data?.list) {
            return { error: true, code: 31001, message: ERROR_CODES[31001]?.message || '\u672a\u767b\u5f55\u6216Cookie\u5df2\u5931\u6548\uff0c\u8bf7\u91cd\u65b0\u83b7\u53d6Cookie' };
        }
        // \u68c0\u67e5\u662f\u5426\u6709\u9519\u8bef\u7801
        if (listData.code && listData.code !== 200 && listData.code !== 0) {
            const errorMsg = ERROR_CODES[listData.code]?.message || listData.message || '\u83b7\u53d6\u76ee\u5f55\u5217\u8868\u5931\u8d25';
            log('\u76ee\u5f55', `\u83b7\u53d6\u5931\u8d25: code=${listData.code}`);
            return { error: true, code: listData.code, message: errorMsg };
        }
        
        // \u68c0\u67e5\u662f\u5426\u6709\u9519\u8bef\u4fe1\u606f
        if (listData.message && listData.code !== 200 && listData.code !== 0) {
            return { error: true, code: listData.code || -1, message: listData.message };
        }
        
        if (listData.data?.list) {
            for (const item of listData.data.list) {
                if (item.file_name === this.saveDirName) {
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
            const createUrl = `${this.apiUrl}/file?${this.pr}`;
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
     * \u4fdd\u5b58\u6587\u4ef6\u5230\u4e2a\u4eba\u7f51\u76d8
     */
    async save(shareId, stoken, fileId, fileToken, clean) {
        const dirResult = await this.createSaveDir(clean);
        if (dirResult.error) {
            return { error: true, code: dirResult.code, message: dirResult.message };
        }
        
        if (clean) Object.keys(this.saveFileIdCaches).forEach(key => delete this.saveFileIdCaches[key]);
        
        if (!stoken) {
            await this.getShareToken({ shareId });
            if (!this.shareTokenCache[shareId]) {
                return { error: true, code: -2, message: '\u83b7\u53d6\u5206\u4eab\u4ee4\u724c\u5931\u8d25' };
            }
            stoken = this.shareTokenCache[shareId].stoken;
        }
        
        const saveUrl = `${this.apiUrl}/share/sharepage/save?${this.pr}`;
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
                const taskUrl = `${this.apiUrl}/task?task_id=${saveResult.data.task_id}&retry_index=${retry}&${this.pr}`;
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
     * \u5237\u65b0Token
     */
    async refreshToken() {
        if (this._isRefreshing) return await this._refreshPromise;
        
        this._isRefreshing = true;
        this._refreshPromise = (async () => {
            const currentToken = this.token;
            if (!currentToken) return false;
            
            try {
                const timestamp = Math.floor(Date.now() / 1000).toString() + '000';
                const deviceID = this.ucConfig.deviceID;
                const reqId = this.generateReqId(deviceID, timestamp);
                const data = {
                    req_id: reqId, app_ver: this.ucConfig.appVer, device_id: deviceID,
                    device_brand: "OPPO", platform: "tv", device_name: "PCRT00",
                    device_model: "PCRT00", build_device: "aosp", build_product: "PCRT00",
                    device_gpu: "Adreno%20(TM)%20640", activity_rect: "%7B%7D",
                    channel: this.ucConfig.channel, refresh_token: currentToken
                };
                const resp = await req('http://api.extscreen.com/ucdrive/token', {
                    method: 'POST',
                    headers: {
                        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 7.1.2; zh-cn; PCRT00 Build/N2G47O) AppleWebKit/533.1 (KHTML, like Gecko) Mobile Safari/533.1',
                        'Connection': 'Keep-Alive', 'Content-Type': 'application/json',
                        'Cookie': 'sl-session=VIaxTAKF8mdJBhU2uda0zA=='
                    },
                    data: data
                });
                if (resp.code == 200 && resp.content) {
                    const result = JSON.parse(resp.content);
                    if (result.data?.access_token) {
                        this.token = result.data.access_token;
                        log('Token', `\u5237\u65b0\u6210\u529f`);
                        return true;
                    }
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
     * \u5237\u65b0Cookie
     */
    async refreshCookie() {
        if (this._isRefreshing) return await this._refreshPromise;
        
        this._isRefreshing = true;
        this._refreshPromise = (async () => {
            const currentCookie = this.cookie;
            if (!currentCookie) return false;
            
            try {
                const resp = await this.request('https://pc-api.uc.cn/1/clouddrive/config?pr=UCBrowser&fr=pc', {
                    method: "GET",
                    headers: {
                        "User-Agent": this.baseHeader['User-Agent'],
                        Origin: 'https://drive.uc.cn',
                        Referer: 'https://drive.uc.cn/',
                        Cookie: currentCookie
                    }
                }, 3, '\u5237\u65b0Cookie');
                const setCookie = resp.headers?.['set-cookie'] || resp.headers?.['Set-Cookie'];
                if (!setCookie) return false;
                
                const cookieObject = {};
                const cookieParts = Array.isArray(setCookie) ? setCookie : [setCookie];
                for (const part of cookieParts) {
                    const match = part.match(/([^=;]+)=([^;]+)/);
                    if (match) cookieObject[match[1].trim()] = match[2].trim();
                }
                if (cookieObject.__puus) {
                    const oldCookies = {};
                    currentCookie.split(';').forEach(part => {
                        const trimmed = part.trim();
                        const eqIndex = trimmed.indexOf('=');
                        if (eqIndex > 0) oldCookies[trimmed.substring(0, eqIndex)] = trimmed.substring(eqIndex + 1);
                    });
                    const newCookie = Object.entries({
                        __pus: oldCookies.__pus, __puus: cookieObject.__puus,
                    }).map(([key, value]) => `${key}=${value}`).join('; ');
                    this.cookie = newCookie;
                    log('Cookie', `\u5237\u65b0\u6210\u529f`);
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
     * \u9a8c\u8bc1Token\u662f\u5426\u6709\u6548
     */
    async validToken() {
        if (!this.token) return false;
        if (this.tokenExpireTime > Date.now()) return true;
        log('Token', `\u5df2\u8fc7\u671f`);
        return false;
    }

    /**
     * \u9a8c\u8bc1Cookie\u662f\u5426\u6709\u6548
     */
    async validCookie() {
        const currentCookie = this.cookie;
        if (!currentCookie) return false;
        try {
            const resp = await this.request('https://pc-api.uc.cn/1/clouddrive/config?pr=UCBrowser&fr=pc', {
                method: "GET",
                headers: {
                    "User-Agent": this.baseHeader['User-Agent'],
                    Origin: 'https://drive.uc.cn',
                    Referer: 'https://drive.uc.cn/',
                    Cookie: currentCookie
                }
            }, 1, '\u9a8c\u8bc1Cookie');
            if (resp.code == 200 || resp.status == 200) return true;
            return false;
        } catch (error) {
            return false;
        }
    }

    /**
     * \u786e\u4fddToken\u548cCookie\u6709\u6548
     */
    async ensureTokenAndCookie() {
        const needRefresh = () => {
            if (this.lastRefreshTime === 0) return true;
            if (Date.now() - this.lastRefreshTime >= this.refreshInterval) return true;
            return false;
        };
        
        if (!needRefresh()) {
            const tokenValid = await this.validToken();
            const cookieValid = await this.validCookie();
            if (tokenValid && cookieValid) return true;
        }
        
        const tokenResult = await this.refreshToken();
        const cookieResult = await this.refreshCookie();
        
        if (tokenResult || cookieResult) {
            this.lastRefreshTime = Date.now();
            return true;
        }
        
        return false;
    }

    /**
     * \u751f\u6210\u8bbe\u5907ID
     */
    generateDeviceID(timestamp) {
        return CryptoJS.MD5(timestamp).toString().slice(0, 16);
    }

    /**
     * \u751f\u6210\u8bf7\u6c42ID
     */
    generateReqId(deviceID, timestamp) {
        return CryptoJS.MD5(deviceID + timestamp).toString().slice(0, 16);
    }

    /**
     * \u83b7\u53d6\u4e0b\u8f7d\u94fe\u63a5
     */
    async getDownload(shareId, stoken, fileId, fileToken, clean = false) {
        // \u5148\u68c0\u67e5\u7f13\u5b58
        const cachedResult = this.getCachedUrl(shareId, fileId);
        if (cachedResult) return cachedResult;
        
        await this.ensureTokenAndCookie();
        
        if (!this.saveFileIdCaches[fileId]) {
            const saveResult = await this.save(shareId, stoken, fileId, fileToken, clean);
            if (saveResult && saveResult.error) return saveResult;
            if (!saveResult) return { error: true, code: -1, message: '\u6587\u4ef6\u8f6c\u5b58\u5931\u8d25' };
            this.saveFileIdCaches[fileId] = saveResult;
        }
        
        let result = null;
        
        // \u5c1d\u8bd5\u83b7\u53d6\u65e0\u9650\u753b\u8d28\u94fe\u63a5
        if (this.token) {
            const timestamp = Math.floor(Date.now() / 1000).toString() + '000';
            const deviceID = this.ucConfig.deviceID;
            const reqId = this.generateReqId(deviceID, timestamp);
            const x_pan_token = CryptoJS.SHA256('GET&/file&' + timestamp + '&' + this.ucConfig.signKey).toString();
            const params = {
                req_id: reqId, access_token: this.token, app_ver: this.ucConfig.appVer,
                device_id: deviceID, device_brand: 'Xiaomi', platform: 'tv',
                device_name: 'M2004J7AC', device_model: 'M2004J7AC',
                build_device: 'M2004J7AC', build_product: 'M2004J7AC',
                device_gpu: 'Adreno (TM) 550', activity_rect: '{}',
                channel: this.ucConfig.channel, method: 'streaming',
                group_by: 'source', fid: this.saveFileIdCaches[fileId],
                resolution: 'low,normal,high,super,2k,4k', support: 'dolby_vision'
            };
            const urlParams = Object.entries(params).map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&');
            const url = `https://open-api-drive.uc.cn/file?${urlParams}`;
            
            const response = await req(url, {
                method: 'GET', headers: {
                    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 9; zh-cn; RMX1931 Build/PQ3A.190605.05081124) AppleWebKit/533.1 (KHTML, like Gecko) Mobile Safari/533.1',
                    'Connection': 'Keep-Alive', 'x-pan-tm': timestamp,
                    'x-pan-token': x_pan_token, 'content-type': 'text/plain;charset=UTF-8',
                    'x-pan-client-id': this.ucConfig.clientID, 'Cookie': this.cookie
                }
            });
            
            if (response.code == 200 && response.content) {
                const jsonData = JSON.parse(response.content);
                if (jsonData.data?.video_info) {
                    result = jsonData.data.video_info.map(item => ({ name: item.resolution, url: item.url }));
                }
            }
        }
        
        // \u964d\u7ea7\u83b7\u53d6\u666e\u901a\u4e0b\u8f7d\u94fe\u63a5
        if (!result) {
            const url = `${this.apiUrl}/file/download?${this.pr}`;
            const downResult = await this.request(url, {
                method: 'POST',
                data: { fids: [this.saveFileIdCaches[fileId]] },
                headers: this.getHeaders()
            }, 3, '\u83b7\u53d6\u4e0b\u8f7d\u94fe\u63a5');
            
            if (downResult.code && downResult.code !== 200 && downResult.code !== 0) {
                return { error: true, code: downResult.code, message: ERROR_CODES[downResult.code]?.message || '\u83b7\u53d6\u4e0b\u8f7d\u94fe\u63a5\u5931\u8d25' };
            }
            
            const downloadData = downResult.data?.[0];
            if (downloadData) {
                result = [{ name: "\u539f\u753b", url: downloadData.download_url }];
            }
        }
        
        if (result) {
            this.setCachedUrl(shareId, fileId, result);
            return result;
        }
        
        return { error: true, code: -2, message: '\u83b7\u53d6\u4e0b\u8f7d\u94fe\u63a5\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5' };
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
            const saveFileId = await this.save(shareId, stoken, fileId, fileToken, true);
            if (!saveFileId || saveFileId.error) {
                log('\u8f6c\u7801', `\u8f6c\u5b58\u5931\u8d25: ${saveFileId?.message || '\u672a\u77e5\u9519\u8bef'}`);
                return null;
            }
            
            // \u8bf7\u6c42\u8f6c\u7801\u753b\u8d28
            const url = `${this.apiUrl}/file/v2/play?${this.pr}`;
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
        const deleteUrl = `${this.apiUrl}/file/delete?${this.pr}`;
        await this.request(deleteUrl, {
            method: 'POST',
            data: { action_type: 2, filelist: [fileId], exclude_fids: [] },
            headers: this.getHeaders()
        }, 3, '\u5220\u9664\u4e34\u65f6\u6587\u4ef6');
    }

    /**
     * \u83b7\u53d6\u61d2\u52a0\u8f7d\u7ed3\u679c
     */
    async getLazyResult(downCache, mediaProxyUrl) {
        const urls = [];
        if (Array.isArray(downCache)) {
            downCache.forEach(it => {
                if (it && it.url) urls.push(it.name, it.url + "#isVideo=true##fastPlayMode##threads=10#");
            });
        } else if (downCache?.download_url) {
            urls.push("\u539f\u753b", downCache.download_url + "#isVideo=true##fastPlayMode##threads=10#");
        } else if (downCache?.error) {
            return { parse: 0, url: [], error: downCache.message };
        }
        return { parse: 0, url: urls };
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

export const UC = new UCHandler();