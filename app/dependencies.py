import os
from pathlib import Path
from app.lib.logger import EnhancedCSVLogger
from fastapi.templating import Jinja2Templates
from fastapi import Request
from .services.supabase_client import supabase
from datetime import datetime, timedelta

# テンプレートの設定 (app/templates を指すように調整)
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))



# 2. 日本時間変換用の関数を定義
def jst_filter(value):
    if not value:
        return ""
    
    # 1. もし文字列(str)で届いたら、datetimeオブジェクトに変換する
    if isinstance(value, str):
        try:
            # ISO形式（2025-12-21T10:00:00Z など）を読み込む
            # 末尾のZを+00:00に置換して読み込むのが一般的です
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return value  # 変換できない場合はそのまま返す

    # 2. 日本時間を計算 (UTCから9時間加算)
    jst_time = value + timedelta(hours=9)
    return jst_time.strftime('%Y/%m/%d %H:%M:%S')

# 3. Jinja2のエコシステムに "jst" という名前で登録
templates.env.filters["jst"] = jst_filter


# 1. アプリ全体で共有するインスタンスを作成（シングルトン）
logger_instance = EnhancedCSVLogger(
    turso_url=os.getenv("TURSO_DATABASE_URL"),
    turso_token=os.getenv("TURSO_AUTH_TOKEN"),
    base_path=os.getenv("LOG_BASE_PATH")
)

# 2. DI用の関数
def get_logger():
    return logger_instance


async def get_current_user(request: Request):
    """
    Cookieからアクセストークンを取得し、Supabaseでユーザー情報を取得する。
    認証失敗時は None を返す。
    """
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        user_response = supabase.auth.get_user(token)
        return user_response.user
    except Exception:
        return None