import uuid
from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks, Depends, Request
from fastapi import APIRouter, Request, Form
from sqlalchemy.orm import Session

from app.lib.logger import EnhancedCSVLogger
from app.dependencies import get_logger
from app.database import get_db
from app.routers.api import cleaning_post_api, CleaningRequest

router = APIRouter()
#get_db_tursoを使って利用すること

@router.post("/loggertest")
async def execute_task_test(request: Request,
    background_tasks: BackgroundTasks,
    logger: EnhancedCSVLogger = Depends(get_logger) # ここでDI
    ):
    trace_id = str(uuid.uuid4())
    
    # --- A. 共通アクセスログ (api_logs) ---
    logger.log(background_tasks, "api_logs", {
        "trace_id": trace_id,
        "method": "POST",
        "endpoint": "/execute-ai-task",
        "request_header": dict(request.headers),
        "request_body": {"item_id": 101}, # 例
        "ip_address": request.client.host
    })

    
    # --- B. 目的別・処理進捗ログ (task_progress_logs) ---
    # ステップ1: 開始
    logger.log(background_tasks, "task_progress_logs", {
        "trace_id": trace_id,
        "task_name": "AI_Refinement",
        "step_name": "Fetch_Data",
        "status": "SUCCESS",
        "execution_order": 1
    })

    # 実際の処理（シミュレーション）
    try:
        # ステップ2: AI処理中...
        logger.log(background_tasks, "task_progress_logs", {
            "trace_id": trace_id,
            "task_name": "AI_Refinement",
            "step_name": "AI_Generation",
            "status": "IN_PROGRESS",
            "input_data": {"text": "修正前の文章"},
            "execution_order": 2
        })
    except Exception as e:
        # 失敗時の記録
        logger.log(background_tasks, "task_progress_logs", {
            "trace_id": trace_id,
            "task_name": "AI_Refinement",
            "step_name": "AI_Generation",
            "status": "FAILED",
            "error_message": str(e),
            "execution_order": 2
        })

    return {"status": "accepted", "trace_id": trace_id}

@router.post("/execute_task")
async def execute_task(request: Request,
    background_tasks: BackgroundTasks,
    logger: EnhancedCSVLogger = Depends(get_logger), # ここでDI
    db: Session = Depends(get_db) # DBセッションを追加
    ):
    trace_id = str(uuid.uuid4())
    
    # --- A. 共通アクセスログ (api_logs) ---
    logger.log(background_tasks, "api_logs", {
        "trace_id": trace_id,
        "method": "POST",
        "endpoint": "/execute-ai-task",
        "request_header": dict(request.headers),
        "request_body": {"item_id": 101}, # 例
        "ip_address": request.client.host
    })

    
    # --- B. 目的別・処理進捗ログ (task_progress_logs) ---
    # ステップ1: 開始
    logger.log(background_tasks, "task_progress_logs", {
        "trace_id": trace_id,
        "task_name": "AI_Refinement",
        "step_name": "Fetch_Data",
        "status": "SUCCESS",
        "execution_order": 1
    })

    # 日本時間 (UTC+9) の設定
    JST = timezone(timedelta(hours=9))
    now_jst = datetime.now(JST)
    
    # 日付範囲の設定 (1日前 〜 1日後)
    date_start = (now_jst - timedelta(days=1)).date()
    date_end = (now_jst + timedelta(days=1)).date()
    
    # 固定ユーザーID (必要に応じて書き換えてください)
    fixed_user_id = "76b8d0ed-825d-43a6-a725-37e10c11015b"

    # CleaningRequest作成
    req = CleaningRequest(
        user_id=fixed_user_id,
        date_start=date_start,
        date_end=date_end,
        target_post_ids=[],
        is_force_reprocess=False,
        log_level_type="normal",
        action_mode="mode_result",
        is_enable_post_status_update=True
    )

    # 実際の処理
    try:
        # ステップ2: AI処理呼び出し開始
        logger.log(background_tasks, "task_progress_logs", {
            "trace_id": trace_id,
            "task_name": "AI_Refinement",
            "step_name": "Call_Cleaning_API",
            "status": "IN_PROGRESS",
            "input_data": req.dict(),
            "execution_order": 2
        })

        # API呼び出し
        result = await cleaning_post_api(req, background_tasks, db)

    except Exception as e:
        # 失敗時の記録
        logger.log(background_tasks, "task_progress_logs", {
            "trace_id": trace_id,
            "task_name": "AI_Refinement",
            "step_name": "Call_Cleaning_API",
            "status": "FAILED",
            "error_message": str(e),
            "execution_order": 2
        })
        return {"status": "error", "trace_id": trace_id, "message": str(e)}

    return {"status": "accepted", "trace_id": trace_id, "api_result": result}