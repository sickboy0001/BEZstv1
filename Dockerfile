# 1. ベースイメージ（安定版の3.12を使用）
FROM python:3.12-slim

# Pythonがpycファイルを書かないようにし、バッファリングを無効にする（ログ即時表示のため）
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. 作業ディレクトリの設定
WORKDIR /app

# 3. 依存ライブラリのインストール（psycopg2用にgccなどが必要な場合があります）
RUN apt-get update && apt-get install -y \
  gcc \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# 4. requirements.txtをコピーしてインストール
COPY requirements.txt .
RUN pip install --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

# 5. ソースコードをコピー
COPY . .

# 6. EXPOSEはCloud Runでは無視されますが、慣習として8080を書いておくか、削除しても動きます
EXPOSE 8080

# 7. 実行コマンド
# --port 10000 を --port ${PORT:-8080} に変更します
# これにより、環境変数 PORT があればそれを使い、なければ 8080 を使います
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]