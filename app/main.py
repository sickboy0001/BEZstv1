from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import auth, pages, system,loggertest
from app.lib.logger import EnhancedCSVLogger
import os

# 1. アプリ全体で共有するインスタンスを作成（シングルトン）
logger_instance = EnhancedCSVLogger(
    turso_url=os.getenv("TURSO_DATABASE_URL"),
    turso_token=os.getenv("TURSO_AUTH_TOKEN"),
    base_path=os.getenv("LOG_BASE_PATH")
)

# 2. DI用の関数
def get_logger():
    return logger_instance


app = FastAPI()

# 静的ファイルのマウント
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# ルーターの登録
app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(system.router)
app.include_router(auth.router)
app.include_router(loggertest.router)