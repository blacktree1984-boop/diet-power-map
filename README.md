# 🏛️ 国会パワーバランス可視化システム

日本の衆議院議員の関係性とパワーバランスをインタラクティブに可視化するウェブアプリケーション。

## 🎯 特徴

- **完全自動化**: GitHub Actionsで毎週自動更新
- **サーバーレス**: GitHub Pagesで配信（DBサーバー不要）
- **インタラクティブ**: マウス操作で自由に探索可能
- **リアルタイム情報**: Wikipediaから最新データを自動取得

## 🚀 セットアップ

### 1. リポジトリの準備

```bash
# リポジトリをクローン
git clone <your-repo-url>
cd <repo-name>

# 必要なディレクトリ構造を確認
# .github/workflows/update.yml
# analyze.py
# index.html
```

### 2. GitHub Pagesの有効化

1. GitHubリポジトリのSettings → Pages に移動
2. Source を「GitHub Actions」に設定
3. または、Branchを`main`、フォルダを`/ (root)`に設定

### 3. 初回データ生成

リポジトリのActionsタブから「Update Political Data」ワークフローを手動実行：

1. Actions タブを開く
2. 「Update Political Data」を選択
3. 「Run workflow」をクリック

数分後、`data.json`が生成されます。

### 4. サイトへのアクセス

GitHub Pagesが有効化されると、以下のURLでアクセス可能：

```
https://<username>.github.io/<repo-name>/
```

## 🧪 ローカルテスト

### 必要な環境

- Python 3.9以上
- 以下のライブラリ:

```bash
pip install pandas networkx lxml html5lib
```

### テスト実行

```bash
# テストスクリプトの実行
python test.py

# analyze.pyの直接実行
python analyze.py

# ローカルサーバーでindex.htmlを確認
python -m http.server 8000
# ブラウザで http://localhost:8000 を開く
```

## 📁 ファイル構成

```
.
├── .github/
│   └── workflows/
│       └── update.yml          # GitHub Actions設定
├── analyze.py                  # データ取得・分析スクリプト
├── index.html                  # フロントエンド
├── test.py                     # テストスクリプト
├── data.json                   # 生成されるデータファイル
└── README.md                   # このファイル
```

## 🔧 技術スタック

### バックエンド（データ収集）
- **Python 3.11**: メイン言語
- **pandas**: Wikipediaテーブルのスクレイピング
- **NetworkX**: ネットワーク分析
- **GitHub Actions**: 自動実行環境

### フロントエンド（可視化）
- **HTML5/CSS3**: UI構築
- **Apache ECharts**: グラフ可視化ライブラリ
- **バニラJavaScript**: インタラクション処理

### インフラ
- **GitHub Pages**: ホスティング
- **GitHub Actions**: CI/CD

## 📊 データソース

- **Wikipedia「衆議院議員一覧」ページ**
  - URL: https://ja.wikipedia.org/wiki/衆議院議員一覧
  - 取得方法: pandas.read_html()
  - 更新頻度: 毎週月曜日 午前9時(JST)

## 🎨 カスタマイズ

### 更新頻度の変更

`.github/workflows/update.yml`のcron設定を編集：

```yaml
schedule:
  - cron: '0 0 * * 1'  # 毎週月曜日0時(UTC) = 9時(JST)
```

例：
- 毎日: `'0 0 * * *'`
- 毎月1日: `'0 0 1 * *'`

### ビジュアルのカスタマイズ

`index.html`の以下の部分を編集：

```javascript
// 政党カラー
const partyColors = {
    '自由民主党': '#e74c3c',
    '立憲民主党': '#3498db',
    // ... 追加/変更
};

// グラフのレイアウト
force: {
    repulsion: 150,      // ノード間の反発力
    gravity: 0.1,        // 中心への引力
    edgeLength: [50, 100] // エッジの長さ
}
```

### データ取得ロジックのカスタマイズ

`analyze.py`の以下の関数を編集：

- `normalize_party_name()`: 政党名の正規化ルール
- `fetch_diet_members()`: データ取得・処理ロジック
- ネットワーク構築ロジック（リング構造、ハブ構造など）

## 🐛 トラブルシューティング

### Q1: data.jsonが生成されない

**A1**: テストスクリプトを実行して問題を特定：

```bash
python test.py
```

考えられる原因：
- 必要なライブラリがインストールされていない
- Wikipediaへのアクセスが失敗している
- テーブル構造が変更された

### Q2: GitHub Actionsが失敗する

**A2**: Actionsのログを確認：

1. Actionsタブを開く
2. 失敗したワークフローをクリック
3. エラーメッセージを確認

よくある原因：
- `pip install`の失敗 → `requirements.txt`を作成
- 権限エラー → Settingsでpermissionsを確認

### Q3: グラフが表示されない

**A3**: ブラウザの開発者ツールでエラーを確認：

1. F12で開発者ツールを開く
2. Consoleタブでエラーメッセージを確認
3. Networkタブで`data.json`が読み込まれているか確認

## 🔒 セキュリティとプライバシー

- 公開データ（Wikipedia）のみを使用
- 個人情報の収集なし
- サーバー側処理なし（完全静的サイト）
- GitHubのセキュリティ機能を活用

## 📈 今後の拡張案

- [ ] 参議院議員の追加
- [ ] 過去データとの比較機能
- [ ] 委員会情報の統合
- [ ] 選挙区情報の可視化
- [ ] モバイル最適化
- [ ] データエクスポート機能

## 🤝 コントリビューション

バグ報告や機能提案は Issue でお願いします。
プルリクエストも歓迎します！

## 📝 ライセンス

MIT License

## 🙏 謝辞

- データソース: Wikipedia
- 可視化ライブラリ: Apache ECharts
- ホスティング: GitHub Pages

---

**注意**: このプロジェクトは教育・研究目的です。政治的立場を示すものではありません。
