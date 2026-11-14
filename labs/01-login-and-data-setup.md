# Lab 01 — サインインと ERP・MES・IoT・非構造化データの準備

> **所要時間**: 約 20 分  
> **ゴール**: 自分の Fabric ワークスペースへ CLI で接続し、Lakehouse `mfg_ontology_lh`（および任意の Eventhouse `mfg_telemetry_eh`）を作成して、ERP・MES・IoT の 15 個の管理 Delta テーブルと 8 本の非構造化ドキュメントを OneLake 上に準備・検証する。

---

## 1-1. このラボで作るデータ基盤の全体像

オントロジーを正しく機能させ、後の Lab 05 でグラフエンジン（Materialized Graph）の比較検証まで行うには、元となる Lakehouse の Delta テーブルに**重要な技術的前提**があります。

- **すべての主キー列が `String` または `BigInt` 型であること**（Fabric Ontology V2 の Entity Key 制約）
- **列名にスペースや特殊文字を含めず、Delta Column Mapping を無効のままにすること**（Column Mapping が有効なテーブルは Graph 投影の対象外になります）
- **非構造化ドキュメント（Markdown 8本）も OneLake `Files/unstructured_docs/` とローカル双方から参照でき、構造化データの ID（`EQ-VBF-204`, `LOT-MAG-088`, `CUS-003` 等）とアンカーキーで紐づいていること**

---

## 1-2. Azure / Microsoft Fabric へサインインしてワークスペースを特定する

まずは登録済みの `student` アカウントでサインインし、自分のワークスペース ID を確定させます。

> 🗣️ **プロンプト**
> ```text
> 登録済みの参加者設定を使って Azure にデバイスコードでサインインし、私の Fabric ワークスペースを特定して Workspace ID を参加者設定ファイルに保存してください。
> ```

🤖 **Copilot の動き**

- `.github/student.local.md` からテナント ID とアカウントを読み取り、`az login --tenant <tenant-id> --use-device-code` を実行します。
- サインイン完了後、`GET https://api.fabric.microsoft.com/v1/workspaces` からワークスペース名に完全一致する 1 件を特定し、Workspace ID を `.github/student.local.md` に追記します。

✅ **期待する結果**

- ターミナルに表示された `https://microsoft.com/devicelogin` にコードを入力してサインインすると、自分のワークスペース名（例: `student01`）と Workspace ID（GUID）が確認・保存されます。

---

## 1-3. Lakehouse `mfg_ontology_lh` の作成とデータの OneLake アップロード

続いて、ERP・MES・IoT データと非構造化ドキュメントを格納する Lakehouse **`mfg_ontology_lh`** を作成し、ローカルの `data/` 配下のファイルを OneLake の `Files/` 領域へアップロードします。

> 🗣️ **プロンプト**
> ```text
> 私のワークスペースに Lakehouse「mfg_ontology_lh」を作成してください（既にある場合は再利用してください）。そのあと、ローカルの data/erp、data/mes、data/iot、data/unstructured_docs の全ファイルを mfg_ontology_lh の Files/raw/ 配下にフォルダ構成を保ってアップロードしてください。
> ```

🤖 **Copilot の動き**

- `fabric-cli` / `spark-cli` の手順に従い、`POST /v1/workspaces/{ws}/items`（`type: Lakehouse`, `displayName: mfg_ontology_lh`）を実行し、Lakehouse ID を `.github/student.local.md` に記録します。
- OneLake DFS API（`https://onelake.dfs.fabric.microsoft.com/{ws}/{lh}/Files/raw/...`、`storage.azure.com` トークン使用）で ERP 7ファイル、MES 5ファイル、IoT 4ファイル、非構造化ドキュメント 9ファイル（8 Markdown + `doc_catalog.csv`）をアップロードします。

✅ **期待する結果**

- `mfg_ontology_lh` が作成され、`Files/raw/erp/`、`Files/raw/mes/`、`Files/raw/iot/`、`Files/raw/unstructured_docs/` のすべてがアップロード完了となります。

---

## 1-4. 15 個の管理 Delta テーブルへの変換・保存（Ontology & Graph 対応スキーマ）

アップロードした CSV から、型を明示した **15 個の Managed Delta テーブル** を作成します。

> 🗣️ **プロンプト**
> ```text
> mfg_ontology_lh の Files/raw/ にアップロードした ERP（7ファイル）・MES（5ファイル）・IoT（3 CSVファイル）を読み込み、同名の15個の管理 Delta テーブル（erp_customers, erp_suppliers, erp_materials, erp_products, erp_bom, erp_sales_orders, erp_purchase_orders, mes_production_lines, mes_equipment, mes_material_lots, mes_work_orders, mes_quality_inspections, iot_sensors, iot_telemetry, iot_equipment_alerts）として overwrite 保存してください。ID列はすべて string、整数コードや金額・数量は bigint（long）、小数は double にキャストし、Delta column mapping は有効化しないでください。まずは変換・保存の完了まで実行してください。
> ```

🤖 **Copilot の動き**

- `spark-cli` を使い、PySpark セッション（Livy API または Spark Job）で 15 個の CSV を厳密な型定義（`StringType`, `LongType`, `DoubleType`）で読み込み、`saveAsTable` で Managed Delta テーブルとして保存します。

✅ **期待する結果**

- Spark ジョブが成功し、`mfg_ontology_lh` の `Tables` 配下に 15 個の Delta テーブルが作成されます。

---

## 1-5. 件数と固定レコードによるデータ品質検証

データ取り込み後は、`LIMIT 5` のような先頭行の目視ではなく、**`data/expected_oracle.json` の正解値に対する全件数照合とキー指定照合** で確実に検証します。

> 🗣️ **プロンプト**
> ```text
> mfg_ontology_lh に作成した15個の Delta テーブルの件数が data/expected_oracle.json の row_counts と完全一致するか確認してください。あわせて次の固定レコードをキー指定で照会して値を表示してください：
> 1) erp_sales_orders の order_id = 'SO-2026-004' と 'SO-2026-015'（金額と order_status_code）
> 2) mes_equipment の equipment_id = 'EQ-VBF-204'（days_since_calibration と operating_state_code）
> 3) mes_material_lots の material_lot_id = 'LOT-MAG-088'（moisture_ppm と supplier_id）
> 4) iot_equipment_alerts の alert_id = 'ALT-2026-901' と 'ALT-2026-902'（alert_code, peak_value, duration_minutes）
> ```

🤖 **Copilot の動き**

- SQL Analytics Endpoint（`sqldw-cli` / `sqlcmd`）または PySpark SQL で 15 テーブルの `COUNT(*)` と指定キーレコードを取得し、`data/expected_oracle.json` と照合します。

✅ **期待する結果**

以下の件数・固定値がすべて一致して表示されます。

| テーブル名 | 期待件数 | 主な確認レコードと期待値 |
| :--- | :---: | :--- |
| `erp_customers` / `erp_suppliers` / `erp_materials` / `erp_products` / `erp_bom` | 10 / 8 / 12 / 6 / 18 | — |
| `erp_sales_orders` / `erp_purchase_orders` | 24 / 16 | `SO-2026-004`: `48,000,000` 円 (`status=3`)、`SO-2026-015`: `19,200,000` 円 (`status=2`) |
| `mes_production_lines` / `mes_equipment` / `mes_material_lots` | 6 / 15 / 18 | `EQ-VBF-204`: `days_since_calibration=109`, `state=3` / `LOT-MAG-088`: `182 ppm` (`SUP-003`) |
| `mes_work_orders` / `mes_quality_inspections` | 30 / 24 | `WO-2026-1007`, `WO-2026-1012`, `WO-2026-1019` が `wo_status_code=30` |
| `iot_sensors` / `iot_telemetry` / `iot_equipment_alerts` | 15 / 360 / 10 | `ALT-2026-901`: `9.5` (28分)、`ALT-2026-902`: `859.4` (24分) |

---

## 1-6. （任意・推奨）Eventhouse `mfg_telemetry_eh` への時系列データ投入

Lab 05 で「高頻度テレメトリは Materialized Graph ではなく Eventhouse KQL で直接集計する方が優れている理由」を実機でも体感したい場合は、Eventhouse にも `iot_telemetry`（360件）をロードしておきます（時間が限られる場合はスキップして Lakehouse SQL との比較で代用可能です）。

> 🗣️ **プロンプト**
> ```text
> （任意ステップ）私のワークスペースに Eventhouse「mfg_telemetry_eh」を作成し、デフォルト KQL データベースに iot_telemetry テーブルを作ってローカルの data/iot/iot_telemetry.csv（360件）を取り込み、件数が 360 件であることを KQL で確認してください。
> ```

---

## 🧹 トラブルシュート（プロンプトで対処）

- **SQL Analytics Endpoint に作成したばかりのテーブルがまだ見えない場合**:
  > `mfg_ontology_lh の SQL Analytics Endpoint のメタデータ同期を実行して、15テーブルすべてが見えるようになるまで待ってから再確認してください。`
- **トークンの有効期限切れエラー（HTTP 401）が出た場合**:
  > `Azure CLI のトークンを再取得して、直前の処理を再実行してください。`

---

## ✅ チェックポイント

- [ ] `.github/student.local.md` に Workspace ID と `mfg_ontology_lh` の Lakehouse ID が記録されている
- [ ] 15 個の管理 Delta テーブルの件数が `expected_oracle.json` と完全一致している
- [ ] `Files/raw/unstructured_docs/` に 8 本の Markdown ドキュメントが格納されている

データの準備ができたら、いきなりオントロジーを作り始めるのではなく、まずは **[Lab 02 — どんなオントロジーを作るべきか AI に相談・設計する](./02-ontology-design-consultation.md)** へ進みましょう！
