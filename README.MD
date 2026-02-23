
# PFXDGRSbase

Python + FastAPI + htmx + Docker + Render + Supabase を組み合わせた、開発効率とモダンなユーザー体験を両立させるためのフルスタック・テンプレートです。

## 🚀 プロジェクト概要

PFXDRS Templateは、ReactやVueなどの重厚なSPAフレームワークを使わずに、HTMLベースで動的なUIを実現する\*\*「ハイパーメディア駆動」\*\*な開発スタイルを提案します。
クリーンなディレクトリ構成とコンテナ化により、迅速な開発からデプロイまでをスムーズに行える構成になっています。

---

## 🛠 技術スタックと選定理由

|技術要素|役割・選定理由|
|-|-|
|**Python / FastAPI**|サーバーサイドの主軸。Router/Service層を分けたクリーンな構成の学習と実践。|
|**htmx**|フロントエンドのUX向上。HTMLベースで動的な非同期通信を実現し、複雑さを軽減。|
|**DaisyUI (Tailwind CSS)**|UIコンポーネントライブラリ。直接CSSを書く手間を省き、一貫したデザインを迅速に構築。|
|**Docker**|環境のポータビリティ確保。Render以外のホスト環境への移行も容易にするため。|
|**Render**|サーバーサイドおよびDockerとの親和性が高く、Vercel以外の有力な選択肢として採用。|
|**Supabase**|データベース(PostgreSQL)および認証基盤(Auth)として利用。|

---

## 📋 基本仕様

### 1\. 開発・実行環境

* **エディタ**: Visual Studio Code (VS Code)
* **開発支援**: Gemini Code Assist
* **ランタイム**: Python 3.11+ / Docker
* **パッケージ管理**: pip (`requirements.txt`)

### 2\. フロントエンド

* **テンプレートエンジン**: Jinja2 (サーバーサイドレンダリング)
* **非同期通信**: htmx (Partial HTMLの差し替え)
* **スタイリング**: DaisyUI (Tailwind CSSベースのコンポーネント)

### 3\. バックエンド \& BaaS

* **Webフレームワーク**: FastAPI
* **バリデーション**: Pydantic
* **DB/Auth**: Supabase (PostgreSQL / Supabase Auth)
* **SDK**: `supabase-py`

---

## 📂 ディレクトリ構成

```
localProject/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── app/
    ├── main.py
    ├── models/          # 【Model】DBテーブル定義 (SQLAlchemy等)
    ├── schemas/         #  入出力バリデーション (Pydantic)
    ├── services/        # 【Business Logic】ここに計算やDB処理を書く
    │   └── item_service.py
    ├── lib/             #  Lib 共通部分
    │   └── utils.py     #  共通関数
    ├── routers/         # 【Controller】ルーティングとViewの制御
    │   └── item_router.py
    ├── templates/       # 【View】HTML (Jinja2)
    │   ├── base.html
    │   └── items/
    │       └── list.html
    └── static/          # 静的ファイル
        ├── css/
        └── js/
```

---

## 🚢 デプロイフロー

Renderを利用したCI/CDが自動化されています。

1. **GitHubへPush**: `main` ブランチへコードをプッシュ。
2. **ビルド**: Renderがリポジトリの `Dockerfile` を検知し、Dockerイメージをビルド。
3. **自動デプロイ**: ビルド成功後、Web Serviceとして自動デプロイ。
4. **環境変数管理**: Render Dashboardおよびローカルの `.env` で秘匿情報を管理。

---

Dockerでの起動方法
ターミナルを開く VS Code で Ctrl + J（または Ctrl + @）を押してターミナルを開きます。

Dockerイメージのビルド 以下のコマンドを実行して、現在のディレクトリ（.）の Dockerfile からイメージを作成します。

```bash
docker build -t testloginrendar .
```

-t testloginrendar: イメージに名前（タグ）を付けます。
コンテナの起動 ビルドが成功したら、以下のコマンドで起動します。

```bash
docker run --rm -p 8000:10000 --env-file .env --name my-test-container testloginrendar
```

--rm: 停止時にコンテナを自動削除します（検証用に便利）。
-p 8000:10000: ホストのポート 8000 をコンテナの 10000 に転送します。
--env-file .env: .env ファイルがある場合、環境変数を読み込みます（docker-compose では自動ですが、docker run では指定が必要です）。 .env については xxxURL="xxxx" はNG　xxxURL=xxxx　はOK　ダブルコーテーションは省くこと。 
検証 ブラウザで http://localhost:8000 にアクセスして動作を確認します。 停止するにはターミナルで Ctrl + C を押します。



## ログ周り

### A. API_Logs（共通アクセスログ）

すべてのリクエストの「外枠」を記録します。パフォーマンス監視やエラーの早期発見に特化したテーブルです。

| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` | BigInt | ログの一意識別子 |
| `trace_id` | UUID | 一連のリクエストを追跡する共通ID（フロントから渡すか、入口で生成） |
| `method` | String | HTTPメソッド (GET, POST, etc.) |
| `endpoint` | String | アクセスされたURLパス |
| `request_header` | JSONB | 認証情報やユーザーエージェントなど |
| `request_body` | JSONB | クライアントから送られてきたデータ |
| `response_status` | Int | HTTPステータスコード (200, 404, 500 etc.) |
| `response_body` | JSONB | 返したレスポンス内容 |
| `duration_ms` | Int | 処理にかかった時間（ミリ秒） |
| `ip_address` | String | 接続元IPアドレス |
| `user_id` | Int | 操作したユーザーのID（ログイン時のみ） |
| `created_at` | Timestamp | リクエスト受信日時 |

---

### B. Task_Progress_Logs（目的別・処理進捗ログ）

特定の重い処理や、複数のステップに分かれるタスクの「中身」を記録します。`API_Logs` と `trace_id` で紐付ける運用を想定しています。

| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` | BigInt | 進捗ログの一意識別子 |
| `trace_id` | UUID | `API_Logs` と紐付けるための追跡ID |
| `task_name` | String | 処理の名前（例: "Image_Optimization", "Bulk_Import"） |
| `step_name` | String | 現在のステップ名（例: "Validation", "AI_Generation", "DB_Commit"） |
| `status` | String | ステップの状態 (START, IN_PROGRESS, SUCCESS, FAILED) |
| `input_data` | JSONB | そのステップに渡された引数やデータ |
| `output_data` | JSONB | そのステップの結果や返り値 |
| `error_message` | Text | 失敗時のエラー内容 |
| `stack_trace` | Text | エラー発生時のスタックトレース |
| `execution_order` | Int | 処理内の実行順序 |
| `created_at` | Timestamp | ステップ開始/記録日時 |

---

### 💡 設計のポイント

1. **Trace ID による紐付け**:
`API_Logs` で「500エラー」を見つけた際、同じ `trace_id` で `Task_Progress_Logs` を検索すれば、どのステップでコケたのかが即座に判明します。
2. **型に JSONB を採用**:
リクエスト内容やタスクごとの個別データは構造が変わりやすいため、`JSONB` 型にしておくことで、スキーマ変更なしで柔軟にログを拡張できます。
3. **BigInt の利用**:
ログテーブルはレコード数が膨大になりやすいため、IDには `Int` よりも範囲の広い `BigInt` を推奨します。

次は、これらのテーブルを使って「エラー調査」や「分析」を行うためのSQLクエリの例を作成しましょうか？あるいは、特定の言語（PythonやNode.jsなど）での実装イメージが必要でしょうか。


### DDL
Turso(SQLite)向け

```sql
-- APIアクセスログ本体
CREATE TABLE api_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- SQLiteではBigInt相当として機能
    trace_id TEXT NOT NULL,               -- UUIDを格納
    method TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    request_header TEXT,                  -- JSONB相当 (TEXTで格納しアプリ側/関数で制御)
    request_body TEXT,                    -- JSONB相当
    response_status INTEGER,
    response_body TEXT,                   -- JSONB相当
    duration_ms INTEGER,
    ip_address TEXT,
    user_id INTEGER,
    created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))
);

-- パフォーマンス最適化のためのインデックス
CREATE INDEX idx_api_logs_trace_id ON api_logs(trace_id);
CREATE INDEX idx_api_logs_created_at ON api_logs(created_at);
CREATE INDEX idx_api_logs_status ON api_logs(response_status);

-- 処理の詳細ステップログ
CREATE TABLE task_progress_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,               -- api_logs.trace_id と紐付け
    task_name TEXT NOT NULL,
    step_name TEXT NOT NULL,
    status TEXT NOT NULL,                 -- START, SUCCESS, FAILED 等
    input_data TEXT,                      -- JSONB相当
    output_data TEXT,                     -- JSONB相当
    error_message TEXT,
    stack_trace TEXT,
    execution_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))
);

-- パフォーマンス最適化のためのインデックス
CREATE INDEX idx_task_progress_trace_id ON task_progress_logs(trace_id);
CREATE INDEX idx_task_progress_created_at ON task_progress_logs(created_at);


```


承知いたしました。提示した「API_Logs」と「Task_Progress_Logs」のテーブルデザインを、そのままPythonの辞書形式（dict）として扱い、CSVとTursoの両方に書き込む拡張版`CSVLogger`の実装を作成します。

これを使うことで、**「ローカルのCSV」と「クラウドのTurso」に全く同じ構造のログが自動的に蓄積**されるようになります。

### 1. 拡張版 `EnhancedCSVLogger` の実装

このクラス1つで、共通ログ（A）と進捗ログ（B）の両方に対応させます。

```python
import csv
import json
import uuid
from datetime import datetime
from typing import Any, Dict
from fastapi import BackgroundTasks
from libsql_client import create_client_sync

class EnhancedCSVLogger:
    def __init__(self, turso_url: str, turso_token: str, base_path: str = "logs"):
        self.turso_url = turso_url
        self.turso_token = turso_token
        self.base_path = base_path

    def _get_csv_path(self, table_name: str) -> str:
        # テーブル名ごとにCSVファイルを分ける (api_logs.csv, task_progress_logs.csv)
        return f"{self.base_path}/{table_name}.csv"

    def _write_to_csv(self, table_name: str, data: Dict[str, Any]):
        path = self._get_csv_path(table_name)
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
        try:
            # Turso(SQLite)用にデータを加工（辞書・リストをJSON文字列へ）
            processed_data = {
                k: (json.dumps(v) if isinstance(v, (dict, list)) else v) 
                for k, v in data.items()
            }
            
            with create_client_sync(self.turso_url, auth_token=self.turso_token) as client:
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
        
        # 2. Tursoへバックグラウンド書き込み
        background_tasks.add_task(self._write_to_turso, table_name, data)

```

### 2. FastAPIでの具体的な利用シーン

先ほど定義したテーブル構成に合わせてデータを流し込みます。

```python
from fastapi import FastAPI, BackgroundTasks, Request

app = FastAPI()
# 初期化
logger = EnhancedCSVLogger(
    turso_url="libsql://your-db-name.turso.io",
    turso_token="your-auth-token"
)

@app.post("/execute-ai-task")
async def execute_task(request: Request, background_tasks: BackgroundTasks):
    trace_id = str(uuid.uuid4())
    
    # --- A. 共通アクセスログ (api_logs) ---
    logger.log(background_tasks, "api_logs", {
        "trace_id": trace_id,
        "method": "POST",
        "endpoint": "/execute-ai-task",
        "request_header": dict(request.headers),
        "request_body": {"item_id": 101}, # 例
        "ip_address": request.client.host
    })

    # --- B. 目的別・処理進捗ログ (task_progress_logs) ---
    # ステップ1: 開始
    logger.log(background_tasks, "task_progress_logs", {
        "trace_id": trace_id,
        "task_name": "AI_Refinement",
        "step_name": "Fetch_Data",
        "status": "SUCCESS",
        "execution_order": 1
    })

    # 実際の処理（シミュレーション）
    try:
        # ステップ2: AI処理中...
        logger.log(background_tasks, "task_progress_logs", {
            "trace_id": trace_id,
            "task_name": "AI_Refinement",
            "step_name": "AI_Generation",
            "status": "IN_PROGRESS",
            "input_data": {"text": "修正前の文章"},
            "execution_order": 2
        })
    except Exception as e:
        # 失敗時の記録
        logger.log(background_tasks, "task_progress_logs", {
            "trace_id": trace_id,
            "task_name": "AI_Refinement",
            "step_name": "AI_Generation",
            "status": "FAILED",
            "error_message": str(e),
            "execution_order": 2
        })

    return {"status": "accepted", "trace_id": trace_id}

```

### この構成で実現できること

1. **データ構造の一致**: CSVのカラム名とTursoのテーブルカラム名が完全に一致するため、後からCSVをSQLで分析したり、逆にTursoからCSVへ書き戻すのも容易です。
2. **型変換の自動化**: `request_header` や `input_data` など、Pythonの辞書をそのまま渡せば、`json.dumps` を経てDBにはテキストとして、CSVには文字列として正しく保存されます。
3. **耐障害性**: もしネット接続が不安定でTursoへのHTTPリクエストが失敗しても、ローカルの `logs/api_logs.csv` には必ずデータが残ります。

この実装をベースに、さらに「特定のユーザーIDで絞り込みたい」や「エラー時だけ詳細なスタックトレースを含める」といった調整も簡単に行えます。実際のプロジェクトに組み込んでみてはいかがでしょうか？



プロジェクトの規模と保守性を考えると、**「`app/lib/` にクラス本体を置き、`app/main.py` でインスタンス化して DI（Dependency Injection）で各所に配る」**構成が最もクリーンで FastAPI らしい設計です。

具体的にどこに何を置くべきか、ディレクトリ構造に合わせて整理しました。

---

### 1. 推奨される配置場所

| 配置場所 | 役割 | 理由 |
| --- | --- | --- |
| **`app/lib/logger.py`** | **クラス定義** | ロガーはビジネスロジックではなく「基盤となる道具」なので `lib` が適切です。 |
| **`app/main.py`** | **初期化 (DI用)** | TursoのURLやトークンを読み込み、1つのインスタンス（シングルトン）を作ります。 |
| **`app/services/`** | **利用場所** | 進捗ログ（Task_Progress_Logs）を記録するために注入して使います。 |

---

### 2. 具体的な実装イメージ

#### ① クラス定義：`app/lib/logger.py`

ここに先ほどの `EnhancedCSVLogger` クラスを置きます。

#### ② 初期化とDI設定：`app/main.py`

FastAPI の `Depends` を使って、どこでもロガーを呼び出せるようにします。

```python
from app.lib.logger import EnhancedCSVLogger
import os

# 1. アプリ全体で共有するインスタンスを作成（シングルトン）
logger_instance = EnhancedCSVLogger(
    turso_url=os.getenv("TURSO_URL"),
    turso_token=os.getenv("TURSO_TOKEN")
)

# 2. DI用の関数
def get_logger():
    return logger_instance

```

#### ③ サービス層での利用：`app/services/item_service.py`

ビジネスロジックの中で「進捗」を記録する場合です。

```python
from fastapi import BackgroundTasks
from app.lib.logger import EnhancedCSVLogger

class ItemService:
    def __init__(self, logger: EnhancedCSVLogger):
        self.logger = logger

    async def do_complex_job(self, trace_id: str, background_tasks: BackgroundTasks):
        # 処理進捗を記録
        self.logger.log(background_tasks, "task_progress_logs", {
            "trace_id": trace_id,
            "task_name": "Item_Update",
            "step_name": "DB_Update_Start",
            "status": "SUCCESS"
        })
        # ...実際の処理...

```

#### ④ ルーター層での利用：`app/routers/item_router.py`

ここで `get_logger` を注入します。

```python
from fastapi import APIRouter, Depends, BackgroundTasks
from app.main import get_logger
from app.lib.logger import EnhancedCSVLogger

router = APIRouter()

@router.post("/items")
async def create_item(
    background_tasks: BackgroundTasks,
    logger: EnhancedCSVLogger = Depends(get_logger) # ここでDI
):
    trace_id = "..." 
    # APIアクセスログを記録
    logger.log(background_tasks, "api_logs", { ... })
    return {"status": "ok"}

```

---

### 3. なぜこの構成が良いのか？

1. **テストがしやすい**:
テスト時に Turso へ接続したくない場合、`get_logger` をオーバーライドして「何もしないロガー」や「CSVだけのロガー」に簡単に差し替えられます。
2. **設定の一元管理**:
`main.py`（または `config.py`）で Turso の接続情報を管理するため、環境変数 (`.env`) との連携がスムーズです。
3. **疎結合**:
`item_service.py` 自体は「どうやってログを保存するか」を知る必要がなく、「渡されたロガーの `.log()` を呼ぶ」だけで済みます。

### 次のステップへの提案

この構成で進める場合、**「共通アクセスログ（api_logs）を各エンドポイントに手動で書くのは面倒」**になりませんか？

もしよろしければ、**FastAPIの「Middleware（ミドルウェア）」を使って、全リクエストの入り口と出口を自動で `api_logs` に記録する仕組み**の実装案も作成できますが、いかがでしょうか？
