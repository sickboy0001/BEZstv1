from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    # デフォルト値を設定しつつ、環境変数があればそちらを優先
    BATCH_TEST_TARGET_USER_ID: str = "76b8d0ed-825d-43a6-a725-37e10c11015b"
    BATCH_DAYS_OFFSET_START: int = 4  # 何日前から
    BATCH_DAYS_OFFSET_END: int = 1    # 何日後まで

    model_config = SettingsConfigDict(
            env_file=".env",
            extra="ignore",  # ← これが重要！定義外の変数（database_url等）があっても無視します
            env_ignore_empty=True
        )

settings = Settings()

# from app.config import settings  # インポート

# # ... (略) ...

#     # 日本時間 (UTC+9) の設定
#     JST = timezone(timedelta(hours=9))
#     now_jst = datetime.now(JST)
    
#     # マジックナンバーを排除し、設定値から計算
#     date_start = (now_jst - timedelta(days=settings.BATCH_DAYS_OFFSET_START)).date()
#     date_end = (now_jst + timedelta(days=settings.BATCH_DAYS_OFFSET_END)).date()
    
#     # 固定ユーザーIDも設定から取得
#     fixed_user_id = settings.BATCH_TARGET_USER_ID

#     # CleaningRequest作成
#     req = CleaningRequest(
#         user_id=fixed_user_id,
#         date_start=date_start,
#         date_end=date_end,
#         # ... (以下同じ)