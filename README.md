# FitEasy Graph Backend

**FitEasy ジムの混雑状況を自動取得・管理するバックエンドAPI**

## 📋 概要

FitEasy Graph Backendは、FitEasyジムチェーンの各店舗の混雑状況をリアルタイムで取得し、データベースに保存・管理するためのRESTful APIサービスです。Webスクレイピング技術を使用してFitEasyの公式サイトから混雑情報を自動取得し、時系列データとして蓄積します。

### 🎯 主な機能

- **自動ログイン・セッション管理**: FitEasyサイトへの自動ログイン機能とセッション継続機能
- **混雑情報取得**: 指定店舗の混雑レベルをリアルタイムで取得
- **複数店舗対応**: 一度のログインで複数店舗の情報を効率的に取得
- **データベース保存**: MongoDB Atlasへの自動データ保存
- **RESTful API**: フロントエンドや他のサービスとの連携用API

## 🛠 技術スタック

### フレームワーク・ライブラリ
- **Flask**: Webアプリケーションフレームワーク
- **Requests**: HTTPクライアントライブラリ
- **BeautifulSoup4**: HTMLパーシング・Webスクレイピング
- **PyMongo**: MongoDB接続ライブラリ
- **python-dotenv**: 環境変数管理

### インフラストラクチャ・サービス
- **Google Cloud Run**: サーバーレスコンテナ実行環境
- **Google Cloud Build**: CI/CDパイプライン
- **Google Secret Manager**: 認証情報の安全な管理
- **MongoDB Atlas**: クラウドデータベース（NoSQL）
- **Docker**: コンテナ化技術

### 開発・運用
- **Python 3.11**: プログラミング言語
- **Git**: バージョン管理
- **Google Artifact Registry**: コンテナイメージレジストリ

## 🚀 API ドキュメント

### エンドポイント一覧

#### 1. 単一店舗の混雑情報取得
```
GET /congestion
```

**説明**: 指定された店舗の現在の混雑状況を取得します。

**レスポンス例**:
```json
{
  "gym_name": "イオンタウン弥富店",
  "level": 3
}
```

#### 2. 複数店舗の混雑情報取得
```
GET /congestion/multiple?targets=店舗1&targets=店舗2
```

**パラメータ**:
- `targets` (query, array): 取得対象の店舗名リスト

**レスポンス例**:
```json
[
  {
    "gym_name": "イオンタウン弥富店",
    "level": 3
  },
  {
    "gym_name": "店舗2",
    "level": 2
  }
]
```

#### 3. 混雑情報の保存
```
POST /congestion
```

**説明**: 混雑情報を取得してMongoDBに保存します。

**レスポンス例**:
```json
{
  "inserted_id": "64a7b2c8f1e2d3a4b5c6d7e8"
}
```

#### 4. 複数店舗の情報をバッチ保存
```
POST /congestion/batch
```

**リクエストボディ**:
```json
{
  "targets": ["イオンタウン弥富店", "店舗2"]
}
```

**レスポンス例**:
```json
{
  "inserted_count": 2,
  "inserted_ids": ["64a7b2c8f1e2d3a4b5c6d7e8", "64a7b2c8f1e2d3a4b5c6d7e9"],
  "results": [
    {
      "gym_name": "イオンタウン弥富店",
      "level": 3
    },
    {
      "gym_name": "店舗2",
      "level": 2
    }
  ]
}
```

#### 5. セッション状態確認
```
GET /session/status
```

**説明**: 現在のログインセッションの状態を確認します。

**レスポンス例**:
```json
{
  "session_valid": true,
  "login_time": "2025-07-25T10:30:45+09:00",
  "session_timeout_hours": 2.0
}
```

### エラーレスポンス

エラーが発生した場合、以下の形式でレスポンスが返されます：

```json
{
  "detail": "エラーメッセージ"
}
```

HTTP ステータスコード: `500 Internal Server Error`

## 🔧 環境設定

### 必要な環境変数

以下の環境変数を設定する必要があります：

```bash
# MongoDB Atlas接続文字列
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>

# FitEasy認証情報
FITEASY_EMAIL=your-email@example.com
FITEASY_PASSWORD=your-password

# ポート番号（オプション、デフォルト: 8080）
PORT=8080
```

### ローカル開発環境のセットアップ

1. **リポジトリのクローン**
```bash
git clone <repository-url>
cd fit-easy-graph-backend
```

2. **仮想環境の作成・有効化**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate     # Windows
```

3. **依存関係のインストール**
```bash
pip install -r requirements.txt
```

4. **環境変数の設定**
```bash
cp .env.example .env
# .envファイルを編集して必要な環境変数を設定
```

5. **アプリケーションの起動**
```bash
python main.py
```

アプリケーションは `http://localhost:8080` で起動します。

## 📦 デプロイメント

### Google Cloud Runへのデプロイ

このプロジェクトはGoogle Cloud Build経由で自動的にCloud Runにデプロイされます。

**自動デプロイの流れ**:
1. GitHubリポジトリへのプッシュ
2. Cloud Build トリガーが発動
3. Dockerイメージのビルド
4. Artifact Registryへのイメージプッシュ
5. Cloud Runサービスの更新

**手動デプロイ**:
```bash
# Google Cloud SDKを使用
gcloud run deploy fit-easy-graph-backend \
  --source . \
  --platform managed \
  --region asia-northeast2 \
  --allow-unauthenticated
```

## 🧪 テスト

### セッション機能のテスト
```bash
python session_example.py
```

### APIエンドポイントのテスト
```bash
# 健康チェック
curl http://localhost:8080/congestion

# 複数店舗の情報取得
curl "http://localhost:8080/congestion/multiple?targets=イオンタウン弥富店"

# セッション状態確認
curl http://localhost:8080/session/status
```

## 📊 データベーススキーマ

### MongoDB Collection: `congestion_info`

```javascript
{
  "_id": ObjectId("..."),
  "gym_id": "61",
  "gym_name": "イオンタウン弥富店",
  "timestamp": ISODate("2025-07-25T10:30:45.123Z"),
  "congestion_level": 3
}
```

**フィールド説明**:
- `gym_id`: ジムの一意識別子
- `gym_name`: ジム店舗名
- `timestamp`: データ取得時刻（JST）
- `congestion_level`: 混雑レベル（数値）

## 🔒 セキュリティ

- **認証情報管理**: Google Secret Managerで機密情報を安全に管理
- **セッション管理**: 適切なセッションタイムアウト設定（2時間）
- **エラーハンドリング**: 詳細なエラー情報の適切な処理

## 🤝 貢献

1. フォークを作成
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📝 ライセンス

このプロジェクトは私的利用を目的としています。

## ⚠️ 注意事項

- このツールはFitEasyの公式APIではなく、Webスクレイピングを使用しています
- 利用規約に従って適切に使用してください
- 過度なリクエストは避け、サーバーに負荷をかけないよう注意してください
- FitEasyのサイト構造変更により動作しなくなる可能性があります

## 📞 サポート

問題が発生した場合や質問がある場合は、GitHubのIssuesページで報告してください。