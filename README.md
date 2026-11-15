# OpenRank Portal | 分散型ゲームランキング・テンプレート

各プレイヤーの公開 `manifest.json` を毎日自動収集し、特定ゲームのRPランキング、または独立したゲーム別ポータルの一覧をGitHub Pagesで表示します。**中央運営者へのゲーム登録申請は不要**です。

## 0. 配布元をテンプレートとして有効化する（管理者が最初に1回だけ）

配布元の管理者が **[OpenRank_portal](https://github.com/takoyariika/OpenRank_portal) → Settings → General → Template repository** にチェックを入れます。これがオフのままでは、下の **Use this template** が表示されません。**この設定は配布元の管理者だけ** が行うもので、参加者には不要です。

## 1. ゲームポータルを自分のGitHubへコピーする

1. GitHubで、自分がポータルを管理するアカウントにログインします。
2. 配布元の **[OpenRank_portal](https://github.com/takoyariika/OpenRank_portal)** を開きます。
3. リポジトリ上部の **Use this template → Create a new repository** をクリックします。**Fork や ZIPの手動アップロードは不要**です。
4. **Owner** は自分のGitHubアカウント、**Repository name** は `kof98um-ranking` など好きな名前、**Visibility** は **Public** にします。**Include all branches** は通常チェック不要です。
5. **Create repository** を押してコピー完了。自分のリポジトリの最上位に `portal.json`、`index.html`、`scripts/crawl.py`、`.github/workflows/crawl.yml` があることを確認します。

たとえば `alice` の `kof98um-ranking` なら、コピー先は `https://github.com/alice/kof98um-ranking` です。**`.github` も自動的にコピーされるため、This file is hidden. のエラーを回避できます。**

**Use this template が見つからない場合：** 配布元の管理者が手順0の **Template repository** を有効にしてください。一般利用者が自分のリポジトリで有効にする必要はありません。

## 2. コピー後の初期設定

**以下は、自分のアカウントにコピーしたポータルのリポジトリで操作します。**

1. `portal.json` を編集する。ゲーム専用サイトなら `mode: "game"`、`game_id`（例 `kof98um`）、`title`、`genre` を設定。参加者が `profile.json` に登録する `id` と **game_idを一致**させる。
2. **Settings → Actions → General → Workflow permissions → Read and write permissions → Save** を設定する。
3. **Settings → Pages → Build and deployment → Deploy from a branch → main → /(root) → Save** を設定する。
4. リポジトリのトップの **About（歯車） → Topics** で `openrank-portal` を追加する（総合ポータルによる発見用）。
5. **Actions → OpenRank - daily crawl → Run workflow** を実行する。初回実行の **Summary（概要）** にPages URLと設定リンクが出る。
6. **Actions → OpenRank - daily crawl → 最新の成功した実行履歴 → Summary（概要）** を開き、そこに表示されるPages URLをコピーする。コードブロック右のコピーアイコン、または文字列を選択して **Ctrl+C** を使う。
7. コピーしたURLをブラウザに貼り付けてランキングを開く。初回は参加プレイヤーがいなければ空で正常。404が出る場合は下記のPages設定を確認する。

デフォルトの `portal.json` は `KOF '98 UM` 用の例です。ほかのゲームにするには `game_id` などを書き換えてください。巡回は毎日1回の予定ですが、GitHub Actionsのスケジュールは厳密な時刻・実行を保証しません。

### 複数ゲームの総合ディレクトリにする

`portal.json` を次のように変更すれば、Topic `openrank-portal` の付いたゲーム別ポータルを探すサイトになります。変更後にActionsを再実行してください。

```json
{
  "protocol": "openrank/1",
  "mode": "directory",
  "title": "ゲーム一覧"
}
```

### Pagesが404のとき

**Settings → Pages** を開き、**Deploy from a branch / main / (root)** を選択して保存してください。`Your site is live at ...` が表示されれば **Visit site** で開けます。公開には数分かかることがあります。初回ActionsのSummaryに出るURLは公開予定のURLであり、公開を保証するものではありません。

### 集計されないとき

- プレイヤーのリポジトリがPublicでTopic `openrank-player` を持ち、`manifest.json` の `repository` と `games` が正しく初期化されているか確認する。
- ゲームIDがプレイヤーとポータルで一致するか確認する。
- 検索の反映には遅延が生じる。GitHub API・検索の制限で全件取得を保証しない。
- `data/catalog.json` の `generated_at` と `players` / `portals` を確認する。

**注意:** 表示データは公開されている各ユーザーの自己管理戦績であり、改ざんや不正を完全に防ぐものではありません。個人のデータはポータルではなく本人のリポジトリに保存されます。

## 配布元の設定（メンテナー向け）

配布元の管理者は、ページ冒頭の「0. 配布元をテンプレートとして有効化する」を参照してください。GitHubの管理画面でオンにする設定であり、コードのPushだけでは有効になりません。
