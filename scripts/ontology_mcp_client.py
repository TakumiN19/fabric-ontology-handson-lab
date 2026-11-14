#!/usr/bin/env python3
"""Fabric Ontology V2 MCP Client (aligned with skills-for-fabric ontology-cli v0.3.22).

Follows mandatory ontology-cli rules:
  1. Sends `x-ms-fabric-skill: ontology-cli` header on every call to api.fabric.microsoft.com.
  2. Uses the V2 data-plane MCP endpoint:
     POST https://api.fabric.microsoft.com/v1/mcp/dataPlane/workspaces/{ws}/items/{ont}/ontologyEndpoint
  3. Performs the mandatory V2 gate (`tools/list` -> checks `ask_ontology` presence) before `tools/call`.
  4. Checks `result.isError` on HTTP 200 JSON-RPC responses and allows >=180s timeout.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any

FABRIC_API_HOST = "https://api.fabric.microsoft.com"
SKILL_HEADER_VALUE = "ontology-cli"


def get_fabric_access_token() -> str:
    cmd = [
        "az",
        "account",
        "get-access-token",
        "--resource",
        FABRIC_API_HOST,
        "--query",
        "accessToken",
        "-o",
        "tsv",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise RuntimeError(
            "Failed to acquire Fabric token via `az account get-access-token`. "
            "Sign in with delegated user credentials (`az login --use-device-code`). "
            f"Details: {proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def fabric_request(
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
    timeout_sec: int = 180,
) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json, text/event-stream",
        "x-ms-fabric-skill": SKILL_HEADER_VALUE,
    }
    body_bytes: bytes | None = None
    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
        body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(url=url, data=body_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            raw = resp.read().decode("utf-8")
            content_type = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} calling {url}: {err_body}") from exc

    if "text/event-stream" in content_type or raw.lstrip().startswith("event:") or "\ndata:" in raw:
        data_lines = [
            line[len("data:") :].strip()
            for line in raw.splitlines()
            if line.startswith("data:") and line[len("data:") :].strip()
        ]
        if not data_lines:
            raise RuntimeError(f"Empty SSE response from {url}: {raw}")
        return json.loads(data_lines[-1])
    return json.loads(raw) if raw.strip() else {}


def resolve_workspace_id(workspace_name: str, token: str) -> str:
    data = fabric_request("GET", f"{FABRIC_API_HOST}/v1/workspaces", token, timeout_sec=60)
    matches = [w for w in data.get("value", []) if w.get("displayName") == workspace_name]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly 1 workspace named '{workspace_name}', found {len(matches)}."
        )
    return matches[0]["id"]


def resolve_ontology_id(workspace_id: str, ontology_name: str, token: str) -> str:
    data = fabric_request(
        "GET",
        f"{FABRIC_API_HOST}/v1/workspaces/{workspace_id}/items?type=Ontology",
        token,
        timeout_sec=60,
    )
    matches = [i for i in data.get("value", []) if i.get("displayName") == ontology_name]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly 1 Ontology named '{ontology_name}' in workspace {workspace_id}, found {len(matches)}."
        )
    return matches[0]["id"]


def mcp_endpoint(workspace_id: str, ontology_id: str) -> str:
    return (
        f"{FABRIC_API_HOST}/v1/mcp/dataPlane/workspaces/{workspace_id}"
        f"/items/{ontology_id}/ontologyEndpoint"
    )


def verify_v2_gate(url: str, token: str) -> list[str]:
    resp = fabric_request(
        "POST",
        url,
        token,
        payload={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        timeout_sec=60,
    )
    tools = [t.get("name", "") for t in resp.get("result", {}).get("tools", [])]
    if "ask_ontology" not in tools:
        raise RuntimeError(
            f"Unsupported V1 Ontology detected (tools={tools}). "
            "`ask_ontology` is absent; V1 natural-language consumption is unsupported. "
            "Recreate or upgrade the Ontology in the V2 new experience."
        )
    return tools


def call_mcp_tool(
    url: str,
    token: str,
    tool_name: str,
    arguments: dict[str, Any],
    timeout_sec: int = 180,
) -> dict[str, Any]:
    resp = fabric_request(
        "POST",
        url,
        token,
        payload={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        },
        timeout_sec=timeout_sec,
    )
    if "error" in resp:
        raise RuntimeError(f"MCP JSON-RPC error: {json.dumps(resp['error'], ensure_ascii=False)}")
    result = resp.get("result", {})
    if result.get("isError"):
        raise RuntimeError(f"Ontology tool returned isError=true: {json.dumps(result, ensure_ascii=False)}")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fabric V2 Ontology MCP CLI helper")
    parser.add_argument("--workspace-id", help="Fabric Workspace GUID")
    parser.add_argument("--workspace-name", help="Fabric Workspace display name (if GUID omitted)")
    parser.add_argument("--ontology-id", help="Ontology item GUID")
    parser.add_argument(
        "--ontology-name",
        default="mfg_enterprise_ontology",
        help="Ontology display name (default: mfg_enterprise_ontology)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("tools", help="Run V2 support gate (tools/list)")

    ent_p = sub.add_parser("entities", help="Call list_ontology_entities")
    ent_p.add_argument("--entity-name", help="Optional exact entity name filter")

    rul_p = sub.add_parser("rules", help="Call list_ontology_rules")
    rul_p.add_argument("--entity-names", nargs="*", help="Optional entity name filters")

    ask_p = sub.add_parser("ask", help="Call ask_ontology with a natural-language question")
    ask_p.add_argument("question", help="Business question or grounded code generation prompt")
    ask_p.add_argument("--output", help="Optional JSON file path to save raw response")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    token = get_fabric_access_token()

    ws_id = args.workspace_id or (
        resolve_workspace_id(args.workspace_name, token) if args.workspace_name else None
    )
    if not ws_id:
        raise SystemExit("Provide either --workspace-id or --workspace-name.")

    ont_id = args.ontology_id or resolve_ontology_id(ws_id, args.ontology_name, token)
    url = mcp_endpoint(ws_id, ont_id)

    tools = verify_v2_gate(url, token)
    if args.command == "tools":
        print(json.dumps({"workspace_id": ws_id, "ontology_id": ont_id, "tools": tools}, indent=2))
        return 0

    if args.command == "entities":
        tool_args = {"entityName": args.entity_name} if args.entity_name else {}
        res = call_mcp_tool(url, token, "list_ontology_entities", tool_args)
    elif args.command == "rules":
        tool_args = {"entityNames": args.entity_names} if args.entity_names else {}
        res = call_mcp_tool(url, token, "list_ontology_rules", tool_args)
    elif args.command == "ask":
        res = call_mcp_tool(url, token, "ask_ontology", {"request": args.question})
    else:
        raise SystemExit(f"Unknown command: {args.command}")

    if getattr(args, "output", None):
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)

    for block in res.get("content", []):
        if block.get("type") == "text":
            print(block.get("text", ""))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
