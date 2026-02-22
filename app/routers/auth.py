from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from ..services.supabase_client import supabase
from ..dependencies import templates

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request, message: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "message": message})

@router.post("/login")
async def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="access_token", value=res.session.access_token, httponly=True, secure=False)
        return response
    except Exception as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": "ログインに失敗しました。メールアドレスかパスワードを確認してください。"})

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.session:
            return templates.TemplateResponse("login.html", {"request": request, "message": "登録が完了しました。ログインしてください。"})
        return templates.TemplateResponse("login.html", {"request": request, "message": "登録確認メールを送信しました。メール内のリンクから登録を完了してください。"})
    except Exception as e:
        print(f"DEBUG: 登録エラー発生: {e}")
        return templates.TemplateResponse("register.html", {"request": request, "error": "登録に失敗しました。入力内容を確認してください。"})

@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_form(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@router.post("/forgot-password")
async def forgot_password_submit(request: Request, email: str = Form(...)):
    try:
        supabase.auth.reset_password_for_email(email)
        return templates.TemplateResponse("check_email.html", {"request": request, "email": email})
    except Exception as e:
        return templates.TemplateResponse("check_email.html", {"request": request, "email": email})

@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_form(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})

@router.post("/update-password")
async def update_password_submit(request: Request, password: str = Form(...), token: str = Form(...)):
    try:
        supabase.auth.update_user(attributes={"password": password}, jwt=token)
        return RedirectResponse(url="/login?message=パスワードが正常に更新されました。新しいパスワードでログインしてください。", status_code=303)
    except Exception as e:
        error_message = "パスワードのリセットに失敗しました。リンクの有効期限が切れているか、無効なリンクです。もう一度やり直してください。"
        return templates.TemplateResponse("reset_password.html", {"request": request, "error": error_message})

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response