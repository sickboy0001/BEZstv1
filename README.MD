- [🚀 プロジェクト概要](#-プロジェクト概要)
- [🛠 技術スタックと選定理由](#-技術スタックと選定理由)
- [📋 基本仕様](#-基本仕様)
  - [1. 開発・実行環境](#1-開発実行環境)
  - [2. フロントエンド](#2-フロントエンド)
  - [3. バックエンド \& データ層](#3-バックエンド--データ層)
  - [4. インフラ](#4-インフラ)
- [📂 ディレクトリ構成](#-ディレクトリ構成)
- [🚢 デプロイフロー](#-デプロイフロー)
- [`zstu_posts`](#zstu_posts)
  - [zstu\_posts:state\_detail](#zstu_postsstate_detail)
- [ログ周り](#ログ周り)
  - [A. API\_Logs（共通アクセスログ）](#a-api_logs共通アクセスログ)
  - [B. Task\_Progress\_Logs（目的別・処理進捗ログ）](#b-task_progress_logs目的別処理進捗ログ)
  - [💡 設計のポイント](#-設計のポイント)
  - [DDL](#ddl)
  - [この構成で実現できること](#この構成で実現できること)
    - [③ サービス層での利用：`app/services/item_service.py`](#-サービス層での利用appservicesitem_servicepy)
    - [④ ルーター層での利用：`app/routers/item_router.py`](#-ルーター層での利用approutersitem_routerpy)
- [AI利用してのポストのタイポ](#ai利用してのポストのタイポ)
  - [UIと基本プロセス](#uiと基本プロセス)
    - [step 1 ログインする（既存機能）](#step-1-ログインする既存機能)
    - [Step 2: UI/API 条件指定 (Input Parameters)](#step-2-uiapi-条件指定-input-parameters)
    - [Step 3: 対象ポスト取得 (Fetch Posts)](#step-3-対象ポスト取得-fetch-posts)
    - [Step 4: プロンプト構築 (Build Prompt)](#step-4-プロンプト構築-build-prompt)
    - [Step 5 : AI問い合わせ (Execution \& Logging)](#step-5--ai問い合わせ-execution--logging)
    - [Step 6: AI結果受領 (Execution \& Logging)](#step-6-ai結果受領-execution--logging)
    - [step 7 結果の送信](#step-7-結果の送信)
    - [Step 8 結果の確認](#step-8-結果の確認)
  - [📊 ログの活用（※1）](#-ログの活用1)
  - [🔄 状態遷移の確定](#-状態遷移の確定)
  - [関連するテーブル `zstu_posts`](#関連するテーブル-zstu_posts)
    - [B.`zstu_posts`](#bzstu_posts)
      - [state\_detail　](#state_detail)
      - [`ai_request` の項目定義](#ai_request-の項目定義)
        - [ステータス遷移とフラグの変化（運用例）](#ステータス遷移とフラグの変化運用例)
        - [💡 運用のポイント](#-運用のポイント)
    - [B. 個別ポスト精査テーブル (`zstu_post_refinements`)](#b-個別ポスト精査テーブル-zstu_post_refinements)
- [🚀 AI週間評価API 設計案](#-ai週間評価api-設計案)
  - [1. Input (引数)](#1-input-引数)
  - [2. Process (ロジックフロー)](#2-process-ロジックフロー)
  - [3. Output (レスポンス)](#3-output-レスポンス)
  - [週次評価結果を保存するテーブル（案）](#週次評価結果を保存するテーブル案)
- [関連するテーブル](#関連するテーブル)
  - [`zstu_tag_descriptions`](#zstu_tag_descriptions)
    - [1. `is_active` (論理削除・有効化)](#1-is_active-論理削除有効化)
    - [2. `is_send_ai` (AI送信フラグ) ※「is\_sendai」の解釈](#2-is_send_ai-ai送信フラグ-is_sendaiの解釈)
    - [3. `display_order` (表示順)](#3-display_order-表示順)
    - [4. `created_at` / `updated_at` (タイムスタンプ)](#4-created_at--updated_at-タイムスタンプ)
  - [`ai_Batches`](#ai_batches)
  - [`ai_Execution_Logs`](#ai_execution_logs)
    - [1. `api_version` の重要性](#1-api_version-の重要性)
    - [2. `duration_ms` (実行時間) の重要性](#2-duration_ms-実行時間-の重要性)
  - [`zstu_post_refinements`](#zstu_post_refinements)
  - [`prompt_templates`](#prompt_templates)
  - [`prompt_versions`](#prompt_versions)
- [todo](#todo)
- [History](#history)



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



## `zstu_posts` 


| カラム物理名 | 論理名 | データ型 | 必須 | デフォルト / 制約 | 備考 |
| --- | --- | --- | --- | --- | --- |
| **id** | 投稿ID | `serial` | ◯ | PRIMARY KEY | 自動採番 |
| **user_id** | ユーザーID | **`uuid`** | ◯ |  | 投稿者の識別子 (auth.users.id) |
| **current_at** | 基準日時 | `timestamp` | - | `CURRENT_TIMESTAMP` | 投稿の対象日・時刻 |
| **title** | タイトル | `text` | ◯ |  |  |
| **content** | 本文 | `text` | ◯ |  |  |
| **tags** | タグリスト | **`text[]`** | ◯ | **`'{}'`** | タグの配列。検索用GINインデックス推奨 |
| **source_type** | 連携元種別 | `varchar` | - |  | `observation`, `hadbit` 等 |
| **source_key** | 連携元キー | **`text`** | - | **UNIQUE (type, key)** | 連携元のID (Int/UUID等を保持) |
| **source_detail** | 連携元詳細 | **`jsonb`** | - |  | 連携元特有の情報 (距離、単位、銘柄等) |
| **second** | 所要秒数 | `integer` | ◯ | `0` | 執筆や実施にかかった秒数 |
| **public_flg** | 公開フラグ | `boolean` | ◯ | `true` | 全体公開設定 |
| **public_content_flg** | 内容公開フラグ | `boolean` | ◯ | `true` | コンテンツ部分の公開設定 |
| **delete_flg** | 削除フラグ | `boolean` | ◯ | `false` | 論理削除フラグ |
| **write_start_at** | 執筆開始日時 | `timestamp` | - | `CURRENT_TIMESTAMP` |  |
| **write_end_at** | 執筆終了日時 | `timestamp` | - | `CURRENT_TIMESTAMP` |  |
| **created_at** | 作成日時 | `timestamp` | ◯ | `CURRENT_TIMESTAMP` | レコード作成日 |
| **updated_at** | 更新日時 | `timestamp` | ◯ | `CURRENT_TIMESTAMP` | レコード更新日 |
| **state_detail** | 状態の詳細 | **`jsonb`** | - |  | AI連携の詳細 |

### zstu_posts:state_detail

AIへの要求などの最終的な状態

|日本語の状態|推奨する英語定数 (Status)|説明・補足|
|:----|:----|:----|
|なし|unprocessed|まだ何もしていない初期状態。|
|再要求|pending_requeue|ユーザーが「やり直し」を求めた状態。次回のバッチ対象。|
|要求中|processing|AIにリクエストを投げた直後、または実行中。|
|受領済み|refined|AIの回答が届き、ユーザーの確認を待っている状態。|
|登録済み（更新あり）|completed_with_edit|AIの結果を元にユーザーが修正して確定させた。|
|登録済み|completed|AIの結果をそのまま確定させた。|

```
{
  "ai_refinement": {
    "status": "refined",
    "is_fixed": false,
    "last_refinement_id": 1234,
    "updated_at": "2026-02-26T14:00:00Z"
  }
}
```



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




## AI利用してのポストのタイポ

- ポストは定期的に、AIでの整形を予定しています。
- １時間に一回生成AIへの要求されていないものがあれば、
- それを要求対象にする動きを想定しています。
- ユーザーにAIでのポストしたことは連携必要
- 画面でも確認できる状態になる。
- そのためには各ポストの状況が必要で、そのための設定については以下のとおりとする。



### UIと基本プロセス

#### step 1 ログインする（既存機能）
#### Step 2: UI/API 条件指定 (Input Parameters)

UIから渡される、またはAPI引数として定義する変数名です。

| 項目 | 変数名 (Python形式) | 型 | デフォルト / 備考 |
| --- | --- | --- | --- |
| **A: ユーザーID** | `user_id` | `uuid` | ログインセッションから取得 |
| **B-1: 期間指定** | `date_start`, `date_end` | `date` | 対象期間（22日〜28日など） |
| **B-2: ポスト個別指定** | `target_post_ids` | `list[int]` | 空リストなら全件対象/ポスト検索時はRead:zstu_posts |
| **B-3: 再問い合わせ** | `is_force_reprocess` | `bool` | `True`なら`refined`済みも対象 |
| **C: 実行モード** | `action_mode` | `str` | `mode_script` , `mode_ai` , `mode_result` |
| **D: ログ詳細度** | `log_level_type` | `str` | `normal`, `detail`, `none` |
| **E: バッチログ登録** | `is_enable_batch_log` | `bool` | `ai_batches` への登録有無 |
| **F: ポスト毎結果登録** | `is_enable_post_refinement` | `bool` | `zstu_post_refinements` への登録 |

**バリデーション・連動ロジック:**

* mode_script スクリプトの作成まで
* mode_ai　aiの問い合わせまで
* mode_result 結果の登録まで
* `if not is_enable_batch_log:` → `is_enable_post_refinement = False`

- Z:「開始」ボタン
  - 参照情報として、対象のプロンプトを確認できること

**バリデーション・連動ロジック:**

* `if is_dry_run_only:` → `log_level_type = 'none'`, `is_enable_batch_log = False`, `is_enable_post_refinement = False`
* `if not is_enable_batch_log:` → `is_enable_post_refinement = False`


#### Step 3: 対象ポスト取得 (Fetch Posts)

1. **検索実行**: `date_start` 〜 `date_end` の範囲で `zstu_posts` を検索。
2. **フィルタリング**:
* `target_post_ids` が指定されていれば、そのIDで絞り込み。
* `is_force_reprocess == False` の場合、`state_detail -> ai_refinement -> status` が `unprocessed` または `pending_requeue` のもののみを抽出。
* 変数 `target_posts` (List[Dict]) に格納。

- 検索条件に合致する件数を API_Logs に記録。
- status: processing へ一括更新。他プロセスからの割り込みを防止。
- 
#### Step 4: プロンプト構築 (Build Prompt)

1. **マスタ取得**: `prompt_versions` から `is_active=True` のテンプレートを取得。
2. **タグ情報取得**: `zstu_tag_descriptions` から `is_send_ai=True` のタグを取得し、コンテキスト用文字列 `tag_context` を作成。
3. **プロンプト生成**: テンプレート内の変数（`{{posts}}`, `{{tags}}` 等）を `target_posts` と `tag_context` で置換。
* 変数名: `final_prompt_text`

1. **早期リターン**: `is_dry_run_only == True` の場合、ここで `final_prompt_text` をレスポンスとして終了。


#### Step 5 : AI問い合わせ (Execution & Logging)

1. **バッチ開始記録**: `is_enable_batch_log == True` なら `ai_batches` にレコード作成。
* 戻り値: `current_batch_id`


2. **AIリクエスト**: Google AI Studioへ `final_prompt_text` を送信。
3. **実行ログ記録**: `ai_execution_logs` に `prompt_template`, `raw_input_json`, `model_info` 等を保存。
4. **個別結果保存**: `is_enable_post_refinement == True` なら、AIの返答をパースし、各ポストに対して `zstu_post_refinements` に `INSERT`。


#### Step 6: AI結果受領 (Execution & Logging)

- 「Step5」の結果受領記録 (Execution & Logging)

1. **実行ログ記録**: `ai_execution_logs` に `prompt_template`, `raw_input_json`, `model_info` 等を保存。
2. **個別結果保存**: `is_enable_post_refinement == True` なら、AIの返答をパースし、各ポストに対して `zstu_post_refinements` に `INSERT`。
* 同時に `zstu_posts.state_detail` の `status` を `refined` に `UPDATE`。

- status: refined へ更新。一連の trace_id を付与。

#### step 7 結果の送信
- 「F」がONの場合は、その結果をメールで送信（ひとまずはログで）
  - insert:api_logs
  - insert:task_progress_logs
#### Step 8 結果の確認
- 「Step 7」を承認するなどの微調整して登録
  - 「F」がOFF対象のPostなし。
  - update:zstu_posts.ai_refinement


### 📊 ログの活用（※1）

`loglevel=detail` の場合、ステップ4のプロンプトとステップ7のAI回答を `API_Logs` に残します。これにより、「AIが変な回答をした」ときに、どのプロンプトが悪かったのか後から完全に再現・調査可能になります。

### 🔄 状態遷移の確定

ステップ9で `refined` になったタイミングで、ユーザー画面（フロントエンド）に「精査完了」のバッジが表示されるようになります。




### 関連するテーブル `zstu_posts` 
#### B.`zstu_posts`

| カラム物理名 | 論理名 | データ型 | 必須 | デフォルト / 制約 | 備考 |
| --- | --- | --- | --- | --- | --- |
| **id** | 投稿ID | `serial` | ◯ | PRIMARY KEY | 自動採番 |
| **user_id** | ユーザーID | **`uuid`** | ◯ |  | 投稿者の識別子 (auth.users.id) |
| **current_at** | 基準日時 | `timestamp` | - | `CURRENT_TIMESTAMP` | 投稿の対象日・時刻 |
| **title** | タイトル | `text` | ◯ |  |  |
| **content** | 本文 | `text` | ◯ |  |  |
| **tags** | タグリスト | **`text[]`** | ◯ | **`'{}'`** | タグの配列。検索用GINインデックス推奨 |
| **source_type** | 連携元種別 | `varchar` | - |  | `observation`, `hadbit` 等 |
| **source_key** | 連携元キー | **`text`** | - | **UNIQUE (type, key)** | 連携元のID (Int/UUID等を保持) |
| **source_detail** | 連携元詳細 | **`jsonb`** | - |  | 連携元特有の情報 (距離、単位、銘柄等) |
| **second** | 所要秒数 | `integer` | ◯ | `0` | 執筆や実施にかかった秒数 |
| **public_flg** | 公開フラグ | `boolean` | ◯ | `true` | 全体公開設定 |
| **public_content_flg** | 内容公開フラグ | `boolean` | ◯ | `true` | コンテンツ部分の公開設定 |
| **delete_flg** | 削除フラグ | `boolean` | ◯ | `false` | 論理削除フラグ |
| **write_start_at** | 執筆開始日時 | `timestamp` | - | `CURRENT_TIMESTAMP` |  |
| **write_end_at** | 執筆終了日時 | `timestamp` | - | `CURRENT_TIMESTAMP` |  |
| **created_at** | 作成日時 | `timestamp` | ◯ | `CURRENT_TIMESTAMP` | レコード作成日 |
| **updated_at** | 更新日時 | `timestamp` | ◯ | `CURRENT_TIMESTAMP` | レコード更新日 |
| **state_detail** | 状態の詳細 | **`jsonb`** | - |  | AI連携の詳細 |

##### state_detail　
* AIへの要求状態をもつ
* AIへの要求などの最終的な状態

* **ai_request.state_detail**

| 状態 (status) | `is_edited` | `is_fixed` | 振る舞い・意味 |
| --- | --- | --- | --- |
| **unprocessed** | `false` | `false` | 初期状態。バッチ処理の対象。 |
| **refined** | `false/true` | `false` | AI回答受領。ユーザー確認待ち。編集すると `is_edited: true`。 |
| **completed** | `any` | `true` | **確定。** ユーザーが保存ボタンを押した後の最終状態。 |
| **pending_requeue** | `any` | `false` | 再要求。バッチがこのフラグを見て `processing` へ戻信。 |
| **processing** |`any`|`false`|AIへのAPIリクエストを投げた直後、またはバッチが処理を開始した状態。|

**unprocessed** **pending_requeue**の場合は、１時間ごとのタスクで生成AIへの要求実施
「要求中」「受領済み」「 登録済み（更新あり）」「登録済み」の物は、一度AIに問い合わせ済なので、対象外とする。





```json
{
  "ai_request": {
    "status": "refined",
    "updated_at": "2026-02-26T14:00:00Z",
    "is_edited": false,
    "is_fixed": false,
    "last_refinement_id": 1234,
    "last_error": null
  }
}

```

#####  `ai_request` の項目定義

| 項目名 | 型 | 説明 |
| --- | --- | --- |
| **`status`** | `string` | **AI連携の現在のステータス。** <br>`unprocessed` (未), `processing` (処理中), `pending_requeue` (再要求), `refined` (受領済), `completed` (完了) のいずれか。 |
| **`updated_at`** | `string` | **ステータスまたは内容の最終更新日時。** <br>ISO8601形式（`2026-02-26T14:00:00Z`）。 |
| **`is_edited`** | `boolean` | **ユーザーによる編集の有無。** <br>AIが生成した `refined_content` に対して、ユーザーが一度でも手動で修正を加えた場合に `true` に設定。 |
| **`is_fixed`** | `boolean` | **確定フラグ。** <br>ユーザーが内容を確認し、「これでOK」として保存・確定させた場合に `true`。これが `true` の間は、バッチ処理の対象から除外される。 |
| **`last_refinement_id`** | `number` | **AIリクエストの履歴ID。** <br>どのバージョンのAIモデルやプロンプトで生成されたかを追跡するための識別子。 |
| **`last_error`** | `string` | **エラーログ。** <br>直近のリクエストで失敗した場合のエラー内容を保持。成功時は `null`。 |


---

###### ステータス遷移とフラグの変化（運用例）

プロセスの流れに沿って、フラグがどう動くかを可視化すると以下のようになります。

1. **初期状態 (`unprocessed`)**
* `is_edited: false`, `is_fixed: false`

2. **AI処理中 (`processing`)**
* バッチがこの行をロック。UIでは「生成中...」と表示。

3. **AI回答受領 (`refined`)**
* `refined_content` にテキストが入り、ユーザーの画面に表示される。

4. **ユーザーが修正 (`is_edited: true`)**
* ユーザーがテキストエリアを書き換えた瞬間に `is_edited` を `true` に変更。
* ※この時点ではまだ `is_fixed` は `false`（下書き状態）。

5. **確定・保存 (`completed`)**
* `is_fixed: true` に更新。これ以降、この投稿はAI連携のサイクルから外れる。


###### 💡 運用のポイント

* **`is_edited` の活用**:
「AIが書いたものをそのまま出した投稿」と「人間がチェック・修正した投稿」を統計的に分析する際に役立ちます。
* **`is_fixed` の役割**:
`status` が `completed` であっても、ユーザーが後から「やっぱりもう一度AIに作り直させたい」とボタンを押した場合、`is_fixed` を `false` に戻し、`status` を `pending_requeue` にすることで、再度バッチの対象に復帰させることができます。



#### B. 個別ポスト精査テーブル (`zstu_post_refinements`)

1つの投稿に対するAIの整形・精査結果を管理します。

| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` |Integer | プライマリキーメール用のトークンは別に管理します |
| `post_id` | Integer | `zstu_posts.id` (FK) |
| `user_id` | UUID | ユーザーID |
| `status` | String | ご提示の `unprocessed` 〜 `completed` |
| `request_title` | Text | 要求時のコンテンツ |
| `request_content` | Text | 要求時のコンテンツ |
| `request_tags` | jsonb | 要求時のコンテンツ |
| `ai_refined_title` | Text | AIからの返答内容 |
| `ai_refined_content` | Text | AIからの返答内容 |
| `ai_refined_tags` | jsonb | AIからの返答内容 |
| `ai_changes` | jsonb | AIからの変更点の指摘 |
| `is_fixed` | boolean | AIからの返答から調整して、登録したかどうか |
| `fixed_title` | Text | 最終的に登録された内容 |
| `fixed_content` | Text | 最終的に登録された内容 |
| `fixed_tags` | jsonb | 最終的に登録された内容 |
| `trace_id` | UUID | 一括処理時のバッチ識別子 |
| `created_at` | Timestamp | 実行日時 |
| `updated_at` | Timestamp | 更新日時 |


- `ai_request` -> 不要、一括処理時の識別からたどれるので
- `ai_response` -> 不要、一括処理時の識別からたどれるので



```
CREATE TABLE public.zstu_post_refinements (
  id serial NOT NULL,
  post_id integer NOT NULL,
  user_id uuid NOT NULL,
  status character varying NOT NULL DEFAULT 'unprocessed',
  
  -- 1. 要求時（Input）
  request_title text,
  request_content text,
  request_tags jsonb DEFAULT '[]'::jsonb,
  
  -- 2. AIからの返答（AI Output）
  ai_refined_title text,
  ai_refined_content text,
  ai_refined_tags jsonb DEFAULT '[]'::jsonb,
  ai_changes jsonb DEFAULT '[]'::jsonb, -- 変更点の指摘など
  
  -- 3. ユーザーによる調整・確定
  is_fixed boolean NOT NULL DEFAULT false, -- 登録済みフラグ
  fixed_title text,
  fixed_content text,
  fixed_tags jsonb DEFAULT '[]'::jsonb,
  
  trace_id uuid, -- 一括処理時のログテーブル等との紐付け用
  created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT zstu_post_refinements_pkey PRIMARY KEY (id),
  CONSTRAINT fk_zstu_post_refinements_post_id FOREIGN KEY (post_id) 
    REFERENCES public.zstu_posts (id) ON DELETE CASCADE
) TABLESPACE pg_default;

-- インデックス：一つのポストに複数溜まるため、post_idでの検索を高速化
CREATE INDEX idx_refinements_post_id ON public.zstu_post_refinements (post_id);
CREATE INDEX idx_refinements_status ON public.zstu_post_refinements (status);
CREATE INDEX idx_refinements_user_id ON public.zstu_post_refinements (user_id);
```



---

## 🚀 AI週間評価API 設計案

このAPIは、1週間分のパブリックなポストと過去2週間のサマリーを読み込み、ユーザーの思考のクセや成長を言語化します。

### 1. Input (引数)

評価の「基準日」を指定することで、過去の任意の週を再評価できるようにします。

| 引数 | 初期値 | 説明 |
| --- | --- | --- |
| **`user_id`** | (必須) | ユーザー識別子。 |
| **`target_date`** | 本日 | 評価対象週の基準日（この日を含む週を評価）。 |
| **`include_past_weeks`** | 2 | 過去何週間分の評価結果をコンテキストに含めるか。 |
| **`options.force_refresh`** | `false` | `true`の場合、既に評価済みでも再計算する。 |
| **`options.focus_theme`** | `none` | 特定のタグやテーマに絞って重点的に評価したい場合に指定。 |
| **`loglevel`** / **`disp`** | `normal` / `none` | 整形APIと同様のデバッグ・保存オプション。 |

---

### 2. Process (ロジックフロー)

週次評価では、**「データの凝縮」**がポイントになります。

1. **対象データの抽出**:
* 指定週の `ZstuPost` のうち、`is_public=true` かつ `status=refined` のものを全取得。

2. **過去コンテキストの取得**:
* 前週・前々週の「週次評価テーブル（後述）」から、AIが作成したサマリーを取得。

3. **タグ統計の算出**:
* 今週多く使われたタグ、出現頻度の変化を数値化。

4. **プロンプト組み立て**:
* 「今週のポスト群」「過去のサマリー」「統計データ」をGeminiに渡し、「変化」と「アドバイス」を求める。

5. **Google AI Studio へのリクエスト**:
* 思考の深まり、習慣の継続、新しい視点の獲得などを分析。

6. **結果の登録**:
* 「週次評価テーブル」に新規保存。

7. **メール通知 (Resend)**:
* 評価結果のダイジェストをユーザーに送信し、アプリへの再訪を促す。



---

### 3. Output (レスポンス)

整形APIと同様、バックグラウンド実行を想定して `trace_id` を即座に返します。

```json
{
  "trace_id": "uuid-eval-12345",
  "status": "accepted",
  "target_week": "2026-W08",
  "message": "週次評価プロセスを開始しました。完了後メールでお知らせします。"
}

```

---

### 週次評価結果を保存するテーブル（案）

AIが生成した評価は、後から振り返れるように専用のテーブル（例：`WeeklyEvaluations`）に保存することを推奨します。

| カラム名 | 説明 |
| --- | --- |
| **`id`** | id |
| **`user_id`** | ユーザーID |
| **`year_week`** | 2026-08 形式の週番号 |
| **`summary`** | AIによる全体サマリー（短文） |
| **`detail_report`** | AIによる詳細分析（Markdown形式） |
| **`top_tags`** | 今週の主要タグ（JSON） |
| **`growth_point`** | AIが見つけた「先週からの変化・成長」 |
| **`post_ids`** | 評価対象となったポストのIDリスト（JSON） |


---


## 関連するテーブル
### `zstu_tag_descriptions`

- prompt作成時に、ローカルのTag情報として作成する。

| カラム名 | 型 | 制約 | 説明 |
| --- | --- | --- | --- |
| `id` | UUID | PK | タグの一意識別子 |
| `user_id` | UUID / Int | FK | どのユーザーのタグかを識別 |
| `tag_name` | String(50) | Not Null | AIへの指示に使う短い識別子 (例: `zstv2`) |
| `name` | String(100) | Not Null | 画面表示用の正式名称 (例: `zerosecthinkv2`) |
| `aliases` | JSONB |  | 同義語リスト（重複回避用）(例：["パイソン", "Py", "python3"]) |
| `description` | Text | - | タグの意味やAIへの補足説明  |
| **`display_order`** | Int | Default: 0 | 画面上での表示順（昇順・降順でソート用） |
| **`is_active`** | Boolean | Default: true | 有効/無効フラグ。削除せずに非表示にしたい場合に使用 |
| **`is_send_ai`** | Boolean | Default: true | **AIへの送信対象にするか。** (※) |
| **`created_at`** | Timestamp | Not Null | レコード作成日時 |
| **`updated_at`** | Timestamp | Not Null | レコード更新日時 |

---

#### 1. `is_active` (論理削除・有効化)

* **必要性：** 非常に高いです。
* **理由：** 過去のメモに関連付けられているタグを物理削除してしまうと、過去ログの整合性が崩れる可能性があります。「今は使わないけれどデータとして残しておきたい」場合に、`false` にすることで管理画面や選択肢から除外できます。

#### 2. `is_send_ai` (AI送信フラグ) ※「is_sendai」の解釈

* **必要性：** 高いです。
* **理由：** おそらく `is_send_ai`（AIに送るかどうか）の意図かと推察します。タグが増えてくると、全てのタグをプロンプト（`{tags}`）に含めるとトークン数（コスト）を消費しすぎたり、AIが混乱したりします。「このタグはAIに文脈を理解させるために必須」というものにチェックを入れて制御できると便利です。

#### 3. `display_order` (表示順)

* **必要性：** 高いです。
* **理由：** 作成順（`created_at`）だけでなく、よく使うタグを上に固定（ピン留め）したり、ユーザーが任意に並び替えたりできると、タグ管理画面の使い勝手が劇的に向上します。

#### 4. `created_at` / `updated_at` (タイムスタンプ)

* **必要性：** 必須レベルです。
* **理由：** データのデバッグ時や、「最近作ったタグから表示する」といった並び替え、またAIの処理履歴との突合に必ず必要になります。


### `ai_Batches`

「1週間分のメモを修正する」という、ユーザーの1回の操作（リクエスト）を管理する親テーブルです。

| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` | Int | バッチ全体の一意識別子 |
| `user_id` | UUID | 実行ユーザー |
| `total_chunks` | Int | 全体の分割数（例：4チャンク） |
| `completed_chunks` | Int | 完了した数（進捗管理用） |
| `total_memos` | Int | 処理対象の総メモ件数（例：70件） |
| `status` | String | `processing`, `completed`, `partial_success`, `failed` |
| `created_at` | Timestamp | 開始日時 |

SQLiteを想定なので、UUID、JSONB -> TEXT型、Boolean -> Integer(0,1)

### `ai_Execution_Logs`

- バッチが対象数多いときに分割した履歴を登録する
- 70件だと1(1-20),2(21-40),3(41-60),4(61-70)と４回に分けて登録するので４行になる。


| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` | Int | ログの一意識別子 |
| `user_id` | UUID | 実行したユーザー |
|`batch_id` |int|`ai_Batches` へのリレーション|
|`chunk_index` |int|「4チャンク中、何番目のリクエストか」を記録します。|
| `prompt_template` | Text | 使用した `typo_content` のスナップショット |
| `raw_input_json` | JSONB | AIに送った実際のJSONデータ |
| `raw_output_text` | Text | AIから返ってきた生のレスポンス |
| `model_info` | String | 使用モデル (Gemini 1.5 Flash等) |
| **`api_version`** | String | `v1` や `v1beta` など。API側の仕様変更の追跡用 |
| **`duration_ms`** | Int | 実行にかかった時間（ミリ秒）。パフォーマンス監視用 |
| `status` | String | `success`, `failed`, `retry` など |
| `used_tags_snapshot` | JSONB | 当時送ったタグ定義（名前・説明）の記録 |
| `error_payload` | JSONB |  APIがエラーを返した際、その詳細をそのまま保存します |
| `token_usage` | JSONB | Geminiから返ってくる `prompt_token_count` と `candidates_token_count` を保存。 |
| `created_at` | Timestamp | 実行日時 |


---

#### 1. `api_version` の重要性

Google AI Studio (Gemini API) は、`v1beta` でのみ先行実装される機能（構造化出力の厳密な定義など）が多いです。
「以前は動いていたのに急にJSONパースに失敗するようになった」という時、**「APIのバージョンが原因か、モデルの更新が原因か」**を切り分ける重要な手がかりになります。

#### 2. `duration_ms` (実行時間) の重要性

提示いただいたコードでは `CHUNK_SIZE` ごとに分割送信し、さらに `WAIT_TIME_MS` (10秒) の待機を入れています。
* ログを見ることで「実際にAIの推論に何秒かかったのか」と「待機時間を含めた全体のUXとしてどうなのか」を数値化できます。
* あまりに時間がかかるチャンクがある場合、プロンプトが長すぎる、あるいはタグの `description` が多すぎるといったボトルネックを発見できます。



### `zstu_post_refinements` 

1つの投稿に対するAIの整形・精査結果を管理します。

| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` |Integer | プライマリキーメール用のトークンは別に管理します |
| `post_id` | Integer | `zstu_posts.id` (FK) |
| `user_id` | UUID | ユーザーID |
| `status` | String | ご提示の `unprocessed` 〜 `completed` |
| `request_title` | Text | 要求時のコンテンツ |
| `request_content` | Text | 要求時のコンテンツ |
| `request_tags` | jsonb | 要求時のコンテンツ |
| `ai_refined_title` | Text | AIからの返答内容 |
| `ai_refined_content` | Text | AIからの返答内容 |
| `ai_refined_tags` | jsonb | AIからの返答内容 |
| `ai_changes` | jsonb | AIからの変更点の指摘 |
| `is_fixed` | boolean | AIからの返答から調整して、登録したかどうか |
| `fixed_title` | Text | 最終的に登録された内容 |
| `fixed_content` | Text | 最終的に登録された内容 |
| `fixed_tags` | jsonb | 最終的に登録された内容 |
| `trace_id` | UUID | 一括処理時のバッチ識別子 |
| `created_at` | Timestamp | 実行日時 |
| `updated_at` | Timestamp | 更新日時 |


---

is_edited,applied,状態の意味
false,true,AIの提案をそのまま採用した。
true,true,AIの提案を人間が手直しして採用した。
false,false,AIが提案したが、採用を見送った（破棄）。
true,false,（レアケース）手直しはしたが、結局採用しなかった。


### `prompt_templates` 

- 複数のシステムから利用される情報（VercelNextJSやFastAPI）なので、テーブルに情報として持つ


プロンプトの「枠組み（名前や用途）」を定義します。

| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` | `integer` | 主キー (PK) |
| `slug` | `text` | プロンプト識別子（例: `typo_propmt`）※一意制約 |
| `name` | `text` | 管理用の表示名（例: カスタマーサポート返信） |
| `description` | `text` | このプロンプトの用途説明 |
| `created_at` | `timestamptz` | 作成日時 |


### `prompt_versions`


プロンプトの「中身（バージョン）」を保持します。

| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` | `integer` | 主キー (PK) |
| `template_id` | `integer` | `prompt_templates.id` への外部キー |
| `version` | `integer` | バージョン番号 (1, 2, 3...) |
| `content` | `text` | **プロンプト本文**（変数は `{{memo}}` `{{tags}}` 等で保持） |
| `comment` | `text` | コメント |
| `model_config` | `jsonb` | モデル設定（`model: "gpt-4o"`, `temperature: 0.7` など） |
| `is_active` | `boolean` | **現在使用中のバージョンか**（Trueは1つのみ） |
| `created_by` | `uuid` | 作成者のユーザーID（Supabase Authと連携） |
| `created_at` | `timestamptz` | 作成日時 |

---
API_Logs（共通アクセスログ）Task_Progress_Logs（目的別・処理進捗ログ）への登録は別途検討

## todo 
- [x] Api経由での呼び出しのテスト
  - [x] EnhancedCSVLoggerでのログの登録、実践的なもの（※１）
    - task_nameなど入力できるようにして作ってみる、インターバルも含む
- [ ] 「※１」で登録した情報が見えること確認
- [ ] タイマー処理で、定期的にPosts取得する動きの実装
- [ ] タイマー処理を手動で、Postsできる動きの追加
- [ ] スタート画面、ダッシュボードの整理(/Dashboard) メニューの追加　ログ一覧画面、タイマーを手動で実行する画面、ログを登録する画面
- [ ] メール: Resend の統合（精査結果の送信）
- [ ] 低：UI調整: htmx を使ったダッシュボードの動的化

- [x] Promtをテーブルからの入手
- [x] 過去分デプロイ済み分で登録
- [x] タイポの実装
  - [x] 処理のモックアップ作成
  - [x] 引数に応じたフロー作成
  - [x] 開始のStatuに変更
  - [x] ログ記載の件
  - [x] 結果登録の件
  - [x] メール送信
- [ ] サマリの実装
  - [ ] 専用テーブルの見直し、Stateいるんでないかな・・・重複回避必要かと
  - [ ] UI作成
  - [ ] 引数選定
  - [ ] 処理のモックアップ作成
  - [ ] 引数に応じたフロー作成
  - [ ] 開始のStatuに変更
  - [ ] ログ記載の件
  - [ ] 結果登録の件
  - [ ] メール送信
- [ ] 他システムサマリ処理の検討
  - [ ] 昨日分拾って、登録するかどうかを翌日の１時に作成
  - [ ] 翌日URLみて、登録するかを選ぶ
  - [ ] どちらにしてもメール機能必要
- [x] メール送信機能整理　Resend候補かと・・・
  - [ ] お名前.comの状況確認
- [ ] stripe 対応
- [ ] twtter(x) 対応

## History 
- 2026/03/09
  - Api Path 調整
  - Api Called User Typo Setting Get
- 2026/03/01
  - GeminiAI調整
  - resend テスト
- 2026/02/25
  - ホスト [CloudRun]([https://](https://bezstv1-420574500377.asia-northeast1.run.app/dashboard))
  - UI回り、APITest用のUi画面作成、Htmxの利用など開始
- 2026/02/23
  - デプロイ完了



---


