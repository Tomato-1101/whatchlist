import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import re

from .base import BaseScraper
from ..config import KABUTAN_URLS, USER_AGENT


class KabutanScraper(BaseScraper):
    """カブタンのスクレイパー"""

    def fetch(self, url: str) -> str:
        """ページを取得"""
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text

    def parse(self, html: str) -> List[str]:
        """HTMLから銘柄コードを抽出"""
        soup = BeautifulSoup(html, "lxml")
        codes = []

        # 銘柄コードは /stock/?code=XXXX のリンクから抽出
        # ただし、td要素内のもののみ（ヘッダー部分のdiv内リンクを除外）
        links = soup.find_all("a", href=re.compile(r"/stock/\?code=\d{4}"))

        for link in links:
            # 親要素がtdの場合のみ抽出
            if link.parent and link.parent.name == "td":
                match = re.search(r"code=(\d{4})", link["href"])
                if match:
                    code = match.group(1)
                    if code not in codes:  # 重複を除外
                        codes.append(code)

        return codes

    def get_url(self, ranking_type: str) -> Optional[str]:
        """ランキング種類に対応するURLを取得"""
        return KABUTAN_URLS.get(ranking_type)
