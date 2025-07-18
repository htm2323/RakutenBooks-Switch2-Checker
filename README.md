# 楽天ブックス Switch2販売状況 監視bot

楽天ブックスにおけるNintendo Switch 2本体の販売状況を自動チェックし、在庫状況に変化があった際にSlackで通知するプログラムです。

## 概要
- 楽天APIを使用してNintendo Switch 2本体の在庫状況を5分間隔でチェックします。
- 在庫状況が注文不可から変化（予約受付開始、販売開始など）した場合、SlackチャンネルまたはDMに通知を送信します。
  - 初回実行時には現在の在庫状況を報告します

## 要件
- Python 3.10
- pyyaml
- slack-bolt

加えて、Slack AppのOAuthトークンと楽天APIの設定が必要です。利用方法など詳しくは以下を確認してください。

- [Slack Bolt 入門ガイド](https://tools.slack.dev/bolt-python/ja-jp/getting-started/)
- [楽天API ご利用ガイド](https://webservice.rakuten.co.jp/guide)



## 使用方法

### 1. 事前準備

#### 依存パッケージのインストール
```bash
pip install pyyaml slack-bolt
```

またはuvでの設定も可能です。

```bash
uv sync
```

#### Slackボット設定
1. [Slack API](https://api.slack.com/apps/)で新しくSlackアプリを作成する。
2. **Basic Information**を開き，`App-Level Tokens`に任意のトークン名で以下のスコープを追加
   - `connections:write`
3. **App Home**を開き、以下の設定を行う
   - `App Display Name`からbotユーザーの名前を設定
   - `Show Tabs`の`Messages Tab`のトグルをオン
4. **OAuth & Permissions**を開き、`Bot Token Scopes`に以下のスコープを追加
   - `chat:write`
   - `groups:read`
   - `im:read`
   - `im:write`
5. **Install App**からワークスペースにインストールし、`Bot User OAuth Token`を取得

#### 楽天API設定
1. [楽天デベロッパー](https://webservice.rakuten.co.jp)でアカウント作成
   - 楽天アカウントでログイン可
2. **アプリID発行**からアプリケーションを登録し、アプリIDを取得

### 2. 設定ファイル作成

プロジェクトルートに`params.yaml`ファイルを作成：

```yaml
# 楽天API設定
rakuten-api-app-id: "YOUR_RAKUTEN_APP_ID"

# Slackトークン設定
SLACK_BOT_USER_OAUTH_TOKEN: "xoxb-your-bot-token"

# 通知先ユーザー（ユーザーIDのリスト）
send_user: ["Uxxxxxxxxx1",  # SlackユーザーID
            "Uxxxxxxxxx2"]  # 複数指定可能
```

なお、ユーザーIDは以下の方法で取得できる。

1. Slackアプリで対象ユーザーのプロフィールを開く
2. 「︙」→「メンバーIDをコピー」を選択すると、`U`で始まる文字列をコピーできる

### 3. プログラム実行

```bash
python app.py

# uvの場合
uv run app.py
```

起動時にログファイル`log/switch2_notifier.log`が自動作成されます。

## 注意事項

- 楽天APIの利用規約を十分確認したうえで、過度なアクセスは避けてください。
- API仕様の変更により動作しなくなる可能性があります。
