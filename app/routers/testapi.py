from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date, datetime, timedelta
import logging
from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID

from libsql_client import Client
from app.database_turso import get_db_turso
from app.dependencies import get_current_user,templates
from app.routers.system_logs import get_system_traces


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






# @router.get("/Cleaning_post_api_test", response_class=HTMLResponse)
# async def cleaning_post_api_test(
#     request: Request,
#     user = Depends(get_current_user),
#     start_date: Optional[date] = Query(None),
#     end_date: Optional[date] = Query(None)
# ):
#     print("cleaning_post_api_test:start")
#     if not user:
#         return RedirectResponse(url="/login")

#     if start_date is None:
#         start_date = date.today()
#     if end_date is None:
#         end_date = date.today()
#     # print("userid:", user.id)

#     context = {
#         "request": request,
#         "user": user,
#         "user_id": user.id,
#         "target_period": {
#             "start_date": start_date.isoformat(),
#             "end_date": end_date.isoformat(),
#         },
#         "post_ids": "",  # 初期値は空
#         "target_condition_options": [
#             {"value": "none", "label": "未処理のみ (unprocessed, requeue)"},
#             {"value": "all", "label": "全データ強制再精査 (refined, completed含む)"}
#         ],
#         "loglevel_options": [
#             {"value": "normal", "label": "Normal: ヘッダ・経緯のみ"},
#             {"value": "detail", "label": "Detail: プロンプト・AI回答をフル保存"},
#             {"value": "none", "label": "None: ログ保存なし"}
#         ],
#         "disp_options": [
#             {"value": "none", "label": "全工程完遂"},
#             {"value": "targets", "label": "工程4まで（対象抽出の確認）"},
#             {"value": "airesult", "label": "工程7まで（AI回答の確認）"},
#             {"value": "results", "label": "工程9まで（DB反映直前までの確認）"}
#         ],
#         # デフォルト選択値
#         "default_target_condition": "none",
#         "default_loglevel": "normal",
#         "default_disp": "none",
#     }
#     # print("cleaning_post_api_test:end:" ,context)
#     return templates.TemplateResponse(
#         "api_test/cleaning_post_test.html",
#         context
#     )


@router.get("/Cleaning_post_api_test", response_class=HTMLResponse)
async def cleaning_post_api_test(
    request: Request,
    user = Depends(get_current_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    print("cleaning_post_api_test2:start")
    if not user:
        return RedirectResponse(url="/login")

    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()
    # print("userid:", user.id)

    # print("cleaning_post_api_test:end:" ,context)
    return templates.TemplateResponse(
        "api_test/cleaning_post_test.html",
        {
            "request": request,
            "user": user,
            "user_id": user.id,
            "target_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        }
    )
 