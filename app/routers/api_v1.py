import uuid
from datetime import datetime, timedelta, timezone
from fastapi import BackgroundTasks, Depends, Request
from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from app.lib.logger import EnhancedCSVLogger
from app.dependencies import get_logger
from app.database import get_db
from app.routers.api import cleaning_post_api, CleaningRequest
from app.config import settings  # インポート
from app.services.user_service import get_users_with_auto_ai_typo

router = APIRouter()
#get_db_tursoを使って利用すること

router = APIRouter(
    prefix="/api/v1",
    tags=["api/v1"]
)
# execute-batch /api/v1/scheduled/execute-batch
@router.post("/scheduled/execute-batch")
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
        "endpoint": "/api/v1/execute-batch",
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
    date_start = (now_jst - timedelta(days=settings.BATCH_DAYS_OFFSET_START)).date()
    date_end = (now_jst + timedelta(days=settings.BATCH_DAYS_OFFSET_END)).date()
    
    # 対象ユーザーの取得 (settings->auto_ai->typo が true)
    user_ids = await get_users_with_auto_ai_typo(db)
    
    if not user_ids:
        logger.log(background_tasks, "task_progress_logs", {
            "trace_id": trace_id,
            "task_name": "AI_Refinement",
            "step_name": "Fetch_Users",
            "status": "SUCCESS",
            "message": "No users with auto_ai typo enabled found.",
            "execution_order": 2
        })
        return {"status": "success", "trace_id": trace_id, "message": "No target users found"}

    print("user_ids:",user_ids)
    # 対象ユーザーが見つかった場合のログ
    logger.log(background_tasks, "task_progress_logs", {
        "trace_id": trace_id,
        "task_name": "AI_Refinement",
        "step_name": "Fetch_Users",
        "status": "SUCCESS",
        "message": f"Found target users: {user_ids}",
        "execution_order": 2
    })

    api_results = []
    for idx, user_id in enumerate(user_ids):
        # CleaningRequest作成
        req = CleaningRequest(
            user_id=user_id,
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
            # AI処理呼び出し開始
            logger.log(background_tasks, "task_progress_logs", {
                "trace_id": trace_id,
                "task_name": "AI_Refinement",
                "step_name": f"Call_Cleaning_API_{user_id}",
                "status": "IN_PROGRESS",
                "input_data": req.dict(),
                "execution_order": 2 + idx
            })

            # API呼び出し
            result = await cleaning_post_api(req, background_tasks, db)
            api_results.append({"user_id": user_id, "result": result})

        except Exception as e:
            # 失敗時の記録
            logger.log(background_tasks, "task_progress_logs", {
                "trace_id": trace_id,
                "task_name": "AI_Refinement",
                "step_name": f"Call_Cleaning_API_{user_id}",
                "status": "FAILED",
                "error_message": str(e),
                "execution_order": 2 + idx
            })
            api_results.append({"user_id": user_id, "error": str(e)})

    return {"status": "accepted", "trace_id": trace_id, "api_results": api_results}
