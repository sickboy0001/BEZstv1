from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
import os

from sqlalchemy.orm import Session

from app.database import get_db
from app.lib.URLGenerator import URLGenerator, UUIDMapping, generate_short_id
from app.lib.UUIDGenerator import UUIDGenerator
from ..dependencies import templates, get_current_user
import uuid

router = APIRouter()



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
        # UUID生成
        secret_key = os.environ.get("FERNET_KEY")
        uuid_generator = UUIDGenerator(secret_key)
        user_id = str(uuid.uuid4())  # Generate a new UUID for each submission
        identifier_uuid = uuid_generator.generate_uuid(system_name, user_id, str(batch_id))

        # 短いIDの生成
        short_id = generate_short_id(identifier_uuid)

        # parametersとしてbatch_idを格納
        parameters = {"batch_id": batch_id}

        # データベースに保存
        db_uuid_mapping = UUIDMapping(short_id=short_id, uuid=identifier_uuid, system_name=system_name, user_id=user_id, parameters=parameters)
        db.add(db_uuid_mapping)
        db.commit()
        db.refresh(db_uuid_mapping)

        # リダイレクトURLの生成
        redirect_url = f"/app/{short_id}"
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
