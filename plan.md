# 株式ランキング取得 → TradingViewウォッチリスト生成ツール

## 概要
複数のウェブサイトから日本株ランキングをスクレーピングし、TradingView用のウォッチリスト（TSE:XXXX形式）を生成するPythonツール。

## データソース

| ランキング種類 | ソース | URL |
|--------------|--------|-------|
| 値上がり率 | カブタン | `https://kabutan.jp/warning/?mode=2_1` |
| 値下がり率 | カブタン | `https://kabutan.jp/warning/?mode=2_2` |
| 出来高上位 | カブタン | `https://kabutan.jp/warning/volume_ranking` |
| 売買代金上位 | カブタン | `https://kabutan.jp/warning/trading_value_ranking` |
| 活況銘柄 | カブタン | `https://kabutan.jp/warning/?mode=2_9` |
| 寄付からの値上がり率 | ストックウェザー | `https://finance.stockweather.co.jp/contents/ranking.aspx?mkt=7&cat=0000&type=2` |
| 寄付からの値下がり率 | ストックウェザー | `https://finance.stockweather.co.jp/contents/ranking.aspx?mkt=7&cat=0000&type=3` |
| 日中値動き変動率 | デイトレードマップ | `https://dt.kabumap.com/servlets/dt/Action?SRC=change%2Fbase` |
| ティック回数 | 松井証券 | `https://finance.matsui.co.jp/ranking-tick/index`（要ヘッドレスブラウザ） |

## 技術スタック

- **Python 3.11+**
- **venv**: 仮想環境管理
- **requests + BeautifulSoup4**: 基本的なスクレーピング
- **Playwright**: 松井証券など403対策が必要なサイト用
- **click**: CLIインターフェース

## ディレクトリ構成

```
D:\project\whatchlist\
├── venv/                    # Python仮想環境
├── src/
│   ├── __init__.py
│   ├── main.py              # CLIエントリーポイント
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py          # 抽象基底クラス
│   │   ├── kabutan.py       # カブタンスクレイパー（値上がり/値下がり/出来高/売買代金/活況銘柄）
│   │   ├── stockweather.py  # ストックウェザースクレイパー（寄付からの値上がり/値下がり）
│   │   ├── kabumap.py       # デイトレードマップスクレイパー（日中値動き変動率）
│   │   └── matsui.py        # 松井証券スクレイパー（ティック回数、Playwright使用）
│   ├── exporters/
│   │   ├── __init__.py
│   │   └── tradingview.py   # TradingView形式出力
│   └── config.py            # 設定管理
├── output/                  # 生成されたウォッチリスト
├── requirements.txt
└── 計画書.txt
```

## 実装ステップ

### Step 1: 環境構築
- venv作成・有効化
- requirements.txt作成
- 依存パッケージインストール

### Step 2: 基底クラス実装
- `src/scrapers/base.py`: 抽象基底クラス
  - `fetch()`: ページ取得
  - `parse()`: 銘柄コード抽出
  - `get_ranking()`: メインメソッド

### Step 3: カブタンスクレイパー
- `src/scrapers/kabutan.py`
- 値上がり率、値下がり率、出来高、売買代金、活況銘柄に対応
- requests + BeautifulSoupで実装

### Step 4: ストックウェザースクレイパー
- `src/scrapers/stockweather.py`
- 寄付からの値上がり率/値下がり率に対応
- requests + BeautifulSoupで実装

### Step 5: デイトレードマップスクレイパー
- `src/scrapers/kabumap.py`
- 日中値動き変動率に対応
- requests + BeautifulSoupで実装

### Step 6: 松井証券スクレイパー
- `src/scrapers/matsui.py`
- ティック回数に対応
- Playwrightで実装（403対策）

### Step 7: TradingViewエクスポーター
- `src/exporters/tradingview.py`
- 銘柄コードリスト → `TSE:XXXX,TSE:YYYY,...` 形式
- `output/watchlist_[ランキング種類]_[日付].txt` に保存

### Step 8: CLIインターフェース
- `src/main.py`
- clickライブラリで実装
- ランキング種類を複数選択可能
- 取得件数指定（デフォルト50件）

## 使用例

```bash
# 仮想環境有効化
.\venv\Scripts\activate

# 値上がり率ランキング取得
python -m src.main --ranking up --count 50

# 複数ランキング取得
python -m src.main --ranking up --ranking down --ranking volume

# 全ランキング取得
python -m src.main --all
```

## 出力形式

```
TSE:7203,TSE:6758,TSE:9984,TSE:8306,...
```

## 注意事項

- サイト構造変更時は各スクレイパーのセレクタを更新
- 松井証券はヘッドレスブラウザ必須（403対策）
- 過度なアクセスを避けるためレート制限を実装
