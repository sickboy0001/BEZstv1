import csv
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict
from fastapi import BackgroundTasks
from libsql_client import create_client_sync

class EnhancedCSVLogger:
    def __init__(self, turso_url: str, turso_token: str, base_path: str = "logs"):
        # wss:// や libsql:// を https:// (HTTP) に変換
        # 毎回接続を切断する使い方の場合、HTTPの方が安定し高速です
        if turso_url:
            if turso_url.startswith("wss://"):
                self.turso_url = turso_url.replace("wss://", "https://", 1)
            elif turso_url.startswith("libsql://"):
                self.turso_url = turso_url.replace("libsql://", "https://", 1)
            else:
                self.turso_url = turso_url
        else:
            self.turso_url = turso_url
        self.turso_token = turso_token
        self.base_path = base_path

    def _get_csv_path(self, table_name: str) -> str:
        # 日付ごとにログファイルをローテーション (e.g., api_logs_2026-02-23.csv)
        today = datetime.now().strftime('%Y-%m-%d')
        return f"{self.base_path}/{table_name}_{today}.csv"

    def _write_to_csv(self, table_name: str, data: Dict[str, Any]):
        path = self._get_csv_path(table_name)

        # ディレクトリが存在しない場合は作成する
        os.makedirs(os.path.dirname(path), exist_ok=True)

        file_exists = False
        try:
            with open(path, 'r') as f: file_exists = True
        except FileNotFoundError: pass

        with open(path, 'a', newline='', encoding='utf-8') as f:
            # 辞書のキーをヘッダーとして使用
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

    def _write_to_turso(self, table_name: str, data: Dict[str, Any]):
        # 念のため実行時にもURLをチェックし、wss:// や libsql:// なら https:// に強制変換する
        # (インスタンス初期化時の変換漏れや、再起動不足への対策)
        use_url = self.turso_url
        if use_url:
            if use_url.startswith("wss://"):
                use_url = use_url.replace("wss://", "https://", 1)
            elif use_url.startswith("libsql://"):
                use_url = use_url.replace("libsql://", "https://", 1)

        try:
            # Turso(SQLite)用にデータを加工（辞書・リストをJSON文字列へ）
            processed_data = {
                k: (json.dumps(v) if isinstance(v, (dict, list)) else v) 
                for k, v in data.items()
            }
            
            with create_client_sync(use_url, auth_token=self.turso_token) as client:
                keys = ", ".join(processed_data.keys())
                placeholders = ", ".join([":" + k for k in processed_data.keys()])
                sql = f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})"
                client.execute(sql, processed_data)
        except Exception as e:
            print(f"【警告】Turso書き込み失敗 (CSVには保存済): {e}")

    def log(self, background_tasks: BackgroundTasks, table_name: str, data: Dict[str, Any]):
        """CSV保存とTurso保存(非同期)を同時に実行"""
        # 共通項目の自動付与
        if "created_at" not in data:
            data["created_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # 1. ローカルCSVへ即時書き込み
        self._write_to_csv(table_name, data)
        
        # 【追加】Cloud Run向け: 標準出力へJSON形式で出力
        # これにより Google Cloud Logging に構造化ログとして保存・永続化されます
        print(json.dumps(data, default=str, ensure_ascii=False))
        
        # 2. Tursoへバックグラウンド書き込み
        background_tasks.add_task(self._write_to_turso, table_name, data)