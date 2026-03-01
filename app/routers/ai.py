import os
from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session

from libsql_client import Client
from app.database import get_db
from app.database_turso import get_db_turso
from app.dependencies import get_current_user, jst_filter,templates
from app.lib.URLGenerator import UUIDMapping
from app.lib.UUIDGenerator import UUIDGenerator
from app.routers.system_logs import get_system_traces
from app.services.ai_log_service import get_ailogexecution_detail_id_from_db, get_ailogexecutions_id_from_db, get_ailoghdlist_userid_from_db, get_ailogposts_id_from_db


router = APIRouter(
    tags=["ai"]
)


@router.get("/ai/typo/list", response_class=HTMLResponse)
async def ai_type_list(
        request: Request,
        user = Depends(get_current_user),
        db: Session = Depends(get_db),
        turso_db: Client = Depends(get_db_turso)
    ):
    if not user:
        return RedirectResponse(url="/login")
    
    # print(f"created_at (UTC): {uuid_mapping.created_at}, created_at (JST): {jst_filter(uuid_mapping.created_at)}")
    # Turso DB接続
    # Depends(get_db_turso) に変更したため、手動での next() は不要です
    
    # batch_id を int に変換 (recovered_batch_id は文字列のため)
    # batch_id_int = int(recovered_batch_id) if recovered_batch_id and recovered_batch_id.isdigit() else 0
    
    ai_loghd_list = get_ailoghdlist_userid_from_db(turso_db, userid=user.id, limit=100)

    # リスト内の各要素に対してJST変換を行い、created_at_jstを追加
    for log in ai_loghd_list:
        if log.get("created_at"):
            log["created_at_jst"] = jst_filter(log["created_at"])

    # for log in ai_loghd_list:
    #     print(f"original created_at: {log.get('created_at')}, created_at_jst: {log.get('created_at_jst')}")


    # テンプレートに情報を渡して表示
    return templates.TemplateResponse("ai/ai_typo_list.html", {
        "user": user,
        "request": request,
        "ai_loghd_list": ai_loghd_list
    })



@router.get("/ai/typo/list", response_class=HTMLResponse)
async def ai_type_list(
        request: Request,
        user = Depends(get_current_user),
        db: Session = Depends(get_db),
        turso_db: Client = Depends(get_db_turso)
    ):
    if not user:
        return RedirectResponse(url="/login")
    
    # print(f"created_at (UTC): {uuid_mapping.created_at}, created_at (JST): {jst_filter(uuid_mapping.created_at)}")
    # Turso DB接続
    # Depends(get_db_turso) に変更したため、手動での next() は不要です
    
    # batch_id を int に変換 (recovered_batch_id は文字列のため)
    # batch_id_int = int(recovered_batch_id) if recovered_batch_id and recovered_batch_id.isdigit() else 0
    
    ai_loghd_list = get_ailoghdlist_userid_from_db(turso_db, userid=user.id, limit=100)

    # リスト内の各要素に対してJST変換を行い、created_at_jstを追加
    for log in ai_loghd_list:
        if log.get("created_at"):
            log["created_at_jst"] = jst_filter(log["created_at"])

    # for log in ai_loghd_list:
    #     print(f"original created_at: {log.get('created_at')}, created_at_jst: {log.get('created_at_jst')}")


    # テンプレートに情報を渡して表示
    return templates.TemplateResponse("ai/ai_typo_list.html", {
        "user": user,
        "request": request,
        "ai_loghd_list": ai_loghd_list
    })

@router.get("/ai/typo_detail/{batche_id}", response_class=HTMLResponse)
async def ai_type_entry(
        request: Request,
        batche_id: int,
        user = Depends(get_current_user),
        db: Session = Depends(get_db),
        turso_db: Client = Depends(get_db_turso)
    ):
    if not user:
        return RedirectResponse(url="/login")
    
    batch_id_int =batche_id
    
    ai_log_posts = get_ailogposts_id_from_db(turso_db, id=batch_id_int, limit=100)
    ai_log_executions = get_ailogexecutions_id_from_db(turso_db, id=batch_id_int, limit=100)
    print(f"ai_type: ai_log_posts count: {len(ai_log_posts)}")
    # テンプレートに情報を渡して表示
    return templates.TemplateResponse("ai/ai_typo_detail.html", {
        "user": user,
        "request": request,
        "ai_log_posts": ai_log_posts,
        "ai_log_executions": ai_log_executions
    })


@router.get("/ai/typo/{short_id}", response_class=HTMLResponse)
async def ai_type_entry(
        request: Request,
        short_id: str,
        user = Depends(get_current_user),
        db: Session = Depends(get_db),
        turso_db: Client = Depends(get_db_turso)
    ):
    if not user:
        return RedirectResponse(url="/login")
    
    """短いIDから詳細ページにリダイレクトします。"""
    uuid_mapping = db.query(UUIDMapping).filter(UUIDMapping.short_id == short_id).first()
    if uuid_mapping is None:
        raise HTTPException(status_code=404, detail="UUID not found")

    # UUIDから復元
    secret_key = os.environ.get("FERNET_KEY")
    uuid_generator = UUIDGenerator(secret_key)
    recovered_system_name, recovered_user_id, recovered_batch_id = uuid_generator.recover_data(uuid_mapping.uuid)

    # ログイン者が違う場合はリダイレクト
    if user.id != recovered_user_id:
        return RedirectResponse(url="/login")
    print(f"created_at (UTC): {uuid_mapping.created_at}, created_at (JST): {jst_filter(uuid_mapping.created_at)}")
    # Turso DB接続
    # Depends(get_db_turso) に変更したため、手動での next() は不要です
    
    # batch_id を int に変換 (recovered_batch_id は文字列のため)
    batch_id_int = int(recovered_batch_id) if recovered_batch_id and recovered_batch_id.isdigit() else 0
    
    ai_log_posts = get_ailogposts_id_from_db(turso_db, id=batch_id_int, limit=100)
    print(f"ai_type: ai_log_posts count: {len(ai_log_posts)}")
    # テンプレートに情報を渡して表示
    return templates.TemplateResponse("ai/ai_typo.html", {
        "user": user,
        "request": request,
        "system_name": uuid_mapping.system_name,
        "user_id": uuid_mapping.user_id,
        "parameters": uuid_mapping.parameters,  # parametersをそのまま渡す
        "recovered_system_name": recovered_system_name,
        "recovered_user_id": recovered_user_id,
        "recovered_batch_id": recovered_batch_id,
        "created_at_jst": jst_filter(uuid_mapping.created_at),
        "ai_log_posts": ai_log_posts
    })

@router.get("/ai/execution_detail/{execution_id}", response_class=HTMLResponse)
async def get_execution_detail(request: Request, execution_id: int,
        db: Session = Depends(get_db),
        turso_db: Client = Depends(get_db_turso)):

    
    print(f"ai_type: execution_id: {execution_id}")
    execution_detail = get_ailogexecution_detail_id_from_db(turso_db, id=execution_id, limit=1)[0]
    print(f"ai_type: execution_detail: {execution_detail}")
    # テンプレートに情報を渡して表示
    return templates.TemplateResponse("ai/components/execution_detail.html", {
        "request": request,
        "execution_id": execution_id,
        "execution_detail": execution_detail
    })
