from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import logging
from sqlalchemy.orm import Session
from app.services.cleaning_post_service import (
    build_prompt_text, call_gemini_api, cleaning_post, CleaningPostRequest, fetch_posts_from_db, filter_posts_with_state_detail
)
from app.database import get_db
from datetime import date
from app.services.db_service import get_datefromto_posts, get_postids_posts
from app.services.prompt_tamplate_service import get_prompt_template_from_db
from app.services.tags_service import get_formatted_tags_json


router = APIRouter(
    prefix="/api",
    tags=["api"]
)

class CleaningRequest(BaseModel):
    user_id: str
    date_start: date
    date_end: date
    target_post_ids: List[int] = []
    is_force_reprocess: bool = False
    is_dry_run_only: bool = False
    log_level_type: str = "normal"
    is_enable_batch_log: bool = True
    is_enable_post_refinement: bool = True
    action_mode: str = "mode_ai" # "mode_ai", "mode_script", "mode_result" などの値を想定


@router.post("/cleaning-post")
async def cleaning_post_api(req: CleaningRequest, db: Session = Depends(get_db)):
    # 手順書の定義に基づく内部フラグの確定
    # C: スクリプト作成のみ
    # is_make_script_only = (req.disp == "targets")
    
    # CがONなら D, E, F は強制OFF
    if req.action_mode == "mode_script" or req.action_mode == "mode_ai":
        log_level = "none"
        is_enable_batch_log = False
        is_enable_post_refinement = False
    else:
        log_level = req.log_level_type
        is_enable_batch_log = (log_level != "none")
        is_enable_post_refinement = is_enable_batch_log # EがOFFならFもOFF

    process_log = []

    # --- Step 3 & 4: 抽出とプロンプト作成 ---
    # (ここは共通処理)
    target_posts = fetch_posts_from_db(db, req.user_id,req.date_start,req.date_end,req.target_post_ids) # 既存の取得処理
    # print("target_posts:", target_posts)
    filtered_posts = filter_posts_with_state_detail(target_posts,req.is_force_reprocess) # state_detailでの絞り込み
    # print("filtered_posts:", filtered_posts)
    
    slug = "typo_prompt" ## todo
    tags_json = get_formatted_tags_json(db, req.user_id) if req.user_id else ""
    prompt_template = get_prompt_template_from_db(db,slug)

    final_prompt = build_prompt_text(db, filtered_posts, req.user_id, prompt_template,tags_json)
    process_log.append("Step 4: プロンプトを作成しました。")


    # --- Step 5 & 6: AI問い合わせ & ログ登録 ---
    if is_enable_batch_log:
        # insert: ai_Batches, ai_Execution_Logs (開始)
        process_log.append("Step 5: バッチ処理ログを登録しました。")

    if req.action_mode == "mode_script":
        return {
            "status": "C_MODE_COMPLETED",
            "result": "Prompt created successfully",
            "prompt": final_prompt,
            "log": process_log
        }

    # AIリクエスト実行
    ai_raw_result = call_gemini_api(db, filtered_posts, req.user_id, prompt_template,tags_json)
    print("ai_raw_result:", ai_raw_result)
    # ai_raw_result=""
    if is_enable_post_refinement:
        # update: zstu_posts.ai_refinement
        # insert: zstu_post_refinements
        process_log.append("Step 6: ポストごとのAI結果をDBに登録しました。")

    # --- Step 7: 結果の送信 ---
    if is_enable_post_refinement:
        # insert: api_logs (メール送信の代わりのログ)
        process_log.append("Step 7: 処理結果をログに送信しました。")

    return {
        "status": "COMPLETED",
        "CleaningRequest": req,
        "log": process_log,
        "batch_id": 12345 if is_enable_batch_log else None
    }

# @router.post("/cleaning-post")
# async def cleaning_post_api(
#     payload: CleaningPostRequest,
#     db: Session = Depends(get_db)
# ):
#     # print(f"cleaning_post_api payload: {payload}")
#     try:
#         result = await cleaning_post(db,payload )
#         # TODO: ここに実際のクリーニング処理を実装
#         # 現在はリクエスト内容をそのまま返却
#         return {
#             "status": "success",
#             "message": "cleaning_post_api accepted",
#             "data": payload,
#             "result": result
#         }
#     except Exception as e:
#         logging.error(f"cleaning_post_api error: {e}")
#         raise HTTPException(status_code=500, detail=f"Error: {str(e)}")