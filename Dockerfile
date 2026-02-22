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

# 6. Renderの仕様（デフォルトポート10000）に合わせる
EXPOSE 10000

# 7. 実行コマンド
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]