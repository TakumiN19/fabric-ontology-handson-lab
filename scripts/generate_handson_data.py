#!/usr/bin/env python3
"""Deterministic cross-domain dummy data generator for Fabric Ontology Hands-on Lab.

Generates interconnected datasets across 4 enterprise domains:
  1. ERP (data/erp/*.csv): Customers, Suppliers, Materials, Products, BOM, Sales Orders, Purchase Orders
  2. MES (data/mes/*.csv): Production Lines, Equipment, Material Lots, Work Orders, Quality Inspections
  3. IoT (data/iot/*.csv + .jsonl): Sensors, Time-series Telemetry, Equipment Alerts
  4. Unstructured Docs metadata catalog (data/unstructured_docs/doc_catalog.csv)
  5. Deterministic ground-truth oracle (data/expected_oracle.json)

Uses only the Python 3.12 standard library so zero external packages are required.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_erp_datasets() -> dict[str, tuple[list[str], list[dict[str, Any]]]]:
    customers = [
        {"customer_id": "CUS-001", "customer_name": "日本ロボティクスシステムズ株式会社", "industry": "IndustrialRobotics", "customer_tier": "Tier1", "region": "Chubu", "account_exec": "佐藤 健一", "sla_penalty_jpy_per_day": 800000, "requires_8d_hours": 48},
        {"customer_id": "CUS-002", "customer_name": "東海モビリティ電装株式会社", "industry": "AutomotiveEV", "customer_tier": "Tier1", "region": "Chubu", "account_exec": "鈴木 美咲", "sla_penalty_jpy_per_day": 650000, "requires_8d_hours": 48},
        {"customer_id": "CUS-003", "customer_name": "関西セミコンダクター装置株式会社", "industry": "SemiconductorEquip", "customer_tier": "Tier1", "region": "Kansai", "account_exec": "高橋 誠", "sla_penalty_jpy_per_day": 900000, "requires_8d_hours": 24},
        {"customer_id": "CUS-004", "customer_name": "首都圏メディカルロボ株式会社", "industry": "MedicalDevices", "customer_tier": "Tier1", "region": "Kanto", "account_exec": "田中 陽子", "sla_penalty_jpy_per_day": 700000, "requires_8d_hours": 48},
        {"customer_id": "CUS-005", "customer_name": "九州ファクトリーオートメーション株式会社", "industry": "FactoryAutomation", "customer_tier": "Tier2", "region": "Kyushu", "account_exec": "伊藤 翔太", "sla_penalty_jpy_per_day": 250000, "requires_8d_hours": 72},
        {"customer_id": "CUS-006", "customer_name": "北陸精密工作機械株式会社", "industry": "MachineTools", "customer_tier": "Tier2", "region": "Hokuriku", "account_exec": "佐藤 健一", "sla_penalty_jpy_per_day": 200000, "requires_8d_hours": 72},
        {"customer_id": "CUS-007", "customer_name": "東北アグリドローンシステムズ株式会社", "industry": "AutonomousSystems", "customer_tier": "Tier2", "region": "Tohoku", "account_exec": "渡辺 大輔", "sla_penalty_jpy_per_day": 150000, "requires_8d_hours": 96},
        {"customer_id": "CUS-008", "customer_name": "瀬戸内マテハンエンジニアリング株式会社", "industry": "LogisticsAutomation", "customer_tier": "Tier2", "region": "Chugoku", "account_exec": "高橋 誠", "sla_penalty_jpy_per_day": 180000, "requires_8d_hours": 72},
        {"customer_id": "CUS-009", "customer_name": "信越クリーン搬送テクノロジーズ株式会社", "industry": "SemiconductorEquip", "customer_tier": "Tier3", "region": "Chubu", "account_exec": "鈴木 美咲", "sla_penalty_jpy_per_day": 100000, "requires_8d_hours": 120},
        {"customer_id": "CUS-010", "customer_name": "相模原テストラボ機器株式会社", "industry": "TestingEquipment", "customer_tier": "Tier3", "region": "Kanto", "account_exec": "田中 陽子", "sla_penalty_jpy_per_day": 80000, "requires_8d_hours": 120},
    ]

    suppliers = [
        {"supplier_id": "SUP-001", "supplier_name": "名港精密ベアリング工業株式会社", "country": "JP", "supplier_tier": "Primary", "lead_time_days": 10, "quality_rating_score": 95, "is_qualified_backup": "false", "iso_cert_status": "ISO9001_IATF16949"},
        {"supplier_id": "SUP-002", "supplier_name": "京都ファインコイル電線株式会社", "country": "JP", "supplier_tier": "Primary", "lead_time_days": 8, "quality_rating_score": 93, "is_qualified_backup": "false", "iso_cert_status": "ISO9001"},
        {"supplier_id": "SUP-003", "supplier_name": "東海レアアース精工株式会社", "country": "JP", "supplier_tier": "Primary", "lead_time_days": 14, "quality_rating_score": 78, "is_qualified_backup": "false", "iso_cert_status": "ConditionalReview"},
        {"supplier_id": "SUP-004", "supplier_name": "武蔵野真空ブレージング合金株式会社", "country": "JP", "supplier_tier": "Primary", "lead_time_days": 12, "quality_rating_score": 91, "is_qualified_backup": "false", "iso_cert_status": "ISO9001_AS9100"},
        {"supplier_id": "SUP-005", "supplier_name": "浜松オプトエンコーダ株式会社", "country": "JP", "supplier_tier": "Primary", "lead_time_days": 9, "quality_rating_score": 97, "is_qualified_backup": "false", "iso_cert_status": "ISO9001_IATF16949"},
        {"supplier_id": "SUP-006", "supplier_name": "北九州アルミダイカスト精機株式会社", "country": "JP", "supplier_tier": "Primary", "lead_time_days": 7, "quality_rating_score": 90, "is_qualified_backup": "false", "iso_cert_status": "ISO9001"},
        {"supplier_id": "SUP-007", "supplier_name": "信州マグネットマテリアルズ株式会社", "country": "JP", "supplier_tier": "BackupQualified", "lead_time_days": 7, "quality_rating_score": 96, "is_qualified_backup": "true", "iso_cert_status": "ISO9001_IATF16949"},
        {"supplier_id": "SUP-008", "supplier_name": "神戸アドバンスドろう材株式会社", "country": "JP", "supplier_tier": "BackupQualified", "lead_time_days": 6, "quality_rating_score": 94, "is_qualified_backup": "true", "iso_cert_status": "ISO9001"},
    ]

    materials = [
        {"material_id": "MAT-BRG-01", "material_name": "セラミック転動体アンギュラ軸受", "material_category": "Bearing", "uom": "PCS", "standard_cost_jpy": 9800, "primary_supplier_id": "SUP-001", "backup_supplier_id": "SUP-001", "criticality_code": "HIGH", "max_moisture_ppm": 500},
        {"material_id": "MAT-COL-02", "material_name": "高占積率平角銅線ステータコイル", "material_category": "StatorCoil", "uom": "SET", "standard_cost_jpy": 14200, "primary_supplier_id": "SUP-002", "backup_supplier_id": "SUP-002", "criticality_code": "HIGH", "max_moisture_ppm": 300},
        {"material_id": "MAT-ENC-03", "material_name": "24bit光学式アブソリュートエンコーダ", "material_category": "SensorModule", "uom": "PCS", "standard_cost_jpy": 22000, "primary_supplier_id": "SUP-005", "backup_supplier_id": "SUP-005", "criticality_code": "CRITICAL", "max_moisture_ppm": 200},
        {"material_id": "MAT-MAG-04", "material_name": "高耐熱ネオジム焼結磁石ロータコア", "material_category": "RareEarthMagnet", "uom": "PCS", "standard_cost_jpy": 18500, "primary_supplier_id": "SUP-003", "backup_supplier_id": "SUP-007", "criticality_code": "CRITICAL", "max_moisture_ppm": 150},
        {"material_id": "MAT-BRZ-05", "material_name": "銀銅系真空ろう材リング", "material_category": "BrazingAlloy", "uom": "PCS", "standard_cost_jpy": 4200, "primary_supplier_id": "SUP-004", "backup_supplier_id": "SUP-008", "criticality_code": "CRITICAL", "max_moisture_ppm": 80},
        {"material_id": "MAT-HSG-06", "material_name": "高剛性アルミ合金中空ハウジング", "material_category": "Housing", "uom": "PCS", "standard_cost_jpy": 11600, "primary_supplier_id": "SUP-006", "backup_supplier_id": "SUP-006", "criticality_code": "MEDIUM", "max_moisture_ppm": 1000},
        {"material_id": "MAT-SHF-07", "material_name": "浸炭焼入れ中空スプラインシャフト", "material_category": "Shaft", "uom": "PCS", "standard_cost_jpy": 13400, "primary_supplier_id": "SUP-001", "backup_supplier_id": "SUP-001", "criticality_code": "HIGH", "max_moisture_ppm": 800},
        {"material_id": "MAT-PCB-08", "material_name": "耐ノイズ電流制御ドライバ基板", "material_category": "Electronics", "uom": "PCS", "standard_cost_jpy": 16900, "primary_supplier_id": "SUP-005", "backup_supplier_id": "SUP-005", "criticality_code": "HIGH", "max_moisture_ppm": 120},
        {"material_id": "MAT-SEL-09", "material_name": "クリーンルーム低発塵フッ素オイルシール", "material_category": "Seal", "uom": "SET", "standard_cost_jpy": 3100, "primary_supplier_id": "SUP-004", "backup_supplier_id": "SUP-008", "criticality_code": "MEDIUM", "max_moisture_ppm": 400},
        {"material_id": "MAT-GRM-10", "material_name": "波動歯車減速機フレックススプライン", "material_category": "GearSet", "uom": "SET", "standard_cost_jpy": 28500, "primary_supplier_id": "SUP-001", "backup_supplier_id": "SUP-001", "criticality_code": "CRITICAL", "max_moisture_ppm": 500},
        {"material_id": "MAT-INS-11", "material_name": "ポリイミド高耐熱スロット絶縁紙", "material_category": "Insulation", "uom": "SET", "standard_cost_jpy": 1900, "primary_supplier_id": "SUP-002", "backup_supplier_id": "SUP-002", "criticality_code": "MEDIUM", "max_moisture_ppm": 250},
        {"material_id": "MAT-THM-12", "material_name": "高熱伝導シリコーン放熱シート", "material_category": "ThermalInterface", "uom": "PCS", "standard_cost_jpy": 1400, "primary_supplier_id": "SUP-006", "backup_supplier_id": "SUP-006", "criticality_code": "LOW", "max_moisture_ppm": 600},
    ]

    products = [
        {"product_id": "PRD-ACT-900", "product_name": "高精度中空サーボアクチュエータ HA-900", "product_family": "ServoActuator", "rated_power_w": 1500, "standard_price_jpy": 480000, "standard_cost_jpy": 297600, "target_margin_pct": 38.0},
        {"product_id": "PRD-ACT-650", "product_name": "クリーンルーム用薄型アクチュエータ CA-650", "product_family": "CleanroomActuator", "rated_power_w": 750, "standard_price_jpy": 650000, "standard_cost_jpy": 396500, "target_margin_pct": 39.0},
        {"product_id": "PRD-ACT-400", "product_name": "小型協働ロボット関節アクチュエータ JA-400", "product_family": "ServoActuator", "rated_power_w": 400, "standard_price_jpy": 320000, "standard_cost_jpy": 204800, "target_margin_pct": 36.0},
        {"product_id": "PRD-LIN-320", "product_name": "高速リニアサーボモジュール LM-320", "product_family": "LinearModule", "rated_power_w": 800, "standard_price_jpy": 390000, "standard_cost_jpy": 253500, "target_margin_pct": 35.0},
        {"product_id": "PRD-LIN-500", "product_name": "高推力リニアステージモジュール LM-500", "product_family": "LinearModule", "rated_power_w": 1200, "standard_price_jpy": 540000, "standard_cost_jpy": 340200, "target_margin_pct": 37.0},
        {"product_id": "PRD-DDM-800", "product_name": "ダイレクトドライブ回転テーブル DD-800", "product_family": "DirectDrive", "rated_power_w": 2000, "standard_price_jpy": 720000, "standard_cost_jpy": 432000, "target_margin_pct": 40.0},
    ]

    bom = [
        {"bom_id": "BOM-001", "product_id": "PRD-ACT-900", "material_id": "MAT-MAG-04", "qty_per_unit": 1, "assembly_stage": "RotorBrazing", "is_critical_component": "true"},
        {"bom_id": "BOM-002", "product_id": "PRD-ACT-900", "material_id": "MAT-BRZ-05", "qty_per_unit": 2, "assembly_stage": "RotorBrazing", "is_critical_component": "true"},
        {"bom_id": "BOM-003", "product_id": "PRD-ACT-900", "material_id": "MAT-COL-02", "qty_per_unit": 1, "assembly_stage": "StatorWinding", "is_critical_component": "true"},
        {"bom_id": "BOM-004", "product_id": "PRD-ACT-900", "material_id": "MAT-GRM-10", "qty_per_unit": 1, "assembly_stage": "FinalAssembly", "is_critical_component": "true"},
        {"bom_id": "BOM-005", "product_id": "PRD-ACT-900", "material_id": "MAT-ENC-03", "qty_per_unit": 1, "assembly_stage": "FinalAssembly", "is_critical_component": "true"},
        {"bom_id": "BOM-006", "product_id": "PRD-ACT-650", "material_id": "MAT-MAG-04", "qty_per_unit": 1, "assembly_stage": "RotorBrazing", "is_critical_component": "true"},
        {"bom_id": "BOM-007", "product_id": "PRD-ACT-650", "material_id": "MAT-BRZ-05", "qty_per_unit": 2, "assembly_stage": "RotorBrazing", "is_critical_component": "true"},
        {"bom_id": "BOM-008", "product_id": "PRD-ACT-650", "material_id": "MAT-SEL-09", "qty_per_unit": 2, "assembly_stage": "CleanAssembly", "is_critical_component": "true"},
        {"bom_id": "BOM-009", "product_id": "PRD-ACT-650", "material_id": "MAT-ENC-03", "qty_per_unit": 1, "assembly_stage": "CleanAssembly", "is_critical_component": "true"},
        {"bom_id": "BOM-010", "product_id": "PRD-ACT-400", "material_id": "MAT-BRG-01", "qty_per_unit": 2, "assembly_stage": "RotorGrinding", "is_critical_component": "true"},
        {"bom_id": "BOM-011", "product_id": "PRD-ACT-400", "material_id": "MAT-COL-02", "qty_per_unit": 1, "assembly_stage": "StatorWinding", "is_critical_component": "true"},
        {"bom_id": "BOM-012", "product_id": "PRD-ACT-400", "material_id": "MAT-PCB-08", "qty_per_unit": 1, "assembly_stage": "FinalAssembly", "is_critical_component": "true"},
        {"bom_id": "BOM-013", "product_id": "PRD-LIN-320", "material_id": "MAT-COL-02", "qty_per_unit": 1, "assembly_stage": "StatorWinding", "is_critical_component": "true"},
        {"bom_id": "BOM-014", "product_id": "PRD-LIN-320", "material_id": "MAT-SHF-07", "qty_per_unit": 1, "assembly_stage": "RotorGrinding", "is_critical_component": "true"},
        {"bom_id": "BOM-015", "product_id": "PRD-LIN-500", "material_id": "MAT-SHF-07", "qty_per_unit": 1, "assembly_stage": "RotorGrinding", "is_critical_component": "true"},
        {"bom_id": "BOM-016", "product_id": "PRD-LIN-500", "material_id": "MAT-HSG-06", "qty_per_unit": 1, "assembly_stage": "FinalAssembly", "is_critical_component": "false"},
        {"bom_id": "BOM-017", "product_id": "PRD-DDM-800", "material_id": "MAT-BRG-01", "qty_per_unit": 2, "assembly_stage": "FinalAssembly", "is_critical_component": "true"},
        {"bom_id": "BOM-018", "product_id": "PRD-DDM-800", "material_id": "MAT-INS-11", "qty_per_unit": 2, "assembly_stage": "StatorWinding", "is_critical_component": "false"},
    ]

    # order_status_code: 0=Cancelled, 1=Confirmed, 2=InProduction, 3=AtRisk, 4=Shipped
    sales_orders = [
        {"order_id": "SO-2026-001", "customer_id": "CUS-001", "product_id": "PRD-ACT-400", "order_date": "2026-04-05", "promised_ship_date": "2026-05-08", "order_qty": 60, "unit_price_jpy": 320000, "order_amount_jpy": 19200000, "order_status_code": 4, "priority_code": "P2", "incoterms": "DAP"},
        {"order_id": "SO-2026-002", "customer_id": "CUS-005", "product_id": "PRD-LIN-320", "order_date": "2026-04-07", "promised_ship_date": "2026-05-10", "order_qty": 30, "unit_price_jpy": 390000, "order_amount_jpy": 11700000, "order_status_code": 4, "priority_code": "P3", "incoterms": "EXW"},
        {"order_id": "SO-2026-003", "customer_id": "CUS-004", "product_id": "PRD-ACT-650", "order_date": "2026-04-10", "promised_ship_date": "2026-05-12", "order_qty": 25, "unit_price_jpy": 650000, "order_amount_jpy": 16250000, "order_status_code": 4, "priority_code": "P1", "incoterms": "DAP"},
        {"order_id": "SO-2026-004", "customer_id": "CUS-001", "product_id": "PRD-ACT-900", "order_date": "2026-04-12", "promised_ship_date": "2026-05-18", "order_qty": 100, "unit_price_jpy": 480000, "order_amount_jpy": 48000000, "order_status_code": 3, "priority_code": "P1", "incoterms": "DAP"},
        {"order_id": "SO-2026-005", "customer_id": "CUS-006", "product_id": "PRD-DDM-800", "order_date": "2026-04-14", "promised_ship_date": "2026-05-20", "order_qty": 15, "unit_price_jpy": 720000, "order_amount_jpy": 10800000, "order_status_code": 2, "priority_code": "P2", "incoterms": "EXW"},
        {"order_id": "SO-2026-006", "customer_id": "CUS-008", "product_id": "PRD-LIN-500", "order_date": "2026-04-15", "promised_ship_date": "2026-05-21", "order_qty": 20, "unit_price_jpy": 540000, "order_amount_jpy": 10800000, "order_status_code": 2, "priority_code": "P3", "incoterms": "EXW"},
        {"order_id": "SO-2026-007", "customer_id": "CUS-002", "product_id": "PRD-ACT-400", "order_date": "2026-04-16", "promised_ship_date": "2026-05-11", "order_qty": 50, "unit_price_jpy": 320000, "order_amount_jpy": 16000000, "order_status_code": 4, "priority_code": "P2", "incoterms": "DAP"},
        {"order_id": "SO-2026-008", "customer_id": "CUS-007", "product_id": "PRD-ACT-400", "order_date": "2026-04-18", "promised_ship_date": "2026-05-24", "order_qty": 25, "unit_price_jpy": 320000, "order_amount_jpy": 8000000, "order_status_code": 1, "priority_code": "P3", "incoterms": "EXW"},
        {"order_id": "SO-2026-009", "customer_id": "CUS-002", "product_id": "PRD-ACT-650", "order_date": "2026-04-19", "promised_ship_date": "2026-05-19", "order_qty": 50, "unit_price_jpy": 650000, "order_amount_jpy": 32500000, "order_status_code": 3, "priority_code": "P1", "incoterms": "DAP"},
        {"order_id": "SO-2026-010", "customer_id": "CUS-009", "product_id": "PRD-LIN-320", "order_date": "2026-04-20", "promised_ship_date": "2026-05-25", "order_qty": 20, "unit_price_jpy": 390000, "order_amount_jpy": 7800000, "order_status_code": 2, "priority_code": "P3", "incoterms": "EXW"},
        {"order_id": "SO-2026-011", "customer_id": "CUS-010", "product_id": "PRD-DDM-800", "order_date": "2026-04-21", "promised_ship_date": "2026-05-26", "order_qty": 10, "unit_price_jpy": 720000, "order_amount_jpy": 7200000, "order_status_code": 0, "priority_code": "P3", "incoterms": "EXW"},
        {"order_id": "SO-2026-012", "customer_id": "CUS-004", "product_id": "PRD-ACT-400", "order_date": "2026-04-22", "promised_ship_date": "2026-05-23", "order_qty": 45, "unit_price_jpy": 320000, "order_amount_jpy": 14400000, "order_status_code": 2, "priority_code": "P1", "incoterms": "DAP"},
        {"order_id": "SO-2026-013", "customer_id": "CUS-003", "product_id": "PRD-DDM-800", "order_date": "2026-04-23", "promised_ship_date": "2026-05-13", "order_qty": 20, "unit_price_jpy": 720000, "order_amount_jpy": 14400000, "order_status_code": 4, "priority_code": "P1", "incoterms": "DAP"},
        {"order_id": "SO-2026-014", "customer_id": "CUS-006", "product_id": "PRD-LIN-500", "order_date": "2026-04-24", "promised_ship_date": "2026-05-27", "order_qty": 30, "unit_price_jpy": 540000, "order_amount_jpy": 16200000, "order_status_code": 2, "priority_code": "P2", "incoterms": "EXW"},
        # Hidden cross-domain risk: ERP still shows status 2 (InProduction), while MES WO-2026-1019 just hit QualityHold (30)!
        {"order_id": "SO-2026-015", "customer_id": "CUS-003", "product_id": "PRD-ACT-900", "order_date": "2026-04-25", "promised_ship_date": "2026-05-22", "order_qty": 40, "unit_price_jpy": 480000, "order_amount_jpy": 19200000, "order_status_code": 2, "priority_code": "P1", "incoterms": "DAP"},
        {"order_id": "SO-2026-016", "customer_id": "CUS-005", "product_id": "PRD-ACT-400", "order_date": "2026-04-26", "promised_ship_date": "2026-05-28", "order_qty": 35, "unit_price_jpy": 320000, "order_amount_jpy": 11200000, "order_status_code": 2, "priority_code": "P2", "incoterms": "EXW"},
        {"order_id": "SO-2026-017", "customer_id": "CUS-001", "product_id": "PRD-LIN-500", "order_date": "2026-04-28", "promised_ship_date": "2026-05-29", "order_qty": 30, "unit_price_jpy": 540000, "order_amount_jpy": 16200000, "order_status_code": 2, "priority_code": "P1", "incoterms": "DAP"},
        {"order_id": "SO-2026-018", "customer_id": "CUS-005", "product_id": "PRD-LIN-320", "order_date": "2026-05-01", "promised_ship_date": "2026-05-26", "order_qty": 40, "unit_price_jpy": 390000, "order_amount_jpy": 15600000, "order_status_code": 2, "priority_code": "P2", "incoterms": "EXW"},
        {"order_id": "SO-2026-019", "customer_id": "CUS-004", "product_id": "PRD-ACT-900", "order_date": "2026-05-02", "promised_ship_date": "2026-05-30", "order_qty": 30, "unit_price_jpy": 480000, "order_amount_jpy": 14400000, "order_status_code": 2, "priority_code": "P1", "incoterms": "DAP"},
        {"order_id": "SO-2026-020", "customer_id": "CUS-008", "product_id": "PRD-DDM-800", "order_date": "2026-05-03", "promised_ship_date": "2026-06-02", "order_qty": 15, "unit_price_jpy": 720000, "order_amount_jpy": 10800000, "order_status_code": 1, "priority_code": "P3", "incoterms": "EXW"},
        {"order_id": "SO-2026-021", "customer_id": "CUS-002", "product_id": "PRD-LIN-500", "order_date": "2026-05-04", "promised_ship_date": "2026-06-03", "order_qty": 25, "unit_price_jpy": 540000, "order_amount_jpy": 13500000, "order_status_code": 1, "priority_code": "P1", "incoterms": "DAP"},
        {"order_id": "SO-2026-022", "customer_id": "CUS-007", "product_id": "PRD-LIN-320", "order_date": "2026-05-05", "promised_ship_date": "2026-06-04", "order_qty": 20, "unit_price_jpy": 390000, "order_amount_jpy": 7800000, "order_status_code": 1, "priority_code": "P3", "incoterms": "EXW"},
        {"order_id": "SO-2026-023", "customer_id": "CUS-009", "product_id": "PRD-ACT-650", "order_date": "2026-05-06", "promised_ship_date": "2026-06-05", "order_qty": 15, "unit_price_jpy": 650000, "order_amount_jpy": 9750000, "order_status_code": 1, "priority_code": "P2", "incoterms": "EXW"},
        {"order_id": "SO-2026-024", "customer_id": "CUS-001", "product_id": "PRD-DDM-800", "order_date": "2026-05-07", "promised_ship_date": "2026-06-08", "order_qty": 20, "unit_price_jpy": 720000, "order_amount_jpy": 14400000, "order_status_code": 1, "priority_code": "P1", "incoterms": "DAP"},
    ]

    purchase_orders = [
        {"po_id": "PO-2026-301", "supplier_id": "SUP-001", "material_id": "MAT-BRG-01", "material_lot_id": "LOT-BRG-011", "order_date": "2026-04-10", "eta_date": "2026-04-20", "ordered_qty": 500, "po_amount_jpy": 4900000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-302", "supplier_id": "SUP-002", "material_id": "MAT-COL-02", "material_lot_id": "LOT-COL-021", "order_date": "2026-04-12", "eta_date": "2026-04-20", "ordered_qty": 400, "po_amount_jpy": 5680000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-303", "supplier_id": "SUP-003", "material_id": "MAT-MAG-04", "material_lot_id": "LOT-MAG-085", "order_date": "2026-04-05", "eta_date": "2026-04-19", "ordered_qty": 150, "po_amount_jpy": 2775000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-304", "supplier_id": "SUP-003", "material_id": "MAT-MAG-04", "material_lot_id": "LOT-MAG-088", "order_date": "2026-04-18", "eta_date": "2026-05-02", "ordered_qty": 240, "po_amount_jpy": 4440000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-305", "supplier_id": "SUP-004", "material_id": "MAT-BRZ-05", "material_lot_id": "LOT-BRZ-041", "order_date": "2026-04-18", "eta_date": "2026-04-30", "ordered_qty": 600, "po_amount_jpy": 2520000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-306", "supplier_id": "SUP-005", "material_id": "MAT-ENC-03", "material_lot_id": "LOT-ENC-051", "order_date": "2026-04-20", "eta_date": "2026-04-29", "ordered_qty": 350, "po_amount_jpy": 7700000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-307", "supplier_id": "SUP-006", "material_id": "MAT-HSG-06", "material_lot_id": "LOT-HSG-061", "order_date": "2026-04-21", "eta_date": "2026-04-28", "ordered_qty": 300, "po_amount_jpy": 3480000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-308", "supplier_id": "SUP-001", "material_id": "MAT-SHF-07", "material_lot_id": "LOT-SHF-071", "order_date": "2026-04-22", "eta_date": "2026-05-02", "ordered_qty": 280, "po_amount_jpy": 3752000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-309", "supplier_id": "SUP-005", "material_id": "MAT-PCB-08", "material_lot_id": "LOT-PCB-081", "order_date": "2026-04-23", "eta_date": "2026-05-02", "ordered_qty": 320, "po_amount_jpy": 5408000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-310", "supplier_id": "SUP-004", "material_id": "MAT-SEL-09", "material_lot_id": "LOT-SEL-092", "order_date": "2026-04-24", "eta_date": "2026-05-04", "ordered_qty": 400, "po_amount_jpy": 1240000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-311", "supplier_id": "SUP-001", "material_id": "MAT-GRM-10", "material_lot_id": "LOT-GRM-103", "order_date": "2026-04-25", "eta_date": "2026-05-05", "ordered_qty": 220, "po_amount_jpy": 6270000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-312", "supplier_id": "SUP-007", "material_id": "MAT-MAG-04", "material_lot_id": "LOT-MAG-091", "order_date": "2026-04-29", "eta_date": "2026-05-06", "ordered_qty": 120, "po_amount_jpy": 2292000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-313", "supplier_id": "SUP-002", "material_id": "MAT-INS-11", "material_lot_id": "LOT-INS-111", "order_date": "2026-05-01", "eta_date": "2026-05-09", "ordered_qty": 500, "po_amount_jpy": 950000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-314", "supplier_id": "SUP-006", "material_id": "MAT-THM-12", "material_lot_id": "LOT-THM-121", "order_date": "2026-05-02", "eta_date": "2026-05-09", "ordered_qty": 500, "po_amount_jpy": 700000, "po_status": "RECEIVED"},
        {"po_id": "PO-2026-315", "supplier_id": "SUP-007", "material_id": "MAT-MAG-04", "material_lot_id": "LOT-MAG-095", "order_date": "2026-05-12", "eta_date": "2026-05-19", "ordered_qty": 200, "po_amount_jpy": 3820000, "po_status": "IN_TRANSIT"},
        {"po_id": "PO-2026-316", "supplier_id": "SUP-008", "material_id": "MAT-BRZ-05", "material_lot_id": "LOT-BRZ-049", "order_date": "2026-05-12", "eta_date": "2026-05-18", "ordered_qty": 300, "po_amount_jpy": 1290000, "po_status": "IN_TRANSIT"},
    ]

    return {
        "erp_customers": (list(customers[0].keys()), customers),
        "erp_suppliers": (list(suppliers[0].keys()), suppliers),
        "erp_materials": (list(materials[0].keys()), materials),
        "erp_products": (list(products[0].keys()), products),
        "erp_bom": (list(bom[0].keys()), bom),
        "erp_sales_orders": (list(sales_orders[0].keys()), sales_orders),
        "erp_purchase_orders": (list(purchase_orders[0].keys()), purchase_orders),
    }


def build_mes_datasets() -> dict[str, tuple[list[str], list[dict[str, Any]]]]:
    lines = [
        {"line_id": "LINE-NGO-01", "plant_id": "PLT-NGO", "plant_name": "名古屋第1工場", "line_name": "名古屋 精密研削・巻線第1ライン", "process_category": "MachiningAndWinding", "oee_target_pct": 86.0},
        {"line_id": "LINE-NGO-02", "plant_id": "PLT-NGO", "plant_name": "名古屋第1工場", "line_name": "名古屋 真空接合・サーボ組立第2ライン", "process_category": "BrazingAndAssembly", "oee_target_pct": 85.0},
        {"line_id": "LINE-HMM-01", "plant_id": "PLT-HMM", "plant_name": "浜松精密工場", "line_name": "浜松 ロータ精密研削第1ライン", "process_category": "PrecisionGrinding", "oee_target_pct": 88.0},
        {"line_id": "LINE-HMM-02", "plant_id": "PLT-HMM", "plant_name": "浜松精密工場", "line_name": "浜松 真空ろう付け・クリーン組立第2ライン", "process_category": "BrazingAndCleanroom", "oee_target_pct": 87.0},
        {"line_id": "LINE-KKJ-01", "plant_id": "PLT-KKJ", "plant_name": "北九州工場", "line_name": "北九州 リニアモジュール加工第1ライン", "process_category": "LinearMachining", "oee_target_pct": 84.0},
        {"line_id": "LINE-KKJ-02", "plant_id": "PLT-KKJ", "plant_name": "北九州工場", "line_name": "北九州 ダイレクトドライブ組立第2ライン", "process_category": "HeavyAssembly", "oee_target_pct": 85.0},
    ]

    # Reference date in scenario: 2026-05-14
    # operating_state_code: 1=NormalRunning, 2=DegradedWarning, 3=MaintenanceHold
    equipment = [
        {"equipment_id": "EQ-CNC-101", "equipment_name": "5軸精密ロータ研削盤 CNC-101", "equipment_type": "CNCGrinder", "line_id": "LINE-HMM-01", "vendor_name": "JTEKT Precision", "install_date": "2023-06-15", "last_calibration_date": "2026-02-08", "calibration_cycle_days": 90, "days_since_calibration": 95, "operating_state_code": 2},
        {"equipment_id": "EQ-CNC-102", "equipment_name": "5軸精密ロータ研削盤 CNC-102", "equipment_type": "CNCGrinder", "line_id": "LINE-NGO-01", "vendor_name": "JTEKT Precision", "install_date": "2024-01-20", "last_calibration_date": "2026-04-02", "calibration_cycle_days": 90, "days_since_calibration": 42, "operating_state_code": 1},
        {"equipment_id": "EQ-CNC-103", "equipment_name": "リニアシャフト研削盤 CNC-103", "equipment_type": "CNCGrinder", "line_id": "LINE-KKJ-01", "vendor_name": "Okuma", "install_date": "2023-09-10", "last_calibration_date": "2026-03-25", "calibration_cycle_days": 90, "days_since_calibration": 50, "operating_state_code": 1},
        {"equipment_id": "EQ-VBF-204", "equipment_name": "第2真空ろう付け炉 VBF-204", "equipment_type": "VacuumBrazingFurnace", "line_id": "LINE-HMM-02", "vendor_name": "Ulvac Thermal", "install_date": "2022-11-01", "last_calibration_date": "2026-01-25", "calibration_cycle_days": 90, "days_since_calibration": 109, "operating_state_code": 3},
        {"equipment_id": "EQ-VBF-205", "equipment_name": "第3真空ろう付け炉 VBF-205", "equipment_type": "VacuumBrazingFurnace", "line_id": "LINE-NGO-02", "vendor_name": "Ulvac Thermal", "install_date": "2024-04-12", "last_calibration_date": "2026-04-20", "calibration_cycle_days": 90, "days_since_calibration": 24, "operating_state_code": 1},
        {"equipment_id": "EQ-WND-301", "equipment_name": "高速自動平角巻線機 WND-301", "equipment_type": "CoilWinder", "line_id": "LINE-NGO-01", "vendor_name": "Nittoku", "install_date": "2023-05-18", "last_calibration_date": "2026-04-10", "calibration_cycle_days": 120, "days_since_calibration": 34, "operating_state_code": 1},
        {"equipment_id": "EQ-WND-302", "equipment_name": "高占積率自動巻線機 WND-302", "equipment_type": "CoilWinder", "line_id": "LINE-HMM-01", "vendor_name": "Nittoku", "install_date": "2023-08-22", "last_calibration_date": "2026-03-30", "calibration_cycle_days": 120, "days_since_calibration": 45, "operating_state_code": 1},
        {"equipment_id": "EQ-WND-303", "equipment_name": "大型ステータ巻線機 WND-303", "equipment_type": "CoilWinder", "line_id": "LINE-KKJ-02", "vendor_name": "Nittoku", "install_date": "2022-12-05", "last_calibration_date": "2026-03-15", "calibration_cycle_days": 120, "days_since_calibration": 60, "operating_state_code": 1},
        {"equipment_id": "EQ-ASM-401", "equipment_name": "クリーンルーム自動圧入セル ASM-401", "equipment_type": "CleanAssemblyCell", "line_id": "LINE-HMM-02", "vendor_name": "Fanuc Integration", "install_date": "2024-02-14", "last_calibration_date": "2026-04-15", "calibration_cycle_days": 90, "days_since_calibration": 29, "operating_state_code": 1},
        {"equipment_id": "EQ-ASM-402", "equipment_name": "サーボ精密組立セル ASM-402", "equipment_type": "ServoAssemblyCell", "line_id": "LINE-NGO-02", "vendor_name": "Fanuc Integration", "install_date": "2024-03-01", "last_calibration_date": "2026-04-18", "calibration_cycle_days": 90, "days_since_calibration": 26, "operating_state_code": 1},
        {"equipment_id": "EQ-ASM-403", "equipment_name": "リニアステージ組立セル ASM-403", "equipment_type": "LinearAssemblyCell", "line_id": "LINE-KKJ-01", "vendor_name": "Yaskawa Integration", "install_date": "2023-10-19", "last_calibration_date": "2026-04-05", "calibration_cycle_days": 90, "days_since_calibration": 39, "operating_state_code": 1},
        {"equipment_id": "EQ-ASM-404", "equipment_name": "ダイレクトドライブ組立セル ASM-404", "equipment_type": "HeavyAssemblyCell", "line_id": "LINE-KKJ-02", "vendor_name": "Yaskawa Integration", "install_date": "2023-11-30", "last_calibration_date": "2026-04-08", "calibration_cycle_days": 90, "days_since_calibration": 36, "operating_state_code": 1},
        {"equipment_id": "EQ-TST-501", "equipment_name": "トルクリップル・絶縁総合検査装置 TST-501", "equipment_type": "EndOfLineTester", "line_id": "LINE-HMM-02", "vendor_name": "HIOKI Custom", "install_date": "2024-01-10", "last_calibration_date": "2026-04-28", "calibration_cycle_days": 60, "days_since_calibration": 16, "operating_state_code": 1},
        {"equipment_id": "EQ-TST-502", "equipment_name": "サーボ総合特性検査装置 TST-502", "equipment_type": "EndOfLineTester", "line_id": "LINE-NGO-02", "vendor_name": "HIOKI Custom", "install_date": "2024-04-15", "last_calibration_date": "2026-05-01", "calibration_cycle_days": 60, "days_since_calibration": 13, "operating_state_code": 1},
        {"equipment_id": "EQ-TST-503", "equipment_name": "高推力負荷試験ベンチ TST-503", "equipment_type": "EndOfLineTester", "line_id": "LINE-KKJ-02", "vendor_name": "Ono Sokki", "install_date": "2023-07-07", "last_calibration_date": "2026-04-22", "calibration_cycle_days": 60, "days_since_calibration": 22, "operating_state_code": 1},
    ]

    material_lots = [
        {"material_lot_id": "LOT-BRG-011", "material_id": "MAT-BRG-01", "supplier_id": "SUP-001", "received_date": "2026-04-20", "lot_qty": 500, "moisture_ppm": 95, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-COL-021", "material_id": "MAT-COL-02", "supplier_id": "SUP-002", "received_date": "2026-04-20", "lot_qty": 400, "moisture_ppm": 110, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-MAG-085", "material_id": "MAT-MAG-04", "supplier_id": "SUP-003", "received_date": "2026-04-19", "lot_qty": 150, "moisture_ppm": 118, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-MAG-088", "material_id": "MAT-MAG-04", "supplier_id": "SUP-003", "received_date": "2026-05-02", "lot_qty": 240, "moisture_ppm": 182, "lot_qc_status": "QUARANTINE_SUSPECT"},
        {"material_lot_id": "LOT-MAG-091", "material_id": "MAT-MAG-04", "supplier_id": "SUP-007", "received_date": "2026-05-06", "lot_qty": 120, "moisture_ppm": 42, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-MAG-095", "material_id": "MAT-MAG-04", "supplier_id": "SUP-007", "received_date": "2026-05-19", "lot_qty": 200, "moisture_ppm": 38, "lot_qc_status": "IN_TRANSIT"},
        {"material_lot_id": "LOT-BRZ-041", "material_id": "MAT-BRZ-05", "supplier_id": "SUP-004", "received_date": "2026-04-30", "lot_qty": 600, "moisture_ppm": 45, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-BRZ-049", "material_id": "MAT-BRZ-05", "supplier_id": "SUP-008", "received_date": "2026-05-18", "lot_qty": 300, "moisture_ppm": 35, "lot_qc_status": "IN_TRANSIT"},
        {"material_lot_id": "LOT-ENC-051", "material_id": "MAT-ENC-03", "supplier_id": "SUP-005", "received_date": "2026-04-29", "lot_qty": 350, "moisture_ppm": 65, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-HSG-061", "material_id": "MAT-HSG-06", "supplier_id": "SUP-006", "received_date": "2026-04-28", "lot_qty": 300, "moisture_ppm": 210, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-SHF-071", "material_id": "MAT-SHF-07", "supplier_id": "SUP-001", "received_date": "2026-05-02", "lot_qty": 280, "moisture_ppm": 180, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-PCB-081", "material_id": "MAT-PCB-08", "supplier_id": "SUP-005", "received_date": "2026-05-02", "lot_qty": 320, "moisture_ppm": 55, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-SEL-092", "material_id": "MAT-SEL-09", "supplier_id": "SUP-004", "received_date": "2026-05-04", "lot_qty": 400, "moisture_ppm": 120, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-GRM-103", "material_id": "MAT-GRM-10", "supplier_id": "SUP-001", "received_date": "2026-05-05", "lot_qty": 220, "moisture_ppm": 140, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-INS-111", "material_id": "MAT-INS-11", "supplier_id": "SUP-002", "received_date": "2026-05-09", "lot_qty": 500, "moisture_ppm": 90, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-THM-121", "material_id": "MAT-THM-12", "supplier_id": "SUP-006", "received_date": "2026-05-09", "lot_qty": 500, "moisture_ppm": 160, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-BRG-014", "material_id": "MAT-BRG-01", "supplier_id": "SUP-001", "received_date": "2026-05-08", "lot_qty": 300, "moisture_ppm": 88, "lot_qc_status": "RELEASED"},
        {"material_lot_id": "LOT-COL-025", "material_id": "MAT-COL-02", "supplier_id": "SUP-002", "received_date": "2026-05-08", "lot_qty": 300, "moisture_ppm": 102, "lot_qc_status": "RELEASED"},
    ]

    # Note: Primary key is intentionally named order_id (WO-2026-1001..1030) to demonstrate
    # same-named concept disambiguation via Namespaces: erp#Order vs mes#Order!
    # wo_status_code: 10=Queued, 20=Running, 30=QualityHold, 40=Completed
    work_orders = [
        {"order_id": "WO-2026-1001", "sales_order_id": "SO-2026-001", "product_id": "PRD-ACT-400", "line_id": "LINE-NGO-01", "equipment_id": "EQ-CNC-102", "material_lot_id": "LOT-BRG-011", "planned_qty": 60, "good_qty": 60, "scrap_qty": 0, "scheduled_start": "2026-05-01", "scheduled_end": "2026-05-06", "wo_status_code": 40},
        {"order_id": "WO-2026-1002", "sales_order_id": "SO-2026-002", "product_id": "PRD-LIN-320", "line_id": "LINE-KKJ-01", "equipment_id": "EQ-CNC-103", "material_lot_id": "LOT-SHF-071", "planned_qty": 30, "good_qty": 30, "scrap_qty": 1, "scheduled_start": "2026-05-02", "scheduled_end": "2026-05-08", "wo_status_code": 40},
        {"order_id": "WO-2026-1003", "sales_order_id": "SO-2026-003", "product_id": "PRD-ACT-650", "line_id": "LINE-HMM-02", "equipment_id": "EQ-ASM-401", "material_lot_id": "LOT-MAG-085", "planned_qty": 25, "good_qty": 25, "scrap_qty": 0, "scheduled_start": "2026-05-03", "scheduled_end": "2026-05-10", "wo_status_code": 40},
        {"order_id": "WO-2026-1004", "sales_order_id": "SO-2026-007", "product_id": "PRD-ACT-400", "line_id": "LINE-NGO-01", "equipment_id": "EQ-WND-301", "material_lot_id": "LOT-COL-021", "planned_qty": 50, "good_qty": 50, "scrap_qty": 1, "scheduled_start": "2026-05-04", "scheduled_end": "2026-05-09", "wo_status_code": 40},
        {"order_id": "WO-2026-1005", "sales_order_id": "SO-2026-013", "product_id": "PRD-DDM-800", "line_id": "LINE-KKJ-02", "equipment_id": "EQ-ASM-404", "material_lot_id": "LOT-BRG-011", "planned_qty": 20, "good_qty": 20, "scrap_qty": 0, "scheduled_start": "2026-05-05", "scheduled_end": "2026-05-11", "wo_status_code": 40},
        {"order_id": "WO-2026-1006", "sales_order_id": "SO-2026-005", "product_id": "PRD-DDM-800", "line_id": "LINE-KKJ-02", "equipment_id": "EQ-WND-303", "material_lot_id": "LOT-INS-111", "planned_qty": 15, "good_qty": 10, "scrap_qty": 0, "scheduled_start": "2026-05-11", "scheduled_end": "2026-05-17", "wo_status_code": 20},
        # Impacted #1: CUS-001 SO-2026-004 (¥48,000,000) -> EQ-VBF-204 + LOT-MAG-088 -> QualityHold (30)
        {"order_id": "WO-2026-1007", "sales_order_id": "SO-2026-004", "product_id": "PRD-ACT-900", "line_id": "LINE-HMM-02", "equipment_id": "EQ-VBF-204", "material_lot_id": "LOT-MAG-088", "planned_qty": 60, "good_qty": 38, "scrap_qty": 12, "scheduled_start": "2026-05-11", "scheduled_end": "2026-05-15", "wo_status_code": 30},
        {"order_id": "WO-2026-1008", "sales_order_id": "SO-2026-004", "product_id": "PRD-ACT-900", "line_id": "LINE-NGO-02", "equipment_id": "EQ-VBF-205", "material_lot_id": "LOT-MAG-091", "planned_qty": 40, "good_qty": 32, "scrap_qty": 0, "scheduled_start": "2026-05-12", "scheduled_end": "2026-05-16", "wo_status_code": 20},
        {"order_id": "WO-2026-1009", "sales_order_id": "SO-2026-006", "product_id": "PRD-LIN-500", "line_id": "LINE-KKJ-01", "equipment_id": "EQ-ASM-403", "material_lot_id": "LOT-HSG-061", "planned_qty": 20, "good_qty": 14, "scrap_qty": 0, "scheduled_start": "2026-05-11", "scheduled_end": "2026-05-18", "wo_status_code": 20},
        {"order_id": "WO-2026-1010", "sales_order_id": "SO-2026-010", "product_id": "PRD-LIN-320", "line_id": "LINE-KKJ-01", "equipment_id": "EQ-CNC-103", "material_lot_id": "LOT-SHF-071", "planned_qty": 20, "good_qty": 12, "scrap_qty": 0, "scheduled_start": "2026-05-12", "scheduled_end": "2026-05-20", "wo_status_code": 20},
        {"order_id": "WO-2026-1011", "sales_order_id": "SO-2026-012", "product_id": "PRD-ACT-400", "line_id": "LINE-NGO-01", "equipment_id": "EQ-CNC-102", "material_lot_id": "LOT-PCB-081", "planned_qty": 45, "good_qty": 28, "scrap_qty": 1, "scheduled_start": "2026-05-12", "scheduled_end": "2026-05-19", "wo_status_code": 20},
        # Impacted #2: CUS-002 SO-2026-009 (¥32,500,000) -> EQ-VBF-204 + LOT-MAG-088 -> QualityHold (30)
        {"order_id": "WO-2026-1012", "sales_order_id": "SO-2026-009", "product_id": "PRD-ACT-650", "line_id": "LINE-HMM-02", "equipment_id": "EQ-VBF-204", "material_lot_id": "LOT-MAG-088", "planned_qty": 50, "good_qty": 28, "scrap_qty": 9, "scheduled_start": "2026-05-12", "scheduled_end": "2026-05-16", "wo_status_code": 30},
        {"order_id": "WO-2026-1013", "sales_order_id": "SO-2026-014", "product_id": "PRD-LIN-500", "line_id": "LINE-KKJ-01", "equipment_id": "EQ-ASM-403", "material_lot_id": "LOT-SHF-071", "planned_qty": 30, "good_qty": 15, "scrap_qty": 0, "scheduled_start": "2026-05-13", "scheduled_end": "2026-05-23", "wo_status_code": 20},
        {"order_id": "WO-2026-1014", "sales_order_id": "SO-2026-016", "product_id": "PRD-ACT-400", "line_id": "LINE-NGO-01", "equipment_id": "EQ-WND-301", "material_lot_id": "LOT-COL-025", "planned_qty": 35, "good_qty": 18, "scrap_qty": 0, "scheduled_start": "2026-05-13", "scheduled_end": "2026-05-24", "wo_status_code": 20},
        {"order_id": "WO-2026-1015", "sales_order_id": "SO-2026-017", "product_id": "PRD-LIN-500", "line_id": "LINE-KKJ-01", "equipment_id": "EQ-CNC-103", "material_lot_id": "LOT-HSG-061", "planned_qty": 30, "good_qty": 10, "scrap_qty": 0, "scheduled_start": "2026-05-13", "scheduled_end": "2026-05-25", "wo_status_code": 20},
        {"order_id": "WO-2026-1016", "sales_order_id": "SO-2026-008", "product_id": "PRD-ACT-400", "line_id": "LINE-HMM-01", "equipment_id": "EQ-WND-302", "material_lot_id": "LOT-COL-021", "planned_qty": 25, "good_qty": 0, "scrap_qty": 0, "scheduled_start": "2026-05-16", "scheduled_end": "2026-05-21", "wo_status_code": 10},
        {"order_id": "WO-2026-1017", "sales_order_id": "SO-2026-019", "product_id": "PRD-ACT-900", "line_id": "LINE-NGO-02", "equipment_id": "EQ-VBF-205", "material_lot_id": "LOT-MAG-091", "planned_qty": 30, "good_qty": 12, "scrap_qty": 0, "scheduled_start": "2026-05-13", "scheduled_end": "2026-05-26", "wo_status_code": 20},
        {"order_id": "WO-2026-1018", "sales_order_id": "SO-2026-019", "product_id": "PRD-ACT-900", "line_id": "LINE-NGO-02", "equipment_id": "EQ-ASM-402", "material_lot_id": "LOT-GRM-103", "planned_qty": 30, "good_qty": 0, "scrap_qty": 0, "scheduled_start": "2026-05-20", "scheduled_end": "2026-05-27", "wo_status_code": 10},
        # Impacted #3 (Hidden risk in ERP!): CUS-003 SO-2026-015 (¥19,200,000) -> EQ-VBF-204 + LOT-MAG-088 -> QualityHold (30)
        {"order_id": "WO-2026-1019", "sales_order_id": "SO-2026-015", "product_id": "PRD-ACT-900", "line_id": "LINE-HMM-02", "equipment_id": "EQ-VBF-204", "material_lot_id": "LOT-MAG-088", "planned_qty": 40, "good_qty": 15, "scrap_qty": 7, "scheduled_start": "2026-05-13", "scheduled_end": "2026-05-18", "wo_status_code": 30},
        {"order_id": "WO-2026-1020", "sales_order_id": "SO-2026-015", "product_id": "PRD-ACT-900", "line_id": "LINE-HMM-02", "equipment_id": "EQ-ASM-401", "material_lot_id": "LOT-ENC-051", "planned_qty": 40, "good_qty": 0, "scrap_qty": 0, "scheduled_start": "2026-05-17", "scheduled_end": "2026-05-20", "wo_status_code": 10},
        # Calibration rule violation check: EQ-CNC-101 (days_since_calibration=95 > 90) running WO-2026-1021 (Tier2 CUS-005)
        # AND queued for WO-2026-1025 (Tier1 CUS-001 SO-2026-024 -> violates CalibrationOverdueGuardrail!)
        {"order_id": "WO-2026-1021", "sales_order_id": "SO-2026-018", "product_id": "PRD-LIN-320", "line_id": "LINE-HMM-01", "equipment_id": "EQ-CNC-101", "material_lot_id": "LOT-SHF-071", "planned_qty": 40, "good_qty": 19, "scrap_qty": 3, "scheduled_start": "2026-05-13", "scheduled_end": "2026-05-22", "wo_status_code": 20},
        {"order_id": "WO-2026-1022", "sales_order_id": "SO-2026-020", "product_id": "PRD-DDM-800", "line_id": "LINE-KKJ-02", "equipment_id": "EQ-ASM-404", "material_lot_id": "LOT-BRG-014", "planned_qty": 15, "good_qty": 0, "scrap_qty": 0, "scheduled_start": "2026-05-18", "scheduled_end": "2026-05-29", "wo_status_code": 10},
        {"order_id": "WO-2026-1023", "sales_order_id": "SO-2026-021", "product_id": "PRD-LIN-500", "line_id": "LINE-KKJ-01", "equipment_id": "EQ-ASM-403", "material_lot_id": "LOT-SHF-071", "planned_qty": 25, "good_qty": 0, "scrap_qty": 0, "scheduled_start": "2026-05-19", "scheduled_end": "2026-05-30", "wo_status_code": 10},
        {"order_id": "WO-2026-1024", "sales_order_id": "SO-2026-022", "product_id": "PRD-LIN-320", "line_id": "LINE-KKJ-01", "equipment_id": "EQ-CNC-103", "material_lot_id": "LOT-COL-025", "planned_qty": 20, "good_qty": 0, "scrap_qty": 0, "scheduled_start": "2026-05-20", "scheduled_end": "2026-05-31", "wo_status_code": 10},
        {"order_id": "WO-2026-1025", "sales_order_id": "SO-2026-024", "product_id": "PRD-DDM-800", "line_id": "LINE-HMM-01", "equipment_id": "EQ-CNC-101", "material_lot_id": "LOT-BRG-014", "planned_qty": 20, "good_qty": 0, "scrap_qty": 0, "scheduled_start": "2026-05-22", "scheduled_end": "2026-06-03", "wo_status_code": 10},
        {"order_id": "WO-2026-1026", "sales_order_id": "SO-2026-023", "product_id": "PRD-ACT-650", "line_id": "LINE-NGO-02", "equipment_id": "EQ-VBF-205", "material_lot_id": "LOT-MAG-091", "planned_qty": 15, "good_qty": 0, "scrap_qty": 0, "scheduled_start": "2026-05-21", "scheduled_end": "2026-06-01", "wo_status_code": 10},
        {"order_id": "WO-2026-1027", "sales_order_id": "SO-2026-012", "product_id": "PRD-ACT-400", "line_id": "LINE-NGO-02", "equipment_id": "EQ-ASM-402", "material_lot_id": "LOT-BRG-014", "planned_qty": 45, "good_qty": 0, "scrap_qty": 0, "scheduled_start": "2026-05-19", "scheduled_end": "2026-05-22", "wo_status_code": 10},
        {"order_id": "WO-2026-1028", "sales_order_id": "SO-2026-004", "product_id": "PRD-ACT-900", "line_id": "LINE-NGO-02", "equipment_id": "EQ-ASM-402", "material_lot_id": "LOT-ENC-051", "planned_qty": 40, "good_qty": 25, "scrap_qty": 0, "scheduled_start": "2026-05-13", "scheduled_end": "2026-05-17", "wo_status_code": 20},
        {"order_id": "WO-2026-1029", "sales_order_id": "SO-2026-009", "product_id": "PRD-ACT-650", "line_id": "LINE-HMM-02", "equipment_id": "EQ-ASM-401", "material_lot_id": "LOT-SEL-092", "planned_qty": 50, "good_qty": 0, "scrap_qty": 0, "scheduled_start": "2026-05-16", "scheduled_end": "2026-05-18", "wo_status_code": 10},
        {"order_id": "WO-2026-1030", "sales_order_id": "SO-2026-017", "product_id": "PRD-LIN-500", "line_id": "LINE-KKJ-01", "equipment_id": "EQ-ASM-403", "material_lot_id": "LOT-THM-121", "planned_qty": 30, "good_qty": 0, "scrap_qty": 0, "scheduled_start": "2026-05-20", "scheduled_end": "2026-05-27", "wo_status_code": 10},
    ]

    # disposition_code: 1=Pass, 2=Rework, 3=ScrapHold
    inspections = [
        {"inspection_id": "INS-2026-5001", "work_order_id": "WO-2026-1001", "equipment_id": "EQ-TST-502", "inspected_at": "2026-05-06T14:20:00Z", "torque_ripple_pct": 1.1, "bond_void_area_pct": 0.4, "insulation_mohm": 920.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5002", "work_order_id": "WO-2026-1002", "equipment_id": "EQ-TST-503", "inspected_at": "2026-05-08T15:10:00Z", "torque_ripple_pct": 1.4, "bond_void_area_pct": 0.0, "insulation_mohm": 880.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5003", "work_order_id": "WO-2026-1003", "equipment_id": "EQ-TST-501", "inspected_at": "2026-05-10T11:30:00Z", "torque_ripple_pct": 0.9, "bond_void_area_pct": 0.6, "insulation_mohm": 950.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5004", "work_order_id": "WO-2026-1004", "equipment_id": "EQ-TST-502", "inspected_at": "2026-05-09T16:40:00Z", "torque_ripple_pct": 1.2, "bond_void_area_pct": 0.3, "insulation_mohm": 910.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5005", "work_order_id": "WO-2026-1005", "equipment_id": "EQ-TST-503", "inspected_at": "2026-05-11T13:05:00Z", "torque_ripple_pct": 1.0, "bond_void_area_pct": 0.2, "insulation_mohm": 970.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5006", "work_order_id": "WO-2026-1006", "equipment_id": "EQ-TST-503", "inspected_at": "2026-05-13T10:15:00Z", "torque_ripple_pct": 1.3, "bond_void_area_pct": 0.3, "insulation_mohm": 895.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5007", "work_order_id": "WO-2026-1007", "equipment_id": "EQ-TST-501", "inspected_at": "2026-05-14T11:45:00Z", "torque_ripple_pct": 4.2, "bond_void_area_pct": 6.8, "insulation_mohm": 840.0, "defect_code": "DEF-BOND-02", "disposition_code": 3},
        {"inspection_id": "INS-2026-5008", "work_order_id": "WO-2026-1007", "equipment_id": "EQ-TST-501", "inspected_at": "2026-05-14T12:10:00Z", "torque_ripple_pct": 4.5, "bond_void_area_pct": 7.1, "insulation_mohm": 830.0, "defect_code": "DEF-TRQ-04", "disposition_code": 3},
        {"inspection_id": "INS-2026-5009", "work_order_id": "WO-2026-1008", "equipment_id": "EQ-TST-502", "inspected_at": "2026-05-14T09:30:00Z", "torque_ripple_pct": 1.1, "bond_void_area_pct": 0.5, "insulation_mohm": 935.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5010", "work_order_id": "WO-2026-1009", "equipment_id": "EQ-TST-503", "inspected_at": "2026-05-14T10:00:00Z", "torque_ripple_pct": 1.3, "bond_void_area_pct": 0.0, "insulation_mohm": 905.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5011", "work_order_id": "WO-2026-1011", "equipment_id": "EQ-TST-502", "inspected_at": "2026-05-14T10:30:00Z", "torque_ripple_pct": 1.2, "bond_void_area_pct": 0.4, "insulation_mohm": 912.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5012", "work_order_id": "WO-2026-1012", "equipment_id": "EQ-TST-501", "inspected_at": "2026-05-14T12:40:00Z", "torque_ripple_pct": 3.9, "bond_void_area_pct": 5.9, "insulation_mohm": 850.0, "defect_code": "DEF-BOND-02", "disposition_code": 3},
        {"inspection_id": "INS-2026-5013", "work_order_id": "WO-2026-1012", "equipment_id": "EQ-TST-501", "inspected_at": "2026-05-14T13:05:00Z", "torque_ripple_pct": 4.1, "bond_void_area_pct": 6.2, "insulation_mohm": 845.0, "defect_code": "DEF-BOND-02", "disposition_code": 3},
        {"inspection_id": "INS-2026-5014", "work_order_id": "WO-2026-1013", "equipment_id": "EQ-TST-503", "inspected_at": "2026-05-14T11:00:00Z", "torque_ripple_pct": 1.5, "bond_void_area_pct": 0.0, "insulation_mohm": 890.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5015", "work_order_id": "WO-2026-1014", "equipment_id": "EQ-TST-502", "inspected_at": "2026-05-14T11:20:00Z", "torque_ripple_pct": 1.2, "bond_void_area_pct": 0.3, "insulation_mohm": 918.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5016", "work_order_id": "WO-2026-1015", "equipment_id": "EQ-TST-503", "inspected_at": "2026-05-14T11:50:00Z", "torque_ripple_pct": 1.4, "bond_void_area_pct": 0.0, "insulation_mohm": 900.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5017", "work_order_id": "WO-2026-1017", "equipment_id": "EQ-TST-502", "inspected_at": "2026-05-14T12:15:00Z", "torque_ripple_pct": 1.0, "bond_void_area_pct": 0.5, "insulation_mohm": 942.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5018", "work_order_id": "WO-2026-1028", "equipment_id": "EQ-TST-502", "inspected_at": "2026-05-14T12:30:00Z", "torque_ripple_pct": 1.1, "bond_void_area_pct": 0.4, "insulation_mohm": 938.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5019", "work_order_id": "WO-2026-1019", "equipment_id": "EQ-TST-501", "inspected_at": "2026-05-14T13:30:00Z", "torque_ripple_pct": 4.7, "bond_void_area_pct": 6.4, "insulation_mohm": 825.0, "defect_code": "DEF-TRQ-04", "disposition_code": 3},
        {"inspection_id": "INS-2026-5020", "work_order_id": "WO-2026-1021", "equipment_id": "EQ-TST-501", "inspected_at": "2026-05-14T13:50:00Z", "torque_ripple_pct": 2.8, "bond_void_area_pct": 0.0, "insulation_mohm": 885.0, "defect_code": "DEF-DIM-01", "disposition_code": 2},
        {"inspection_id": "INS-2026-5021", "work_order_id": "WO-2026-1010", "equipment_id": "EQ-TST-503", "inspected_at": "2026-05-14T14:00:00Z", "torque_ripple_pct": 1.3, "bond_void_area_pct": 0.0, "insulation_mohm": 904.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5022", "work_order_id": "WO-2026-1001", "equipment_id": "EQ-TST-502", "inspected_at": "2026-05-05T10:00:00Z", "torque_ripple_pct": 1.0, "bond_void_area_pct": 0.3, "insulation_mohm": 930.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5023", "work_order_id": "WO-2026-1003", "equipment_id": "EQ-TST-501", "inspected_at": "2026-05-09T14:00:00Z", "torque_ripple_pct": 0.9, "bond_void_area_pct": 0.5, "insulation_mohm": 948.0, "defect_code": "DEF-00", "disposition_code": 1},
        {"inspection_id": "INS-2026-5024", "work_order_id": "WO-2026-1008", "equipment_id": "EQ-TST-502", "inspected_at": "2026-05-13T16:15:00Z", "torque_ripple_pct": 1.2, "bond_void_area_pct": 0.5, "insulation_mohm": 932.0, "defect_code": "DEF-00", "disposition_code": 1},
    ]

    return {
        "mes_production_lines": (list(lines[0].keys()), lines),
        "mes_equipment": (list(equipment[0].keys()), equipment),
        "mes_material_lots": (list(material_lots[0].keys()), material_lots),
        "mes_work_orders": (list(work_orders[0].keys()), work_orders),
        "mes_quality_inspections": (list(inspections[0].keys()), inspections),
    }


def build_iot_datasets() -> tuple[dict[str, tuple[list[str], list[dict[str, Any]]]], list[dict[str, Any]]]:
    sensors = [
        {"sensor_id": "SNS-CNC-101", "equipment_id": "EQ-CNC-101", "sensor_model": "Keyence-VT200", "measurement_domain": "SpindleVibTemp", "sampling_interval_sec": 10, "temp_warn_c": 65.0, "temp_crit_c": 75.0, "vib_crit_mm_s": 4.5, "vacuum_crit_pa": 0.0},
        {"sensor_id": "SNS-CNC-102", "equipment_id": "EQ-CNC-102", "sensor_model": "Keyence-VT200", "measurement_domain": "SpindleVibTemp", "sampling_interval_sec": 10, "temp_warn_c": 65.0, "temp_crit_c": 75.0, "vib_crit_mm_s": 4.5, "vacuum_crit_pa": 0.0},
        {"sensor_id": "SNS-CNC-103", "equipment_id": "EQ-CNC-103", "sensor_model": "Keyence-VT200", "measurement_domain": "SpindleVibTemp", "sampling_interval_sec": 10, "temp_warn_c": 65.0, "temp_crit_c": 75.0, "vib_crit_mm_s": 4.5, "vacuum_crit_pa": 0.0},
        {"sensor_id": "SNS-VBF-204", "equipment_id": "EQ-VBF-204", "sensor_model": "Ulvac-TM900", "measurement_domain": "FurnaceTempVacuum", "sampling_interval_sec": 5, "temp_warn_c": 820.0, "temp_crit_c": 835.0, "vib_crit_mm_s": 2.5, "vacuum_crit_pa": 5.0},
        {"sensor_id": "SNS-VBF-205", "equipment_id": "EQ-VBF-205", "sensor_model": "Ulvac-TM900", "measurement_domain": "FurnaceTempVacuum", "sampling_interval_sec": 5, "temp_warn_c": 820.0, "temp_crit_c": 835.0, "vib_crit_mm_s": 2.5, "vacuum_crit_pa": 5.0},
        {"sensor_id": "SNS-WND-301", "equipment_id": "EQ-WND-301", "sensor_model": "Omron-K6CM", "measurement_domain": "TensionVibTemp", "sampling_interval_sec": 15, "temp_warn_c": 55.0, "temp_crit_c": 65.0, "vib_crit_mm_s": 3.5, "vacuum_crit_pa": 0.0},
        {"sensor_id": "SNS-WND-302", "equipment_id": "EQ-WND-302", "sensor_model": "Omron-K6CM", "measurement_domain": "TensionVibTemp", "sampling_interval_sec": 15, "temp_warn_c": 55.0, "temp_crit_c": 65.0, "vib_crit_mm_s": 3.5, "vacuum_crit_pa": 0.0},
        {"sensor_id": "SNS-WND-303", "equipment_id": "EQ-WND-303", "sensor_model": "Omron-K6CM", "measurement_domain": "TensionVibTemp", "sampling_interval_sec": 15, "temp_warn_c": 55.0, "temp_crit_c": 65.0, "vib_crit_mm_s": 3.5, "vacuum_crit_pa": 0.0},
        {"sensor_id": "SNS-ASM-401", "equipment_id": "EQ-ASM-401", "sensor_model": "SMC-PF3W", "measurement_domain": "CleanPressCell", "sampling_interval_sec": 30, "temp_warn_c": 26.0, "temp_crit_c": 28.0, "vib_crit_mm_s": 2.0, "vacuum_crit_pa": 0.0},
        {"sensor_id": "SNS-ASM-402", "equipment_id": "EQ-ASM-402", "sensor_model": "SMC-PF3W", "measurement_domain": "PressCell", "sampling_interval_sec": 30, "temp_warn_c": 30.0, "temp_crit_c": 35.0, "vib_crit_mm_s": 2.2, "vacuum_crit_pa": 0.0},
        {"sensor_id": "SNS-ASM-403", "equipment_id": "EQ-ASM-403", "sensor_model": "SMC-PF3W", "measurement_domain": "PressCell", "sampling_interval_sec": 30, "temp_warn_c": 30.0, "temp_crit_c": 35.0, "vib_crit_mm_s": 2.2, "vacuum_crit_pa": 0.0},
        {"sensor_id": "SNS-ASM-404", "equipment_id": "EQ-ASM-404", "sensor_model": "SMC-PF3W", "measurement_domain": "PressCell", "sampling_interval_sec": 30, "temp_warn_c": 30.0, "temp_crit_c": 35.0, "vib_crit_mm_s": 2.2, "vacuum_crit_pa": 0.0},
        {"sensor_id": "SNS-TST-501", "equipment_id": "EQ-TST-501", "sensor_model": "HIOKI-PW3390", "measurement_domain": "BenchMonitor", "sampling_interval_sec": 60, "temp_warn_c": 32.0, "temp_crit_c": 38.0, "vib_crit_mm_s": 1.8, "vacuum_crit_pa": 0.0},
        {"sensor_id": "SNS-TST-502", "equipment_id": "EQ-TST-502", "sensor_model": "HIOKI-PW3390", "measurement_domain": "BenchMonitor", "sampling_interval_sec": 60, "temp_warn_c": 32.0, "temp_crit_c": 38.0, "vib_crit_mm_s": 1.8, "vacuum_crit_pa": 0.0},
        {"sensor_id": "SNS-TST-503", "equipment_id": "EQ-TST-503", "sensor_model": "HIOKI-PW3390", "measurement_domain": "BenchMonitor", "sampling_interval_sec": 60, "temp_warn_c": 32.0, "temp_crit_c": 38.0, "vib_crit_mm_s": 1.8, "vacuum_crit_pa": 0.0},
    ]

    # Deterministic 360 telemetry rows: 15 sensors x 24 hourly timestamps on 2026-05-14
    telemetry: list[dict[str, Any]] = []
    reading_seq = 1
    for s_idx, sensor in enumerate(sensors):
        eq_id = sensor["equipment_id"]
        sns_id = sensor["sensor_id"]
        for hour in range(24):
            ts = f"2026-05-14T{hour:02d}:00:00Z"
            drift = ((s_idx * 7 + hour * 3) % 9) * 0.15
            anomaly = "false"

            if eq_id == "EQ-VBF-204":
                if 9 <= hour <= 12:
                    # Thermal excursion & vacuum seal leak during brazing cycles!
                    temp = round(842.0 + (hour - 9) * 5.4 + drift, 2)
                    vac = round(6.8 + (hour - 9) * 0.9, 2)
                    vib = round(1.45 + (hour - 9) * 0.12, 2)
                    pwr = round(68.5 + (hour - 9) * 2.1, 2)
                    anomaly = "true"
                else:
                    temp = round(798.0 + drift * 4.0, 2)
                    vac = round(1.8 + (hour % 3) * 0.2, 2)
                    vib = round(0.95 + (hour % 4) * 0.05, 2)
                    pwr = round(58.0 + drift * 2.0, 2)
            elif eq_id == "EQ-VBF-205":
                temp = round(796.5 + drift * 3.0, 2)
                vac = round(1.4 + (hour % 3) * 0.15, 2)
                vib = round(0.82 + (hour % 3) * 0.04, 2)
                pwr = round(56.5 + drift * 1.5, 2)
            elif eq_id == "EQ-CNC-101":
                if hour in (10, 11):
                    temp = round(68.4 + (hour - 10) * 1.8, 2)
                    vib = round(4.82 + (hour - 10) * 0.30, 2)
                    vac = 0.0
                    pwr = round(24.6 + (hour - 10) * 0.9, 2)
                    anomaly = "true"
                else:
                    temp = round(54.0 + drift * 2.0, 2)
                    vib = round(2.35 + (hour % 5) * 0.14, 2)
                    vac = 0.0
                    pwr = round(19.5 + drift, 2)
            elif eq_id.startswith("EQ-CNC-"):
                temp = round(51.5 + drift * 2.0, 2)
                vib = round(1.85 + (hour % 4) * 0.10, 2)
                vac = 0.0
                pwr = round(18.2 + drift, 2)
            elif eq_id.startswith("EQ-WND-"):
                temp = round(42.0 + drift * 1.5, 2)
                vib = round(1.35 + (hour % 4) * 0.08, 2)
                vac = 0.0
                pwr = round(11.4 + drift * 0.8, 2)
            elif eq_id.startswith("EQ-ASM-"):
                temp = round(23.2 + (hour % 4) * 0.25, 2)
                vib = round(0.65 + (hour % 3) * 0.05, 2)
                vac = 0.0
                pwr = round(6.8 + drift * 0.5, 2)
            else:
                temp = round(24.5 + (hour % 3) * 0.3, 2)
                vib = round(0.42 + (hour % 3) * 0.03, 2)
                vac = 0.0
                pwr = round(4.5 + drift * 0.4, 2)

            telemetry.append(
                {
                    "reading_id": f"RD-20260514-{reading_seq:04d}",
                    "timestamp_utc": ts,
                    "equipment_id": eq_id,
                    "sensor_id": sns_id,
                    "chamber_or_spindle_temp_c": temp,
                    "vibration_rms_mm_s": vib,
                    "vacuum_pressure_pa": vac,
                    "power_draw_kw": pwr,
                    "anomaly_flag": anomaly,
                }
            )
            reading_seq += 1

    # severity_code: 1=Info, 2=Warning, 3=Critical
    alerts = [
        {"alert_id": "ALT-2026-901", "equipment_id": "EQ-VBF-204", "sensor_id": "SNS-VBF-204", "triggered_at_utc": "2026-05-14T09:18:00Z", "alert_code": "ALT-VAC-LEAK", "severity_code": 3, "peak_value": 9.5, "duration_minutes": 28, "is_resolved": "false"},
        {"alert_id": "ALT-2026-902", "equipment_id": "EQ-VBF-204", "sensor_id": "SNS-VBF-204", "triggered_at_utc": "2026-05-14T10:05:00Z", "alert_code": "ALT-TMP-HIGH", "severity_code": 3, "peak_value": 859.4, "duration_minutes": 24, "is_resolved": "false"},
        {"alert_id": "ALT-2026-903", "equipment_id": "EQ-VBF-204", "sensor_id": "SNS-VBF-204", "triggered_at_utc": "2026-05-14T11:40:00Z", "alert_code": "ALT-VAC-LEAK", "severity_code": 3, "peak_value": 9.5, "duration_minutes": 21, "is_resolved": "false"},
        {"alert_id": "ALT-2026-904", "equipment_id": "EQ-CNC-101", "sensor_id": "SNS-CNC-101", "triggered_at_utc": "2026-05-14T10:12:00Z", "alert_code": "ALT-VIB-SPIKE", "severity_code": 2, "peak_value": 5.12, "duration_minutes": 11, "is_resolved": "false"},
        {"alert_id": "ALT-2026-905", "equipment_id": "EQ-CNC-101", "sensor_id": "SNS-CNC-101", "triggered_at_utc": "2026-05-14T11:04:00Z", "alert_code": "ALT-TMP-WARN", "severity_code": 2, "peak_value": 70.2, "duration_minutes": 9, "is_resolved": "false"},
        {"alert_id": "ALT-2026-906", "equipment_id": "EQ-WND-302", "sensor_id": "SNS-WND-302", "triggered_at_utc": "2026-05-12T15:20:00Z", "alert_code": "ALT-TNS-DRIFT", "severity_code": 1, "peak_value": 2.9, "duration_minutes": 4, "is_resolved": "true"},
        {"alert_id": "ALT-2026-907", "equipment_id": "EQ-CNC-102", "sensor_id": "SNS-CNC-102", "triggered_at_utc": "2026-05-11T08:45:00Z", "alert_code": "ALT-COOL-LOW", "severity_code": 1, "peak_value": 58.1, "duration_minutes": 6, "is_resolved": "true"},
        {"alert_id": "ALT-2026-908", "equipment_id": "EQ-ASM-401", "sensor_id": "SNS-ASM-401", "triggered_at_utc": "2026-05-13T07:30:00Z", "alert_code": "ALT-DIFF-PRESS", "severity_code": 1, "peak_value": 24.8, "duration_minutes": 3, "is_resolved": "true"},
        {"alert_id": "ALT-2026-909", "equipment_id": "EQ-VBF-205", "sensor_id": "SNS-VBF-205", "triggered_at_utc": "2026-05-10T14:10:00Z", "alert_code": "ALT-N2-PURGE", "severity_code": 1, "peak_value": 2.1, "duration_minutes": 2, "is_resolved": "true"},
        {"alert_id": "ALT-2026-910", "equipment_id": "EQ-WND-303", "sensor_id": "SNS-WND-303", "triggered_at_utc": "2026-05-13T16:50:00Z", "alert_code": "ALT-TNS-DRIFT", "severity_code": 1, "peak_value": 3.0, "duration_minutes": 5, "is_resolved": "true"},
    ]

    csv_map = {
        "iot_sensors": (list(sensors[0].keys()), sensors),
        "iot_telemetry": (list(telemetry[0].keys()), telemetry),
        "iot_equipment_alerts": (list(alerts[0].keys()), alerts),
    }
    return csv_map, telemetry


def build_doc_catalog() -> tuple[list[str], list[dict[str, Any]]]:
    docs = [
        {"doc_id": "DOC-SOP-VBF204", "file_name": "SOP-EQ-VBF-204_vacuum_brazing_furnace.md", "doc_type": "SOP", "domain": "MES_IoT", "anchor_keys": "EQ-VBF-204;EQ-VBF-205;ALT-VAC-LEAK;ALT-TMP-HIGH", "owner_dept": "ProductionEngineering", "effective_date": "2026-01-15"},
        {"doc_id": "DOC-SOP-CNC101", "file_name": "SOP-EQ-CNC-101_spindle_vibration_maintenance.md", "doc_type": "SOP", "domain": "MES_IoT", "anchor_keys": "EQ-CNC-101;ALT-VIB-SPIKE;DEF-DIM-01", "owner_dept": "Maintenance", "effective_date": "2026-02-01"},
        {"doc_id": "DOC-QMS-004", "file_name": "QMS-STD-004_actuator_quality_disposition.md", "doc_type": "QualityStandard", "domain": "Quality", "anchor_keys": "DEF-BOND-02;DEF-TRQ-04;PRD-ACT-900;PRD-ACT-650", "owner_dept": "QualityAssurance", "effective_date": "2026-01-10"},
        {"doc_id": "DOC-POL-SCM002", "file_name": "POL-SCM-002_emergency_expedite_and_airfreight.md", "doc_type": "CorporatePolicy", "domain": "ERP_SCM", "anchor_keys": "Tier1;AtRisk;SUP-007;EQ-VBF-205", "owner_dept": "SupplyChainManagement", "effective_date": "2025-11-01"},
        {"doc_id": "DOC-MAN-NDFEB", "file_name": "MAN-MAT-NDFEB_magnet_lot_handling.md", "doc_type": "MaterialSpec", "domain": "ERP_MES", "anchor_keys": "MAT-MAG-04;SUP-003;SUP-007;LOT-MAG-088", "owner_dept": "MaterialsEngineering", "effective_date": "2026-01-20"},
        {"doc_id": "DOC-INC-1028", "file_name": "INC-2026-1028_hamamatsu_line2_brazing_incident.md", "doc_type": "IncidentReport", "domain": "MES_Quality", "anchor_keys": "EQ-VBF-204;LINE-HMM-02;DEF-BOND-02;PART-SEAL-KF40", "owner_dept": "QualityAssurance", "effective_date": "2026-03-05"},
        {"doc_id": "DOC-SLA-TIER1", "file_name": "SLA-CUS-001_tier1_robotics_contract_summary.md", "doc_type": "ContractSummary", "domain": "ERP_Sales", "anchor_keys": "CUS-001;CUS-002;CUS-003;CUS-004", "owner_dept": "EnterpriseSales", "effective_date": "2026-04-01"},
        {"doc_id": "DOC-GLOSSARY", "file_name": "GLOSSARY_enterprise_domain_terms.md", "doc_type": "DomainInterviewNotes", "domain": "CrossDomain", "anchor_keys": "erp#Order;mes#Order;Equipment;QualityHold;AtRisk", "owner_dept": "EnterpriseArchitecture", "effective_date": "2026-05-01"},
    ]
    return list(docs[0].keys()), docs


def compute_oracle(
    erp: dict[str, tuple[list[str], list[dict[str, Any]]]],
    mes: dict[str, tuple[list[str], list[dict[str, Any]]]],
    iot: dict[str, tuple[list[str], list[dict[str, Any]]]],
    docs: tuple[list[str], list[dict[str, Any]]],
) -> dict[str, Any]:
    customers = {r["customer_id"]: r for r in erp["erp_customers"][1]}
    sales_orders = {r["order_id"]: r for r in erp["erp_sales_orders"][1]}
    work_orders = mes["mes_work_orders"][1]
    equipment = {r["equipment_id"]: r for r in mes["mes_equipment"][1]}
    lots = {r["material_lot_id"]: r for r in mes["mes_material_lots"][1]}

    # Multi-hop blast radius from EQ-VBF-204 or LOT-MAG-088 -> Work Orders -> Sales Orders -> Tier 1 Customers
    impacted_wos = [
        wo for wo in work_orders
        if wo["equipment_id"] == "EQ-VBF-204" or wo["material_lot_id"] == "LOT-MAG-088"
    ]
    impacted_so_ids = sorted({wo["sales_order_id"] for wo in impacted_wos})
    impacted_sos = [sales_orders[so_id] for so_id in impacted_so_ids]
    total_impacted_revenue = sum(so["order_amount_jpy"] for so in impacted_sos)
    total_daily_sla_penalty = sum(
        customers[so["customer_id"]]["sla_penalty_jpy_per_day"] for so in impacted_sos
    )

    # Calibration overdue equipment (> calibration_cycle_days)
    overdue_eq = sorted(
        eq["equipment_id"]
        for eq in equipment.values()
        if eq["days_since_calibration"] > eq["calibration_cycle_days"]
    )

    # Active sales revenue (excluding status 0=Cancelled)
    active_revenue_by_family: dict[str, int] = {}
    products = {r["product_id"]: r for r in erp["erp_products"][1]}
    for so in sales_orders.values():
        if so["order_status_code"] != 0:
            fam = products[so["product_id"]]["product_family"]
            active_revenue_by_family[fam] = active_revenue_by_family.get(fam, 0) + so["order_amount_jpy"]

    row_counts = {
        **{k: len(v[1]) for k, v in erp.items()},
        **{k: len(v[1]) for k, v in mes.items()},
        **{k: len(v[1]) for k, v in iot.items()},
        "unstructured_doc_catalog": len(docs[1]),
    }

    return {
        "scenario_reference_date": "2026-05-14",
        "row_counts": row_counts,
        "blast_radius_eq_vbf_204_and_lot_mag_088": {
            "root_equipment_id": "EQ-VBF-204",
            "root_material_lot_id": "LOT-MAG-088",
            "root_supplier_id": lots["LOT-MAG-088"]["supplier_id"],
            "qualified_backup_supplier_id": "SUP-007",
            "healthy_alternate_equipment_id": "EQ-VBF-205",
            "impacted_work_order_ids": [wo["order_id"] for wo in impacted_wos],
            "impacted_sales_order_ids": impacted_so_ids,
            "hidden_erp_inproduction_sales_order_id": "SO-2026-015",
            "impacted_customer_ids": [sales_orders[sid]["customer_id"] for sid in impacted_so_ids],
            "total_impacted_order_amount_jpy": total_impacted_revenue,
            "total_daily_sla_penalty_jpy": total_daily_sla_penalty,
        },
        "calibration_overdue_equipment_ids": overdue_eq,
        "tier1_calibration_violation_work_order_id": "WO-2026-1025",
        "moisture_violation_lot_id": "LOT-MAG-088",
        "moisture_violation_ppm": lots["LOT-MAG-088"]["moisture_ppm"],
        "active_sales_amount_by_product_family_jpy": active_revenue_by_family,
    }


def main() -> None:
    erp = build_erp_datasets()
    for name, (fields, rows) in erp.items():
        write_csv(DATA_DIR / "erp" / f"{name}.csv", fields, rows)

    mes = build_mes_datasets()
    for name, (fields, rows) in mes.items():
        write_csv(DATA_DIR / "mes" / f"{name}.csv", fields, rows)

    iot, telemetry_rows = build_iot_datasets()
    for name, (fields, rows) in iot.items():
        write_csv(DATA_DIR / "iot" / f"{name}.csv", fields, rows)
    write_jsonl(DATA_DIR / "iot" / "iot_telemetry.jsonl", telemetry_rows)

    doc_fields, doc_rows = build_doc_catalog()
    write_csv(DATA_DIR / "unstructured_docs" / "doc_catalog.csv", doc_fields, doc_rows)

    oracle = compute_oracle(erp, mes, iot, (doc_fields, doc_rows))
    oracle_path = DATA_DIR / "expected_oracle.json"
    oracle_path.write_text(json.dumps(oracle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated datasets successfully. Summary row counts: {oracle['row_counts']}")


if __name__ == "__main__":
    main()
