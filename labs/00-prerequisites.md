# Lab 00 — 事前準備と Skills for Fabric の導入

> **所要時間**: 約 15 分（GitHub Codespaces 利用時は約 5 分）  
> **ゴール**: GitHub Copilot CLI と `microsoft/skills-for-fabric`（`ontology-cli` を含むプラグイン群）を有効化し、自分の `student` 番号を登録して Lab 01 以降をプレースホルダー置換なしで進められる状態にする。

---

## ⚡ GitHub Codespaces を使っている場合（推奨ルート）

Codespace の起動時に `.devcontainer/devcontainer.json` の自動セットアップが完了しています。ターミナルを開き、確認スクリプトを実行してください。

```bash
bash .devcontainer/scripts/verify.sh
```

`Environment verification completed successfully.` と表示されたら、0-1〜0-5 は完了済みです。そのまま **[0-6. GitHub Copilot CLI を起動してサインインする](#0-6-github-copilot-cli-を起動してサインインする)** へ進んでください。

---

## 0-1. ローカル PC で実施する場合の必須ツール

ローカル環境（macOS / Linux / Windows WSL2）で進める場合は、以下のツールがインストールされていることを確認します。

| ツール | 推奨バージョン | 確認コマンド |
| :--- | :--- | :--- |
| **Git** | 2.39 以上 | `git --version` |
| **Python** | 3.11 以上（3.12 推奨） | `python3 --version` |
| **Node.js / npm** | Node.js 20 LTS または 22 LTS | `node --version && npm --version` |
| **Azure CLI** | 2.65 以上 | `az version` |
| **jq / curl** | 任意の安定版 | `jq --version && curl --version` |

## 0-2. リポジトリのクローンとローカルデータの整合性チェック

```bash
git clone https://github.com/TakumiN19/fabric-ontology-handson-lab.git
cd fabric-ontology-handson-lab
python3 scripts/verify_local_assets.py
```

`OK: All local ERP/MES/IoT datasets, unstructured docs, oracle math, and Ontology specs verified.` と表示されれば、ダミーデータとオントロジー定義ファイルは正常です。

## 0-3. GitHub Copilot CLI のインストール

```bash
npm install --global @github/copilot
copilot --version
```

## 0-4. Skills for Fabric マーケットプレイスの登録

Microsoft 公式の **[skills-for-fabric](https://github.com/microsoft/skills-for-fabric)** を Copilot CLI のプラグインマーケットプレイスとして追加します。

```bash
copilot plugin marketplace add microsoft/skills-for-fabric
```

## 0-5. Fabric スキルプラグインのインストール確認

`ontology-cli`・`spark-cli`・`eventhouse-cli`・`fabric-cli` を含む `fabric-skills` プラグインをインストールします。

```bash
copilot plugin install fabric-skills@fabric-collection
copilot plugin install powerbi-authoring@fabric-collection
copilot plugin list
```

一覧に `fabric-skills@fabric-collection` が表示されていれば導入完了です。

---

## 0-6. GitHub Copilot CLI を起動してサインインする

**必ずこのリポジトリのルートディレクトリ（`fabric-ontology-handson-lab/`）で** `copilot` を起動します（`.github/copilot-instructions.md` を自動読み込みさせるためです）。

```bash
copilot
```

初回起動時に GitHub へのサインインを求められたら、チャット欄で `/login` を実行して認証を完了します。また、ファイル編集や CLI コマンド実行の確認をスムーズにするため、必要に応じて `/allow-all`（または都度承認）を設定してください。

あわせて、別ウィンドウのブラウザで [Fabric ポータルへの初回サインイン手順](./fabric-portal-login.md) を一度済ませておきます。

---

## 0-7. 自分の `student` 番号を一度だけ登録する（必須）

このハンズオンでは、最初に一度だけ自分の番号を伝えると、Copilot がアカウント名・ワークスペース名・テナント ID を `.github/student.local.md`（Git 管理外）に保存し、**Lab 01 以降はワークスペース名や各種 GUID を毎回入力しなくても自動で特定・解決**します。

以下のプロンプトの `<あなたの番号>` だけを配布された番号（例: `01` や `12`）に変えて Copilot CLI に送信してください。

> 🗣️ **プロンプト**
> ```text
> 私の student 番号は <あなたの番号> です。このハンズオンの参加者設定として登録して、設定内容を表示してください。
> ```

> 💡 **自分の独自テナント／独自ワークスペースで実施する場合**は、次のようにそのまま伝えてください：  
> `私のハンズオン環境として、アカウント <you@yourdomain.com>、テナントID <tenant-guid>、ワークスペース名 <workspace-name> を .github/student.local.md に登録して表示してください。`

🤖 **Copilot の動き**

- `.github/copilot-instructions.md` のルールに従い、番号から `student<番号>` ワークスペース名、アカウント名、テナント ID を生成して `.github/student.local.md` に保存します。
- この時点ではまだ Azure / Fabric へのサインインは行いません。

✅ **期待する結果**

- `.github/student.local.md` が作成され、保存された `student` 番号・ワークスペース名・アカウント・テナント ID が画面に表示されます。

---

## 0-8. 搭載スキル（`ontology-cli`）が認識されているか確認する

最後に、Copilot が `skills-for-fabric` のオントロジースキルを認識しているか軽く確認してみましょう。

> 🗣️ **プロンプト**
> ```text
> この環境で利用可能な Fabric 関連スキルを確認し、特に ontology-cli でできることと V1 / V2 オントロジーに関する注意点を3行で要約してください。Azure への接続はまだ行わないでください。
> ```

🤖 **Copilot の動き**

- インストール済みの `fabric-skills` プラグインから `ontology-cli` の概要を確認して回答します。

✅ **期待する結果**

- `ontology-cli` が認識されており、「V2（New Experience）の Ontology MCP エンドポイント（`ask_ontology`, `list_ontology_entities`, `list_ontology_rules`）を使った自然言語照会に対応していること」「V1 への自然言語照会は非対応であり、V2 の作成・編集境界に注意が必要であること」が簡潔に返ってきます。

---

## ✅ チェックポイント

- [ ] `python3 scripts/verify_local_assets.py` が `OK` を返した
- [ ] `copilot` がリポジトリルートで起動し、`fabric-skills@fabric-collection` が有効になっている
- [ ] `.github/student.local.md` に自分の参加者設定が保存された

次は **[Lab 01 — サインインと ERP・MES・IoT・非構造化データの準備](./01-login-and-data-setup.md)** へ進みます。
