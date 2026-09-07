            "vod_year": row["vod_year"] or "",
            "vod_tags": tags,
            "vod_content": row["vod_content"] or "",
            "vod_play_from": row["vod_play_from"] or "whos.tv",
            "vod_play_url": play_url,
            "type_name": row["type_name"] or "成人影片"
        }]}

    def _fix_v_encoded_url(self, raw_url):
        if not raw_url:
            return raw_url
        for prefix in ["高清$ ", "高清$", "高清 ", "高清"]:
            if raw_url.startswith(prefix):
                raw_url = raw_url[len(prefix):]
                break
        url = raw_url.replace('://V', '://')
        url = url.replace('V', '/')
        return url

    # ==================== 播放 ====================
    def playerContent(self, flag, id, vipFlags=None):
        playurl = id.split("|")[0]
        playurl = self._fix_v_encoded_url(playurl)
        headers = {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; MIbox PRO Build/PI)"}
        if playurl.strip().lower().endswith('.m3u8'):
            try:
                parsed = urlparse(playurl)
                headers["Referer"] = f"{parsed.scheme}://{parsed.netloc}/"
            except:
                pass
        return {"parse": 0, "url": playurl, "header": headers}

    # ==================== 搜索（暂不启用） ====================
    def searchContent(self, key, quick, pg="1"):
        return {"list": [], "page": pg}


# ========== 蜜桃主爬虫（不变） ==========
