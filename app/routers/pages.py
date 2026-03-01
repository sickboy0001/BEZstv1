from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from ..dependencies import templates, get_current_user
from ..database import get_db
from ..services.post_service import get_recent_posts

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    
    # テスト用ツールの情報を辞書で定義（テンプレート側でループ回したり、直接指定したりできます）
    developer_tools = [
        {
            "name": "Turso APIログ確認",
            "url": "/test-api/read-turso-api-log",
            "description": "API実行履歴とタスク進捗ログを結合して表示します。DB接続確認やログ入手テスト用です。"
        },
        {
            "name": "test api gemini",
            "url": "/test-api/Cleaning_post_api_test",
            "description": "UserId,TargetPeriod,TargetPostIdsを指定して、Cleaning_post_apiのテストを行います。"
        },
        {
            "name": "test-router-py",
            "url": "/test",
            "description": "Url作成と登録のテスト用です。"
        },
        {
            "name": "mail-test",
            "url": "/docs",
            "description": "docsのtest-mail notify_testからの投稿可能"
        },    
        {
            "name": "typo-log-list",
            "url": "/ai/typo/list",
            "description": "Typo修正のAIログのリストを表示します。TursoDBからユーザーIDに紐づくログを取得して表示するテスト用です。"
        },    
        ]
        
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request, 
            "user": user,
            "dev_tools": developer_tools
        }
    )

@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request, user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("settings.html", {"request": request, "user": user})

@router.get("/test_supabase", response_class=HTMLResponse)
async def test_supabase(request: Request, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse(url="/login")

    posts = []
    error_msg = None
    try:
        # サービス層経由でデータを取得
        posts = get_recent_posts(db)
    except Exception as e:
        error_msg = f"データ取得エラー: {str(e)}"

    return templates.TemplateResponse("test_supabase.html", {"request": request, "user": user, "posts": posts, "error": error_msg})