# OpenRank Portal | 分散型ゲームランキング・テンプレート

各プレイヤーの公開 `manifest.json` を毎日自動収集し、特定ゲームのRPランキング、または独立したゲーム別ポータルの一覧をGitHub Pagesで表示します。**中央運営者へのゲーム登録申請は不要**です。

## 導入手順

このリポジトリを **Use this template → Create a new repository** で各自のGitHubアカウントに**公開リポジトリ**として複製してください。`.github/workflows/crawl.yml` を含めてコピーされます。

1. `portal.json` を編集する。ゲーム専用サイトなら `mode: "game"`、`game_id`（例 `kof98um`）、`title`、`genre` を設定。参加者が `profile.json` に登録する `id` と **game_idを一致**させる。
2. **Settings → Actions → General → Workflow permissions → Read and write permissions → Save** を設定する。
3. **Settings → Pages → Build and deployment → Deploy from a branch → main → /(root) → Save** を設定する。
4. リポジトリのトップの **About（歯車） → Topics** で `openrank-portal` を追加する（総合ポータルによる発見用）。
5. **Actions → OpenRank - daily crawl → Run workflow** を実行する。初回実行の **Summary（概要）** にPages URLと設定リンクが出る。
6. 公開URLを開いてランキングを確認する。初回は参加プレイヤーがいなければ空で正常。

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

このリポジトリの所有者が **Settings → General → Template repository** をオンにしてください。この設定はGitHubの管理画面で行います。新規ユーザーは **Use this template** でポータルを作成できます。
