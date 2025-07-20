FROM python:3.11

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.txt .

# 依存関係のインストール
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y ffmpeg

# アプリケーションのソースコードをコピー
COPY . .

# 環境変数の設定
ENV PORT=8080

# アプリケーションの実行
CMD ["python", "main.py"]