            doc = self.html(rsp.text)
            videos = self._get_videos(doc, limit=20)
            result['list'] = videos
        except Exception as e:
            self.log(f"首页获取出错: {str(e)}")
            result['list'] = []
        return result
