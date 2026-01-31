# 🚀 デプロイガイド

このガイドでは、国会パワーバランス可視化システムをGitHub Pagesにデプロイする手順を詳しく説明します。

## 📋 前提条件

- GitHubアカウント
- Gitの基本的な知識
- （オプション）ローカル環境でPython 3.9以上

## 🔧 ステップ1: リポジトリのセットアップ

### 1.1 新規リポジトリの作成

1. GitHubにログイン
2. 右上の「+」→「New repository」をクリック
3. リポジトリ名を入力（例: `japan-diet-network`）
4. 「Public」を選択（GitHub Pages無料版はPublicのみ）
5. 「Create repository」をクリック

### 1.2 ファイルのアップロード

以下のファイルをリポジトリにアップロードします：

```
リポジトリルート/
├── .github/
│   └── workflows/
│       └── update.yml
├── analyze.py
├── index.html
├── README.md
└── (data.jsonは自動生成されるため不要)
```

**方法A: Web UIから直接アップロード**

1. リポジトリページで「Add file」→「Upload files」
2. ファイルをドラッグ&ドロップ
3. Commit message を入力
4. 「Commit changes」をクリック

**方法B: Git CLIを使用**

```bash
# ローカルにクローン
git clone https://github.com/<username>/<repo-name>.git
cd <repo-name>

# ファイルをコピー
# analyze.py, index.html, .github/workflows/update.yml をコピー

# コミット&プッシュ
git add .
git commit -m "Initial commit: Add political network visualization"
git push origin main
```

## 🔧 ステップ2: GitHub Actionsの設定

### 2.1 Actionsの有効化

1. リポジトリの「Settings」タブを開く
2. 左メニューから「Actions」→「General」を選択
3. 「Allow all actions and reusable workflows」を選択
4. 「Save」をクリック

### 2.2 ワークフローの権限設定

1. 同じ「Actions」→「General」ページで下にスクロール
2. 「Workflow permissions」セクションを見つける
3. 「Read and write permissions」を選択
4. 「Allow GitHub Actions to create and approve pull requests」にチェック
5. 「Save」をクリック

### 2.3 初回実行

1. リポジトリの「Actions」タブを開く
2. 左サイドバーから「Update Political Data」を選択
3. 右上の「Run workflow」をクリック
4. 「Run workflow」ボタンをクリックして実行開始

**実行の確認**

- ワークフローが完了すると、緑色のチェックマークが表示されます
- `data.json`がリポジトリに追加されます
- エラーが出た場合は、ログを確認して修正してください

## 🔧 ステップ3: GitHub Pagesの設定

### 3.1 Pagesの有効化

1. リポジトリの「Settings」タブを開く
2. 左メニューから「Pages」を選択
3. 「Source」で以下のいずれかを選択：

**オプションA: GitHub Actions（推奨）**
- 「Source」→「GitHub Actions」を選択
- 自動的にデプロイワークフローが作成されます

**オプションB: Branch**
- 「Source」→「Deploy from a branch」を選択
- 「Branch」→「main」、フォルダ「/ (root)」を選択
- 「Save」をクリック

### 3.2 デプロイの確認

1. 数分待つ（初回は5-10分程度）
2. 「Pages」設定ページに戻る
3. 上部に「Your site is live at https://<username>.github.io/<repo-name>/」と表示される
4. URLをクリックしてサイトを確認

## 🔧 ステップ4: 動作確認

### 4.1 データの確認

ブラウザで以下のURLにアクセス：

```
https://<username>.github.io/<repo-name>/data.json
```

JSONデータが表示されればOK。

### 4.2 サイトの確認

メインURLにアクセス：

```
https://<username>.github.io/<repo-name>/
```

以下が表示されることを確認：

- ✅ ヘッダー「国会パワーバランス可視化システム」
- ✅ 左サイドの統計パネル
- ✅ 中央のネットワークグラフ
- ✅ マウスでドラッグ・ズーム可能

### 4.3 インタラクションテスト

- **ズーム**: マウスホイールで拡大/縮小
- **移動**: ドラッグでグラフを移動
- **ノードクリック**: 議員をクリックして詳細表示
- **政党クリック**: 左パネルの政党をクリックでハイライト

## 🛠️ トラブルシューティング

### 問題1: GitHub Actionsが失敗する

**症状**: ワークフローが赤色のXマークで失敗

**解決策**:

1. Actionsタブで失敗したワークフローをクリック
2. ログを確認
3. よくあるエラー：

```bash
# エラー: permission denied
→ ワークフローの権限を「Read and write」に変更

# エラー: pip install失敗
→ requirements.txtを作成して依存関係を明示

# エラー: data.json not created
→ analyze.pyのログを確認、Wikipediaアクセスエラーの可能性
```

### 問題2: サイトが表示されない（404エラー）

**症状**: https://<username>.github.io/<repo-name>/ で404エラー

**解決策**:

1. Settings → Pages でPagesが有効になっているか確認
2. リポジトリがPublicであることを確認
3. index.htmlがリポジトリのルートにあることを確認
4. 10-15分待ってから再度アクセス（初回デプロイは時間がかかる）

### 問題3: グラフが表示されない（白い画面）

**症状**: ページは開くが、グラフが表示されない

**解決策**:

1. ブラウザの開発者ツール（F12）を開く
2. Consoleタブでエラーを確認
3. よくあるエラー：

```javascript
// エラー: Failed to fetch data.json
→ data.jsonが生成されていない、またはパスが間違っている
→ GitHub Actionsを実行してdata.jsonを生成

// エラー: echarts is not defined
→ CDNがブロックされている
→ ネットワーク環境を確認
```

### 問題4: データが更新されない

**症状**: 週次更新が動作しない

**解決策**:

1. Actions タブで自動実行履歴を確認
2. cronが正しく設定されているか確認
3. 手動で「Run workflow」を実行してテスト
4. Actionsの権限が正しいか確認

## 📊 カスタマイズ例

### カスタム1: 更新頻度の変更

毎日更新に変更する場合：

```yaml
# .github/workflows/update.yml
schedule:
  - cron: '0 0 * * *'  # 毎日午前9時(JST)
```

### カスタム2: カスタムドメインの設定

1. Settings → Pages → Custom domain
2. ドメインを入力（例: diet.example.com）
3. DNSレコードを設定（GitHubのドキュメント参照）
4. 「Enforce HTTPS」にチェック

### カスタム3: プライベートリポジトリで運用

**注意**: GitHub Pagesの無料版はPublicリポジトリのみ対応

Proプランの場合：
1. Settings → Danger Zone → Change visibility → Make private
2. GitHub Pages設定はそのまま使用可能

## 🔒 セキュリティベストプラクティス

1. **シークレット管理**
   - 現在は外部APIキー不要
   - 将来的に追加する場合は Settings → Secrets で管理

2. **依存関係の更新**
   ```bash
   # 定期的に依存ライブラリを更新
   pip install --upgrade pandas networkx
   ```

3. **Dependabot有効化**
   - Settings → Security → Dependabot
   - 「Enable」をクリック

## 📈 パフォーマンス最適化

### 大規模データ対応

議員数が100名を超える場合：

```javascript
// index.html内で調整
force: {
    repulsion: 200,        // 反発力を増やす
    edgeLength: [80, 150], // エッジを長くする
}
```

### キャッシュ戦略

```html
<!-- index.htmlに追加 -->
<meta http-equiv="Cache-Control" content="max-age=3600">
```

## 🎯 次のステップ

1. ✅ 基本デプロイ完了
2. 🔄 週次自動更新の動作確認
3. 🎨 デザインのカスタマイズ
4. 📊 追加データソースの統合
5. 📱 モバイル最適化

## 💡 便利なツール

- **GitHub CLI**: コマンドラインからGitHub操作
  ```bash
  gh repo view --web
  gh workflow run update.yml
  ```

- **VS Code GitHub拡張機能**: GUI でGitHub操作

## 🆘 サポート

問題が解決しない場合：

1. リポジトリのIssueを作成
2. 以下の情報を含める：
   - エラーメッセージ
   - ワークフローログ
   - ブラウザコンソールのエラー
   - 環境情報（OS、ブラウザなど）

---

**おめでとうございます！** 🎉

これで国会パワーバランス可視化システムがデプロイされました。
