from typing import List
from datetime import datetime
import os


# ランキング種類の日本語ファイル名
RANKING_FILENAMES = {
    "up": "値上がり",
    "down": "値下がり",
    "volume": "出来高",
    "trading_value": "売買代金",
    "active": "活況銘柄",
    "up_from_open": "寄りからの上昇",
    "down_from_open": "寄りからの下落",
    "tick": "ティック回数",
}


class TradingViewExporter:
    """TradingView形式でウォッチリストを出力"""

    def __init__(self, output_dir: str = "output"):
        """
        Args:
            output_dir: 出力ディレクトリ
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export(self, codes: List[str], ranking_type: str) -> str:
        """
        銘柄コードリストをTradingView形式で出力

        Args:
            codes: 銘柄コードのリスト（例: ['7203', '6758', ...]）
            ranking_type: ランキング種類（ファイル名に使用）

        Returns:
            出力ファイルパス
        """
        # TSE:XXXX,TSE:YYYY,... 形式に変換
        tse_codes = [f"TSE:{code}" for code in codes]
        watchlist = ",".join(tse_codes)

        # ファイル名生成: [日本語ランキング名]_[日付].txt
        date_str = datetime.now().strftime("%Y%m%d")
        japanese_name = RANKING_FILENAMES.get(ranking_type, ranking_type)
        filename = f"{japanese_name}_{date_str}.txt"
        filepath = os.path.join(self.output_dir, filename)

        # ファイルに書き込み
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(watchlist)

        return filepath

