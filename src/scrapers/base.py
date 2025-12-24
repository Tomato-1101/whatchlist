from abc import ABC, abstractmethod
from typing import List, Optional
import time


class BaseScraper(ABC):
    """株式ランキングスクレイパーの抽象基底クラス"""

    def __init__(self, count: int = 50, rate_limit: float = 1.0):
        """
        Args:
            count: 取得する銘柄数（デフォルト50件）
            rate_limit: リクエスト間隔（秒）
        """
        self.count = count
        self.rate_limit = rate_limit

    @abstractmethod
    def fetch(self, url: str) -> str:
        """
        ページを取得

        Args:
            url: 取得するURL

        Returns:
            HTMLコンテンツ
        """
        pass

    @abstractmethod
    def parse(self, html: str) -> List[str]:
        """
        HTMLから銘柄コードを抽出

        Args:
            html: HTMLコンテンツ

        Returns:
            銘柄コードのリスト（例: ['7203', '6758', ...]）
        """
        pass

    def get_ranking(self, ranking_type: str) -> List[str]:
        """
        ランキングを取得するメインメソッド

        Args:
            ranking_type: ランキング種類

        Returns:
            銘柄コードのリスト
        """
        url = self.get_url(ranking_type)
        if not url:
            raise ValueError(f"Unknown ranking type: {ranking_type}")

        # レート制限
        time.sleep(self.rate_limit)

        html = self.fetch(url)
        codes = self.parse(html)

        # 指定件数まで絞る
        return codes[:self.count]

    @abstractmethod
    def get_url(self, ranking_type: str) -> Optional[str]:
        """
        ランキング種類に対応するURLを取得

        Args:
            ranking_type: ランキング種類

        Returns:
            URL（対応していない場合はNone）
        """
        pass
