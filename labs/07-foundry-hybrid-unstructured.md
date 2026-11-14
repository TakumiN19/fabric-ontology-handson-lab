# Lab 07 — Microsoft Foundry 連携：Fabric Data Agent（Ontology）× 非構造化ドキュメントのハイブリッドエージェント

> **所要時間**: 約 30 分  
> **ゴール**: 保全 SOP・品質基準書・緊急空輸決裁規程・顧客 SLA 契約サマリなどの **非構造化ドキュメント（8本）を Microsoft Foundry から検索可能にし**、Lab 06 で公開した **Fabric Data Agent（`mfg_ops_data_agent` / Ontology）と統合** して、構造化データ単体でも非構造化検索単体でも到達できない「経営判断・現場復旧アクションプラン」を導き出す。

---

## 7-1. なぜ「Ontology × Foundry（非構造化）」の組み合わせが決定的な価値を生むのか？

今回の浜松工場 第2ラインのインシデントで、もし片方の仕組みしか無かったらどうなるでしょうか？

| アプローチ | 分かること | 致命的に欠けること（誤判断リスク） |
| :--- | :--- | :--- |
| **① 非構造化検索（RAG）のみ** | 空輸決裁基準（`9,000万円以上はCOO決裁`）、交換部品型番（`PART-SEAL-KF40-VT`）、磁石水分 `175ppm` 超は返品、顧客 `CUS-003` は `24時間以内` に 8D 提出 | **「今どの設備・ロットが異常で、どの顧客のいくらの受注に波及しているか」が一切分からない** |
| **② 素の ERP テーブル参照のみ** | `AtRisk(3)` になっている受注 2 件の合計 **`8,050万円`** | 隠れリスク `SO-2026-015`（`1,920万円`, `CUS-003`）を見落とすため、**誤って「SCM本部長決裁（9,000万円未満）」と判断し、`CUS-003` の「24時間以内 8D 提出期限」に違反してしまう！** |
| **③ Fabric Ontology + Foundry ハイブリッド** | Ontology が 5-Hop トレース＋ルールで **実質影響額 `9,970万円`（3件）** と原因（`EQ-VBF-204` + `LOT-MAG-088` `182ppm`）を特定し、そのアンカー ID と金額をもとに Foundry が非構造化文書を引く | **「影響額 9,970万円 ≥ 9,000万円のため COO 決裁が必要」「`CUS-003` へ 24時間以内に 8D 提出」「`LOT-MAG-088` は 175ppm 超のため再ベーキング禁止・全数返品し `SUP-007` へ切替」「`PART-SEAL-KF40-VT` 交換後に `EQ-VBF-205` で代替生産」** まで一気通貫で導出できる！ |

---

## 7-2. アーキテクチャ：Microsoft Foundry と Fabric Data Agent（Ontology）の接続パターン

本ラボでは、環境権限に応じて **A. Microsoft Foundry ポータル GUI でのノーコード統合** と、**B. Copilot CLI からのハイブリッドエージェントスクリプト実行（`scripts/foundry_hybrid_agent.py`）** の両方（またはどちらか）を実行できます。

> 💡 **既存リソース再利用の推奨**:
> Azure サブスクリプション内に既存の **Microsoft Foundry プロジェクト（旧 Azure AI Foundry）** および **Azure OpenAI / Azure AI Search** リソースがある場合は、新規作成せず既存リソースを再利用してください。Identity Passthrough（OBO 認証）のため、Fabric ワークスペースと同一 Microsoft Entra テナント上の Foundry プロジェクトを使用します。

---

## 7-3. パターン A：Microsoft Foundry ポータルで Data Agent + 非構造化ドキュメントを統合する

### Step A-1: 非構造化ドキュメント（8本）を Foundry Agent の Knowledge に登録する

1. [Microsoft Foundry ポータル (`https://ai.azure.com`)](https://ai.azure.com) を開き、使用する Project を選択して左メニューの **`Agents`** を開きます。
2. **`+ New agent`** をクリックし、Agent 名を **`mfg-hybrid-crisis-advisor`**、モデルに `gpt-4o`（または利用可能な最新推論モデル）を選択します。
3. **`Knowledge`（ナレッジ）** セクションの **`+ Add`** をクリックします：
   - **Foundry IQ / Azure AI Search を使う場合**: OneLake（`mfg_ontology_lh/Files/raw/unstructured_docs/`）またはアップロードした 8 本の Markdown をインデックス接続します。
   - **最短で試す場合（Files / Vector Store）**: **`Files`** を選択し、このリポジトリの `data/unstructured_docs/` にある **8 つの `.md` ファイル**（`SOP-EQ-VBF-204_...md`, `SOP-EQ-CNC-101_...md`, `QMS-STD-004_...md`, `POL-SCM-002_...md`, `MAN-MAT-NDFEB_...md`, `INC-2026-1028_...md`, `SLA-CUS-001_...md`, `GLOSSARY_...md`）をドラッグ＆ドロップでアップロードして Vector Store を作成します。

### Step A-2: Publish 済みの Fabric Data Agent（`mfg_ops_data_agent`）を Tool として接続する

1. 同じ Agent 設定画面の **`Tools`（ツール）** セクションで **`+ Add`** をクリックします。
2. カタログから **`Fabric IQ (OneLake Catalog)`** または **`Microsoft Fabric`**（Data Agent コネクタ）を選択します。
3. 自分のワークスペースにある Publish 済みの **`mfg_ops_data_agent`** を選択して接続します（ユーザー自身の権限でクエリが実行される Identity Passthrough が使われます）。
4. Agent の **`Instructions`** に以下のオーケストレーション指示を設定します：
   ```text
   あなたは製造・品質・サプライチェーン統合危機管理アドバイザーです。
   質問に回答する際は必ず次の2段階を踏んでください：
   1. まず Fabric Data Agent (mfg_ops_data_agent) ツールを呼び出し、オントロジーに基づいて対象の設備ID・ロットID・ワークID・顧客受注ID・実質影響受注総額（隠れリスク含む）・代替設備・代替サプライヤーを正確に取得する。
   2. 次に、取得した設備ID・品目ID・顧客ID・不良コード・影響金額をキーとして Knowledge（非構造化ドキュメント：SOP、QMS基準書、SCM空輸決裁規程 POL-SCM-002、磁石管理手順 MAN-MAT-NDFEB、顧客SLA契約 SLA-CUS-001、過去事例 INC-2026-1028）を検索し、交換部品番号・試験基準・返品可否・顧客別報告期限・最終決裁権限者を根拠文書IDつきで統合回答する。
   ```

---

## 7-4. パターン B（全員実行可能）：GitHub Copilot CLI からハイブリッドエージェントを実行・検証する

このリポジトリには、**Fabric Ontology V2 MCP（構造化データ・ルール・グラフ）** と **非構造化ドキュメント検索（Foundry Agents API / Azure AI Search / ローカルハイブリッドフォールバック対応）** を統合実行する **`scripts/foundry_hybrid_agent.py`** が同梱されています。

Copilot CLI にプロンプトを投げて、`ontology/evaluation_questions.json` のハイブリッドシナリオ **`HYBRID-01`** と **`HYBRID-02`** を実行させましょう！

> 🗣️ **プロンプト**
> ```text
> scripts/foundry_hybrid_agent.py と ontology-cli を活用して、mfg_enterprise_ontology（構造化オントロジー）と data/unstructured_docs/（非構造化ドキュメント群、Foundry 設定がある場合は Foundry エンドポイントも利用）を組み合わせ、ontology/evaluation_questions.json の HYBRID-01 と HYBRID-02 の2問に対する統合回答を作成して artifacts/hybrid_executive_brief.md に保存し、要点を表示してください。
> ```

🤖 **Copilot の動き**

- `.github/student.local.md`（および設定済みの場合は Foundry / Azure OpenAI / Azure AI Search 環境変数）を読み取り、まず `mfg_enterprise_ontology` の MCP `ask_ontology` から構造化ファクト（影響 3 受注・総額 9,970万円・`EQ-VBF-204`・`LOT-MAG-088` `182ppm`・`EQ-CNC-101` `95日`）を取得します。
- 取得したアンカーキー（`EQ-VBF-204`, `MAT-MAG-04`, `CUS-003`, `ALT-VIB-SPIKE`, `EQ-CNC-101` 等）で非構造化ドキュメント群を検索・統合し、根拠文書 ID つきの経営ブリーフィングを生成します。

---

## 7-5. 最終検証：導き出される「エグゼクティブ意思決定レポート」の正解チェック

Foundry Playground（パターン A）および CLI（パターン B）の出力に、以下の **構造化 × 非構造化のクロスオーバー結論** がすべて揃っていることを確認しましょう！

### `HYBRID-01`：浜松第2ライン緊急インシデントの総合復旧・決裁プラン

| 項目 | 構造化データ（Fabric Ontology）から判明した事実 | 非構造化文書（Microsoft Foundry）と結合して確定した判断 |
| :--- | :--- | :--- |
| **1. 影響受注と空輸決裁権限** | `SO-2026-004` (4,800万円) + `SO-2026-009` (3,250万円) + **隠れリスク `SO-2026-015` (1,920万円)** = **総額 99,700,000 円（9,970万円）**、SLA違約金 **235万円/日** | `DOC-POL-SCM002` の基準（**9,000万円以上**）に該当するため、SCM本部長ではなく **COO（最高執行責任者）決裁** で緊急チャーター空輸・特急手配を発動！ |
| **2. 顧客別 8D 報告のデッドライン** | 影響顧客は `CUS-001`、`CUS-002`、**`CUS-003`（関西セミコンダクター装置）** の Tier 1 計 3 社 | `DOC-SLA-TIER1` により、`CUS-001`/`002` は 48時間以内だが、**`CUS-003` のみ「異常検知から 24時間以内」の厳格 SLA** のため最優先で一次 8D 報告書を提出！ |
| **3. 真空ろう付け炉 `EQ-VBF-204` の復旧と代替生産** | `9.5 Pa`（28分）・`859.4 ℃`（24分）の重大逸脱で `MaintenanceHold(3)`。校正有効な同型炉は名古屋第1工場 第2ラインの **`EQ-VBF-205`（校正後24日）** | `DOC-SOP-VBF204` & 過去事例 `DOC-INC-1028` に従い、バイトンOリング **`PART-SEAL-KF40-VT`** と熱電対 **`PART-TC-R850`** を交換し、ヘリウムリーク試験（`<= 1.0×10^-8 Pa·m3/s`）合格まで隔離。緊急再製造は **`EQ-VBF-205`** へ振替！ |
| **4. 磁石ロット `LOT-MAG-088` の処置と代替調達** | `SUP-003` 納入の `LOT-MAG-088`（`MAT-MAG-04`）が **水分 `182 ppm`**（上限 150 ppm 超過）。代替認定先は **`SUP-007`**（合格ロット `LOT-MAG-091`, 水分 `42 ppm` 在庫あり） | `DOC-MAN-NDFEB` により、`151〜175 ppm` なら真空再ベーキング可能だが **`175 ppm` 超（182 ppm）は結晶粒界酸化が不可逆なため再ベーキング禁止・全数返品** と判定し、即座に **`SUP-007`（`LOT-MAG-091`）** へ切替！ |

### `HYBRID-02`：CNC 研削盤 `EQ-CNC-101` の予防保全・割当停止アクション

- **Ontology 側**: `EQ-CNC-101` は校正経過 **`95日`（周期90日超過）** かつ振動アラート `ALT-2026-904`（`ALT-VIB-SPIKE`: **`5.12 mm/s`**）が発生しており、Tier 1 向け投入待ちワーク **`WO-2026-1025`**（`SO-2026-024`, `CUS-001`）への割当は `CalibrationOverdueTier1Prohibition` ルール違反。健全な同型機 **`EQ-CNC-102`（名古屋第1工場、校正後42日）** または **`EQ-CNC-103`（北九州工場、校正後50日）** への振替が可能。
- **Foundry 非構造化 SOP（`DOC-SOP-CNC101`）側**: 振動 `4.5 mm/s` 超のため自動送りをホールドし、フィールドバランサ **`BAL-FIELD-02`** で 12,000 rpm 動的アンバランス補正を実施して振動RMS **`2.5 mm/s` 以下** への復帰およびレーザー干渉計による定期校正を実施する手順を提示。

---

## 🎉 おめでとうございます！全ラボ完了です

ここまで完了すると、Microsoft Fabric IQ Ontology × Skills for Fabric × Microsoft Foundry の一連の実践サイクルをすべて体験できました：

1. **設計相談（Lab 02）**: Competency Questions から逆算して Entity / Namespace / Graph 対象 / 非構造化境界を設計する
2. **セマンティック強化と Before/After 実証（Lab 03 & Lab 04）**: Namespace（`erp#Order` / `mes#Order`）・Synonym・Metadata・Business Rules によって、エージェントの曖昧さや隠れリスクの見落としを解消する
3. **適材適所のエンジン選択（Lab 05）**: 多段ホップ探索は **Materialized Graph（GQL）**、大規模ロールアップ・高頻度時系列は **SQL / Eventhouse KQL（＋オントロジーによるクエリ生成）** を使い分ける
4. **マルチエージェント統合（Lab 06 & Lab 07）**: **Fabric Data Agent（構造化オントロジー）** と **Microsoft Foundry（非構造化文書）** を組み合わせ、数値根拠と社内規程・SOP が噛み合った意思決定を実現する

---

## 🧹 クリーンアップ（必要に応じて実行）

ハンズオン終了後にワークスペース内の作成アイテムを整理したい場合は、Copilot CLI に以下のように指示できます（共有テナントの他の人のワークスペースには触れません）。

> 🗣️ **プロンプト（任意・削除したい場合のみ）**
> ```text
> 私のワークスペース内に今回のハンズオンで作成したアイテム一覧を表示し、削除してよいか私に確認してからクリーンアップしてください。
> ```
