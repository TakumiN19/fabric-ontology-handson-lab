#!/usr/bin/env python3
"""Comprehensive integrity test suite for fabric-ontology-handson-lab."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_csv(rel_path: str) -> list[dict[str, str]]:
    with (REPO_ROOT / rel_path).open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class TestHandsonRepo(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required = [
            "README.md",
            ".gitignore",
            ".github/copilot-instructions.md",
            ".devcontainer/devcontainer.json",
            ".devcontainer/Dockerfile",
            ".devcontainer/scripts/versions.env",
            ".devcontainer/scripts/setup.sh",
            ".devcontainer/scripts/verify.sh",
            "data/expected_oracle.json",
            "data/unstructured_docs/doc_catalog.csv",
            "ontology/design-blueprint.json",
            "ontology/evaluation_questions.json",
            "ontology/v2_tmdl/database.tmdl",
            "ontology/v2_tmdl/model.tmdl",
            "ontology/v2_tmdl/entityRelationships.tmdl",
            "ontology/v2_tmdl/namespaces/erp.tmdl",
            "ontology/v2_tmdl/namespaces/mes.tmdl",
            "ontology/v2_tmdl/namespaces/iot.tmdl",
            "ontology/v2_tmdl/entities/erp#Order.tmdl",
            "ontology/v2_tmdl/entities/mes#Order.tmdl",
            "scripts/generate_handson_data.py",
            "scripts/ontology_mcp_client.py",
            "scripts/foundry_hybrid_agent.py",
            "scripts/verify_local_assets.py",
            "labs/fabric-portal-login.md",
            "labs/00-prerequisites.md",
            "labs/01-login-and-data-setup.md",
            "labs/02-ontology-design-consultation.md",
            "labs/03-create-base-ontology.md",
            "labs/04-namespaces-synonyms-metadata-rules.md",
            "labs/05-graph-engine-scenarios.md",
            "labs/06-data-agent-ontology-context.md",
            "labs/07-foundry-hybrid-unstructured.md",
            "labs/glossary.md",
            "labs/images/handson-architecture.svg",
            "labs/images/sub-ontology-namespaces.svg",
            "labs/images/graph-vs-tabular-decision.svg",
        ]
        for rel in required:
            self.assertTrue((REPO_ROOT / rel).exists(), f"Missing required file: {rel}")

    def test_markdown_relative_links_and_images_resolve(self) -> None:
        md_files = [REPO_ROOT / "README.md", *sorted((REPO_ROOT / "labs").glob("*.md"))]
        link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")

        for md_file in md_files:
            text = md_file.read_text(encoding="utf-8")
            for raw_target in link_pattern.findall(text):
                target = raw_target.strip()
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                path_part = target.split("#", 1)[0]
                if not path_part:
                    continue
                resolved = (md_file.parent / path_part).resolve()
                self.assertTrue(
                    resolved.exists(),
                    f"Broken relative link in {md_file.relative_to(REPO_ROOT)}: {target} -> {resolved}",
                )

    def test_svg_diagrams_are_valid_xml(self) -> None:
        svg_files = sorted((REPO_ROOT / "labs" / "images").glob("*.svg"))
        self.assertGreaterEqual(len(svg_files), 3)
        for svg_path in svg_files:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            self.assertTrue(root.tag.endswith("svg"), f"Invalid SVG root in {svg_path}")

    def test_shell_scripts_syntax(self) -> None:
        for sh_rel in [".devcontainer/scripts/setup.sh", ".devcontainer/scripts/verify.sh"]:
            res = subprocess.run(
                ["bash", "-n", str(REPO_ROOT / sh_rel)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0, f"bash -n failed for {sh_rel}: {res.stderr}")

    def test_devcontainer_matches_versions_env(self) -> None:
        devcontainer = json.loads((REPO_ROOT / ".devcontainer" / "devcontainer.json").read_text(encoding="utf-8"))
        versions: dict[str, str] = {}
        for line in (REPO_ROOT / ".devcontainer" / "scripts" / "versions.env").read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                versions[k.strip()] = v.strip()

        node_feat = devcontainer["features"]["ghcr.io/devcontainers/features/node:2.1.0"]
        az_feat = devcontainer["features"]["ghcr.io/devcontainers/features/azure-cli:1.3.0"]
        self.assertEqual(node_feat["version"], versions["NODE_VERSION"])
        self.assertEqual(node_feat["npmVersion"], versions["NPM_VERSION"])
        self.assertEqual(az_feat["version"], versions["AZURE_CLI_VERSION"])
        self.assertIn("setup.sh", devcontainer["postCreateCommand"])
        self.assertIn("verify.sh", devcontainer["postCreateCommand"])

    def test_blueprint_matches_csv_schemas_and_namespaces(self) -> None:
        blueprint = json.loads((REPO_ROOT / "ontology" / "design-blueprint.json").read_text(encoding="utf-8"))
        ns_prefixes = {ns["prefix"] for ns in blueprint["namespaces"]}
        self.assertEqual(ns_prefixes, {"erp", "mes", "iot"})

        table_headers: dict[str, list[str]] = {}
        for domain in ["erp", "mes", "iot"]:
            for csv_file in (REPO_ROOT / "data" / domain).glob("*.csv"):
                with csv_file.open("r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    table_headers[csv_file.stem] = next(reader)

        entity_map: dict[str, dict] = {}
        for ent in blueprint["entity_types"]:
            qname = ent["qualified_name"]
            entity_map[qname] = ent
            self.assertIn(ent["namespace"], ns_prefixes)
            src = ent["source_table"]
            self.assertIn(src, table_headers, f"Unknown source_table {src} for {qname}")
            headers = table_headers[src]
            self.assertIn(ent["key_column"], headers, f"Missing key_column {ent['key_column']} in {src}")
            for prop_col in ent.get("property_metadata", {}):
                self.assertIn(prop_col, headers, f"Missing property {prop_col} in {src}")

        # Verify same-named Order disambiguation across erp and mes namespaces
        self.assertIn("erp#Order", entity_map)
        self.assertIn("mes#Order", entity_map)
        self.assertEqual(entity_map["erp#Order"]["name"], "Order")
        self.assertEqual(entity_map["mes#Order"]["name"], "Order")

        # Verify relationship columns exist on source and target tables
        for rel in blueprint["relationships"]:
            src_ent = entity_map[rel["source"]]
            tgt_ent = entity_map[rel["target"]]
            self.assertIn(rel["source_column"], table_headers[src_ent["source_table"]])
            self.assertIn(rel["target_column"], table_headers[tgt_ent["source_table"]])

    def test_ground_truth_storyline_and_oracle_consistency(self) -> None:
        oracle = json.loads((REPO_ROOT / "data" / "expected_oracle.json").read_text(encoding="utf-8"))
        sales_orders = {r["order_id"]: r for r in load_csv("data/erp/erp_sales_orders.csv")}
        customers = {r["customer_id"]: r for r in load_csv("data/erp/erp_customers.csv")}
        work_orders = load_csv("data/mes/mes_work_orders.csv")
        lots = {r["material_lot_id"]: r for r in load_csv("data/mes/mes_material_lots.csv")}
        equipment = {r["equipment_id"]: r for r in load_csv("data/mes/mes_equipment.csv")}

        # 5-hop blast radius from EQ-VBF-204 & LOT-MAG-088
        vbf_wos = [w for w in work_orders if w["equipment_id"] == "EQ-VBF-204" and w["wo_status_code"] == "30"]
        self.assertEqual(sorted(w["order_id"] for w in vbf_wos), ["WO-2026-1007", "WO-2026-1012", "WO-2026-1019"])
        for w in vbf_wos:
            self.assertEqual(w["material_lot_id"], "LOT-MAG-088")

        impacted_sos = [sales_orders[w["sales_order_id"]] for w in vbf_wos]
        total_jpy = sum(int(so["order_amount_jpy"]) for so in impacted_sos)
        self.assertEqual(total_jpy, 99_700_000)
        self.assertEqual(sales_orders["SO-2026-015"]["order_status_code"], "2")  # Hidden risk in ERP!

        total_sla = sum(int(customers[so["customer_id"]]["sla_penalty_jpy_per_day"]) for so in impacted_sos)
        self.assertEqual(total_sla, 2_350_000)
        self.assertEqual(int(lots["LOT-MAG-088"]["moisture_ppm"]), 182)
        self.assertEqual(int(equipment["EQ-CNC-101"]["days_since_calibration"]), 95)

        # Verify oracle matches
        self.assertEqual(oracle["blast_radius_eq_vbf_204_and_lot_mag_088"]["total_impacted_order_amount_jpy"], 99_700_000)
        self.assertEqual(oracle["blast_radius_eq_vbf_204_and_lot_mag_088"]["total_daily_sla_penalty_jpy"], 2_350_000)
        self.assertEqual(oracle["tier1_calibration_violation_work_order_id"], "WO-2026-1025")

    def test_cli_scripts_and_telemetry_header_compliance(self) -> None:
        mcp_src = (REPO_ROOT / "scripts" / "ontology_mcp_client.py").read_text(encoding="utf-8")
        self.assertIn("x-ms-fabric-skill", mcp_src)
        self.assertIn('"ontology-cli"', mcp_src)
        self.assertIn("ask_ontology", mcp_src)

        for cmd in [
            [sys.executable, str(REPO_ROOT / "scripts" / "verify_local_assets.py")],
            [sys.executable, str(REPO_ROOT / "scripts" / "foundry_hybrid_agent.py"), "verify-local"],
            [sys.executable, str(REPO_ROOT / "scripts" / "ontology_mcp_client.py"), "--help"],
        ]:
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.assertEqual(res.returncode, 0, f"Command failed ({cmd}): {res.stderr}\n{res.stdout}")


if __name__ == "__main__":
    unittest.main()
