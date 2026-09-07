
    def homeContent(self, filter):
        self._select_best_site()
        self._ensure_session()
        if not self._categories:
