import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# 環境変数の読み込み
# このファイルは app/services/ にあるため、parent.parent で app の親(ルート)に行きます
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(f"環境変数 SUPABASE_URL または SUPABASE_KEY が読み込めませんでした。")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)