from __future__ import annotations

import json
from pathlib import Path

from src.config import DATA_DIR

PATTERN_OF_COLLISION = {
    1: "Single Vehicle",
    2: "Vehicle to Vehicle",
    3: "Vehicle to Pedestrian",
    4: "Vehicle to Bicycle",
    5: "Vehicle to Animal",
    6: "Hit Standing/Parked Vehicle",
    7: "Hit Fixed/Stationary Object",
    8: "Others (Specify)",
}

TYPE_OF_COLLISION = {
    1: "Hit from Back",
    2: "Hit from Side",
    3: "Run Off Road",
    4: "Vehicle Overturn/Skidding",
    5: "Head On Collision",
    6: "Hit and Run",
    7: "Side Swipe",
    8: "Hit Pedestrian",
    9: "Passenger Fell Down",
    10: "Not Known",
    11: "Others (Specify)",
}

TYPE_OF_VEHICLE = {
    1: "Motorised Two-Wheeler",
    2: "Passenger Auto",
    3: "Car/Jeep/Taxi",
    4: "Bus",
    5: "Mini Bus/Passenger Tempo/Passenger Van",
    6: "Goods Auto/Goods Pick-up Van",
    7: "Goods LCV/Goods Tempo/Mini Lorry/Mini Truck",
    8: "Truck/Lorry",
    9: "Multi-Axle Truck",
    10: "Bicycle",
    11: "Pedestrian",
    12: "Unknown Vehicle",
    13: "Ambulance",
    14: "Others (Specify)",
}

DEFAULT_MASTER_REF_TABLES = {
    "Pattern of Collision": PATTERN_OF_COLLISION,
    "Type of Collision": TYPE_OF_COLLISION,
    "Type of Vehicle": TYPE_OF_VEHICLE,
}

MASTER_REFERENCE_FILE = DATA_DIR / "master_reference.json"


def _normalize_table(mapping: dict) -> dict[int, str]:
    out = {}
    for k, v in mapping.items():
        try:
            key = int(k)
            val = str(v).strip()
            if val:
                out[key] = val
        except Exception:
            continue
    return dict(sorted(out.items(), key=lambda x: x[0]))


def load_master_reference() -> dict[str, dict[int, str]]:
    if MASTER_REFERENCE_FILE.exists():
        payload = json.loads(MASTER_REFERENCE_FILE.read_text())
        loaded = {
            "Pattern of Collision": _normalize_table(payload.get("Pattern of Collision", {})),
            "Type of Collision": _normalize_table(payload.get("Type of Collision", {})),
            "Type of Vehicle": _normalize_table(payload.get("Type of Vehicle", {})),
        }
        for key, default in DEFAULT_MASTER_REF_TABLES.items():
            if not loaded[key]:
                loaded[key] = default.copy()
        return loaded
    return {k: v.copy() for k, v in DEFAULT_MASTER_REF_TABLES.items()}


def save_master_reference(master_tables: dict[str, dict[int, str]]) -> None:
    MASTER_REFERENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    clean_payload = {name: _normalize_table(mapping) for name, mapping in master_tables.items()}
    MASTER_REFERENCE_FILE.write_text(json.dumps(clean_payload, indent=2))
