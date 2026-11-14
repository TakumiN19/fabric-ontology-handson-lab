# Lab 04 — Namespace（サブオントロジー）・Synonym・Metadata・Business Rules の設定と Before/After 精度検証

> **所要時間**: 約 30 分  
> **ゴール**: `mfg_enterprise_ontology` に対して **① サブオントロジー（Namespace）による同名概念 `Order` の分離、② Synonym（部門別同義語・現場用語）、③ Metadata（物理単位・数値ステータスコード定義）、④ Business Rules（4つの業務ガードレール）** を設定し、TMDL 定義への反映を確認した上で、Lab 03 と同一の質問に対する回答精度がどう劇的に改善するか（Before vs After）を検証する。

---

## 4-1. オントロジーの 4 大セマンティック設定が AI に与えるコンテキスト

Lab 03 で確認した「素のスキーマの限界」は、以下の 4 つのセマンティック設定によってそれぞれ解決されます。

| 設定要素 | 解決する課題 | 本ハンズオンでの具体例 |
| :--- | :--- | :--- |
| **1. Namespace（サブオントロジー）** | 複数部門で同じ言葉が違う実体を指す「同名概念の衝突」とオーナーシップ境界 | `erp`・`mes`・`iot` の 3 名前空間を定義し、顧客受注を **`erp#Order`**、製造指図を **`mes#Order`** として曖昧さなく分離 |
| **2. Synonym（同義語）** | 現場スラング・略語・部門方言と正式 Entity / Property 名のギャップ | `号機` → `mes#Equipment`、`チョコ停` / `警報` → `iot#EquipmentAlert`、`ワーク` → `mes#Order` |
| **3. Metadata（説明・単位・コード定義）** | 数値フラグ・コード値・単位なし数値列の意味解釈ミス | `order_status_code`（`2=InProduction`, `3=AtRisk`）、`moisture_ppm`（単位 `ppm`, 上限 `150`）、`peak_value`（`℃` / `Pa` / `mm/s`） |
| **4. Business Rules（業務ルール）** | テーブルに書かれていない社内基準・品質ガードレール・横断判定ロジック | 校正90日超の Tier 1 割当禁止、磁石水分 150ppm 超の投入禁止、ERP 未更新 `status=2` を含む隠れ納期リスク合算 |

---

## 4-2. Step 1: サブオントロジー（Namespace `erp` / `mes` / `iot`）の定義と同名 `Order` の分離

Fabric ポータルで `mfg_enterprise_ontology` を開き、3 つのサブオントロジー名前空間を構成して、`SalesOrder` と `WorkOrder` をそれぞれのドメイン本来の概念名 **`Order`**（`erp#Order` と `mes#Order`）へ進化させます。

### Ontology Agent（Act モード）または UI での設定手順

`mfg_enterprise_ontology` の **Ontology Agent（Act モード）** に以下のプロンプトを入力して適用します（上部の **`Manage namespaces`** メニューから手動確認・編集することも可能です）。

> 🗣️ **Ontology Agent（ポータル画面内・Act モード）への入力プロンプト ①：Namespace 定義と割当**
> ```text
> 次の3つの Namespace（サブオントロジー）を作成し、13個の Entity Type をそれぞれのドメインへ割り当ててください。あわせて Namespace 分離を活かして、erp 側の SalesOrder の表示名を「Order」（erp#Order）に、mes 側の WorkOrder の表示名を「Order」（mes#Order）に変更してください。
>
> 1. Namespace: erp
>    - URI: https://ontology.contoso-motors.example/erp#
>    - Description: 営業・受注・購買・品目マスタを管理するERP商流サブオントロジー。「Order」は顧客からの確定受注（Sales Order: SO-*）を表す。
>    - 所属Entity: Customer, Supplier, Material, Product, Order (旧SalesOrder), PurchaseOrder
>
> 2. Namespace: mes
>    - URI: https://ontology.contoso-motors.example/mes#
>    - Description: 工場ライン・生産設備・部材ロット・製造指図・品質検査を管理するMES製造実行サブオントロジー。「Order」は現場の製造指図（Work Order: WO-*）を表す。
>    - 所属Entity: ProductionLine, Equipment, MaterialLot, Order (旧WorkOrder), QualityInspection
>
> 3. Namespace: iot
>    - URI: https://ontology.contoso-motors.example/iot#
>    - Description: 設備センサー構成および異常アラート検知イベントを管理するOT/IoT監視サブオントロジー。
>    - 所属Entity: Sensor, EquipmentAlert
> ```

> 💡 **ここがポイント！**
> これまで 1 つのフラットな空間では衝突して作れなかった 2 つの `Order` が、**`erp#Order`** と **`mes#Order`** として綺麗に共存できるようになります。営業担当者も工場長も、普段どおり「オーダー」という言葉を使いつつ、AI 側が文脈と Namespace の説明からどちらの `Order` か（あるいは両方か）を正確に判断できるようになります。

---

## 4-3. Step 2: Synonym（同義語）と Metadata（説明・単位・ステータスコード表）の設定

続いて、現場用語の Synonym と、数値コード・物理単位の Metadata を一括で付与します。

> 🗣️ **Ontology Agent（ポータル画面内・Act モード）への入力プロンプト ②：Synonym と Metadata の設定**
> ```text
> 主要な Entity Type と Property に以下の Synonym（同義語）および Metadata（Description・単位・コード定義）を設定してください。
>
> 【Synonyms と Entity Description】
> - erp#Order: Synonyms = ["顧客受注", "受注オーダー", "営業オーダー", "受注伝票", "SO", "SalesOrder"]
>   Description = "顧客からの確定受注（Sales Order）。order_status_code: 0=Cancelled(取消), 1=Confirmed(受注確定), 2=InProduction(製造手配中), 3=AtRisk(納期遅延リスク), 4=Shipped(出荷済)。ERP上で2(InProduction)でも紐づくmes#Orderが30(QualityHold)の場合は実質納期リスク対象。"
> - mes#Order: Synonyms = ["製造指図", "作業指示", "製造オーダー", "ワーク", "ジョブ", "WO", "WorkOrder"]
>   Description = "工場ラインへの製造指図（Work Order）。wo_status_code: 10=Queued(投入待ち), 20=Running(加工中), 30=QualityHold(品質保留・隔離), 40=Completed(完了)。"
> - erp#Customer: Synonyms = ["取引先", "顧客", "納入先", "得意先", "OEM顧客"]
>   Description = "納入先OEM顧客。customer_tier='Tier1'は最優先顧客であり、納期遅延時にsla_penalty_jpy_per_day（円/日）の違約金が発生する。"
> - erp#Supplier: Synonyms = ["サプライヤー", "仕入先", "部材メーカー", "ベンダー"]
>   Description = "原材料サプライヤー。quality_rating_score(0-100)が80未満の場合は新規ロット受入時に全数検査または代替認定サプライヤーへの切替対象。"
> - mes#Equipment: Synonyms = ["生産設備", "設備", "装置", "号機", "マシン", "炉", "加工機"]
>   Description = "工場内の生産設備。operating_state_code: 1=NormalRunning(正常稼働), 2=DegradedWarning(劣化・校正注意), 3=MaintenanceHold(異常停止・保全隔離中)。days_since_calibration(日)がcalibration_cycle_days(90日)を超過した設備はTier1向け稼働禁止。"
> - mes#MaterialLot: Synonyms = ["部材ロット", "原材料ロット", "投入ロット", "磁石ロット", "ロット"]
>   Description = "工場受入済みの部材ロット。MAT-MAG-04（NdFeB焼結磁石）はmoisture_ppm（水分率, 単位: ppm）が150 ppm以下でなければならず、175 ppm超は再ベーキング不可・全数返品対象。"
> - mes#QualityInspection: Synonyms = ["品質検査", "検査記録", "合否判定", "不適合記録", "QC結果"]
>   Description = "工程内・出荷前の品質検査結果。disposition_code: 1=Pass(合格), 2=Rework(手直し再加工), 3=ScrapHold(廃棄・赤札隔離保留)。"
> - iot#EquipmentAlert: Synonyms = ["設備アラーム", "異常アラート", "設備警報", "チョコ停", "センサー異常"]
>   Description = "閾値逸脱アラート。alert_code別のpeak_value単位: ALT-TMP-HIGH/ALT-TMP-WARN=温度(℃, 炉上限835℃), ALT-VAC-LEAK=真空度(Pa, 上限5.0Pa), ALT-VIB-SPIKE=振動速度(mm/s, 警報4.5mm/s)。duration_minutesの単位は分(minutes)。"
>
> 【主要 Property Description】
> - erp#Order.order_amount_jpy: "受注合計金額（日本円, JPY）。緊急空輸・特急手配の決裁権限判定（3,000万円以上SCM本部長、9,000万円以上COO決裁）の基礎金額。"
> - erp#Order.order_status_code: "ERP受注ステータスコード（0=Cancelled, 1=Confirmed, 2=InProduction, 3=AtRisk, 4=Shipped）"
> - mes#Order.wo_status_code: "MES製造指図ステータスコード（10=Queued, 20=Running, 30=QualityHold, 40=Completed）"
> - mes#Equipment.operating_state_code: "設備稼働状態コード（1=NormalRunning, 2=DegradedWarning, 3=MaintenanceHold）"
> - mes#Equipment.days_since_calibration: "前回校正からの経過日数（単位: 日 / days）。calibration_cycle_days(90日)超過は校正期限切れ。"
> - mes#MaterialLot.moisture_ppm: "受入・保管時の水分含有率（単位: ppm）。NdFeB磁石ロットの許容上限は 150 ppm。"
> - iot#EquipmentAlert.peak_value: "異常検知時のピーク計測値（ALT-TMP-HIGH/WARNは℃、ALT-VAC-LEAKはPa、ALT-VIB-SPIKEはmm/s）。"
> ```

---

## 4-4. Step 3: Business Rules（4つの業務ルール・ガードレール）の設定

次に、スキーマだけでは絶対に読み取れない **4 つの社内ルール** を Ontology の **Business Rules** として登録します。ポータルの **`Rules`** タブ（または Ontology Agent Act モード）から以下の 4 ルールを追加します。

> 🗣️ **Ontology Agent（ポータル画面内・Act モード）への入力プロンプト ③：Business Rules 登録**
> ```text
> mfg_enterprise_ontology に以下の4つの Business Rules を登録してください。
>
> 1. Rule Name: ThermalBrazingExcursionQuarantine
>    - Scope: iot#EquipmentAlert, mes#Equipment, mes#Order
>    - Condition: VacuumBrazingFurnace において ALT-TMP-HIGH (peak_value > 835 ℃) または ALT-VAC-LEAK (peak_value > 5.0 Pa) が duration_minutes >= 15 分継続した場合
>    - Action: 対象 mes#Equipment を operating_state_code = 3 (MaintenanceHold) に隔離し、処理した mes#Order をすべて wo_status_code = 30 (QualityHold) として不適合隔離・再製造手配の対象とする。
>
> 2. Rule Name: CalibrationOverdueTier1Prohibition
>    - Scope: mes#Equipment, mes#Order, erp#Order, erp#Customer
>    - Condition: mes#Equipment.days_since_calibration > mes#Equipment.calibration_cycle_days (90日超過) かつ 紐づく erp#Customer.customer_tier = 'Tier1' の場合
>    - Action: 投入待ち(wo_status_code = 10)であっても当該設備での製造着手を禁止し、校正有効な代替設備への振替または緊急校正完了まで保留とする。
>
> 3. Rule Name: CriticalMagnetMoistureLimit
>    - Scope: mes#MaterialLot, erp#Material, erp#Supplier
>    - Condition: erp#Material.material_id = 'MAT-MAG-04' かつ mes#MaterialLot.moisture_ppm > 150 の場合（特に moisture_ppm > 175 の場合は再ベーキング禁止）
>    - Action: 当該ロットを即時隔離・使用禁止とし、moisture_ppm > 175 の場合は全数サプライヤー返品の上、認定代替サプライヤー(backup_supplier_id)の合格ロットへ切り替える。
>
> 4. Rule Name: HiddenErpOrderRiskEscalation
>    - Scope: erp#Order, mes#Order, erp#Customer
>    - Condition: mes#Order.wo_status_code = 30 (QualityHold) に紐づく erp#Order は、たとえ ERP 上の order_status_code が 2 (InProduction) のまま未更新であっても
>    - Action: 実質的な納期遅延リスク受注(Effective AtRisk)として扱い、影響受注総額(order_amount_jpy)および顧客SLAペナルティ日額の集計・経営エスカレーション判定に必ず合算する。
> ```

> 📌 **（ポータル UI からの確認ポイント）**:
> 上記を適用したら、キャンバス上で `erp#Order` と `mes#Order` にそれぞれの Namespace バッジが付いていること、および `Rules` 一覧に 4 件のルールが表示されていることを確認して保存します。

---

## 4-5. Step 4: CLI から TMDL 定義と MCP メタデータの反映を検証する

ポータルで設定した Namespace・Synonym・Metadata・Business Rules が、裏側の **V2 TMDL（Tabular Model Definition Language）定義** と **Ontology MCP エンドポイント** にどう格納されているかを CLI で確認しましょう！

> 🗣️ **プロンプト**
> ```text
> ontology-cli を使って mfg_enterprise_ontology の最新の定義（getDefinition）と MCP の list_ontology_entities / list_ontology_rules を取得し、次の3点を確認してください：
> 1) erp, mes, iot の3つの Namespace と erp#Order / mes#Order が認識されていること
> 2) Synonym と単位・ステータスコードの Metadata が含まれていること
> 3) 4つの Business Rules が登録されていること
> あわせてローカルのリファレンス定義 ontology/v2_tmdl/ と構造を見比べて要点を教えてください。
> ```

🤖 **Copilot の動き**

- `POST /v1/workspaces/{ws}/items/{ont}/getDefinition`（LRO ポーリング対応、`x-ms-fabric-skill: ontology-cli` 付与）で Base64 デコードした TMDL パート群を確認し、さらに MCP の `list_ontology_entities` と `list_ontology_rules` を呼び出します。
- ローカルの `ontology/v2_tmdl/namespaces/*.tmdl`、`entities/erp#Order.tmdl`、`rules/*.tmdl` と比較して解説します。

✅ **期待する結果**

- V2 Ontology の実体が `namespaces/erp.tmdl`、`entities/erp#Order.tmdl`、`entities/mes#Order.tmdl`、`rules/*.tmdl` のような **人間にも AI にも読みやすい宣言的 TMDL ファイル群** として保持されていることが確認できます。
- `list_ontology_rules` で 4 件の Business Rules が返却されます。

---

## 4-6. 【実験：After】まったく同じ 3 つの質問を再度投げて Before vs After を比較する！

お待たせしました！Lab 03 で投げたのと**一字一句同じ 3 つの質問（`EVAL-01`, `EVAL-02`, `EVAL-03`）** を、エンリッチ後の `mfg_enterprise_ontology` に投げて、`artifacts/eval_before.md` と比較させましょう。

> 🗣️ **プロンプト**
> ```text
> エンリッチ後の mfg_enterprise_ontology に対して、Lab 03 とまったく同じ ontology/evaluation_questions.json の EVAL-01、EVAL-02、EVAL-03 の3問を ontology-cli の ask_ontology で実行してください。結果を artifacts/eval_after.md に保存した上で、artifacts/eval_before.md と比較した「Before / After 改善スコアカード」を表形式で表示してください。
> ```

🤖 **Copilot の動き**

- `ask_ontology` で `EVAL-01`〜`EVAL-03` を再実行し、`artifacts/eval_before.md` と突き合わせて改善点を整理します。

✅ **期待する結果（劇的なコンテキスト理解の改善！）**

| テストID | エンリッチ前（Before） | エンリッチ後（After）の回答内容 | 効いた設定要素 |
| :--- | :--- | :--- | :--- |
| **EVAL-01**<br>（保留・リスク状態のオーダー） | `Order` の曖昧さや数値コードの不明瞭さで迷い、`SO-2026-015` を見落とす | 営業視点（`erp#Order`）と現場視点（`mes#Order`）を明確に分離し、現場保留 3件（`WO-2026-1007`, `1012`, `1019`）に加え、**ERP上はまだ `2=InProduction` の隠れリスク `SO-2026-015`（1,920万円）を含む計 3 件・総額 9,970万円** を正確に特定！ | **Namespace** (`erp#Order` / `mes#Order`)<br>**Metadata** (コード定義)<br>**Rule** (`HiddenErpOrderRiskEscalation`) |
| **EVAL-02**<br>（チョコ停・重大アラームの号機） | 「号機」「チョコ停」の解釈が弱く、単位（`℃` / `Pa`）や状態コードの意味が欠落 | 「号機＝`mes#Equipment`」「チョコ停＝`iot#EquipmentAlert`」を即座に解決し、**`EQ-VBF-204` が `MaintenanceHold（保全停止: 3）` であり、真空度 `9.5 Pa`（28分 / 21分）・温度 `859.4 ℃`（24分）** の重大逸脱であることを単位つきで回答！ | **Synonym** (`号機`, `チョコ停`)<br>**Metadata** (`℃`, `Pa`, 稼働コード) |
| **EVAL-03**<br>（ガードレール違反の投入待ちワーク・ロット） | 社内基準が分からず、投入待ちの `WO-2026-1025` を見逃す | ① **投入待ち `WO-2026-1025`** が校正期限超過の **`EQ-CNC-101`（95日 > 90日周期）** に割り当てられており Tier 1 顧客 `CUS-001` 向けのため着手禁止であること、② **`LOT-MAG-088`（水分 `182 ppm` > `150 ppm` 上限、`SUP-003`）** が全数返品＆代替 `SUP-007` 切替対象であることを正確に指摘！ | **Business Rules** (`CalibrationOverdueTier1Prohibition`, `CriticalMagnetMoistureLimit`) |

---

## ✅ チェックポイント

- [ ] `erp`, `mes`, `iot` の 3 つのサブオントロジー（Namespace）で `erp#Order` と `mes#Order` を分離できた
- [ ] Synonym・Metadata・4 つの Business Rules を設定し、TMDL / MCP で反映を確認できた
- [ ] Before / After の比較で、隠れリスク受注 `SO-2026-015` や投入待ち違反 `WO-2026-1025` が検出できるようになったことを確認した

次は、オントロジーの裏側で動く **グラフエンジン（Materialized Graph）を有効にすべきシナリオと、逆に有効にしない方がよいシナリオ** を実データで検証する **[Lab 05 — グラフエンジン ON / OFF シナリオの比較検証](./05-graph-engine-scenarios.md)** へ進みます！
