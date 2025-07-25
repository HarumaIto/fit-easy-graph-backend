# 開発者ガイド

## 🚀 開発環境のセットアップ

### 前提条件

- Python 3.11以上
- Git
- MongoDB Atlas アカウント（または ローカルMongoDB）
- FitEasy アカウント

### ローカル開発環境の構築

1. **リポジトリのクローン**
```bash
git clone <repository-url>
cd fit-easy-graph-backend
```

2. **Python仮想環境の作成**
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
```

`.env`ファイルを編集して以下の環境変数を設定：
```bash
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/fit_easy_graph
FITEASY_EMAIL=your-email@example.com
FITEASY_PASSWORD=your-password
PORT=8080
```

5. **アプリケーションの起動**
```bash
python main.py
```

## 🧪 テスト

### 基本的なテスト
```bash
# セッション機能のテスト
python session_example.py

# APIエンドポイントのテスト
curl http://localhost:8080/congestion
curl http://localhost:8080/session/status
```

### 単体テストの追加

将来的には以下のようなテストを追加予定：

```python
# test_scraper.py
import unittest
from scraper import FitEasySession

class TestFitEasySession(unittest.TestCase):
    def test_session_creation(self):
        # テストコード
        pass
```

## 🏗 プロジェクト構造

```
fit-easy-graph-backend/
├── main.py                 # Flaskアプリケーションのメインファイル
├── scraper.py              # スクレイピング・セッション管理
├── session_example.py      # 使用例・テストスクリプト
├── requirements.txt        # Python依存関係
├── Dockerfile             # Dockerコンテナ設定
├── cloudbuild.yaml        # Google Cloud Build設定
├── api-docs.yaml          # OpenAPI仕様書
├── .env.example           # 環境変数のテンプレート
├── README.md              # プロジェクト概要
└── CONTRIBUTING.md        # 開発者ガイド（このファイル）
```

## 🔧 開発のベストプラクティス

### コーディング規約

- **PEP 8**: Pythonの標準コーディング規約に従う
- **型ヒント**: 可能な限り型ヒントを使用
- **ドキュメント**: 関数・クラスにはdocstringを記述
- **ログ**: 適切なログレベルでログを出力

### Git ワークフロー

1. **機能ブランチの作成**
```bash
git checkout -b feature/new-feature
```

2. **変更のコミット**
```bash
git add .
git commit -m "feat: 新機能の追加"
```

3. **プッシュとプルリクエスト**
```bash
git push origin feature/new-feature
```

### コミットメッセージの規約

- `feat:` 新機能の追加
- `fix:` バグ修正
- `docs:` ドキュメントの変更
- `style:` コードフォーマットの変更
- `refactor:` リファクタリング
- `test:` テストの追加・修正
- `chore:` その他の変更

## 🐳 Docker開発

### ローカルでのDockerビルド・実行

```bash
# イメージのビルド
docker build -t fit-easy-graph-backend .

# コンテナの実行
docker run -p 8080:8080 \
  -e MONGO_URI="your-mongo-uri" \
  -e FITEASY_EMAIL="your-email" \
  -e FITEASY_PASSWORD="your-password" \
  fit-easy-graph-backend
```

### docker-compose（開発用）

将来的に追加予定のdocker-compose.yml:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - MONGO_URI=${MONGO_URI}
      - FITEASY_EMAIL=${FITEASY_EMAIL}
      - FITEASY_PASSWORD=${FITEASY_PASSWORD}
    env_file:
      - .env
```

## ☁️ Google Cloud Platform デプロイ

### 手動デプロイ

```bash
# Google Cloud SDKでデプロイ
gcloud run deploy fit-easy-graph-backend \
  --source . \
  --platform managed \
  --region asia-northeast2 \
  --allow-unauthenticated \
  --set-secrets="MONGO_URI=MONGO_URI:latest,FITEASY_EMAIL=FITEASY_EMAIL:latest,FITEASY_PASSWORD=FITEASY_PASSWORD:latest"
```

### 環境変数の設定

Google Secret Managerでシークレットを管理：

```bash
# シークレットの作成
echo -n "your-mongo-uri" | gcloud secrets create MONGO_URI --data-file=-
echo -n "your-email" | gcloud secrets create FITEASY_EMAIL --data-file=-
echo -n "your-password" | gcloud secrets create FITEASY_PASSWORD --data-file=-
```

## 🚨 トラブルシューティング

### よくある問題

1. **ログイン失敗**
   - FitEasyの認証情報を確認
   - サイトの構造変更の可能性

2. **MongoDB接続エラー**
   - MONGO_URIの確認
   - ネットワーク接続の確認

3. **セッションタイムアウト**
   - セッション管理の設定確認
   - 自動再ログイン機能の動作確認

### デバッグ方法

```python
# ログレベルの変更
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 パフォーマンス最適化

### 推奨事項

- セッション再利用によるログイン回数の削減
- 適切なリクエスト間隔の設定
- エラーハンドリングの強化
- レスポンスキャッシュの実装（将来的）

## 🔒 セキュリティ考慮事項

- 環境変数での認証情報管理
- Google Secret Managerの利用
- 適切なエラーメッセージ（内部情報の漏洩防止）
- レート制限の実装（将来的）

## 📞 サポート・質問

開発に関する質問や問題は以下の方法で報告してください：

1. GitHub Issues で問題を報告
2. プルリクエストで改善提案
3. ディスカッションで技術的な質問

## 🎯 今後の改善予定

- [ ] 単体テストの追加
- [ ] ログローテーションの実装
- [ ] メトリクス・モニタリングの追加
- [ ] レート制限の実装
- [ ] 複数のFitEasy店舗対応の拡張
- [ ] キャッシュシステムの導入
- [ ] CI/CDパイプラインの改善
