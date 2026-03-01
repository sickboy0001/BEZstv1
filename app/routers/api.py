from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from pydantic import BaseModel
import logging
from sqlalchemy.orm import Session
from app.services.cleaning_post_service import (
    build_prompt_text, call_gemini_api, cleaning_post, CleaningPostRequest, fetch_posts_from_db, filter_posts_with_state_detail
)
from app.database import get_db
from datetime import date
from app.services.db_service import get_datefromto_posts, get_postids_posts
from app.services.mailsend import mailsend_typo
from app.services.prompt_tamplate_service import get_prompt_template_from_db
from app.services.tags_service import get_formatted_tags_json
from app.services.user_service import get_user_mail


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
    # is_enable_batch_log: bool = True # 未使用？
    # is_enable_post_refinement: bool = True  # 未使用？
    action_mode: str = "mode_ai" # "mode_ai", "mode_script", "mode_result" などの値を想定
    is_enable_post_status_update: bool = True # 追加: ポストのステータス更新を行うかどうかのフラグ

@router.post("/cleaning-post")
async def cleaning_post_api(req: CleaningRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    # 手順書の定義に基づく内部フラグの確定
    # C: スクリプト作成のみ
    # is_make_script_only = (req.disp == "targets")
    
    # CがONなら D, E, F は強制OFF
    if req.action_mode == "mode_script" or req.action_mode == "mode_ai":
        log_level = "none"
        # is_enable_batch_log = False
        # is_enable_post_refinement = False
    else:
        req.log_level_type
        # is_enable_batch_log = (log_level != "none")
        # is_enable_post_refinement = is_enable_batch_log # EがOFFならFもOFF

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

    if req.is_enable_post_status_update:    
        # todo ポストのステータスを「処理中」に更新するロジックをここに追加 
        # ポストのステータスを「処理中」に更新するロジックをここに追加
        # 例: update_post_status_to_processing(db, filtered_posts)
        process_log.append("Step 4.1: ポストのステータスを「処理中」に更新しました。未実装")
        

    if req.action_mode == "mode_script":
        return {
            "status": "C_MODE_COMPLETED",
            "result": "Prompt created successfully",
            "prompt": final_prompt,
            "log": process_log
        }


    process_log.append("Step 5 : AI問い合わせ (Execution & Logging)")
    ai_raw_result = call_gemini_api(db, filtered_posts, req.user_id, prompt_template,tags_json)
    process_log.append("Step 6: AI結果受領 (Execution & Logging)")

    if req.is_enable_post_status_update:    
        # todo ポストのステータスを「処理中」に更新するロジックをここに追加 
        # ポストのステータスを「処理中」に更新するロジックをここに追加
        # 例: update_post_status_to_processing(db, filtered_posts)
        process_log.append("Step 6.1: ポストのステータスを「処理済み」に更新しました。未実装")
        process_log.append("is_enable_post_status_update=trueのため")

    # print("ai called after this actionmode ",req.action_mode)
    batch_id_for_log = ai_raw_result.get("batch_id") if ai_raw_result else None    
    # batch_id_for_log = ai_raw_result.batch_id if ai_raw_result else None
    print("batch_id_for_log: ", batch_id_for_log)
    if req.action_mode == "mode_ai":
        return {
            "status": "AI_MODE_COMPLETED",
            "result": "AI processing completed",
            "batch_id": batch_id_for_log, # AI処理の結果からbatch_idを取得して返す
            "ai_raw_result": ai_raw_result,
            "log": process_log
        }
    
    # if req.action_mode == "mode_result":
    user_mail = await get_user_mail(db, req.user_id) if req.user_id else "unknown"
    if(user_mail):
        # 結果の送信 (メール送信などの処理をここに実装)
        # 例: send_result_email(user_mail, ai_raw_result)
        # mailsend_typo(db,req.user_id , user_mail,batch_id_for_log)
        await mailsend_typo(db, req.user_id, user_mail, batch_id_for_log, background_tasks)
        process_log.append(f"Step 7: 結果をユーザー({user_mail})に送信しました。")
    


    return {
        "status": "SUCCESS",
        "CleaningRequest": req,
        "log": process_log,
        "batch_id": batch_id_for_log 
    }
