import click
from .scrapers.kabutan import KabutanScraper
from .scrapers.stockweather import StockWeatherScraper
from .scrapers.matsui import MatsuiScraper
from .exporters.tradingview import TradingViewExporter


# ランキング種類とスクレイパーのマッピング
SCRAPER_MAP = {
    # カブタン
    "up": ("kabutan", KabutanScraper),
    "down": ("kabutan", KabutanScraper),
    "volume": ("kabutan", KabutanScraper),
    "trading_value": ("kabutan", KabutanScraper),
    "active": ("kabutan", KabutanScraper),
    # ストックウェザー
    "up_from_open": ("stockweather", StockWeatherScraper),
    "down_from_open": ("stockweather", StockWeatherScraper),
    # 松井証券
    "tick": ("matsui", MatsuiScraper),
}

# ランキング種類の日本語名
RANKING_NAMES = {
    "up": "値上がり率",
    "down": "値下がり率",
    "volume": "出来高上位",
    "trading_value": "売買代金上位",
    "active": "活況銘柄",
    "up_from_open": "寄付からの値上がり率",
    "down_from_open": "寄付からの値下がり率",
    "tick": "ティック回数",
}

# 全ランキング種類
ALL_RANKINGS = list(SCRAPER_MAP.keys())


def show_menu():
    """メニューを表示"""
    click.echo("\n" + "=" * 60)
    click.echo("  株式ランキング取得 → TradingViewウォッチリスト生成")
    click.echo("=" * 60)
    click.echo("\n【ランキング種類】")
    for i, (key, name) in enumerate(RANKING_NAMES.items(), 1):
        click.echo(f"  {i}. {name} ({key})")
    click.echo(f"  0. すべて取得")
    click.echo(f"  q. 終了")
    click.echo()


def select_rankings():
    """ランキングを選択"""
    show_menu()

    selections = click.prompt(
        "取得するランキングを選択してください（複数選択可: 123 または 1,2,3 または 0 で全て）",
        default="0"
    )

    if selections.strip().lower() == 'q':
        return None

    # 全て取得
    if selections.strip() == '0':
        return ALL_RANKINGS

    # 複数選択をパース
    selected = []
    ranking_list = list(RANKING_NAMES.keys())

    # スペースを削除
    selections = selections.replace(' ', '')

    # コンマがある場合は従来通り split
    # コンマがない場合は各文字を個別の選択として扱う（例: "123" → ["1", "2", "3"]）
    if ',' in selections:
        selection_list = selections.split(',')
    else:
        # 連続した数字を1文字ずつ分割（例: "123" → ["1", "2", "3"]）
        selection_list = list(selections)

    for sel in selection_list:
        try:
            idx = int(sel) - 1
            if 0 <= idx < len(ranking_list):
                # 重複チェック
                ranking_key = ranking_list[idx]
                if ranking_key not in selected:
                    selected.append(ranking_key)
            else:
                click.echo(f"警告: {sel} は無効な番号です（スキップ）")
        except ValueError:
            click.echo(f"警告: '{sel}' は無効な入力です（スキップ）")

    return selected if selected else None


def interactive_mode():
    """インタラクティブモード"""
    # ランキング選択
    rankings_to_fetch = select_rankings()

    if not rankings_to_fetch:
        click.echo("終了します")
        return

    # 選択されたランキングを表示
    click.echo("\n【選択されたランキング】")
    for r in rankings_to_fetch:
        click.echo(f"  - {RANKING_NAMES[r]}")

    # 取得件数を入力（Enterでデフォルト50件）
    count = click.prompt("\n取得する銘柄数を入力してください", type=int, default=50)

    # エクスポーター初期化
    exporter = TradingViewExporter(output_dir="output")

    # 各ランキングを取得
    click.echo("\n" + "=" * 60)
    click.echo("  取得開始")
    click.echo("=" * 60)

    for ranking_type in rankings_to_fetch:
        try:
            click.echo(f"\n[{RANKING_NAMES[ranking_type]}] 取得中...")

            # スクレイパーを取得
            source, scraper_class = SCRAPER_MAP[ranking_type]
            scraper = scraper_class(count=count)

            # ランキング取得
            codes = scraper.get_ranking(ranking_type)

            if not codes:
                click.echo(f"  → 銘柄が取得できませんでした")
                continue

            click.echo(f"  → {len(codes)}件の銘柄を取得しました")

            # TradingView形式で出力
            filepath = exporter.export(codes, ranking_type)
            click.echo(f"  → 出力: {filepath}")

        except Exception as e:
            click.echo(f"  → エラー: {e}", err=True)

    click.echo("\n" + "=" * 60)
    click.echo("  完了しました")
    click.echo("=" * 60)


@click.command()
@click.option(
    "--ranking",
    "-r",
    multiple=True,
    type=click.Choice(ALL_RANKINGS, case_sensitive=False),
    help="ランキング種類（複数指定可能）",
)
@click.option(
    "--count",
    "-c",
    default=50,
    type=int,
    help="取得する銘柄数（デフォルト: 50）",
)
@click.option(
    "--all",
    "-a",
    is_flag=True,
    help="全ランキングを取得",
)
@click.option(
    "--output",
    "-o",
    default="output",
    help="出力ディレクトリ（デフォルト: output）",
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="インタラクティブモードで起動",
)
def main(ranking, count, all, output, interactive):
    """株式ランキング取得 → TradingViewウォッチリスト生成ツール"""

    # インタラクティブモード
    if interactive or (not ranking and not all):
        interactive_mode()
        return

    # 取得するランキングを決定
    if all:
        rankings_to_fetch = ALL_RANKINGS
    elif ranking:
        rankings_to_fetch = list(ranking)
    else:
        click.echo("エラー: --ranking または --all を指定してください")
        click.echo("インタラクティブモードで起動するには: python -m src.main")
        return

    # エクスポーター初期化
    exporter = TradingViewExporter(output_dir=output)

    # 各ランキングを取得
    for ranking_type in rankings_to_fetch:
        try:
            click.echo(f"\n[{ranking_type}] ランキングを取得中...")

            # スクレイパーを取得
            source, scraper_class = SCRAPER_MAP[ranking_type]
            scraper = scraper_class(count=count)

            # ランキング取得
            codes = scraper.get_ranking(ranking_type)

            if not codes:
                click.echo(f"[{ranking_type}] 銘柄が取得できませんでした")
                continue

            click.echo(f"[{ranking_type}] {len(codes)}件の銘柄を取得しました")

            # TradingView形式で出力
            filepath = exporter.export(codes, ranking_type)
            click.echo(f"[{ranking_type}] 出力: {filepath}")

        except Exception as e:
            click.echo(f"[{ranking_type}] エラー: {e}", err=True)

    click.echo("\n完了しました")


if __name__ == "__main__":
    main()
