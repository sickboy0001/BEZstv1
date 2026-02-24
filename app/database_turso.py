import os
from libsql_client import create_client_sync # インストールしたライブラリ
from dotenv import load_dotenv

load_dotenv()

def get_db_turso():
    """
    SQLAlchemyを介さず、ダイレクトにTursoクライアントを生成します。
    リクエストごとに接続・切断する使い方のため、プロトコルはHTTP(S)を強制します。
    """
    url = os.getenv("TURSO_DATABASE_URL")
    token = os.getenv("TURSO_AUTH_TOKEN")
    
    # wss:// や libsql:// を https:// (HTTP) に変換
    # リクエストごとに接続・切断する使い方の場合、HTTPの方が安定し高速です
    if url:
        if url.startswith("wss://"):
            url = url.replace("wss://", "https://", 1)
        elif url.startswith("libsql://"):
            url = url.replace("libsql://", "https://", 1)

    # クライアントの作成
    client = create_client_sync(url, auth_token=token)
    try:
        yield client
    finally:
        client.close()