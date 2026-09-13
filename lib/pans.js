/**
 * \u7f51\u76d8\u670d\u52a1\u6a21\u5757\u96c6\u5408
 * \u7edf\u4e00\u5bfc\u5165\u548c\u5bfc\u51fa\u5404\u79cd\u7f51\u76d8\u670d\u52a1\u63d0\u4f9b\u5546\u7684\u5b9e\u73b0
 * 
 * \u652f\u6301\u7684\u7f51\u76d8\u670d\u52a1\uff1a
 * - Ali: \u963f\u91cc\u4e91\u76d8\u670d\u52a1
 * - Baidu: \u767e\u5ea6\u7f51\u76d8\u670d\u52a1
 * - Baidu2: \u767e\u5ea6\u7f51\u76d8\u670d\u52a1\uff08\u7b2c\u4e8c\u7248\u672c\uff09
 * - Cloud: \u5929\u7ffc\u4e91\u76d8\u670d\u52a1
 * - Pan: 123\u7f51\u76d8\u670d\u52a1
 * - Quark: \u5938\u514b\u7f51\u76d8\u670d\u52a1
 * - UC: UC\u7f51\u76d8\u670d\u52a1
 * - Yun: 115\u7f51\u76d8\u670d\u52a1
 * 
 * @example
 * import pans from './pans.js';
 * const aliPan = new pans.Ali(config);
 * const files = await aliPan.getFileList();
 */
//import  "./cookie.js";    // \u7f51\u76d8ck\u670d\u52a1

// \u5bfc\u5165\u5404\u79cd\u7f51\u76d8\u670d\u52a1\u5b9e\u73b0
//import {Ali} from './pan/ali.js';        // \u963f\u91cc\u4e91\u76d8\u670d\u52a1
import {Baidu} from "./pan/baidu.js";    // \u767e\u5ea6\u7f51\u76d8\u670d\u52a1
//import {Baidu2} from "./pan/baidu2.js";  // \u767e\u5ea6\u7f51\u76d8\u670d\u52a1\uff08\u7b2c\u4e8c\u7248\u672c\uff09
//import {Cloud} from "./pan/cloud.js";    // \u5929\u7ffc\u4e91\u76d8\u670d\u52a1
//import {Pan} from "./pan/pan123.js";     // 123\u7f51\u76d8\u670d\u52a1
import {Quark} from "./pan/quark.js";    // \u5938\u514b\u7f51\u76d8\u670d\u52a1
import {UC} from "./pan/uc.js";          // UC\u7f51\u76d8\u670d\u52a1
//import {Yun} from "./pan/yun.js";        // 115\u7f51\u76d8\u670d\u52a1

// \u7edf\u4e00\u5bfc\u51fa\u6240\u6709\u7f51\u76d8\u670d\u52a1
//export default {Ali, Baidu, Baidu2, Cloud, Pan, Quark, UC, Yun}
export { Quark, Baidu, UC}
 //  export default { Quark, Baidu}

