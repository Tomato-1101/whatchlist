"""設定ファイル - URL定義とランキング種類"""

# カブタン
KABUTAN_URLS = {
    "up": "https://kabutan.jp/warning/?mode=2_1",  # 値上がり率
    "down": "https://kabutan.jp/warning/?mode=2_2",  # 値下がり率
    "volume": "https://kabutan.jp/warning/volume_ranking",  # 出来高
    "trading_value": "https://kabutan.jp/warning/trading_value_ranking",  # 売買代金
    "active": "https://kabutan.jp/warning/?mode=2_9",  # 活況銘柄
}

# ストックウェザー
STOCKWEATHER_URLS = {
    "up_from_open": "https://finance.stockweather.co.jp/contents/ranking.aspx?mkt=7&cat=0000&type=2",  # 寄付からの値上がり率
    "down_from_open": "https://finance.stockweather.co.jp/contents/ranking.aspx?mkt=7&cat=0000&type=3",  # 寄付からの値下がり率
}

# デイトレードマップ
KABUMAP_URLS = {
    "volatility": "https://dt.kabumap.com/servlets/dt/Action?SRC=change%2Fbase",  # 日中値動き変動率
}

# 松井証券
MATSUI_URLS = {
    "tick": "https://finance.matsui.co.jp/ranking-tick/index",  # ティック回数
}

# User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
