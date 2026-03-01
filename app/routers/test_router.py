from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
import os

from sqlalchemy.orm import Session

from app.database import get_db
from app.lib.URLGenerator import UUIDMapping
from ..dependencies import templates, get_current_user
import uuid

router = APIRouter()


from app.services.url_service import register_short_url
from app.lib.UUIDGenerator import UUIDGenerator

@router.get("/test", response_class=HTMLResponse)
async def test_form(request: Request):
    return templates.TemplateResponse("test_url_form.html", {"request": request})


@router.post("/test", response_class=HTMLResponse)
async def test_submit(
        request: Request,
        system_name: str = Form(...),
        user_id: str = Form(...),
        batch_id: int = Form(...),
        db: Session = Depends(get_db)
    ):
        # ユーザーIDを新規生成 (元のロジックを踏襲)
        # ※フォームから受け取ったuser_idを使いたい場合は、この行を削除してください
        generated_user_id = str(uuid.uuid4())

        # サービス層のメソッドを呼び出して登録処理を実行
        short_id, redirect_url = register_short_url(db, system_name, generated_user_id, batch_id)

        print (f"Generated short_id: {short_id}, redirect_url: {redirect_url}")

        # テンプレートに渡すデータ
        template_data = {
            "request": request,
            "short_id": short_id,
            "redirect_url": redirect_url,
        }
        # テンプレートをレンダリングして返す
        return templates.TemplateResponse("test_url_form.html", template_data)

@router.get("/app/{short_id}", response_class=HTMLResponse)
async def redirect_to_details(short_id: str, request: Request, db: Session = Depends(get_db)):
    """短いIDから詳細ページにリダイレクトします。"""
    uuid_mapping = db.query(UUIDMapping).filter(UUIDMapping.short_id == short_id).first()
    if uuid_mapping is None:
        raise HTTPException(status_code=404, detail="UUID not found")

    # UUIDから復元
    secret_key = os.environ.get("FERNET_KEY")
    uuid_generator = UUIDGenerator(secret_key)
    recovered_system_name, recovered_user_id, recovered_batch_id = uuid_generator.recover_data(uuid_mapping.uuid)

    # テンプレートに情報を渡して表示
    return templates.TemplateResponse("test_url_detail.html", {
        "request": request,
        "system_name": uuid_mapping.system_name,
        "user_id": uuid_mapping.user_id,
        "parameters": uuid_mapping.parameters,  # parametersをそのまま渡す
        "recovered_system_name": recovered_system_name,
        "recovered_user_id": recovered_user_id,
        "recovered_batch_id": recovered_batch_id,
        "created_at": uuid_mapping.created_at
    })
