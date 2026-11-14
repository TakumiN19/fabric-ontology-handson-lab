# ハンズオンの参加者設定と Copilot 共通指示

## 1. student 番号の登録と自動反映

ユーザーが自分の student 番号を伝えて登録・記憶を依頼したら、その番号から次の参加者設定を自動生成し、
教材ルートの `.github/student.local.md` に Markdown で保存する。
番号は数字だけであることを確認し、先頭の 0 を含めて入力された表記を保持する。
番号が不明または不正なら保存せず、正しい番号の入力を求める。

- student 番号: ユーザーが伝えた番号
- ワークスペース名: `student` の直後にその番号を連結した文字列
- アカウント: ワークスペース名の直後に `@M365x43914722.onmicrosoft.com` を連結した文字列
- テナント ID: `e6c1292e-65b7-4e2d-9e1b-13f24e7753fd`

（講師から別のテナント ID・ドメイン・Foundry エンドポイントが案内されている場合は、ユーザーが明示した値のみを `.github/student.local.md` に併記する。未確認の値を推測しない。）

ユーザーにアカウント名やワークスペース名を別途入力・置換させない。
既存の番号と同じなら確認済みの Workspace ID やアイテム ID を保持し、番号を変更した場合は以前の Workspace ID・アイテム ID を削除する。
保存後にファイルを読み直し、保存済みの番号・アカウント・ワークスペース名・テナント ID を表示して確認できるようにする。
登録の依頼だけでは Azure / Fabric へのサインインやワークスペースの作成は実行しない。
他の指示ファイルは変更しない。

## 2. ワークスペース・アイテム解決ルール

この教材で Azure / Fabric / Microsoft Foundry の操作を行う前に、教材ルートの `.github/student.local.md` を読み、参加者設定を確認する。
「自分のアカウント」「自分のワークスペース」は、このファイルに記録されたアカウントとワークスペースを指す。
Lab ごとに student 番号を聞き直さない。新しい会話でも、まずこのファイルを読み込む。

Lab 01 以降は、ユーザーが作業内容だけを指示した場合も、登録済みのアカウント・テナント・ワークスペースを既定の対象にする。
サインイン、アイテム作成・一覧・照会・更新、Ontology 定義の反映、MCP 呼び出し、Foundry 連携を含め、
ユーザー名、ワークスペース名、Workspace ID、Lakehouse ID、Eventhouse ID、Ontology ID、Data Agent ID をユーザーに入力・置換させない。
初めて接続するときは登録済みの名前と完全一致するワークスペースを API（`GET /v1/workspaces` + JMESPath 厳密一致フィルタ）で一意に特定し、
確認できた名前と Workspace ID を `.github/student.local.md` に保存する。
各アイテムはそのワークスペース内で教材の既定名（`mfg_ontology_lh`, `mfg_telemetry_eh`, `mfg_enterprise_ontology`, `mfg_ops_data_agent`）と種類から API で特定する。
取得できない・同名候補が複数ある場合は操作を止め、理由を伝える。未確認の ID や接続先を推測しない。

設定ファイルがない、番号が未設定、または設定が矛盾している場合は、Azure / Fabric の操作を止め、
Lab 00 の 0-7 に従って登録または修正するよう案内する。
パスワード、MFA コード、アクセストークンは `.github/student.local.md` やファイルに保存しない。

## 3. Skills for Fabric（`ontology-cli` ほか）の厳守ルール

1. **テレメトリヘッダーの付与**: `api.fabric.microsoft.com` へのすべての呼び出し（LRO ポーリング・MCP `tools/list`・`tools/call` を含む）に、使用スキルに応じた `x-ms-fabric-skill` ヘッダー（例: `x-ms-fabric-skill: ontology-cli`）を必ず付与する。
2. **Ontology V2（New Experience / TMDL）と V1（Legacy JSON）の境界の明示**:
   - 自然言語での Ontology 照会（`ontology-cli` の `consumption` モード）は **V2（New Experience）の Ontology MCP エンドポイント**（`POST /v1/mcp/dataPlane/workspaces/{ws}/items/{ont}/ontologyEndpoint`）のみを対象とする。必ず最初に `tools/list` を呼び、`ask_ontology` が存在することを確認してから `tools/call` を実行する。
   - 現行 `ontology-cli` の `authoring` モードは Legacy V1 JSON 定義用であり、V2 Ontology への変換や V1 への自然言語照会はサポートしない。V2 Ontology の作成・拡張では、教材の `ontology/v2_tmdl/` テンプレート（`POST /v1/workspaces/{ws}/ontologies` / `updateDefinition`）およびポータル内の **Ontology Agent（Plan → Act モード）** の手順に従い、API で未サポートの操作やプレビュー制約があれば隠さず明示して報告する。
   - Ontology に対する質問で MCP を迂回して勝手に生テーブルへ SQL/KQL を手書き実行しない（ただし Lab 01 のデータ検証および Lab 05 の「グラフエンジン vs ソースネイティブ比較」で明示的に比較検証を求められた場合を除く）。
3. **MCP ペイロードと課金防止**:
   - Ontology MCP の呼び出しでは、クォート崩れを防ぐため必ず UTF-8（BOM なし）の JSON ファイルに出力して `--body @payload.json` で渡し、応答も `1>resp.json` に保存してから読み取る（1 回の質問で複数回 `tools/call` を再送しない）。タイムアウトは 120 秒以上を見込む。
4. **API 制限・プレビュー制約の誠実な報告**:
   - 未提供の API フィールド、スキーマ enum 未対応（例: Data Agent の REST 定義スキーマにおける `ontology` / `azure_ai_search` ソース種別の扱い、TMDL 単体デプロイ時の Graph Eligibility 注釈など）に遭遇した場合は、架空の成功を装ったり黙って別リソースで代替したりせず、制限事項と公式のポータル／MCP 手順を明確に報告する。
   - Foundry や Azure AI Search / Azure OpenAI リソースを扱う際は、講師・環境で用意された既存リソースを優先して再利用し、指示なく新規の課金 Azure リソースを作成しない。

## 4. Lab 別の参照・検証ルール

- **Lab 01（データ取り込み・変換）**: 実行前に `labs/01-login-and-data-setup.md` を読み、ERP（7テーブル）・MES（5テーブル）・IoT（3テーブル）の件数・主キー・Delta column mapping 回避ルール（スペースや特殊文字を含めない列名）を確認する。取り込み・保存と、固定レコード照合・品質確認は分けて実施する。`LIMIT` / `TOP` の先頭行を正しさの根拠にせず、`WHERE` キー指定で期待値と照合する。
- **Lab 02（オントロジー設計相談）**: いきなり Fabric 上にアイテムを作成せず、まず `data/` 配下のスキーマ・サンプル行と `data/unstructured_docs/GLOSSARY_enterprise_domain_terms.md` を分析し、Competency Questions・Namespace（サブオントロジー）分割・Synonym・Metadata・Rules・構造化/非構造化の境界案を提示してユーザーと合意する（Plan ファースト）。
- **Lab 04（セマンティック拡張と精度比較）**: `labs/04-namespaces-synonyms-metadata-rules.md` と `ontology/evaluation_questions.json` を参照し、設定前（Lab 03 時点）と設定後（Namespace / Synonym / Metadata / Rules 反映後）でエージェントの解釈・回答根拠がどう変化したかを対比表で示す。
- **Lab 05（グラフエンジンの要否判断）**: `labs/05-graph-engine-scenarios.md` を参照し、多段経路・波及影響（Graph / GQL が有効なケース）と、全体集計・高頻度リアルタイム時系列（SQL / DAX / KQL のままにすべきケース）の両方を比較し、選択的 Materialization（必要なエンティティのみ投影）の根拠を説明する。
