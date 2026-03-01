
import os
from fastapi import FastAPI, BackgroundTasks,APIRouter, Depends, HTTPException, Request, Form
from app.lib.Resend import send_resend_email
from app.services.url_service import register_short_url


async def mailsend_typo(db,user_id , user_mail, batch_id, background_tasks: BackgroundTasks):
    print(f"Sending typo notification to {user_mail} with batch_id {batch_id}") 
    # ここに実際のメール送信ロジックを実装してくださ
    # い。
    application_name = "BEZST"
    system_name="ai-typo"
    controller_name = "ai/typo"
    short_id, redirect_url = register_short_url(db, 
                                                system_name, 
                                                user_id, batch_id,
                                                controller_name=controller_name)

    background_tasks.add_task(
        send_resend_email,
        to=[user_mail],
        subject=f"[{application_name}] AI処理結果のお知らせ (typo通知) {system_name}",
        html_content=f"<strong>無事に届きました！</strong> <br>short_id : {short_id}, redirect_url: {redirect_url}"
    )
