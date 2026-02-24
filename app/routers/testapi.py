from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import date, datetime, timedelta
import logging

from libsql_client import Client
from app.database_turso import get_db_turso
from app.routers.system_logs import get_system_traces

# テンプレートエンジンの設定（templatesディレクトリを指すように調整してください）
templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/test-api",
    tags=["TestAPI"]
)

@router.get("/read-turso-api-log", response_class=HTMLResponse)
async def read_turso_api_log(
    request: Request,
    start_date: date = Query(None),
    end_date: date = Query(None)
):
    # デフォルトの日付設定（指定がない場合は今日一日分）
    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = date.today()

    logs = []
    error_msg = None

    try:
        # system_logs.py のロジックを再利用
        result = await get_system_traces(start_date=start_date, end_date=end_date, limit=100,db=None)
        raw_logs = result.get("data", [])

        # --- 日本時間(JST)への変換処理 ---
        for log in raw_logs:
            for key in ["api_created_at", "task_created_at"]:
                if log.get(key):
                    try:
                        # 文字列をdatetimeオブジェクトに変換 (2026-02-24 06:50:58.123 形式を想定)
                        dt_utc = datetime.strptime(log[key], '%Y-%m-%d %H:%M:%S.%f')
                        # 9時間を加算して日本時間にする
                        dt_jst = dt_utc + timedelta(hours=9)
                        # 表示用の文字列に戻す (ミリ秒なしの方が見やすい場合は .%f を削る)
                        log[key] = dt_jst.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception as e:
                        # フォーマットが合わない等の場合はそのままにする
                        logging.warning(f"Time conversion failed for {log[key]}: {e}")
        
        logs = raw_logs
    except Exception as e:
        logging.error(f"Turso取得エラー: {e}")
        error_msg = f"ログの取得に失敗しました: {str(e)}"

    return templates.TemplateResponse(
        "read_turso_api_log.html", 
        {
            "request": request, 
            "logs": logs, 
            "error": error_msg,
            "start_date": start_date,
            "end_date": end_date
        }
    )