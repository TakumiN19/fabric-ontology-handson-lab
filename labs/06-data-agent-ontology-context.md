# Lab 06 — Fabric Data Agent からの Ontology 呼び出しとコンテキスト理解の検証

> **所要時間**: 約 20 分  
> **ゴール**: Fabric Data Agent `mfg_ops_data_agent` を作成し、生テーブルではなく **`mfg_enterprise_ontology` をデータソースとして接続** することで、Data Agent が Namespace・Synonym・Metadata・Business Rules をどうプロンプトコンテキストに組み込み、自動で GQL / SQL を生成して高精度に回答するかを確認・公開（Publish）する。

---

## 6-1. なぜ Data Agent に「生 Lakehouse」ではなく「Ontology」をつなぐのか？

Fabric Data Agent に Lakehouse の 15 個のテーブルを直接つないだ場合、Data Agent ごとに毎回長い Agent Instructions（カスタム指示文）や Few-shot SQL 例を手書きする必要があり、別のエージェントを作るたびに知識が分散（サイロ化）します。

一方、**Data Agent のデータソースに `mfg_enterprise_ontology` を指定** すると：

1. Lab 04 で定義した **Namespace（`erp#Order` / `mes#Order`）・Synonym・単位やコードの Metadata・4つの Business Rules** が、自動的に Data Agent へ構造化コンテキストとして注入されます。
2. 多段関係探索が必要な質問には、裏側の Materialized Graph に対して **GQL クエリを自動生成・実行** します。
3. 公開（Publish）した Data Agent は、次の Lab 07 で **Microsoft Foundry のマルチツールエージェントから MCP / Fabric IQ ツールとしてそのまま呼び出す** ことができます。

---

## 6-2. Step 1: Fabric Data Agent `mfg_ops_data_agent` を作成して Ontology を接続する

> ⚠️ **現行 Preview 仕様のポイント**:
> Fabric REST API で空の `DataAgent` アイテム自体は作成可能ですが、**Ontology データソースの紐づけ設定と Publish 操作は現在 Fabric ポータル UI 専用** です（公開 API の JSON スキーマでは Ontology ソースの紐づけはまだサポートされていません）。以下の手順で作成・接続します。

### ポータル手順（約 3 分）

1. Fabric ワークスペース（例: `student01`）を開き、左上の **`+ New item`** から **`Data agent (preview)`** を選択します。
2. Name に **`mfg_ops_data_agent`** と入力して **`Create`** をクリックします。
3. Data Agent の設定画面が開いたら、**`+ Add data source`（データソースの追加）** をクリックし、一覧から **`mfg_enterprise_ontology`**（Ontology アイテム）を選択して **`Add`** します。
4. 左側の Explorer ツリーで `mfg_enterprise_ontology` にチェックが入っていることを確認します。
5. （最小限の役割設定のみ追加）**`Agent instructions`** 欄には、テーブル定義やコード表を書き直す必要はありません！以下の一文だけ入力します：
   ```text
   あなたは Contoso Precision Motors の生産・品質・SCM 統合オペレーションを支援するアシスタントです。必ず接続されたオントロジーの Namespace・Metadata・Business Rules に基づいて根拠ID・単位・金額を明示して日本語で回答してください。
   ```

CLI からも `mfg_ops_data_agent` がワークスペース上に作成されたことを記録しておきましょう。

> 🗣️ **プロンプト**
> ```text
> 私のワークスペースにある DataAgent アイテム「mfg_ops_data_agent」の ID を確認し、参加者設定ファイルに記録してください。
> ```

---

## 6-3. Step 2: Data Agent が受け取っている「Ontology Context」の中身を覗いてみる

Fabric Data Agent には、オントロジーからどのような構造化知識を受け取っているかを直接確認できる診断機能があります。

1. Data Agent 画面左側の Explorer で `mfg_enterprise_ontology` の横にある **`...`（その他のオプション）** をクリックし、**`Download ontology context`**（またはスキーマ詳細表示）を選択します。
2. ダウンロードされたコンテキストを開くと、Lab 04 で設定した以下がすべて含まれていることが分かります：
   - `erp#Order` と `mes#Order` の Namespace 分離と説明
   - 「号機」「チョコ停」「ワーク」などの Synonym
   - `order_status_code`・`wo_status_code`・`moisture_ppm`・`peak_value` の単位とコード定義
   - 4 つの Business Rules（`HiddenErpOrderRiskEscalation` など）

---

## 6-4. Step 3: Data Agent チャット画面でコンテキスト理解と GQL トレースを確認する

Data Agent 右側のテストチャット欄に、以下の **3 つの実践プロンプト** を順番に入力し、回答の下に表示される **実行ステップ（生成された GQL クエリと参照ルール）** を開いて確認しましょう！

### テスト質問 ①：現場用語（Synonym）＋コード解釈＋多段ホップ＋隠れリスクルール

> 🗣️ **Data Agent チャットへの入力 ①**
> ```text
> 浜松第2ラインでチョコ停・重大アラームが出ている号機を特定し、その号機で加工されたワークと紐づく顧客受注オーダーをすべて挙げてください。ERPステータスが未更新の実質納期リスク分も含めて、影響受注総額（円）と1日あたりSLAペナルティ合計（円/日）を計算してください。
> ```

✅ **確認ポイント**:
- 「チョコ停」→ `iot#EquipmentAlert`、「号機」→ `mes#Equipment`、「ワーク」→ `mes#Order`、「顧客受注オーダー」→ `erp#Order` がカスタム指示書なしで自動解決されること。
- 実行トレースを展開すると、Data Agent が多段リレーションをたどる **GQL クエリ** を生成していること。
- `SO-2026-004`（4,800万円）＋ `SO-2026-009`（3,250万円）に加え、**ERP上は `2=InProduction` のままの `SO-2026-015`（1,920万円、`CUS-003`）** を `HiddenErpOrderRiskEscalation` ルールに従って含め、**総額 99,700,000 円・SLA ペナルティ合計 2,350,000 円/日** と正確に回答すること！

### テスト質問 ②：投入待ちワークに対する予防的ガードレール検知

> 🗣️ **Data Agent チャットへの入力 ②**
> ```text
> 現在「投入待ち」になっているワークの中で、社内ルール（校正期限やTier1顧客向け制限、または磁石ロット水分率ルール）に違反しているため着手を止めるべき案件があれば、理由と対象IDを教えてください。
> ```

✅ **確認ポイント**:
- **`WO-2026-1025`** が抽出され、割当設備 **`EQ-CNC-101` の校正経過日数が `95日`（周期 `90日` 超過）** であり、紐づく `SO-2026-024` が Tier 1 顧客 `CUS-001` 向けであるため、`CalibrationOverdueTier1Prohibition` ルールにより着手禁止と判定されること。

---

## 6-5. Step 4: Data Agent を公開（Publish）して Microsoft Foundry から呼べるようにする

次の Lab 07 で Microsoft Foundry のエージェントからこの Data Agent をツールとして呼び出せるように公開します。

1. `mfg_ops_data_agent` 画面上部リボンの **`Publish`（公開）** をクリックします。
2. 公開説明欄に以下のように入力して公開を確定します（この説明文は Foundry 側のオーケストレーターが「いつこのツールを呼ぶか」を判断するルーティング情報になります）：
   ```text
   Contoso Precision Motors の ERP（顧客・受注・サプライヤー・品目）、MES（製造ライン・設備・部材ロット・製造指図・品質検査）、IoT（設備アラート）を統合したエンタープライズオントロジーエージェント。受注影響額、ロット・設備の多段トレース、校正・水分率などの業務ルール判定を回答する。
   ```

あわせて CLI 側でも、同じ質問を `ontology-cli` 経由で実行して回答の一貫性を確認しておきましょう。

> 🗣️ **プロンプト**
> ```text
> Lab 06 の確認として、mfg_enterprise_ontology の ask_ontology に対して「浜松第2ラインで重大アラームが出ている号機から影響を受ける顧客受注総額とSLAペナルティ日額合計、および投入待ちワークのルール違反案件」を照会し、Data Agent の回答と同じ正解値（99,700,000円、2,350,000円/日、WO-2026-1025）が返ることを確認してください。
> ```

---

## ✅ チェックポイント

- [ ] `mfg_ops_data_agent` に `mfg_enterprise_ontology` を接続し、長い SQL 指示文を書かなくても Synonym・Namespace・Metadata・Rules が効くことを確認した
- [ ] `Download ontology context` と実行トレース（GQL 生成）を確認した
- [ ] `mfg_ops_data_agent` を Publish した

いよいよ最終ステップです！構造化オントロジーだけでは答えられない **「SOP の交換部品型番」「磁石返品・再ベーキング可否規定」「顧客別の 8D 報告書提出期限（24時間 vs 48時間）」「9,000万円超の緊急空輸決裁権限」** を **Microsoft Foundry** の非構造化ドキュメント検索と融合させる **[Lab 07 — Microsoft Foundry 連携：Ontology（構造化）× 非構造化ドキュメントのハイブリッドエージェント](./07-foundry-hybrid-unstructured.md)** へ進みましょう！
