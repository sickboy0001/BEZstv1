from fastapi import FastAPI, BackgroundTasks,APIRouter, Depends, HTTPException, Request, Form
from app.lib.Resend import send_resend_email


router = APIRouter(
    tags=["test_mail"]
)

@router.post("/notify_test")
async def notify_user(email: str, background_tasks: BackgroundTasks):
    # email = "syunjyu0001@gmail.com" テストなので、省く、/docsでフォーム入力できるようにする
    # 重い処理を避けるため、BackgroundTasksで投げるのがおすすめ
    background_tasks.add_task(
        send_resend_email,
        to=[email],
        subject="お知らせ",
        html_content="<strong>無事に届きました！</strong>"
    )
    
    return {"message": "送信予約を完了しました"}