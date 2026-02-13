import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
# 日本語フォントの設定（macOS用）
matplotlib.rcParams['font.family'] = 'Hiragino Sans'  # macOS用日本語フォント
plt.rcParams['font.family'] = 'Hiragino Sans'

# 2つのCSVファイルのパス
csv_file1 = '/Users/sayane/Desktop/4-1課題/4-1-2_3.実践課題_グラフ化/課題2.csv'
csv_file2 = '/Users/sayane/Desktop/4-1課題/4-1-2_3.実践課題_グラフ化/課題3.csv'

try:
    # CSVファイルを読み込む
    df1 = pd.read_csv(csv_file1, encoding='utf-8')
    df2 = pd.read_csv(csv_file2, encoding='utf-8')
    
    # 課題2.csv: 同じ人が複数回記録されている可能性があるため、名前で重複を排除
    # 「所属」が空でない行のみを対象とし、名前と所属の組み合わせでユニークな参加者を抽出
    df1_clean = df1[df1['所属'].notna() & (df1['所属'] != '')].copy()
    df1_unique = df1_clean[['名前', '所属']].drop_duplicates(subset=['名前'])
    
    # 課題3.csv: 名前と所属の列を抽出
    df2_unique = df2[['名前', '所属']].copy()
    
    # 2つのデータフレームを結合
    df_combined = pd.concat([df1_unique, df2_unique], ignore_index=True)
    
    # 「所属」カラムが存在するか確認
    if '所属' not in df_combined.columns:
        print("エラー: '所属'というカラムが見つかりません。")
        print("利用可能なカラム:", df_combined.columns.tolist())
    else:
        # 所属名を正規化（営業と営業部、開発と開発部を統合）
        def normalize_affiliation(affiliation):
            if pd.isna(affiliation) or affiliation == '':
                return affiliation
            affiliation_str = str(affiliation).strip()
            # 「営業部」→「営業」に統一
            if affiliation_str == '営業部':
                return '営業'
            # 「開発部」→「開発」に統一
            elif affiliation_str == '開発部':
                return '開発'
            return affiliation_str
        
        df_combined['所属'] = df_combined['所属'].apply(normalize_affiliation)
        
        # 「所属」ごとの参加者数を集計
        affiliation_counts = df_combined['所属'].value_counts()
        
        # 円グラフを作成
        plt.figure(figsize=(10, 8))
        
        # 円グラフを描画（割合を表示）
        colors = plt.cm.Set3(range(len(affiliation_counts)))
        wedges, texts, autotexts = plt.pie(
            affiliation_counts.values,
            labels=affiliation_counts.index,
            autopct='%1.1f%%',  # 割合を表示
            startangle=90,
            colors=colors
        )
        
        # テキストのスタイルを調整
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        for text in texts:
            text.set_fontsize(11)
        
        plt.title('所属ごとの参加者数（割合）', fontsize=16, fontweight='bold', pad=20)
        plt.axis('equal')  # 円を正円にする
        
        # 凡例を追加（参加者数も表示）
        legend_labels = [f'{label}: {count}人' for label, count in zip(affiliation_counts.index, affiliation_counts.values)]
        plt.legend(wedges, legend_labels, title="参加者数", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        plt.savefig('所属別参加者数_円グラフ.png', dpi=300, bbox_inches='tight')
        print(f"グラフを '所属別参加者数_円グラフ.png' として保存しました。")
        plt.show()
        
        # 集計結果をコンソールに表示
        print("\n【所属ごとの参加者数】")
        print(affiliation_counts)
        print(f"\n合計参加者数: {affiliation_counts.sum()}人")
        
        # ===== 棒グラフの作成 =====
        # スコアデータを読み込む（所属名を正規化）
        df1_scores = df1[df1['所属'].notna() & (df1['所属'] != '')].copy()
        df1_scores['所属'] = df1_scores['所属'].apply(normalize_affiliation)
        
        df2_scores = df2.copy()
        df2_scores['所属'] = df2_scores['所属'].apply(normalize_affiliation)
        
        # 2つのデータフレームを結合（スコアデータ）
        df_scores_combined = pd.concat([
            df1_scores[['所属', 'スコア']],
            df2_scores[['所属', 'スコア']]
        ], ignore_index=True)
        
        # 所属ごとの統計を計算
        score_stats = df_scores_combined.groupby('所属')['スコア'].agg(['mean', 'max', 'min']).round(1)
        score_stats.columns = ['平均', '最高点', '最低点']
        score_stats = score_stats.sort_index()
        
        # 棒グラフを作成
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # X軸の位置を設定
        x = range(len(score_stats.index))
        width = 0.25  # 棒の幅
        
        # 各指標の棒を描画
        bars1 = ax.bar([i - width for i in x], score_stats['平均'], width, 
                       label='平均スコア', color='#4CAF50', alpha=0.8)
        bars2 = ax.bar(x, score_stats['最高点'], width, 
                       label='最高点', color='#2196F3', alpha=0.8)
        bars3 = ax.bar([i + width for i in x], score_stats['最低点'], width, 
                       label='最低点', color='#FF9800', alpha=0.8)
        
        # グラフの設定
        ax.set_xlabel('所属', fontsize=14, fontweight='bold')
        ax.set_ylabel('スコア', fontsize=14, fontweight='bold')
        ax.set_title('所属ごとのスコア統計（平均・最高点・最低点）', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(score_stats.index, fontsize=11)
        ax.legend(fontsize=11, loc='upper left')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_ylim(0, max(score_stats['最高点']) * 1.15)  # Y軸の上限を設定
        
        # 各棒の上に値を表示
        def add_value_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        add_value_labels(bars1)
        add_value_labels(bars2)
        add_value_labels(bars3)
        
        plt.tight_layout()
        plt.savefig('所属別スコア統計_棒グラフ.png', dpi=300, bbox_inches='tight')
        print(f"\nグラフを '所属別スコア統計_棒グラフ.png' として保存しました。")
        plt.show()
        
        # 統計結果をコンソールに表示
        print("\n【所属ごとのスコア統計】")
        print(score_stats)
        print(f"\n全体の平均スコア: {df_scores_combined['スコア'].mean():.1f}点")
        print(f"全体の最高点: {df_scores_combined['スコア'].max():.0f}点")
        print(f"全体の最低点: {df_scores_combined['スコア'].min():.0f}点")
        
        # ===== スコア分布のヒストグラム作成 =====
        all_scores = df_scores_combined['スコア'].dropna()
        
        # 適切なビン数を計算（Freedman-Diaconisのルールを使用）
        q1 = all_scores.quantile(0.25)
        q3 = all_scores.quantile(0.75)
        iqr = q3 - q1
        n = len(all_scores)
        bin_width = 2 * iqr / (n ** (1/3))
        num_bins = int((all_scores.max() - all_scores.min()) / bin_width) if bin_width > 0 else 20
        
        # ビン数が多すぎる、または少なすぎる場合は調整
        if num_bins < 10:
            num_bins = 10
        elif num_bins > 30:
            num_bins = 30
        
        # ヒストグラムを作成
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # ヒストグラムを描画
        n, bins, patches = ax.hist(all_scores, bins=num_bins, color='#2196F3', 
                                   alpha=0.7, edgecolor='black', linewidth=1.2)
        
        # 平均値と中央値を縦線で表示
        mean_score = all_scores.mean()
        median_score = all_scores.median()
        ax.axvline(mean_score, color='red', linestyle='--', linewidth=2, 
                   label=f'平均値: {mean_score:.1f}点')
        ax.axvline(median_score, color='green', linestyle='--', linewidth=2, 
                   label=f'中央値: {median_score:.1f}点')
        
        # グラフの設定
        ax.set_xlabel('スコア', fontsize=14, fontweight='bold')
        ax.set_ylabel('頻度（人数）', fontsize=14, fontweight='bold')
        ax.set_title('全参加者のスコア分布', fontsize=16, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='upper right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # 統計情報をテキストで表示
        std_score = all_scores.std()
        stats_text = f'データ数: {len(all_scores)}件\n'
        stats_text += f'標準偏差: {std_score:.1f}点\n'
        stats_text += f'最小値: {all_scores.min():.0f}点\n'
        stats_text += f'最大値: {all_scores.max():.0f}点'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig('スコア分布_ヒストグラム.png', dpi=300, bbox_inches='tight')
        print(f"\nグラフを 'スコア分布_ヒストグラム.png' として保存しました。")
        plt.show()
        
        # 分布の統計をコンソールに表示
        print("\n【スコア分布の統計】")
        print(f"データ数: {len(all_scores)}件")
        print(f"平均値: {mean_score:.1f}点")
        print(f"中央値: {median_score:.1f}点")
        print(f"標準偏差: {std_score:.1f}点")
        print(f"最小値: {all_scores.min():.0f}点")
        print(f"最大値: {all_scores.max():.0f}点")
        print(f"使用したビン数: {num_bins}個")

except FileNotFoundError as e:
    print(f"エラー: ファイルが見つかりません。{e}")
    print("CSVファイルが同じディレクトリにあることを確認してください。")
except Exception as e:
    print(f"エラーが発生しました: {e}")

