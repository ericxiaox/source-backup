# coding=utf-8
# !/usr/bin/python
# 蜜桃视频 T3 爬虫（完全合并涩库引擎 + 指定扫描目录）
import sys
sys.path.append('..')

from base.spider import BaseSpider
import requests
import json
import base64
import hashlib
import time
import re
import os
import string
import random
import threading
import sqlite3
from urllib.parse import quote, unquote, urlparse
from Crypto.Cipher import AES
import concurrent.futures

# ========== 蜜桃配置 ==========
TIMEOUT = 10
SITES_REMOTE_URL = ""
SITES = [
    {'name': 'nht966', 'host': 'https://www.nht966hht.vip:9527'},
    {'name': 'httre666', 'host': 'https://www.newhttestre666.cc'},
]
BACKUP_SITES = [
    {'name': 'backup1', 'host': 'https://www.mitao555.com'},
    {'name': 'backup2', 'host': 'https://www.mitao666.cc'},
]
SIGN_KEY  = 'opum3_Loily$SV^6H'
BUNDLE_ID = 'com.ht9.web20.video'
BRAND_ID  = 'hongtao'
VERSION   = '1.0.0'
PROJECT_ID = '1'
PROXY_TYPE = 'mitao_img'

def log(msg):
    print(f"[蜜桃] {time.strftime('%H:%M:%S')} {msg}")

# ========== 涩库引擎（完整合并，仅修改扫描目录） ==========
class SikuEngine:
    DB_DIRS = [
        "/storage/emulated/0/纯福利/db/",
        "/storage/emulated/0/女优库/",
        "/storage/emulated/0/私藏视频/",
        "/storage/emulated/0/lz/db/"
    ]
    DEFAULT_COVER = "https://cloud.7so.top/f/p8PPHA/%E5%90%88%E9%9B%86.png"
    MOVIE_ICON = "https://img.icons8.com/color/512/movie.png"

    def __init__(self):
        self._db_cache = {}
        self.databases = {}
        self.sub_icons = {}

    def init(self, extend=""):
        self._auto_scan_databases()
        icon_config_path = "/storage/emulated/0/私藏视频/二级分类.json"
        if os.path.exists(icon_config_path):
            try:
                with open(icon_config_path, 'r', encoding='utf-8') as f:
                    self.sub_icons = json.load(f)
            except:
                pass

    def _auto_scan_databases(self):
        seen_paths = set()
        for d in self.DB_DIRS:
            if not os.path.exists(d):
                continue
            for root, _, files in os.walk(d):
                for file in files:
                    if file.endswith(".db"):
                        full_path = os.path.join(root, file)
                        abs_path = os.path.abspath(full_path)
                        if abs_path in seen_paths:
                            continue
                        seen_paths.add(abs_path)
                        db_key = f"auto_{file}"
                        if db_key in self.databases:
                            db_key = f"auto_{os.path.basename(root)}_{file}"
                        self.databases[db_key] = {"name": file, "path": abs_path}

    def _get_connection(self, db_key):
        info = self.databases.get(db_key)
        if not info or not os.path.exists(info["path"]):
            return None
        conn = sqlite3.connect(info["path"])
        conn.row_factory = sqlite3.Row
        return conn

    def _is_exclusive_db(self, conn):
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='video_actress'")
            return cur.fetchone() is not None
        except:
            return False

    # ==================== 首页（数据库列表） ====================
    def homeContent(self, filter):
        classes = []
        for db_key, db_info in self.databases.items():
            name = os.path.splitext(db_info['name'])[0]
            conn = self._get_connection(db_key)
            count_str = ""
            if conn:
                try:
                    if self._is_exclusive_db(conn):
                        cur = conn.cursor()
                        cur.execute("SELECT COUNT(*) FROM videos")
                        total = cur.fetchone()[0]
                        count_str = f" ({total})"
                except:
                    pass
                finally:
                    conn.close()
            classes.append({
                "type_id": f"siku:{db_key}",  # 涩库内部路径前缀
                "type_name": f"{name}{count_str}",
                "type_pic": self.DEFAULT_COVER,
                "pic": self.DEFAULT_COVER,
                "icon": self.DEFAULT_COVER,
                "vod_pic": self.DEFAULT_COVER
            })
        return {"class": classes}

    # ==================== 分类内容 ====================
    def categoryContent(self, tid, pg, filter=None, extend=None):
        """tid 格式: siku:db_key$sub..."""
        if tid.startswith("siku:"):
            tid = tid[5:]
        parts = tid.split('$')
        db_key = parts[0]
        conn = self._get_connection(db_key)
        if not conn:
            return {"list": []}
        if self._is_exclusive_db(conn):
            result = self._exclusive_category(conn, db_key, parts, pg)
        else:
            result = self._legacy_category(conn, db_key, parts, pg)
        conn.close()
        # 所有返回的 vod_id 添加前缀 siku: 以便蜜桃路由
        for vod in result.get('list', []):
            if 'vod_id' in vod:
                vod['vod_id'] = f"siku:{vod['vod_id']}"
        return result

    def _exclusive_category(self, conn, db_key, parts, pg):
        class_id = parts[1] if len(parts) > 1 else ""
        sub_name = parts[2] if len(parts) > 2 else ""

        if not class_id:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM video_actress")
            actress_cnt = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM videos")
            video_total = cur.fetchone()[0]

            vod_list = [
                {"vod_id": f"{db_key}$actor_ranking", "vod_name": f"演员榜 ({actress_cnt})", "vod_pic": self.DEFAULT_COVER, "vod_tag": "folder"},
                {"vod_id": f"{db_key}$video_ranking", "vod_name": f"影片榜 ({video_total})", "vod_pic": self.DEFAULT_COVER, "vod_tag": "folder"},
            ]
            return {"page": 1, "pagecount": 2, "limit": 20, "list": vod_list}

        if class_id == "actor_ranking":
            if not sub_name:
                return self._list_actresses(conn, db_key, pg)
            else:
                return self._list_videos_by_actress(conn, db_key, sub_name, pg)

        elif class_id == "video_ranking":
            if not sub_name:
                return self._list_video_ranking(conn, db_key, pg)
            else:
                return self._list_videos_by_category(conn, db_key, sub_name, pg)

        elif class_id == "actress":
            if not sub_name:
                return self._list_actresses(conn, db_key, pg)
            else:
                return self._list_videos_by_actress(conn, db_key, sub_name, pg)

        elif class_id == "video_cate":
            if not sub_name:
                return self._list_hot_videos(conn, db_key, pg)
            else:
                return self._list_videos_by_category(conn, db_key, sub_name, pg)

        elif class_id == "tag":
            if not sub_name:
                return self._list_categories(conn, db_key, pg, "video_cate")
            else:
                return self._list_videos_by_category(conn, db_key, sub_name, pg)

        return {"list": []}

    def _list_actresses(self, conn, db_key, pg):
        cur = conn.cursor()
        cur.execute("""
            SELECT a.name, a.avatar, COUNT(va.vod_id) as cnt
            FROM actresses a
            LEFT JOIN video_actress va ON a.cate_id = va.cate_id
            GROUP BY a.cate_id HAVING cnt > 0
            ORDER BY cnt DESC
        """)
        rows = cur.fetchall()
        return self._paginate_dirs(rows, pg, db_key, "actor_ranking")

    def _list_hot_videos(self, conn, db_key, pg):
        cur = conn.cursor()
        cur.execute("""
            SELECT v.title, v.pic_url, COUNT(vr.vod_id) as cnt
            FROM videos v
            JOIN video_ranking vr ON v.vod_id = vr.vod_id
            GROUP BY v.vod_id
            ORDER BY cnt DESC
            LIMIT 100
        """)
        rows = cur.fetchall()
        if not rows:
            cur.execute("SELECT title, pic_url, 1 as cnt FROM videos ORDER BY created_at DESC LIMIT 100")
            rows = cur.fetchall()
        limit = 20
        page = int(pg)
        start = (page - 1) * limit
        paged = rows[start:start+limit]
        vod_list = []
        for r in paged:
            name = r[0]
            pic = r[1] if r[1] else self.MOVIE_ICON
            vod_list.append({
                "vod_id": f"{db_key}$video_cate${name}",
                "vod_name": name,
                "vod_pic": pic,
                "vod_tag": "video"
            })
        return {"page": page, "pagecount": page+1, "limit": limit, "list": vod_list}

    def _list_video_ranking(self, conn, db_key, pg):
        cur = conn.cursor()
        cur.execute("""
            SELECT v.vod_id, v.title, v.pic_url, COUNT(vr.vod_id) as cnt
            FROM videos v
            JOIN video_ranking vr ON v.vod_id = vr.vod_id
            GROUP BY v.vod_id
            ORDER BY cnt DESC
            LIMIT 100
        """)
        rows = cur.fetchall()
        if not rows:
            cur.execute("SELECT vod_id, title, pic_url, 1 as cnt FROM videos ORDER BY created_at DESC LIMIT 100")
            rows = cur.fetchall()
        limit = 20
        page = int(pg)
        start = (page - 1) * limit
        paged = rows[start:start+limit]
        vod_list = []
        for r in paged:
            vid = r[0]
            name = r[1]
            pic = r[2] if r[2] else self.MOVIE_ICON
            vod_list.append({
                "vod_id": f"{db_key}#ID#{vid}",
                "vod_name": name,
                "vod_pic": pic,
                "vod_tag": "video"
            })
        return {"page": page, "pagecount": page+1, "limit": limit, "list": vod_list}

    def _list_categories(self, conn, db_key, pg, cat_type="video_cate"):
        cur = conn.cursor()
        cur.execute("SELECT main_category, COUNT(*) as cnt FROM video_category GROUP BY main_category ORDER BY cnt DESC")
        rows = cur.fetchall()
        limit = 20
        page = int(pg)
        start = (page - 1) * limit
        paged = rows[start:start+limit]
        vod_list = []
        for r in paged:
            cat = r[0]
            cnt = r[1]
            vod_list.append({
                "vod_id": f"{db_key}${cat_type}${cat}",
                "vod_name": f"{cat} ({cnt})",
                "vod_pic": self.DEFAULT_COVER,
                "vod_tag": "folder"
            })
        return {"page": page, "pagecount": page+1, "limit": limit, "list": vod_list}

    def _list_videos_by_category(self, conn, db_key, category_val, pg):
        limit = 20
        page = int(pg)
        offset = (page - 1) * limit
        cur = conn.cursor()
        cur.execute("""
            SELECT v.vod_id, v.title, v.pic_url, v.vod_remarks
            FROM videos v
            JOIN video_category vc ON v.vod_id = vc.vod_id
            WHERE vc.main_category = ?
            LIMIT ? OFFSET ?
        """, (category_val, limit, offset))
        rows = cur.fetchall()
        vod_list = []
        for r in rows:
            pic = r[2] if r[2] else self.MOVIE_ICON
            vod_list.append({
                "vod_id": f"{db_key}#ID#{r[0]}",
                "vod_name": r[1] or r[0],
                "vod_pic": pic,
                "vod_remarks": r[3] or ""
            })
        return {"page": page, "pagecount": page+1, "limit": limit, "list": vod_list}

    def _list_videos_by_actress(self, conn, db_key, actress_name, pg):
        limit = 20
        page = int(pg)
        offset = (page - 1) * limit
        cur = conn.cursor()
        cur.execute("""
            SELECT v.vod_id, v.title, v.pic_url, v.vod_remarks
            FROM videos v
            JOIN video_actress va ON v.vod_id = va.vod_id
            JOIN actresses a ON va.cate_id = a.cate_id
            WHERE a.name = ?
            LIMIT ? OFFSET ?
        """, (actress_name, limit, offset))
        rows = cur.fetchall()
        vod_list = []
        for r in rows:
            pic = r[2] if r[2] else self.MOVIE_ICON
            vod_list.append({
                "vod_id": f"{db_key}#ID#{r[0]}",
                "vod_name": r[1] or r[0],
                "vod_pic": pic,
                "vod_remarks": r[3] or ""
            })
        return {"page": page, "pagecount": page+1, "limit": limit, "list": vod_list}

    def _paginate_dirs(self, rows, pg, db_key, cat_type):
        limit = 20
        page = int(pg)
        start = (page - 1) * limit
        paged = rows[start:start + limit]
        vod_list = []
        for r in paged:
            name = r[0]
            avatar = r[1] or ""
            cnt = r[2]
            pic = avatar if avatar else self.DEFAULT_COVER
            vod_list.append({
                "vod_id": f"{db_key}${cat_type}${name}",
                "vod_name": f"{name} ({cnt})",
                "vod_pic": pic,
                "vod_tag": "folder"
            })
        return {"page": page, "pagecount": page + 1, "limit": limit, "list": vod_list}

    # ==================== 旧版数据库兼容 ====================
    def _legacy_category(self, conn, db_key, parts, pg):
        curr_path = parts[1] if len(parts) > 1 else ""
        cache_key = f"tree_{db_key}"
        if cache_key not in self._db_cache:
            auto_info = self._get_auto_mapping(conn)
            if not auto_info:
                return {"list": []}
            cursor = conn.cursor()
            table_name = auto_info['table_name']
            mapping = auto_info['field_mapping']

            cursor.execute(f"PRAGMA table_info(`{table_name}`)")
            all_cols = [str(r[1]) for r in cursor.fetchall()]

            filter_field = mapping.get("category_field")
            if not filter_field:
                for cand in ["type_name", "category", "cate_name", "type", "tag", "class_name", "actress_id"]:
                    if cand in all_cols:
                        filter_field = cand
                        break
            if not filter_field:
                self._db_cache[cache_key] = {
                    "types": [], "counts": {}, "field": None,
                    "table": table_name, "mapping": mapping, "avatar_map": {}
                }
                return self._legacy_fetch_video_list(conn, db_key, table_name, mapping, None, None, pg, 20, (int(pg)-1)*20)

            cursor.execute(f"SELECT `{filter_field}`, COUNT(*) FROM `{table_name}` WHERE `{filter_field}` IS NOT NULL GROUP BY `{filter_field}`")
            raw_data = cursor.fetchall()
            type_counts = {str(row[0]): row[1] for row in raw_data}
            avatar_map = {}
            if "actress_avatar" in all_cols:
                try:
                    cursor.execute(
                        f"SELECT `{filter_field}`, `actress_avatar` FROM `{table_name}` "
                        "WHERE `actress_avatar` IS NOT NULL AND `actress_avatar` != ''"
                    )
                    for row in cursor.fetchall():
                        cat_val = str(row[0])
                        avatar_url = row[1]
                        if cat_val not in avatar_map:
                            avatar_map[cat_val] = avatar_url
                except: pass
            self._db_cache[cache_key] = {
                "types": list(type_counts.keys()), "counts": type_counts,
                "field": filter_field, "table": table_name,
                "mapping": mapping, "avatar_map": avatar_map
            }

        db_data = self._db_cache[cache_key]
        all_vals = db_data["types"]
        all_counts = db_data["counts"]
        avatar_map = db_data.get("avatar_map", {})
        filter_field = db_data.get("field")
        if not filter_field:
            return self._legacy_fetch_video_list(conn, db_key, db_data["table"], db_data["mapping"], None, None, pg, 20, (int(pg)-1)*20)

        sub_dirs_info = {}
        for val in all_vals:
            count = all_counts.get(val, 0)
            if curr_path == "":
                d = val.split('/')[0]
                sub_dirs_info[d] = sub_dirs_info.get(d, 0) + count
            elif val.startswith(curr_path + "/"):
                suffix = val[len(curr_path):].lstrip('/')
                if suffix:
                    d = f"{curr_path}/{suffix.split('/')[0]}"
                    sub_dirs_info[d] = sub_dirs_info.get(d, 0) + count

        limit = 20
        offset = (int(pg) - 1) * limit
        if not sub_dirs_info:
            return self._legacy_fetch_video_list(conn, db_key, db_data["table"], db_data["mapping"],
                                                 filter_field, curr_path if curr_path else None, pg, limit, offset)
        if len(sub_dirs_info) == 1:
            single_dir = list(sub_dirs_info.keys())[0]
            has_deeper = any(v.startswith(single_dir + "/") for v in all_vals)
            if not has_deeper:
                return self._legacy_fetch_video_list(conn, db_key, db_data["table"], db_data["mapping"],
                                                     filter_field, single_dir, pg, limit, offset)

        sorted_dirs = sorted(sub_dirs_info.keys(), key=lambda d: (-sub_dirs_info[d], d))
        paged_dirs = sorted_dirs[offset : offset + limit]
        vod_list = []
        for d in paged_dirs:
            display_name = d.split('/')[-1]
            num = sub_dirs_info[d]
            pic = avatar_map.get(d) or self.sub_icons.get(d) or self.sub_icons.get(display_name) or self.DEFAULT_COVER
            vod_list.append({
                "vod_id": f"{db_key}${d}",
                "vod_name": f"{display_name} ({num})",
                "vod_pic": pic,
                "vod_tag": "folder",
                "style": {"type": "rect", "ratio": 1.8}
            })
        return {"page": int(pg), "pagecount": int(pg) + 1, "limit": limit, "list": vod_list}

    def _get_auto_mapping(self, conn):
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            if not tables:
                return None
            target_table = next((t for t in ["videos", "vod_unified_data", "cj", "vod", "data", "list", "video_detail"] if t in tables), tables[-1])
            cursor.execute(f"PRAGMA table_info(`{target_table}`)")
            cols = [str(r[1]) for r in cursor.fetchall()]
            mapping = {}
            field_candidates = {
                "vod_id": ["id", "vod_id", "uuid", "guid", "vid"],
                "vod_name": ["name", "vod_name", "title", "subject", "display_name"],
                "vod_pic": ["image", "vod_pic", "pic", "pic_url", "thumbnail", "img", "cover"],
                "vod_play_url": ["play_url", "vod_play_url", "url", "link", "m3u8_url"],
                "vod_remarks": ["vod_remarks", "remarks", "note", "desc"],
                "category_field": ["type_name", "category_id", "class_name", "cate_name", "actress_id", "tag", "type", "category"],
                "vod_actor": ["vod_actor", "actor", "star", "actress", "artist", "performer"],
                "vod_content": ["vod_content", "description", "summary", "intro", "detail", "content"],
                "vod_pubdate": ["vod_pubdate", "pubdate", "release_date", "date"],
                "vod_area": ["vod_area", "area", "region", "country"],
                "vod_year": ["vod_year", "year"],
                "vod_tags": ["vod_tags", "tags", "keywords", "label"],
                "vod_play_from": ["vod_play_from", "play_from", "source"]
            }
            for target_field, candidates in field_candidates.items():
                matches = [cand for cand in candidates if cand in cols]
                mapping[target_field] = matches[0] if matches else None
            return {"table_name": target_table, "field_mapping": mapping}
        except:
            return None

    def _legacy_fetch_video_list(self, conn, db_key, table_name, mapping, filter_field, category_val, pg, limit, offset):
        cursor = conn.cursor()
        vod_list = []
        f_id = mapping.get("vod_id") or "rowid"
        f_name = mapping.get("vod_name") or "rowid"
        f_pic = mapping.get("vod_pic") or "''"
        f_rem = mapping.get("vod_remarks") or "''"
        try:
            if category_val is not None and filter_field is not None:
                sql = f"SELECT `{f_id}`, `{f_name}`, `{f_pic}`, `{f_rem}` FROM `{table_name}` WHERE `{filter_field}` = ? LIMIT ? OFFSET ?"
                cursor.execute(sql, (category_val, limit, offset))
            else:
                sql = f"SELECT `{f_id}`, `{f_name}`, `{f_pic}`, `{f_rem}` FROM `{table_name}` LIMIT ? OFFSET ?"
                cursor.execute(sql, (limit, offset))
            for row in cursor.fetchall():
                pic = str(row[2]) if row[2] else ""
                if not pic:
                    pic = self.MOVIE_ICON
                vod_list.append({
                    "vod_id": f"{db_key}#ID#{row[0]}",
                    "vod_name": str(row[1]),
                    "vod_pic": pic,
                    "vod_remarks": str(row[3]) if len(row) > 3 else ""
                })
        except:
            pass
        return {"page": int(pg), "pagecount": int(pg) + 1, "limit": limit, "list": vod_list}

    # ==================== 详情 ====================
    def detailContent(self, ids):
        mid = ids[0]
        if mid.startswith("siku:"):
            mid = mid[5:]
        if '#ID#' in mid:
            parts = mid.split('#ID#')
            db_key, real_id = parts[0], parts[1]
        elif '#NAME#' in mid:
            parts = mid.split('#NAME#')
            db_key, vod_name = parts[0], parts[1]
            real_id = vod_name
        else:
            return {"list": []}
        conn = self._get_connection(db_key)
        if not conn:
            return {"list": []}
        if self._is_exclusive_db(conn):
            return self._exclusive_detail(conn, db_key, real_id)
        return self._legacy_detail(conn, db_key, real_id)

    def _legacy_detail(self, conn, db_key, real_id):
        auto_info = self._get_auto_mapping(conn)
        if not auto_info:
            conn.close()
            return {"list": []}
        table_name = auto_info["table_name"]
        mapping = auto_info["field_mapping"]
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        id_col = mapping.get("vod_id") or "rowid"
        cursor.execute(f"SELECT * FROM `{table_name}` WHERE `{id_col}` = ?", (real_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"list": []}
        def get_val(m_key):
            real_col = mapping.get(m_key)
            return str(row[real_col]) if (real_col and real_col in row.keys() and row[real_col] is not None) else ""
        raw_play_url = get_val("vod_play_url")
        play_url = raw_play_url.split('$$$')[-1] if '$$$' in raw_play_url else raw_play_url
        play_url = self._fix_v_encoded_url(play_url)
        vod = {
            "vod_id": f"siku:{db_key}#ID#{real_id}",
            "vod_name": get_val("vod_name"),
            "vod_pic": get_val("vod_pic"),
            "vod_actor": get_val("vod_actor") or get_val("category_field"),
            "vod_director": "",
            "vod_remarks": get_val("vod_remarks"),
            "vod_pubdate": get_val("vod_pubdate"),
            "vod_area": get_val("vod_area"),
            "vod_year": get_val("vod_year"),
            "vod_tags": get_val("vod_tags"),
            "vod_content": get_val("vod_content") or get_val("vod_remarks"),
            "vod_play_from": get_val("vod_play_from") or "自动识别",
            "vod_play_url": play_url,
            "type_name": get_val("category_field") or get_val("type_name")
        }
        conn.close()
        return {"list": [vod]}

    def _exclusive_detail(self, conn, db_key, vid_or_name):
        cur = conn.cursor()
        cur.execute("SELECT * FROM videos WHERE vod_id = ? OR title = ?", (vid_or_name, vid_or_name))
        row = cur.fetchone()
        if not row:
            conn.close()
            return {"list": []}
        vod_id = row["vod_id"]
        actors, tags = "", ""
        try:
            cur.execute("SELECT a.name FROM actresses a JOIN video_actress va ON a.cate_id = va.cate_id WHERE va.vod_id = ?", (vod_id,))
            actors = ",".join([r[0] for r in cur.fetchall()])
            cur.execute("SELECT t.tag_name FROM tags t JOIN video_tag vt ON t.tag_name = vt.tag_name WHERE vt.vod_id = ?", (vod_id,))
            tags = ",".join([r[0] for r in cur.fetchall()])
        except:
            pass
        raw_play = row["m3u8_url"] or row["vod_play_url"] or ""
        play_url = self._fix_v_encoded_url(raw_play)
        conn.close()
        return {"list": [{
            "vod_id": f"siku:{db_key}#ID#{vod_id}",
            "vod_name": row["title"] or vid_or_name,
            "vod_pic": row["pic_url"] or "",
            "vod_actor": actors,
            "vod_director": "whos.tv",
            "vod_remarks": row["vod_remarks"] or "",
            "vod_pubdate": row["vod_pubdate"] or "",
            "vod_area": row["vod_area"] or "",
