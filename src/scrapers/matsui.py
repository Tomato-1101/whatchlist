from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from typing import List, Optional, Tuple
import re

from .base import BaseScraper
from ..config import MATSUI_URLS


class MatsuiScraper(BaseScraper):
    """松井証券のスクレイパー（Playwright使用）"""

    def fetch(self, url: str) -> str:
        """Playwrightでページを取得"""
        with sync_playwright() as p:
            # ボット対策のためより現実的な設定
            browser = p.chromium.launch(
                headless=False,  # ヘッドレスモードを無効化
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='ja-JP',
            )

            page = context.new_page()

            # webdriver検出を回避
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            page.goto(url, wait_until="networkidle", timeout=60000)
            html = page.content()
            browser.close()
            return html

    def parse(self, html: str) -> List[str]:
        """HTMLから銘柄コードを抽出"""
        soup = BeautifulSoup(html, "lxml")
        codes = []

        # ティック回数ランキングテーブルから銘柄コードを抽出
        # 松井証券の場合、2つ目のテーブルがランキングデータ
        tables = soup.find_all("table")
        if len(tables) >= 2:
            table = tables[1]  # 2つ目のテーブルを使用
            rows = table.find_all("tr")
            for row in rows[1:]:  # ヘッダー行をスキップ
                cells = row.find_all("td")
                if len(cells) >= 2:
                    # 2列目（銘柄名・コード列）から抽出
                    text = cells[1].get_text(strip=True)
                    # 4桁の数字、または3-4桁の数字+1文字のアルファベット（例: 285A）を抽出
                    match = re.search(r"(\d{3,4}[A-Z]?)(?:\s|東)", text)
                    if match:
                        code = match.group(1)
                        # 3桁以下は除外（正規のコードは4桁以上）
                        if len(code) >= 4 and code not in codes:
                            codes.append(code)

        return codes

    def get_url(self, ranking_type: str) -> Optional[str]:
        """ランキング種類に対応するURLを取得"""
        return MATSUI_URLS.get(ranking_type)
