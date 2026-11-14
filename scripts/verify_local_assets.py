#!/usr/bin/env python3
"""Validates all local datasets, unstructured docs, oracle math, and Ontology specs."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_csv(rel_path: str) -> list[dict[str, str]]:
    full = REPO_ROOT / rel_path
    if not full.is_file():
        raise AssertionError(f"Missing CSV file: {rel_path}")
    with full.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    oracle = json.loads((REPO_ROOT / "data" / "expected_oracle.json").read_text(encoding="utf-8"))
    blueprint = json.loads((REPO_ROOT / "ontology" / "design-blueprint.json").read_text(encoding="utf-8"))
    eval_suite = json.loads((REPO_ROOT / "ontology" / "evaluation_questions.json").read_text(encoding="utf-8"))

    table_paths = {
        "erp_customers": "data/erp/erp_customers.csv",
        "erp_suppliers": "data/erp/erp_suppliers.csv",
        "erp_materials": "data/erp/erp_materials.csv",
        "erp_products": "data/erp/erp_products.csv",
        "erp_bom": "data/erp/erp_bom.csv",
        "erp_sales_orders": "data/erp/erp_sales_orders.csv",
        "erp_purchase_orders": "data/erp/erp_purchase_orders.csv",
        "mes_production_lines": "data/mes/mes_production_lines.csv",
        "mes_equipment": "data/mes/mes_equipment.csv",
        "mes_material_lots": "data/mes/mes_material_lots.csv",
        "mes_work_orders": "data/mes/mes_work_orders.csv",
        "mes_quality_inspections": "data/mes/mes_quality_inspections.csv",
        "iot_sensors": "data/iot/iot_sensors.csv",
        "iot_telemetry": "data/iot/iot_telemetry.csv",
        "iot_equipment_alerts": "data/iot/iot_equipment_alerts.csv",
        "unstructured_doc_catalog": "data/unstructured_docs/doc_catalog.csv",
    }

    loaded: dict[str, list[dict[str, str]]] = {}
    for key, rel in table_paths.items():
        rows = load_csv(rel)
        loaded[key] = rows
        expected_n = oracle["row_counts"][key]
        if len(rows) != expected_n:
            raise AssertionError(f"Row count mismatch for {key}: got {len(rows)}, expected {expected_n}")
        # Ensure zero spaces/special chars in column names (Delta column mapping prevention)
        for col in rows[0].keys():
            if not col.replace("_", "").isalnum():
                raise AssertionError(f"Unsafe column name '{col}' in {rel}")

    # Verify JSONL telemetry matches CSV count
    jsonl_lines = (REPO_ROOT / "data/iot/iot_telemetry.jsonl").read_text(encoding="utf-8").strip().splitlines()
    if len(jsonl_lines) != oracle["row_counts"]["iot_telemetry"]:
        raise AssertionError("iot_telemetry.jsonl line count mismatch")

    # Verify all unstructured Markdown docs exist and are non-empty
    for doc_row in loaded["unstructured_doc_catalog"]:
        doc_path = REPO_ROOT / "data/unstructured_docs" / doc_row["file_name"]
        if not doc_path.is_file() or doc_path.stat().st_size < 300:
            raise AssertionError(f"Missing or truncated unstructured doc: {doc_path}")

    # Verify Ontology blueprint entity -> table & column mappings
    entities_by_qname = {e["qualified_name"]: e for e in blueprint["entity_types"]}
    if "erp#Order" not in entities_by_qname or "mes#Order" not in entities_by_qname:
        raise AssertionError("Blueprint must include disambiguated erp#Order and mes#Order")

    for ent in blueprint["entity_types"]:
        tbl = ent["source_table"]
        if tbl not in loaded:
            raise AssertionError(f"Entity {ent['qualified_name']} references unknown table {tbl}")
        cols = set(loaded[tbl][0].keys())
        if ent["key_column"] not in cols:
            raise AssertionError(f"Key column {ent['key_column']} missing in {tbl}")
        for prop_col in ent.get("property_metadata", {}).keys():
            if prop_col not in cols:
                raise AssertionError(f"Property metadata column {prop_col} missing in {tbl}")

    for rel in blueprint["relationships"]:
        src = entities_by_qname[rel["source"]]
        tgt = entities_by_qname[rel["target"]]
        if rel["source_column"] not in loaded[src["source_table"]][0]:
            raise AssertionError(f"Relationship {rel['name']} source_column invalid")
        if rel["target_column"] not in loaded[tgt["source_table"]][0]:
            raise AssertionError(f"Relationship {rel['name']} target_column invalid")

    if len(eval_suite["enrichment_before_after_suite"]) < 3 or len(eval_suite["graph_vs_tabular_suite"]) < 4:
        raise AssertionError("Evaluation suite incomplete")

    print("OK: All local ERP/MES/IoT datasets, unstructured docs, oracle math, and Ontology specs verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
