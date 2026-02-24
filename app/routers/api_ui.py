from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.dependencies import templates, get_current_user
router = APIRouter(
    prefix="/api/ui",
    tags=["UI Components"]
)


@router.get("/post-selector", response_class=HTMLResponse)
async def post_selector_modal(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    """
    HTMXリクエストに応答して、Post選択用のモーダルHTMLを返します。
    """
    print(user)
    if not user:
        return templates.TemplateResponse(
            "api_test/components/post_selector_modal.html",
            {"request": request, "posts": []}
        )

    posts = []
    try:
        # zstu_postsテーブルから最新の投稿を取得 (最大50件)
        # ※カラム名は実際のDB定義に合わせて調整が必要な場合があります
        query = text("SELECT * FROM zstu_posts WHERE user_id = :user_id ORDER BY updated_at DESC LIMIT 50")
        result = db.execute(query, {"user_id": user.id})
        # 行を辞書形式に変換
        posts = [dict(row._mapping) for row in result]
    except Exception as e:
        print(f"Error fetching posts: {e}")
        # エラー時は空リストで続行（テンプレート側で「データなし」表示）
    
    return templates.TemplateResponse(
        "api_test/components/post_selector_modal.html",
        {"request": request, "posts": posts}
    )
