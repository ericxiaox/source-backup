/**
 * \u7edf\u4e00 HTML/JSON \u89e3\u6790\u5668
 * \u7ed3\u5408\u8f7b\u91cf\u7ea7HTML\u89e3\u6790\u5668(lite)\u548c\u5b8c\u6574HTML\u89e3\u6790\u5668(cheerio\u7248\u672c)
 * \u4e0d\u4f9d\u8d56 cheerio\uff0c\u4f7f\u7528\u7eaf\u6b63\u5219\u8868\u8fbe\u5f0f\u5b9e\u73b0\uff0c\u540c\u65f6\u652f\u6301JSONPath\u89e3\u6790
 * 
 * \u652f\u6301\u7684\u9009\u62e9\u5668\u8bed\u6cd5\uff1a
 * - \u6807\u7b7e\u540d: div, p, a, img
 * - \u7c7b\u9009\u62e9\u5668: .class-name
 * - ID\u9009\u62e9\u5668: #id-name
 * - \u5c5e\u6027\u9009\u62e9\u5668: [attr], [attr=value]
 * - \u7ec4\u5408\u9009\u62e9\u5668: div.class, div#id, img:last-of-type
 * - \u540e\u4ee3\u9009\u62e9\u5668: div p (\u7a7a\u683c\u5206\u9694)
 * - \u4f2a\u9009\u62e9\u5668: :eq(n), :first, :last, :eq(-1), :last-of-type, :first-of-type
 * - :has(selector) - \u5339\u914d\u5305\u542b\u6307\u5b9a\u5b50\u5143\u7d20\u7684\u5143\u7d20
 * - :contains(text) - \u5339\u914d\u5305\u542b\u6307\u5b9a\u6587\u672c\u7684\u5143\u7d20
 * - \u6392\u9664\u8bed\u6cd5: p--a (\u83b7\u53d6p\u6807\u7b7e\u5185\u5bb9\u4f46\u6392\u9664a\u6807\u7b7e)
 * - \u6d77\u9614\u89c6\u754c\u8bed\u6cd5: && \u5206\u9694, Text, Html
 */

(function(global) {
  'use strict';

  // ============================================
  // \u5e38\u91cf\u5b9a\u4e49
  // ============================================
  var URLJOIN_ATTR = /(url|src|href|-original|-src|-play|-url|style)$|^(data-|url-|src-)/;
  var SPECIAL_URL = /^(ftp|magnet|thunder|ws):/;
  var SELF_CLOSING_TAGS = /^(img|br|hr|input|meta|link|area|base|col|embed|param|source|track|wbr)$/i;
  
  // \u89e3\u6790\u7f13\u5b58\u5f00\u5173
  var PARSE_CACHE = true;
  // \u4e0d\u81ea\u52a8\u52a0eq\u4e0b\u6807\u7d22\u5f15\u7684\u9009\u62e9\u5668
  var NOADD_INDEX = ':eq|:lt|:gt|:first|:last|:not|:even|:odd|:has|:contains|:matches|:empty|^body$|^#';

  // ============================================
  // HTML \u5143\u7d20\u7c7b
  // ============================================
  function HtmlElement(tagName, attributes, innerHTML, outerHTML) {
    this.tagName = (tagName || '').toLowerCase();
    this.attributes = attributes || {};
    this.innerHTML = innerHTML || '';
    this.outerHTML = outerHTML || '';
  }

  HtmlElement.prototype.attr = function(name) {
    if (!name) return '';
    var lowerName = name.toLowerCase();
    return this.attributes[name] || this.attributes[lowerName] || '';
  };

  HtmlElement.prototype.text = function() {
    return this.innerHTML
      .replace(/<script[\s\S]*?<\/script>/gi, '')
      .replace(/<style[\s\S]*?<\/style>/gi, '')
      .replace(/<[^>]+>/g, ' ')
      .replace(/&nbsp;/g, ' ')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&amp;/g, '&')
      .replace(/&quot;/g, '"')
      .replace(/&#(\d+);/g, function(m, c) { return String.fromCharCode(c); })
      .replace(/\s+/g, ' ')
      .trim();
  };

  HtmlElement.prototype.html = function() {
    return this.innerHTML;
  };

  // ============================================
  // \u5de5\u5177\u51fd\u6570
  // ============================================
  
  /**
   * \u89e3\u6790 HTML \u6807\u7b7e\u7684\u5c5e\u6027
   */
  function parseAttributes(attrString) {
    var attrs = {};
    if (!attrString) return attrs;
    
    var attrRegex = /([\w-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g;
    var match;
    
    while ((match = attrRegex.exec(attrString)) !== null) {
      var name = match[1].toLowerCase();
      var value = match[2] !== undefined ? match[2] : 
                  match[3] !== undefined ? match[3] : 
                  match[4] !== undefined ? match[4] : '';
      attrs[name] = value;
    }
    
    return attrs;
  }

  /**
   * URL \u62fc\u63a5
   */
  function urlJoin(base, path) {
    if (!path) return base || '';
    if (!base) return path;
    if (/^https?:\/\//i.test(path)) return path;
    if (path.indexOf('//') === 0) {
      return (base.indexOf('https://') === 0 ? 'https:' : 'http:') + path;
    }
    if (path.indexOf('/') === 0) {
      var m = base.match(/^(https?:\/\/[^\/]+)/i);
      return m ? m[1] + path : path;
    }
    
    var baseUrl = base.split('?')[0];
    if (baseUrl.charAt(baseUrl.length - 1) !== '/') {
      var idx = baseUrl.lastIndexOf('/');
      baseUrl = idx > 8 ? baseUrl.substring(0, idx + 1) : baseUrl + '/';
    }
    
    while (path.indexOf('../') === 0) {
      path = path.substring(3);
      var idx2 = baseUrl.lastIndexOf('/', baseUrl.length - 2);
      if (idx2 > 8) baseUrl = baseUrl.substring(0, idx2 + 1);
    }
    
    if (path.indexOf('./') === 0) path = path.substring(2);
    return baseUrl + path;
  }

  /**
   * \u6e05\u7406\u6587\u672c
   */
  function cleanText(text) {
    if (!text) return '';
    return text.replace(/[\s]+/g, ' ').trim();
  }

  /**
   * \u6b63\u5219\u6d4b\u8bd5
   */
  function regexTest(pattern, text) {
    if (!pattern || !text) return false;
    var regex = new RegExp(pattern, 'i');
    return regex.test(text);
  }

  /**
   * \u68c0\u67e5\u5b57\u7b26\u4e32\u662f\u5426\u5305\u542b\u6307\u5b9a\u5185\u5bb9
   */
  function contains(text, match) {
    return text && text.indexOf(match) !== -1;
  }

  // ============================================
  // \u9009\u62e9\u5668\u89e3\u6790
  // ============================================
  
  /**
   * \u89e3\u6790\u9009\u62e9\u5668\uff0c\u63d0\u53d6\u6807\u7b7e\u540d\u3001\u7c7b\u540d\u3001ID\u3001\u5c5e\u6027\u548c\u4f2a\u9009\u62e9\u5668
   */
  function parseSelector(selector) {
    var result = {
      tagName: null,
      classNames: [],
      idName: null,
      attrs: {},
      pseudo: null,
      pseudoArg: null,
      hasSelector: null
    };
    
    if (!selector) return result;
    selector = selector.trim();
    
    // \u89e3\u6790 :has() \u4f2a\u9009\u62e9\u5668
    var hasMatch = selector.match(/:has\(([^)]+)\)/);
    if (hasMatch) {
      result.hasSelector = hasMatch[1].trim();
      selector = selector.replace(/:has\([^)]+\)/, '');
    }
    
    // \u89e3\u6790 :contains() \u4f2a\u9009\u62e9\u5668
    var containsMatch = selector.match(/:contains\(([^)]+)\)/);
    if (containsMatch) {
      result.pseudo = 'contains';
      result.pseudoArg = containsMatch[1].replace(/^['"]|['"]$/g, '');
      selector = selector.replace(/:contains\([^)]+\)/, '');
    }
    
    // \u89e3\u6790\u4f2a\u9009\u62e9\u5668
    var pseudoMatch = selector.match(/:(\w+(?:-\w+)*)(?:\((-?\d+)\))?$/);
    if (pseudoMatch && !result.pseudo) {
      result.pseudo = pseudoMatch[1];
      result.pseudoArg = pseudoMatch[2] !== undefined ? parseInt(pseudoMatch[2]) : null;
      selector = selector.replace(/:[\w-]+(?:\(-?\d+\))?$/, '');
    }
    
    // \u89e3\u6790\u5c5e\u6027\u9009\u62e9\u5668
    var attrRegex = /\[([\w-]+)(?:([*^$~]?)=["']?([^"'\]]+)["']?)?\]/g;
    var attrMatch;
    while ((attrMatch = attrRegex.exec(selector)) !== null) {
      var attrName = attrMatch[1].toLowerCase();
      var matchMode = attrMatch[2] || '';
      var attrValue = attrMatch[3];
      
      if (attrValue === undefined) {
        result.attrs[attrName] = { mode: 'exists', value: true };
      } else {
        result.attrs[attrName] = { mode: matchMode || 'exact', value: attrValue };
      }
    }
    selector = selector.replace(/\[[\w-]+(?:[*^$~]?=["']?[^"'\]]+["']?)?\]/g, '');
    
    // \u89e3\u6790 #id
    var idMatch = selector.match(/#([\w-]+)/);
    if (idMatch) {
      result.idName = idMatch[1];
      selector = selector.replace(/#[\w-]+/, '');
    }
    
    // \u89e3\u6790 .class
    var classRegex = /\.([\w-]+)/g;
    var classMatch;
    while ((classMatch = classRegex.exec(selector)) !== null) {
      result.classNames.push(classMatch[1]);
    }
    selector = selector.replace(/\.[\w-]+/g, '');
    
    // \u5269\u4f59\u7684\u662f\u6807\u7b7e\u540d
    selector = selector.trim();
    if (selector && selector !== '*') {
      result.tagName = selector.toLowerCase();
    }
    
    return result;
  }

  /**
   * \u68c0\u67e5\u5143\u7d20\u662f\u5426\u5339\u914d\u9009\u62e9\u5668\u6761\u4ef6
   */
  function matchesSelector(element, selectorInfo) {
    if (selectorInfo.tagName && element.tagName !== selectorInfo.tagName) return false;
    if (selectorInfo.idName && element.attributes.id !== selectorInfo.idName) return false;
    
    if (selectorInfo.classNames.length > 0) {
      var elementClasses = (element.attributes.class || '').split(/\s+/);
      for (var i = 0; i < selectorInfo.classNames.length; i++) {
        if (elementClasses.indexOf(selectorInfo.classNames[i]) === -1) return false;
      }
    }
    
    for (var attrKey in selectorInfo.attrs) {
      var attrVal = element.attributes[attrKey];
      var attrRule = selectorInfo.attrs[attrKey];
      
      if (typeof attrRule !== 'object') {
        attrRule = { mode: attrRule === true ? 'exists' : 'exact', value: attrRule };
      }
      
      if (attrVal === undefined) return false;
      
      switch (attrRule.mode) {
        case 'exists': break;
        case 'exact': case '': if (attrVal !== attrRule.value) return false; break;
        case '*': if (attrVal.indexOf(attrRule.value) === -1) return false; break;
        case '^': if (attrVal.indexOf(attrRule.value) !== 0) return false; break;
        case '$': if (attrVal.indexOf(attrRule.value) !== attrVal.length - attrRule.value.length) return false; break;
        case '~':
          var words = attrVal.split(/\s+/);
          if (words.indexOf(attrRule.value) === -1) return false;
          break;
        default: if (attrVal !== attrRule.value) return false;
      }
    }
    
    if (selectorInfo.hasSelector) {
      var innerHtml = element.innerHTML || element.outerHTML;
      var hasElements = findElements(innerHtml, selectorInfo.hasSelector);
      if (hasElements.length === 0) return false;
    }
    
    if (selectorInfo.pseudo === 'contains' && selectorInfo.pseudoArg) {
      var text = element.text ? element.text() : '';
      if (text.indexOf(selectorInfo.pseudoArg) === -1) return false;
    }
    
    return true;
  }

  /**
   * \u5e94\u7528\u4f2a\u9009\u62e9\u5668\u8fc7\u6ee4
   */
  function applyPseudo(elements, pseudo, pseudoArg) {
    if (!pseudo || elements.length === 0) return elements;
    
    switch (pseudo) {
      case 'eq':
        if (pseudoArg !== null) {
          var idx = pseudoArg < 0 ? elements.length + pseudoArg : pseudoArg;
          return (idx >= 0 && idx < elements.length) ? [elements[idx]] : [];
        }
        return elements;
      case 'first': return elements.length > 0 ? [elements[0]] : [];
      case 'last': return elements.length > 0 ? [elements[elements.length - 1]] : [];
      case 'first-of-type': return elements.length > 0 ? [elements[0]] : [];
      case 'last-of-type': return elements.length > 0 ? [elements[elements.length - 1]] : [];
      case 'lt': return pseudoArg !== null ? elements.slice(0, pseudoArg) : elements;
      case 'gt': return pseudoArg !== null ? elements.slice(pseudoArg + 1) : elements;
      case 'even': return elements.filter(function(_, i) { return i % 2 === 0; });
      case 'odd': return elements.filter(function(_, i) { return i % 2 === 1; });
      default: return elements;
    }
  }

  /**
   * \u5728 HTML \u4e2d\u67e5\u627e\u6240\u6709\u5339\u914d\u7684\u5143\u7d20
   */
  function findElements(html, selector) {
    if (!html || !selector) return [];
    
    var selectorInfo = parseSelector(selector);
    var results = [];
    
    var tagToFind = selectorInfo.tagName || '[a-zA-Z][a-zA-Z0-9]*';
    var openTagRegex = new RegExp('<(' + tagToFind + ')(\\s[^>]*)?>|<(' + tagToFind + ')(\\s[^>]*)?/>', 'gi');
    var match;
    
    while ((match = openTagRegex.exec(html)) !== null) {
      var matchedTag = (match[1] || match[3] || '').toLowerCase();
      var attrString = match[2] || match[4] || '';
      var startPos = match.index;
      var isSelfClosing = match[0].endsWith('/>') || SELF_CLOSING_TAGS.test(matchedTag);
      
      var parsedAttrs = parseAttributes(attrString);
      var element = new HtmlElement(matchedTag, parsedAttrs, '', match[0]);
      
      if (!matchesSelector(element, selectorInfo)) continue;
      
      if (!isSelfClosing) {
        var depth = 1;
        var searchPos = startPos + match[0].length;
        var contentStart = searchPos;
        
        var closeTagRegex = new RegExp('<(/?)(' + matchedTag + ')(\\s[^>]*)?>|<' + matchedTag + '(\\s[^>]*)?/>', 'gi');
        closeTagRegex.lastIndex = searchPos;
        
        var tagMatch;
        while ((tagMatch = closeTagRegex.exec(html)) !== null) {
          if (tagMatch[0].endsWith('/>')) continue;
          if (tagMatch[1] === '/') {
            depth--;
            if (depth === 0) {
              element.innerHTML = html.substring(contentStart, tagMatch.index);
              element.outerHTML = html.substring(startPos, tagMatch.index + tagMatch[0].length);
              break;
            }
          } else if (tagMatch[2]) {
            depth++;
          }
        }
      }
      
      results.push(element);
    }
    
    return applyPseudo(results, selectorInfo.pseudo, selectorInfo.pseudoArg);
  }

  // ============================================
  // \u6d77\u9614\u89c6\u754c\u8bed\u6cd5\u8f6c\u6362
  // ============================================
  
  /**
   * \u5c06\u6d77\u9614\u89c6\u754c\u89e3\u6790\u8bed\u6cd5\u8f6c\u6362\u4e3a\u9009\u62e9\u5668
   */
  function parseHikerToJq(parse, first) {
    if (!parse) return parse;
    
    if (contains(parse, '&&')) {
      var parses = parse.split('&&');
      var newParses = [];
      for (var i = 0; i < parses.length; i++) {
        var psList = parses[i].split(' ');
        var ps = psList[psList.length - 1];
        if (!regexTest(NOADD_INDEX, ps)) {
          if (!first && i >= parses.length - 1) {
            newParses.push(parses[i]);
          } else {
            newParses.push(parses[i] + ':eq(0)');
          }
        } else {
          newParses.push(parses[i]);
        }
      }
      parse = newParses.join(' ');
    } else {
      var psList = parse.split(' ');
      var ps = psList[psList.length - 1];
      if (!regexTest(NOADD_INDEX, ps) && first) {
        parse = parse + ':eq(0)';
      }
    }
    return parse;
  }

  /**
   * \u83b7\u53d6\u89e3\u6790\u4fe1\u606f
   */
  function getParseInfo(nparse) {
    var excludes = [];
    var nparseIndex = 0;
    var nparseRule = nparse;
    
    if (contains(nparse, ':eq')) {
      nparseRule = nparse.split(':eq')[0];
      var nparsePos = nparse.split(':eq')[1];
      if (contains(nparseRule, '--')) {
        excludes = nparseRule.split('--').slice(1);
        nparseRule = nparseRule.split('--')[0];
      } else if (contains(nparsePos, '--')) {
        excludes = nparsePos.split('--').slice(1);
        nparsePos = nparsePos.split('--')[0];
      }
      try {
        nparseIndex = parseInt(nparsePos.split('(')[1].split(')')[0]);
      } catch(e) {}
    } else if (contains(nparse, '--')) {
      nparseRule = nparse.split('--')[0];
      excludes = nparse.split('--').slice(1);
    }
    
    return { nparseRule: nparseRule, nparseIndex: nparseIndex, excludes: excludes };
  }

  /**
   * \u91cd\u6392\u76f8\u90bb\u7684 :gt \u548c :lt \u9009\u62e9\u5668
   */
  function reorderAdjacentLtAndGt(selector) {
    var adjacentPattern = /:gt\((\d+)\):lt\((\d+)\)/;
    var match;
    while ((match = adjacentPattern.exec(selector)) !== null) {
      var replacement = ':lt(' + match[2] + '):gt(' + match[1] + ')';
      selector = selector.substring(0, match.index) + replacement + selector.substring(match.index + match[0].length);
      adjacentPattern.lastIndex = match.index;
    }
    return selector;
  }

  /**
   * \u89e3\u6790\u5355\u4e2a\u89c4\u5219
   */
  function parseOneRule(doc, nparse, ret, findElementsFn) {
    var info = getParseInfo(nparse);
    var nparseRule = reorderAdjacentLtAndGt(info.nparseRule);
    
    if (!ret) {
      ret = findElementsFn(doc, nparseRule);
    } else {
      // \u5728\u5df2\u6709\u5143\u7d20\u4e2d\u67e5\u627e
      var newRet = [];
      for (var i = 0; i < ret.length; i++) {
        var innerElements = findElementsFn(ret[i].innerHTML, nparseRule);
        newRet = newRet.concat(innerElements);
      }
      ret = newRet;
    }
    
    if (contains(nparse, ':eq') && ret && ret.length > info.nparseIndex) {
      ret = [ret[info.nparseIndex]];
    }
    
    if (info.excludes.length > 0 && ret && ret.length > 0) {
      // \u6392\u9664\u6307\u5b9a\u6807\u7b7e
      var newRet = [];
      for (var j = 0; j < ret.length; j++) {
        var html = ret[j].innerHTML;
        for (var k = 0; k < info.excludes.length; k++) {
          var excludeRegex = new RegExp('<' + info.excludes[k] + '[^>]*>[\\s\\S]*?</' + info.excludes[k] + '>', 'gi');
          html = html.replace(excludeRegex, '');
          var selfCloseRegex = new RegExp('<' + info.excludes[k] + '[^>]*/>', 'gi');
          html = html.replace(selfCloseRegex, '');
        }
        var newElement = new HtmlElement(ret[j].tagName, ret[j].attributes, html, '');
        newRet.push(newElement);
      }
      ret = newRet;
    }
    
    return ret || [];
  }

  // ============================================
  // JSONPath \u652f\u6301
  // ============================================
  
  /**
   * JSONPath \u67e5\u8be2
   */
  var jsonpath = {
    query: function(jsonObject, path) {
      if (typeof JSONPath !== 'undefined' && JSONPath.JSONPath) {
        return JSONPath.JSONPath({ path: path, json: jsonObject });
      }
      // \u7b80\u6613 JSONPath \u5b9e\u73b0\uff08\u4ec5\u652f\u6301\u57fa\u7840\u8bed\u6cd5\uff09
      try {
        if (!path.startsWith('$.')) path = '$.' + path;
        var keys = path.replace(/^\$\./, '').split('.');
        var result = jsonObject;
        for (var i = 0; i < keys.length; i++) {
          var key = keys[i];
          if (key === '*') {
            if (Array.isArray(result)) return result;
            return [];
          }
          if (key.includes('[')) {
            var bracketMatch = key.match(/([^\[]+)?\[(\d+)\]/);
            if (bracketMatch) {
              var arrKey = bracketMatch[1];
              var idx = parseInt(bracketMatch[2]);
              if (arrKey) result = result[arrKey];
              result = Array.isArray(result) && result[idx] ? result[idx] : undefined;
            }
          } else {
            result = result ? result[key] : undefined;
          }
          if (result === undefined) return [];
        }
        return result !== undefined ? [result] : [];
      } catch(e) {
        return [];
      }
    }
  };

  // ============================================
  // \u5bfc\u51fa API
  // ============================================
  
  /**
   * load - cheerio \u517c\u5bb9\u63a5\u53e3
   */
  function load(html) {
    if (!html) html = '';
    
    function createEmpty() {
      return {
        each: function() {},
        find: function() { return createEmpty(); },
        attr: function() { return ''; },
        text: function() { return ''; },
        html: function() { return ''; },
        toArray: function() { return []; }
      };
    }
    
    function wrapElement(el) {
      if (!el) return createEmpty();
      return {
        find: function(selector) {
          var inner = findElements(el.innerHTML || el.outerHTML || '', selector);
          return inner.length > 0 ? wrapElement(inner[0]) : createEmpty();
        },
        attr: function(name) {
          return (el.attr && el.attr(name)) || (el.attributes && (el.attributes[name] || el.attributes[name.toLowerCase()])) || '';
        },
        text: function() {
          var t = (el.text && el.text()) || '';
          return typeof t === 'string' ? t.trim() : '';
        },
        html: function() {
          return (el.innerHTML || '');
        },
        toArray: function() {
          return [el];
        }
      };
    }
    
    function query(sel) {
      if (typeof sel === 'string') {
        var elements = findElements(html, sel);
        return {
          each: function(cb) {
            for (var i = 0; i < elements.length; i++) {
              cb(i, elements[i]);
            }
          },
          find: function(selector) {
            var first = elements[0];
            return first ? wrapElement(first).find(selector) : createEmpty();
          },
          attr: function(name) {
            var first = elements[0];
            return first ? wrapElement(first).attr(name) : '';
          },
          text: function() {
            var first = elements[0];
            return first ? wrapElement(first).text() : '';
          },
          html: function() {
            var first = elements[0];
            return first ? (first.innerHTML || '') : '';
          },
          toArray: function() {
            return elements;
          }
        };
      }
      if (sel && (sel.innerHTML !== undefined || sel.outerHTML !== undefined)) {
        return wrapElement(sel);
      }
      return createEmpty();
    }
    
    query.html = function() { return html; };
    query.text = function() { return cleanText(html.replace(/<[^>]+>/g, ' ')); };
    
    return query;
  }

  /**
   * pdfa - \u89e3\u6790 HTML \u8fd4\u56de\u5339\u914d\u9009\u62e9\u5668\u7684\u6240\u6709\u5143\u7d20\u6570\u7ec4
   */
  function pdfa(html, parse) {
    if (!html || !parse) return [];
    
    try {
      parse = parseHikerToJq(parse, false);
      var parts = parse.split(' ');
      var currentElements = [html];
      
      for (var i = 0; i < parts.length; i++) {
        var selector = parts[i];
        var newElements = [];
        
        for (var j = 0; j < currentElements.length; j++) {
          var elements;
          if (typeof currentElements[j] === 'string') {
            elements = findElements(currentElements[j], selector);
          } else if (currentElements[j].innerHTML !== undefined) {
            elements = findElements(currentElements[j].innerHTML, selector);
          } else {
            elements = findElements(currentElements[j], selector);
          }
          newElements = newElements.concat(elements);
        }
        
        currentElements = newElements;
        if (currentElements.length === 0) break;
      }
      
      return currentElements.map(function(el) {
        return el.outerHTML;
      });
    } catch (e) {
      console.log('[pdfa] 异常: ' + e.message);
      return [];
    }
  }

  /**
   * pdfh - \u89e3\u6790 HTML \u8fd4\u56de\u5339\u914d\u9009\u62e9\u5668\u7684\u7b2c\u4e00\u4e2a\u5143\u7d20\u7684\u6587\u672c/\u5c5e\u6027
   */
  function pdfh(html, parse, baseUrl) {
    if (!html || !parse) return '';
    
    try {
      if (parse === 'body&&Text' || parse === 'Text') {
        var tempEl = new HtmlElement('body', {}, html, html);
        return cleanText(tempEl.text());
      }
      if (parse === 'body&&Html' || parse === 'Html') {
        return html;
      }
      
      var parts = parse.split('&&');
      var option = null;
      var excludeTag = null;
      var selectors = [];
      
      for (var i = 0; i < parts.length; i++) {
        var part = parts[i].trim();
        if (!part) continue;
        if (part.toLowerCase() === 'body') continue;
        
        if (part.indexOf('--') > -1) {
          var excludeParts = part.split('--');
          part = excludeParts[0];
          excludeTag = excludeParts[1];
        }
        
        if (i === parts.length - 1) {
          var isAttr = (part === 'Text' || part === 'text' || 
                        part === 'Html' || part === 'html' ||
                        /^[\w-]+(\|\|[\w-]+)*$/.test(part));
          var commonTags = /^(div|span|p|a|img|ul|li|ol|h[1-6]|table|tr|td|th|tbody|thead|tfoot|body|head|html|section|article|nav|aside|header|footer|main|form|input|button|select|option|textarea|label|dl|dt|dd|figure|figcaption|video|audio|source|canvas|svg|iframe|script|style|link|meta|br|hr)$/i;
          
          if (isAttr && !commonTags.test(part.split('||')[0].split(':')[0])) {
            option = part;
            continue;
          }
        }
        
        var subParts = part.split(/\s+/);
        for (var j = 0; j < subParts.length; j++) {
          if (subParts[j]) selectors.push(subParts[j]);
        }
      }
      
      var currentHtml = html;
      var element = null;
      
      for (var k = 0; k < selectors.length; k++) {
        var elements = findElements(currentHtml, selectors[k]);
        if (elements.length === 0) return '';
        element = elements[0];
        currentHtml = element.innerHTML;
      }
      
      if (!element) return '';
      
      var processedHtml = element.innerHTML;
      if (excludeTag) {
        var excludeRegex = new RegExp('<' + excludeTag + '[^>]*>[\\s\\S]*?</' + excludeTag + '>', 'gi');
        processedHtml = processedHtml.replace(excludeRegex, '');
        var selfCloseRegex = new RegExp('<' + excludeTag + '[^>]*/>', 'gi');
        processedHtml = processedHtml.replace(selfCloseRegex, '');
      }
      
      if (option) {
        if (option === 'Text' || option === 'text') {
          var tempElement = new HtmlElement(element.tagName, element.attributes, processedHtml, '');
          return cleanText(tempElement.text());
        }
        if (option === 'Html' || option === 'html') {
          return processedHtml;
        }
        
        var attrOptions = option.split('||');
        var attrVal = '';
        
        for (var m = 0; m < attrOptions.length; m++) {
          var opt = attrOptions[m].trim();
          attrVal = element.attr(opt);
          
          if (/style/i.test(opt) && attrVal && attrVal.indexOf('url(') > -1) {
            var urlMatch = attrVal.match(/url\((['"]?)([^)]+)\1\)/);
            if (urlMatch) attrVal = urlMatch[2];
          }
          
          if (attrVal && baseUrl && regexTest(URLJOIN_ATTR.source, opt) && !regexTest(SPECIAL_URL.source, attrVal)) {
            attrVal = attrVal.indexOf('http') > -1 ? 
                      attrVal.slice(attrVal.indexOf('http')) : 
                      urlJoin(baseUrl, attrVal);
          }
          
          if (attrVal) break;
        }
        
        return attrVal;
      }
      
      return element.innerHTML;
    } catch (e) {
      console.log('[pdfh] \u5f02\u5e38: ' + e.message);
      return '';
    }
  }

  /**
   * pd - \u589e\u5f3a\u7248\u7684 pdfh\uff0c\u81ea\u52a8\u5904\u7406URL\u62fc\u63a5\u5e76\u89e3\u7801HTML\u5b9e\u4f53
   */
  function pd(html, parse, baseUrl) {
    if (!baseUrl) {
      baseUrl = (typeof MY_URL !== 'undefined' && MY_URL) ? MY_URL : 
                (typeof HOST !== 'undefined' && HOST) ? HOST : '';
    }
    
    var result = pdfh(html, parse, baseUrl);
    
    if (result) {
      result = result.replace(/&amp;/g, '&')
                     .replace(/&lt;/g, '<')
                     .replace(/&gt;/g, '>')
                     .replace(/&quot;/g, '"')
                     .replace(/&#39;/g, "'")
                     .replace(/&#(\d+);/g, function(match, dec) {
                       return String.fromCharCode(dec);
                     });
    }
    
    if (!result && parse && parse.includes('&&')) {
      var parts = parse.split('&&');
      var lastPart = parts[parts.length - 1];
      
      if (/data-original|data-src|src|original/.test(lastPart)) {
        var possibleAttrs = ['data-original', 'data-src', 'src', 'original'];
        for (var i = 0; i < possibleAttrs.length; i++) {
          var attr = possibleAttrs[i];
          var newParse = parts.slice(0, -1).concat(attr).join('&&');
          var tempResult = pdfh(html, newParse, baseUrl);
          if (tempResult) {
            tempResult = tempResult.replace(/&amp;/g, '&')
                                   .replace(/&lt;/g, '<')
                                   .replace(/&gt;/g, '>')
                                   .replace(/&quot;/g, '"')
                                   .replace(/&#39;/g, "'")
                                   .replace(/&#(\d+);/g, function(match, dec) {
                                     return String.fromCharCode(dec);
                                   });
            result = tempResult;
            break;
          }
        }
      }
    }
    
    if (result && baseUrl && regexTest(URLJOIN_ATTR.source, parse) && !regexTest(SPECIAL_URL.source, result)) {
      if (result.indexOf('http') > -1) {
        result = result.slice(result.indexOf('http'));
      } else {
        result = urlJoin(baseUrl, result);
      }
    }
    
    return result;
  }

  /**
   * pdfl - \u89e3\u6790HTML\u83b7\u53d6\u5217\u8868\u6570\u636e
   */
  function pdfl(html, parse, listText, listUrl, baseUrl) {
    if (!html || !parse) return [];
    
    var elements = pdfa(html, parse);
    var results = [];
    
    for (var i = 0; i < elements.length; i++) {
      var itemHtml = elements[i];
      var title = pdfh(itemHtml, listText, baseUrl);
      var url = pd(itemHtml, listUrl, baseUrl);
      if (title || url) {
        results.push(title + '$' + url);
      }
    }
    
    return results;
  }

  /**
   * pjfh - \u89e3\u6790JSON\u83b7\u53d6\u5355\u4e2a\u503c
   */
  function pjfh(json, parse, addUrl, baseUrl) {
    if (!json || !parse) return '';
    
    try {
      if (typeof json === 'string') {
        json = JSON.parse(json);
      }
    } catch(e) {
      console.log('[pjfh] JSON\u89e3\u6790\u5931\u8d25: ' + e.message);
      return '';
    }
    
    if (!parse.startsWith('$.')) parse = '$.' + parse;
    
    var result = '';
    var paths = parse.split('||');
    
    for (var i = 0; i < paths.length; i++) {
      var path = paths[i];
      var queryResult = jsonpath.query(json, path);
      result = Array.isArray(queryResult) ? (queryResult[0] || '') : (queryResult || '');
      if (addUrl && result && baseUrl) {
        result = urlJoin(baseUrl, result);
      }
      if (result) break;
    }
    
    return result;
  }

  /**
   * pj - \u89e3\u6790JSON\u5e76\u81ea\u52a8\u62fc\u63a5URL
   */
  function pj(json, parse, baseUrl) {
    if (!baseUrl) {
      baseUrl = (typeof MY_URL !== 'undefined' && MY_URL) ? MY_URL : 
                (typeof HOST !== 'undefined' && HOST) ? HOST : '';
    }
    return pjfh(json, parse, true, baseUrl);
  }

  /**
   * pjfa - \u89e3\u6790JSON\u83b7\u53d6\u6570\u7ec4\u7ed3\u679c
   */
  function pjfa(json, parse) {
    if (!json || !parse) return [];
    
    try {
      if (typeof json === 'string') {
        json = JSON.parse(json);
      }
    } catch(e) {
      return [];
    }
    
    if (!parse.startsWith('$.')) parse = '$.' + parse;
    
    var result = jsonpath.query(json, parse);
    if (Array.isArray(result) && Array.isArray(result[0]) && result.length === 1) {
      return result[0];
    }
    
    return result || [];
  }

  /**
   * Jsoup \u7c7b - \u517c\u5bb9\u539f\u6709\u63a5\u53e3
   */
  function Jsoup(MY_URL) {
    this.MY_URL = MY_URL || '';
    this.pdfh_html = '';
    this.pdfa_html = '';
  }
  
  Jsoup.prototype = {
    test: function(pattern, text) {
      return regexTest(pattern, text);
    },
    contains: function(text, match) {
      return contains(text, match);
    },
    parseHikerToJq: parseHikerToJq,
    getParseInfo: getParseInfo,
    reorderAdjacentLtAndGt: reorderAdjacentLtAndGt,
    parseText: function(text) {
      return cleanText(text);
    },
    pdfa: function(html, parse) {
      return pdfa(html, parse);
    },
    pdfl: function(html, parse, listText, listUrl, MY_URL) {
      return pdfl(html, parse, listText, listUrl, MY_URL || this.MY_URL);
    },
    pdfh: function(html, parse, baseUrl) {
      return pdfh(html, parse, baseUrl || this.MY_URL);
    },
    pd: function(html, parse, baseUrl) {
      return pd(html, parse, baseUrl || this.MY_URL);
    },
    pjfh: function(json, parse, addUrl) {
      return pjfh(json, parse, addUrl, this.MY_URL);
    },
    pj: function(json, parse) {
      return pj(json, parse, this.MY_URL);
    },
    pjfa: function(json, parse) {
      return pjfa(json, parse);
    },
    pq: function(html) {
      return load(html);
    }
  };

  // ============================================
  // \u5bfc\u51fa\u5230\u5168\u5c40
  // ============================================
  
  var exports = {
    // HTML\u89e3\u6790
    pdfa: pdfa,
    pdfh: pdfh,
    pd: pd,
    pdfl: pdfl,
    load: load,
    
    // JSON\u89e3\u6790
    pjfh: pjfh,
    pj: pj,
    pjfa: pjfa,
    jsonpath: jsonpath,
    
    // \u5de5\u5177\u51fd\u6570
    urlJoin: urlJoin,
    cleanText: cleanText,
    
    // \u7c7b
    Jsoup: Jsoup,
    HtmlElement: HtmlElement,
    
    // \u517c\u5bb9\u522b\u540d
    pdfa_advanced: pdfa,
    pdfh_advanced: pdfh,
    pd_advanced: pd,
    pdfa_lite: pdfa,
    pdfh_lite: pdfh,
    pd_lite: pd
  };
  
  // \u521b\u5efa jsp \u5bf9\u8c61
  var jsp = {
    pdfa: pdfa,
    pdfh: pdfh,
    pd: pd,
    pdfl: pdfl,
    pjfh: pjfh,
    pj: pj,
    pjfa: pjfa,
    Jsoup: Jsoup
  };
  
  // \u8bbe\u7f6e\u5230\u5168\u5c40
  for (var key in exports) {
    global[key] = exports[key];
  }
  
  global.jsp = jsp;
  global.cheerio = { load: load };
  
  if (typeof globalThis !== 'undefined') {
    for (var key in exports) {
      globalThis[key] = exports[key];
    }
    globalThis.jsp = jsp;
    globalThis.cheerio = { load: load };
  }
  
  console.log('[\u7edf\u4e00\u89e3\u6790\u5668] HTML/JSON \u89e3\u6790\u5668\u5df2\u52a0\u8f7d');

})(typeof globalThis !== 'undefined' ? globalThis : (typeof window !== 'undefined' ? window : this));