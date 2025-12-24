import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import re

from .base import BaseScraper
from ..config import KABUMAP_URLS, USER_AGENT


class KabumapScraper(BaseScraper):
    """デイトレードマップ（カブマップ）のスクレイパー"""

    def fetch(self, url: str) -> str:
        """ページを取得"""
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text

    def parse(self, html: str) -> List[str]:
        """HTMLから銘柄コードを抽出"""
        soup = BeautifulSoup(html, "lxml")
        codes = []

        # ランキングテーブルから4桁の銘柄コードを抽出
        # テーブルの行を探す
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                for cell in cells:
                    text = cell.get_text(strip=True)
                    # 4桁の数字を探す
                    match = re.search(r"\b(\d{4})\b", text)
                    if match:
                        code = match.group(1)
                        if code not in codes:
                            codes.append(code)

        return codes

    def get_url(self, ranking_type: str) -> Optional[str]:
        """ランキング種類に対応するURLを取得"""
        return KABUMAP_URLS.get(ranking_type)
