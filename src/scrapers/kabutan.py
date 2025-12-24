import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import BaseScraper
from ..config import KABUTAN_URLS, USER_AGENT


class KabutanScraper(BaseScraper):
    """カブタンのスクレイパー"""

    def fetch(self, url: str) -> str:
        """ページを取得（複数ページを並列取得）"""
        # この関数は互換性のために残すが、実際の処理はget_rankingで行う
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
        # 4桁の数字、または3-4桁の数字+1文字のアルファベット（例: 285A）に対応
        links = soup.find_all("a", href=re.compile(r"/stock/\?code="))

        for link in links:
            # 親要素がtdの場合のみ抽出
            if link.parent and link.parent.name == "td":
                # 4桁の数字、または3-4桁の数字+1文字のアルファベットを抽出
                match = re.search(r"code=(\d{3,4}[A-Z]?)", link["href"])
                if match:
                    code = match.group(1)
                    # 3桁以下は除外（正規のコードは4桁以上）
                    if len(code) >= 4 and code not in codes:
                        codes.append(code)

        return codes

    def get_ranking(self, ranking_type: str, count: int = 50) -> List[str]:
        """ランキングを取得（オーバーライド：並列ページ取得）"""
        url = self.get_url(ranking_type)
        if not url:
            raise ValueError(f"Unknown ranking type: {ranking_type}")

        headers = {"User-Agent": USER_AGENT}

        # 最大4ページを並列取得して50件以上確保
        pages_to_fetch = 4

        def fetch_and_parse_page(page_num):
            if page_num == 1:
                page_url = url
            else:
                # Kabutanのページネーション形式に合わせる
                if "?" in url:
                    page_url = f"{url}&market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page={page_num}"
                else:
                    page_url = f"{url}?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page={page_num}"

            response = requests.get(page_url, headers=headers, timeout=30)
            response.raise_for_status()
            return page_num, self.parse(response.text)

        # 並列でページを取得・解析し、ページ番号と結果を保持
        page_results = {}
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_page = {executor.submit(fetch_and_parse_page, i): i for i in range(1, pages_to_fetch + 1)}
            for future in as_completed(future_to_page):
                page_num, codes = future.result()
                page_results[page_num] = codes

        # ページ番号順に並べてコードを結合
        all_codes = []
        for page_num in sorted(page_results.keys()):
            all_codes.extend(page_results[page_num])

        # 重複を除去しつつ順序を保持
        seen = set()
        unique_codes = []
        for code in all_codes:
            if code not in seen:
                seen.add(code)
                unique_codes.append(code)

        return unique_codes[:count]

    def get_url(self, ranking_type: str) -> Optional[str]:
        """ランキング種類に対応するURLを取得"""
        return KABUTAN_URLS.get(ranking_type)
