# 用語集（Glossary）— Fabric IQ Ontology × Skills for Fabric × Microsoft Foundry

本ハンズオンで登場する Microsoft Fabric IQ・オントロジー・グラフ・エージェント関連の主要用語リファレンスです。

| 用語 | 解説 |
| :--- | :--- |
| **Microsoft Fabric IQ** | OneLake 上のデータに対してビジネス概念・関係・ルールを付与し、人間と AI エージェントが同じ業務文脈でデータを理解・操作できるようにするセマンティックインテリジェンス層。 |
| **Ontology（オントロジー）** | 物理テーブルをそのまま並べるのではなく、企業内の「モノ・概念（Entity Type）」「つながり（Relationship）」「同義語（Synonym）」「単位やコードの意味（Metadata）」「業務上の制約・判断基準（Business Rules）」を宣言的に定義した知識モデル。 |
| **Ontology V2（New Experience / TMDL）** | 現在の Fabric Ontology の標準アーキテクチャ。裏側の定義を **TMDL（Tabular Model Definition Language）** で保持し、Namespace・Business Rules・Ontology Agent・MCP エンドポイント（`ask_ontology` 等）をサポートする。（旧 V1 JSON 形式は 2027年1月31日廃止予定）。 |
| **Namespace（サブオントロジー）** | 部門やドメインごとに語彙空間を分離する仕組み（本ラボでは `erp`, `mes`, `iot`）。これにより、営業部門の **`erp#Order`（顧客受注）** と工場現場の **`mes#Order`（製造指図）** のような同名概念を衝突させずに統制できる。 |
| **Synonym（同義語）** | Entity Type や Property に対して現場の別名・略称・スラング（「号機」「チョコ停」「ワーク」「SO」など）を紐づける設定。AI エージェントの用語解決精度を大きく高める。 |
| **Metadata（メタデータ）** | 数値ステータスコード（`3=AtRisk`, `30=QualityHold`）や物理単位（`℃`, `Pa`, `ppm`, `JPY`）、許容閾値などの説明情報。 |
| **Business Rules（業務ルール）** | スキーマや外部キーだけでは表現できない社内基準・品質ガードレール・横断エスカレーション条件（例：校正90日超の設備は Tier 1 案件への割当禁止、ERP 未更新でも MES 品質保留なら実質リスク受注に合算など）。 |
| **Graph in Microsoft Fabric（Materialized Graph）** | Ontology のうち選択した Entity Type と Relationship をノード・エッジとして投影するネイティブグラフエンジン（子アイテム `GraphModel`）。ISO 標準 **GQL（Graph Query Language）** で多段ホップ探索を高速実行できる。 |
| **Selective Graph Materialization（選択的グラフ投影）** | すべてのテーブルを無差別にグラフ化せず、多段関係トレースが必要なエンティティだけを `Manage graph` で ON にし、全件集計や高頻度 IoT 生テレメトリは SQL / Eventhouse KQL に任せる設計手法。 |
| **Skills for Fabric（`skills-for-fabric`）** | GitHub Copilot CLI などのコーディングエージェントに Microsoft Fabric の REST API・OneLake・Spark・SQL・Eventhouse・Ontology MCP のベストプラクティス手順を与える公式プラグイン群（本ラボでは `ontology-cli`, `fabric-cli`, `spark-cli` 等を使用）。 |
| **Ontology MCP Endpoint** | V2 Ontology アイテムが公開する Model Context Protocol（JSON-RPC 2.0）データプレーンエンドポイント。`ask_ontology`（自然言語照会＆根拠付き SQL/KQL コード生成）、`list_ontology_entities`、`list_ontology_rules`、`search_ontology` を提供する。 |
| **Fabric Data Agent** | Ontology・Lakehouse・Warehouse・Eventhouse・Semantic Model を接続して自然言語 Q&A を提供する Fabric ネイティブエージェント。Ontology を接続すると Namespace・Metadata・Rules を受け取り、GQL 等を自動生成する。 |
| **Microsoft Foundry（および Foundry IQ）** | マルチツール・マルチデータソースの AI エージェントを構築・運用するプラットフォーム。Publish された Fabric Data Agent（構造化オントロジー）と、SOP・規程・契約書などの非構造化ドキュメントナレッジを 1 つのエージェントに統合できる。 |
| **Competency Questions（コンピテンシークエスチョン）** | オントロジー設計の最初に洗い出す「このオントロジーが答えられなければならない代表的な業務上の問い」。ここから逆算して必要な Entity・Relationship・Metadata・Rules を決める。 |
