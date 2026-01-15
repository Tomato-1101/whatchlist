import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Tuple
import re

from .base import BaseScraper
from ..config import STOCKWEATHER_URLS, USER_AGENT


class StockWeatherScraper(BaseScraper):
    """ストックウェザーのスクレイパー"""

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

        # ランキングテーブルから銘柄コードを抽出
        # stockdetail.aspx?cntcode=JP&skubun=1&stkcode=[銘柄コード] の形式
        # 銘柄コードは4桁の数字、または3-4桁の数字+1文字のアルファベット（例: 485A）
        links = soup.find_all("a", href=re.compile(r"stockdetail\.aspx.*stkcode="))

        for link in links:
            # 4桁の数字、または3-4桁の数字+1文字のアルファベットを抽出
            match = re.search(r"stkcode=(\d{3,4}[A-Z]?)", link["href"])
            if match:
                code = match.group(1)
                if code not in codes:  # 重複を除外
                    codes.append(code)

        return codes

    def get_url(self, ranking_type: str) -> Optional[str]:
        """ランキング種類に対応するURLを取得"""
        return STOCKWEATHER_URLS.get(ranking_type)
