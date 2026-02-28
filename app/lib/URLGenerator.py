import os
import hashlib
from sqlalchemy import create_engine, Column, String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base
class URLGenerator:
    def __init__(self):
        # 環境変数から環境タイプを取得します。
        self.environment = os.environ.get("APP_ENVIRONMENT", "local")  # デフォルトはローカル

        # 環境に基づいてホスト名を設定します。
        self.host_names = {
            "local": "http://localhost:8000",
            "production": "https://gemini.google.com",
            # 他の環境もここに追加できます
        }
        self.host_name = self.host_names.get(self.environment, "http://localhost:8000")  # デフォルトはローカル

    def generate_url(self, controller_name, batch_id):
        # URLを生成します。
        return f"{self.host_name}/{controller_name}/{batch_id}"

# 短いIDを生成する関数
def generate_short_id(uuid_str):
    """UUIDから短いIDを生成します。"""
    hash_object = hashlib.sha256(uuid_str.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig[:8]  # 最初の8文字を短いIDとして使用
# データベースモデル

Base = declarative_base()

class UUIDMapping(Base):
    __tablename__ = "uuid_mapping"

    short_id = Column(String, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    system_name = Column(String)
    user_id = Column(String)
    parameters = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
# # URLGeneratorのインスタンスを作成します。
# url_generator = URLGenerator()

# # コントローラー名とbatch_idを使用してURLを生成します。
# controller_name = "app"
# batch_id = "9311634c423927eb"
# url = url_generator.generate_url(controller_name, batch_id)

# # 生成されたURLを印刷します。
# print(f"生成されたURL: {url}")