import os
from pathlib import Path
from app.lib.logger import EnhancedCSVLogger
from fastapi.templating import Jinja2Templates
from fastapi import Request
from .services.supabase_client import supabase

# テンプレートの設定 (app/templates を指すように調整)
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


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