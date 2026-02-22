from pathlib import Path
from fastapi import Request
from fastapi.templating import Jinja2Templates
from .services.supabase_client import supabase

# テンプレートの設定 (app/templates を指すように調整)
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

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