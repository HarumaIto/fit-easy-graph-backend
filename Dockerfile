FROM python:3.11

ARG MONGO_URI_ARG
ENV MONGO_URI=$MONGO_URI_ARG

ARG FITEASY_EMAIL_ARG
ENV FITEASY_EMAIL=$FITEASY_EMAIL_ARG

ARG FITEASY_PASSWORD_ARG
ENV FITEASY_PASSWORD=$FITEASY_PASSWORD_ARG

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.txt .

# 依存関係のインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# 環境変数の設定
ENV PORT=8080

# アプリケーションの実行
CMD ["python", "main.py"]