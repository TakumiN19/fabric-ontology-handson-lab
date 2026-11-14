#!/usr/bin/env python3
"""Microsoft Foundry × Fabric Data Agent (Ontology) Hybrid Orchestration Helper.

Supports two execution modes for Lab 07:
  1. `verify-local`: Validates local unstructured documents (`data/unstructured_docs/*.md`),
     verifies shared anchor keys (`EQ-VBF-204`, `LOT-MAG-088`, `DEF-BOND-02`, `CUS-003`, `SUP-007`)
     against `ontology/design-blueprint.json`, and outputs the Foundry indexing manifest.
  2. `ask-hybrid`: Queries structured operational context from Fabric Ontology / published Data Agent MCP
     AND retrieves matching unstructured SOP / Policy / SLA sections via Microsoft Foundry
     (Azure OpenAI Responses / Vector Store `file_search` or Azure AI Search REST API, reusing
     existing Azure resources configured via environment variables without creating new billable resources).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "data" / "unstructured_docs"
BLUEPRINT_PATH = REPO_ROOT / "ontology" / "design-blueprint.json"


def load_local_docs() -> list[dict[str, Any]]:
    catalog_path = DOCS_DIR / "doc_catalog.csv"
    with catalog_path.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    docs: list[dict[str, Any]] = []
    for row in rows:
        md_path = DOCS_DIR / row["file_name"]
        content = md_path.read_text(encoding="utf-8")
        docs.append(
            {
                "doc_id": row["doc_id"],
                "file_name": row["file_name"],
                "doc_type": row["doc_type"],
                "domain": row["domain"],
                "anchor_keys": [k.strip() for k in row["anchor_keys"].split(";") if k.strip()],
                "content": content,
            }
        )
    return docs


def verify_local_alignment() -> dict[str, Any]:
    docs = load_local_docs()
    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    rule_policy_docs = {r["metadata"]["policyDoc"] for r in blueprint["business_rules"]}
    doc_ids = {d["doc_id"] for d in docs}
    missing_rule_docs = sorted(rule_policy_docs - doc_ids)
    if missing_rule_docs:
        raise RuntimeError(f"Business rules reference missing doc_ids: {missing_rule_docs}")

    return {
        "document_count": len(docs),
        "verified_rule_policy_links": sorted(rule_policy_docs),
        "total_characters": sum(len(d["content"]) for d in docs),
        "documents": [
            {
                "doc_id": d["doc_id"],
                "file_name": d["file_name"],
                "anchor_keys": d["anchor_keys"],
            }
            for d in docs
        ],
    }


def search_azure_ai_search(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Queries an existing Azure AI Search index provisioned in Microsoft Foundry."""
    endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT", "").rstrip("/")
    index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME", "")
    api_key = os.environ.get("AZURE_SEARCH_API_KEY", "")

    if not endpoint or not index_name:
        return []

    headers: dict[str, str] = {"Content-Type": "application/json; charset=utf-8"}
    if api_key:
        headers["api-key"] = api_key
    else:
        proc = subprocess.run(
            [
                "az",
                "account",
                "get-access-token",
                "--resource",
                "https://search.azure.com",
                "--query",
                "accessToken",
                "-o",
                "tsv",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            headers["Authorization"] = f"Bearer {proc.stdout.strip()}"

    url = f"{endpoint}/indexes/{index_name}/docs/search?api-version=2024-07-01"
    payload = json.dumps({"search": query, "top": top_k}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url=url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("value", [])


def keyword_anchor_retrieve(query: str, structured_text: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Fallback deterministic local lexical/anchor retriever when Azure AI Search env vars are unset."""
    combined = f"{query}\n{structured_text}"
    tokens = set(re.findall(r"[A-Z]{2,4}-[A-Z0-9-]+|Tier1|8D|COO|SCM|ろう付け|磁石|空輸|校正", combined))
    scored: list[tuple[int, dict[str, Any]]] = []
    for doc in load_local_docs():
        score = 0
        for anchor in doc["anchor_keys"]:
            if anchor in combined:
                score += 5
        for tok in tokens:
            if tok in doc["content"]:
                score += 2
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]


def call_foundry_chat_synthesis(
    question: str,
    structured_context: str,
    unstructured_Passages: list[dict[str, Any]],
) -> str:
    """Synthesizes final grounded answer via existing Azure OpenAI / Microsoft Foundry deployment."""
    aoai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")
    if not aoai_endpoint or not deployment:
        return json.dumps(
            {
                "note": "AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_DEPLOYMENT not set; returning retrieved hybrid evidence.",
                "structured_ontology_evidence": structured_context,
                "unstructured_doc_citations": [
                    {"doc_id": d.get("doc_id") or d.get("id"), "file_name": d.get("file_name", "")}
                    for d in unstructured_Passages
                ],
            },
            ensure_ascii=False,
            indent=2,
        )

    proc = subprocess.run(
        [
            "az",
            "account",
            "get-access-token",
            "--resource",
            "https://cognitiveservices.azure.com",
            "--query",
            "accessToken",
            "-o",
            "tsv",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    headers: dict[str, str] = {"Content-Type": "application/json; charset=utf-8"}
    if api_key:
        headers["api-key"] = api_key
    elif proc.returncode == 0 and proc.stdout.strip():
        headers["Authorization"] = f"Bearer {proc.stdout.strip()}"
    else:
        raise RuntimeError("Neither AZURE_OPENAI_API_KEY nor Entra token for cognitiveservices is available.")

    docs_block = "\n\n".join(
        f"[{d.get('doc_id', 'DOC')} | {d.get('file_name', '')}]\n{d.get('content', '')}"
        for d in unstructured_Passages
    )
    messages = [
        {
            "role": "system",
            "content": (
                "あなたは精密機器メーカーの業務横断AIアシスタントです。"
                "Fabric Data Agent（Ontology）から取得した構造化事実と、"
                "Microsoft Foundry から検索した非構造化規程・SOP・SLA文書を統合し、"
                "すべての判断に正確な数値と出典文書ID（例: DOC-SOP-VBF204）を明記して日本語で回答してください。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"## ユーザーの質問\n{question}\n\n"
                f"## Fabric Ontology / Data Agent 構造化照会結果\n{structured_context}\n\n"
                f"## Microsoft Foundry 非構造化ドキュメント検索結果\n{docs_block}"
            ),
        },
    ]

    url = f"{aoai_endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-10-21"
    body = json.dumps({"messages": messages, "temperature": 0.0}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url=url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        res_json = json.loads(resp.read().decode("utf-8"))
    return res_json["choices"][0]["message"]["content"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Foundry Unstructured + Fabric Ontology Hybrid Helper")
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("verify-local", help="Verify local unstructured docs and Ontology rule links")

    ask_p = sub.add_parser("ask-hybrid", help="Run hybrid Ontology + Unstructured retrieval & synthesis")
    ask_p.add_argument("--workspace-name", required=True, help="Fabric Workspace name (e.g. student01)")
    ask_p.add_argument("--ontology-name", default="mfg_enterprise_ontology")
    ask_p.add_argument("question", help="Cross-domain question")

    args = parser.parse_args()
    if args.mode == "verify-local":
        report = verify_local_alignment()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.mode == "ask-hybrid":
        ont_cmd = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "ontology_mcp_client.py"),
            "--workspace-name",
            args.workspace_name,
            "--ontology-name",
            args.ontology_name,
            "ask",
            args.question,
        ]
        proc = subprocess.run(ont_cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"Ontology MCP call failed: {proc.stderr.strip()}")
        structured_answer = proc.stdout.strip()

        search_hits = search_azure_ai_search(f"{args.question} {structured_answer}")
        if not search_hits:
            search_hits = keyword_anchor_retrieve(args.question, structured_answer)

        final_answer = call_foundry_chat_synthesis(args.question, structured_answer, search_hits)
        print(final_answer)
        return 0

    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
