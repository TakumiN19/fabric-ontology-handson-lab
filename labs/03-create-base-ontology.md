# Lab 03 — ベースオントロジーの構築と「エンリッチ前（Before）」の弱点確認

> **所要時間**: 約 25 分  
> **ゴール**: 新エクスペリエンス（V2 / TMDL）の Ontology アイテム `mfg_enterprise_ontology` を作成して ERP・MES・IoT のテーブルとリレーションシップをバインドし、**Synonym・Namespace 分離・Metadata・Business Rules を設定する前の状態（Before）** で `ontology-cli`（MCP）から質問して、素のスキーマだけではどこで回答精度が落ちるかを実測する。

---

## 3-1. 【重要】Skills for Fabric（`ontology-cli`）における V1 と V2 の仕様境界

構築に入る前に、現行の Microsoft Fabric Ontology（Preview）および `skills-for-fabric`（`v0.3.22`）の重要な仕様を押さえておきましょう。

1. **Fabric Ontology には旧エクスペリエンス（V1 / JSON 定義）と新エクスペリエンス（V2 / TMDL 定義）がある**:
   - 旧 V1 は 2027年1月31日で廃止予定であり、自然言語エージェント照会（`ask_ontology`）に**対応していません**。
   - 新 V2（現在のポータル既定）は TMDL（Tabular Model Definition Language）ベースであり、Namespace・Business Rules・Ontology Agent MCP（`ask_ontology`, `list_ontology_entities`, `list_ontology_rules`）のすべてに対応しています。
2. **`ontology-cli` スキルの役割分担**:
   - **Consumption（照会・検証）モード**: V2 Ontology の MCP エンドポイントに対して CLI から自然言語質問・エンティティ確認・ルール確認・コード生成を実行できます（本ラボおよび Lab 04・05 でフル活用します）。
   - **Authoring（作成・編集）の注意点**: `ontology-cli` の JSON オーサリングテンプレートは V1 用であり、また生の TMDL だけを REST API で直接書き込むとポータル側が付与する Graph 適格注釈（`ONT_` アノテーション）が生成されない制約があります。そのため、**V2 Ontology の初期バインドは Fabric ポータルの Ontology Agent（Plan → Act）またはキャンバス UI で構成し、CLI（`ontology-cli`）で定義の検証と MCP クエリ評価を行う**のが最も確実で公式仕様に沿った手順です。

---

## 3-2. V2 Ontology アイテム `mfg_enterprise_ontology` を作成する

まずは Fabric ポータル（またはアイテム作成 API）で空の V2 Ontology アイテムを作成し、Copilot CLI にその ID を認識させます。

### ポータル手順（約 1 分）

1. ブラウザで自分の Fabric ワークスペース（例: `student01`）を開きます。
2. 左上の **`+ New item`（新しいアイテム）** をクリックし、検索ボックスに `Ontology` と入力して **`Ontology (preview)`** を選択します。
3. Name に **`mfg_enterprise_ontology`** と入力して **`Create`** をクリックします（新エクスペリエンスのキャンバスが開きます）。

作成したら、Copilot CLI でアイテムの認識と **V2 MCP サポートゲート（`tools/list`）** を確認します。

> 🗣️ **プロンプト**
> ```text
> 私のワークスペースにある Ontology アイテム「mfg_enterprise_ontology」の ID を特定して参加者設定ファイルに保存し、ontology-cli の手順に従って Ontology MCP エンドポイントの tools/list を呼び出し、V2（ask_ontology 対応）であることを確認してください。
> ```

🤖 **Copilot の動き**

- `GET /v1/workspaces/{ws}/items?type=Ontology`（ヘッダー `x-ms-fabric-skill: ontology-cli` 付与）で `mfg_enterprise_ontology` の GUID を特定し、`.github/student.local.md` に記録します。
- `POST https://api.fabric.microsoft.com/v1/mcp/dataPlane/workspaces/{ws}/items/{ont}/ontologyEndpoint` へ `tools/list` を送信します。

✅ **期待する結果**

返却ツール一覧に以下の 4 つが含まれており、**`ask_ontology`** が存在すること（＝V2 新エクスペリエンスであること）が確認できます。

```json
["search_ontology", "ask_ontology", "list_ontology_rules", "list_ontology_entities"]
```

---

## 3-3. ベースオントロジー（テーブルバインド＋リレーションのみ）を構築する

Lab 04 での「設定前 vs 設定後」の違いを鮮明に体験するため、ここでは **あえて Namespace 未分離（Default のまま）・Synonym なし・Metadata なし・Business Rules なし** の素のベースモデルを作成します。

### Ontology Agent（Act モード）を使った高速セットアップ手順

Fabric ポータルで開いている `mfg_enterprise_ontology` の画面右上から **Ontology Agent** パネルを開き、モードを **`Act`** に切り替えて、次のプロンプトを貼り付けて送信します。

> 🗣️ **Ontology Agent（ポータル画面内）への入力プロンプト**
> ```text
> Lakehouse「mfg_ontology_lh」のテーブルを使って、以下の13個の Entity Type と主キー（Key）を作成してデータをバインドしてください。この時点ではすべて Default 名前空間のままとし、Synonym や追加メタデータ、Business Rules はまだ設定しないでください。
>
> 1. Customer (erp_customers, key: customer_id)
> 2. Supplier (erp_suppliers, key: supplier_id)
> 3. Material (erp_materials, key: material_id)
> 4. Product (erp_products, key: product_id)
> 5. SalesOrder (erp_sales_orders, key: order_id)
> 6. PurchaseOrder (erp_purchase_orders, key: po_id)
> 7. ProductionLine (mes_production_lines, key: line_id)
> 8. Equipment (mes_equipment, key: equipment_id)
> 9. MaterialLot (mes_material_lots, key: material_lot_id)
> 10. WorkOrder (mes_work_orders, key: order_id)
> 11. QualityInspection (mes_quality_inspections, key: inspection_id)
> 12. Sensor (iot_sensors, key: sensor_id)
> 13. EquipmentAlert (iot_equipment_alerts, key: alert_id)
>
> あわせて次の主要リレーションシップを作成してください：
> - SalesOrder (customer_id) -> Customer (customer_id) : placedByCustomer
> - SalesOrder (product_id) -> Product (product_id) : ordersProduct
> - WorkOrder (sales_order_id) -> SalesOrder (order_id) : fulfillsSalesOrder
> - WorkOrder (product_id) -> Product (product_id) : producesProduct
> - WorkOrder (line_id) -> ProductionLine (line_id) : scheduledOnLine
> - WorkOrder (equipment_id) -> Equipment (equipment_id) : processedByEquipment
> - WorkOrder (material_lot_id) -> MaterialLot (material_lot_id) : consumesMaterialLot
> - Equipment (line_id) -> ProductionLine (line_id) : locatedInLine
> - MaterialLot (material_id) -> Material (material_id) : lotOfMaterial
> - MaterialLot (supplier_id) -> Supplier (supplier_id) : suppliedByVendor
> - Material (backup_supplier_id) -> Supplier (supplier_id) : backupSupplier
> - QualityInspection (work_order_id) -> WorkOrder (order_id) : inspectedForWorkOrder
> - EquipmentAlert (equipment_id) -> Equipment (equipment_id) : triggeredOnEquipment
> - Sensor (equipment_id) -> Equipment (equipment_id) : monitoredBySensor
> ```

> 💡 **ワンポイント**:
> - Ontology Agent が変更プレビュー（Preview changes）を表示したら、各 Entity Type に **Key プロパティ（`customer_id` など）** が設定されていることを確認して **`Apply` / `Accept`** をクリックします。
> - もし Default 名前空間に同じ `Order` という名前を2つ作ろうとすると重複エラーになるため、Namespace をまだ使わないこの段階では `SalesOrder` / `WorkOrder` とせざるを得ない点にも注目してください！（次の Lab 04 で `erp#Order` と `mes#Order` に進化させます）。
> - 手動で追加・補正したい場合は、リボンの **`+ Entity type`** → **`Bind data`**（`mfg_ontology_lh` を選択）および **`+ Relationship`** から数分で構成できます。

---

## 3-4. CLI からベースオントロジーの登録状態を確認する

ポータルでベース構成を保存したら、GitHub Copilot CLI に戻って MCP 経由でスキーマを確認します。

> 🗣️ **プロンプト**
> ```text
> ontology-cli を使って mfg_enterprise_ontology の登録済みエンティティ一覧を確認し、各エンティティの主キーとバインド先テーブルが揃っているか、また現時点で登録されている Business Rules が 0 件であることを確認してください。
> ```

🤖 **Copilot の動き**

- Ontology MCP の `list_ontology_entities` と `list_ontology_rules` を呼び出し（または `scripts/ontology_mcp_client.py` を活用）、13個の Entity Type が認識され、Synonym・Metadata・Rules がまだ空であることを報告します。

✅ **期待する結果**

- 13 個の Entity Type とその Backing Table が一覧表示され、Business Rules が `0 件` であることが確認できます。

---

## 3-5. 【実験：Before】セマンティック設定「なし」の状態で 3 つの業務質問を投げる

いよいよ重要な比較実験の **前半（Before 測定）** です。`ontology/evaluation_questions.json` に定義された 3 つの現場質問を、**今の素のオントロジー** に対して `ask_ontology` でそのまま投げ、回答の特徴・弱点を記録させましょう！

> 🗣️ **プロンプト**
> ```text
> Lab 04 での改善効果と比較するため、現在のエンリッチ前の mfg_enterprise_ontology に対して、ontology/evaluation_questions.json の EVAL-01、EVAL-02、EVAL-03 の3つの質問（prompt_ja）を順番に ontology-cli の ask_ontology で投げてください。生テーブルへの直接 SQL 実行は行わず、ask_ontology が返した回答をそのまま要約し、どこが曖昧・不足・見落としになっているかを artifacts/eval_before.md に記録してください。
> ```

🤖 **Copilot の動き**

- `ask_ontology` を 3 回（`EVAL-01`, `EVAL-02`, `EVAL-03`）順番に呼び出し、応答結果を `artifacts/eval_before.md` に保存します。

✅ **期待する結果（Before で観察される典型的な弱点）**

素のテーブルとリレーションだけをバインドした状態では、AI エージェントは以下のような限界を示します：

| テストID | 投げた質問のポイント | エンリッチ前（Before）で起きる典型的な弱点・見落とし |
| :--- | :--- | :--- |
| **EVAL-01** | 「保留またはリスク状態にある**オーダー**を営業視点と現場視点で挙げて」 | `order_status_code = 3` や `wo_status_code = 30` のコード定義がないため推測に頼るか確認を求め、さらに **ERP上はまだ `2` だが MES が品質保留になっている隠れリスク受注 `SO-2026-015`（1,920万円）を見落とす**。 |
| **EVAL-02** | 「チョコ停・重大アラームが出ている**号機**の稼働状態とピーク計測値を**単位つき**で教えて」 | 現場用語「号機」「チョコ停」と Entity の対応が弱く、`operating_state_code = 3` の意味や `peak_value`（`9.5` や `859.4`）の物理単位（`Pa` なのか `℃` なのか）をメタデータから特定できない。 |
| **EVAL-03** | 「投入待ちワークも含め、**品質・保全ガードレール（社内ルール）違反**の設備割当や部材ロットを洗い出して」 | スキーマ上に「校正周期超過で Tier 1 割当禁止」「磁石水分 150ppm 超は投入禁止」というルールが存在しないため、**投入待ち（`wo_status_code=10`）の `WO-2026-1025`（校正95日超過の `EQ-CNC-101` × Tier 1 顧客 `CUS-001`）を違反として検出できない**。 |

---

## 🔍（参考）裏側で実行される MCP リクエスト構造

`ontology-cli`（および同梱の `scripts/ontology_mcp_client.py`）は、裏側で以下の JSON-RPC 2.0 ペイロードを UTF-8 ファイル経由で Ontology MCP エンドポイントへ POST しています。

```bash
python3 scripts/ontology_mcp_client.py \
  --workspace-name student01 \
  --ontology-name mfg_enterprise_ontology \
  ask "現在『保留またはリスク状態にあるオーダー』を、営業部門の視点と工場現場の視点に分けて件数とIDをすべて挙げて。"
```

---

## ✅ チェックポイント

- [ ] V2 Ontology `mfg_enterprise_ontology` が作成され、`tools/list` で `ask_ontology` が確認できた
- [ ] 13 個の Entity Type と主要リレーションシップがバインドされた
- [ ] エンリッチ前の回答結果が `artifacts/eval_before.md` に保存され、素のスキーマの限界（コード値・現場用語・暗黙ルール・隠れリスクの見落とし）を確認できた

次は、このオントロジーに **サブオントロジー（Namespace）・Synonym・Metadata・Business Rules** を設定し、同じ質問への回答精度がどう劇的に変わるかを検証する **[Lab 04 — Namespace・Synonym・Metadata・Rules の設定と精度比較](./04-namespaces-synonyms-metadata-rules.md)** へ進みます！
