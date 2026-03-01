import os
import resend
from typing import List, Optional
from fastapi import HTTPException
from dotenv import load_dotenv

# .envを読み込み
load_dotenv()

# APIキーの設定
resend.api_key = os.getenv("FASTAPI_RESEND_API_KEY")

def send_resend_email(
    to: List[str],
    subject: str,
    html_content: str,
    from_email: str = "onboarding@resend.dev" # ドメイン認証後は自分のドメインに変更
):
    """
    Resend APIを使用してメールを送信する共通関数
    """
    try:
        params: resend.Emails.SendParams = {
            "from": from_email,
            "to": to,
            "subject": subject,
            "html": html_content,
        }
        
        email = resend.Emails.send(params)
        return email
    except Exception as e:
        # ログ出力などをここに入れると便利です
        print(f"Email sending failed: {e}")
        raise HTTPException(status_code=500, detail="メール送信に失敗しました")