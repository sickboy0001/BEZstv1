import uuid

from fastapi import BackgroundTasks, Depends, Request
from fastapi import APIRouter, Request, Form

from app.lib.logger import EnhancedCSVLogger
from app.dependencies import get_logger


router = APIRouter()


@router.post("/loggertest")
async def execute_task(request: Request,
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