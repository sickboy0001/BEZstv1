from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

def generate_fernet_key():
    """Fernetキーを生成し、既存の.envファイルに保存、または表示します。"""
    key = Fernet.generate_key().decode()

    # .envファイルが存在する場合、キーを追加または更新します
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            lines = f.readlines()

        key_exists = False
        with open(".env", "w") as f:
            for line in lines:
                if line.startswith("SECRET_KEY="):
                    f.write(f"SECRET_KEY=\"{key}\"\n")
                    key_exists = True
                else:
                    f.write(line)
            if not key_exists:
                f.write(f"SECRET_KEY=\"{key}\"\n")  # 存在しない場合はキーを追加
        print(".envファイルに新しいFernetキーを保存しました。")

    # .envファイルが存在しない場合は、キーを表示します
    else:
        print(f"Fernetキー: {key}")
        print("このキーをSECRET_KEYとして.envファイルに保存してください。")

if __name__ == "__main__":
    generate_fernet_key()