## 🚀 プロジェクト概要

**BackEndZeroSecondThink** は、Python/FastAPI と htmx を組み合わせ、SPAのような操作感を最小限の JavaScript で実現するモダンな Web アプリケーションです。Cloud Run によるオートスケーリングと、Turso による高速なエッジ・ロギングを組み合わせ、高可用かつ低遅延なシステムを目指しています。

---

## 🛠 技術スタックと選定理由

| 技術要素 | 役割・選定理由 |
| --- | --- |
| **Python / FastAPI** | サーバーサイドの主軸。非同期処理と型安全性を両立し、DIを活用した保守性の高い設計を実践。 |
| **htmx** | フロントエンドのUX向上。サーバーサイドから部分的なHTMLを返すことで、複雑なJSフレームワークなしに動的なUIを実現。 |
| **DaisyUI (Tailwind)** | UIコンポーネント。一貫したデザインと迅速なスタイリングを可能にするため採用。 |
| **Cloud Run (Docker)** | インフラ基盤。Renderから移行し、リクエストに応じた柔軟なスケーリングとデプロイの高速化を実現。 |
| **Supabase** | 認証基盤（Auth）およびメインの構造化データ（PostgreSQL）の管理。 |
| **Turso (libSQL)** | **エッジ・ロギング。** CSVLoggerを拡張し、APIアクセスログや処理進捗を低遅延でクラウド上に蓄積。 |

---

## 📋 基本仕様

### 1. 開発・実行環境

* **エディタ**: Visual Studio Code (VS Code)
* **ランタイム**: Python 3.12+ / Docker
* **ローカル環境**: `venv` による仮想環境管理
* **パッケージ管理**: pip (`requirements.txt`)

### 2. フロントエンド

* **テンプレートエンジン**: Jinja2 (サーバーサイド・レンダリング)
* **非同期通信**: htmx (HTMLの部分置換、ローディング制御)
* **デザイン**: DaisyUI / Tailwind CSS

### 3. バックエンド & データ層

* **Webフレームワーク**: FastAPI (Async対応)
* **バリデーション**: Pydantic v2
* **メインDB/認証**: Supabase 
* **ログ基盤**: Turso (HTTPベースのSQLite) ＋ ローカルCSVのハイブリッド構成

### 4. インフラ

* **デプロイ**: Google Cloud Build -> Cloud Run
* **環境変数管理**: `.env` による環境分離 (Local / Production)

---



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

CloudRunを利用したCI/CDが自動化されています。

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


### この構成で実現できること

1. **データ構造の一致**: CSVのカラム名とTursoのテーブルカラム名が完全に一致するため、後からCSVをSQLで分析したり、逆にTursoからCSVへ書き戻すのも容易です。
2. **型変換の自動化**: `request_header` や `input_data` など、Pythonの辞書をそのまま渡せば、`json.dumps` を経てDBにはテキストとして、CSVには文字列として正しく保存されます。
3. **耐障害性**: もしネット接続が不安定でTursoへのHTTPリクエストが失敗しても、ローカルの `logs/api_logs.csv` には必ずデータが残ります。

この実装をベースに、さらに「特定のユーザーIDで絞り込みたい」や「エラー時だけ詳細なスタックトレースを含める」といった調整も簡単に行えます。実際のプロジェクトに組み込んでみてはいかがでしょうか？



プロジェクトの規模と保守性を考えると、**「`app/lib/` にクラス本体を置き、`app/main.py` でインスタンス化して DI（Dependency Injection）で各所に配る」**構成が最もクリーンで FastAPI らしい設計です。

具体的にどこに何を置くべきか、ディレクトリ構造に合わせて整理しました。

---


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
