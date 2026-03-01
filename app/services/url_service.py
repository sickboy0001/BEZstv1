import os
from sqlalchemy.orm import Session
from app.lib.URLGenerator import URLGenerator, UUIDMapping, generate_short_id
from app.lib.UUIDGenerator import UUIDGenerator as CryptoUUIDGenerator

def register_short_url(db: Session, system_name: str, user_id: str, batch_id: int,controller_name:str="ai"):
    """
    UUIDを生成してDBに登録し、短縮URLとリダイレクトURLを返します。
    """
    # UUID生成 (暗号化)
    secret_key = os.environ.get("FERNET_KEY")
    uuid_generator = CryptoUUIDGenerator(secret_key)
    
    # system_name, user_id, batch_id を元に暗号化されたUUIDを生成
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
    url_generator = URLGenerator()
    redirect_url = url_generator.generate_url(controller_name, short_id)
    
    return short_id, redirect_url