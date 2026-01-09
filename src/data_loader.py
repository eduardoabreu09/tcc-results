"""
Funções utilitárias para ler JSONs de auditoria e listar arquivos por app/módulo/página.
Compartilha lógica entre process_lighthouse.py e generate_consolidated_csv.py.
"""
import json
from pathlib import Path

from src.charts_common import APPS, MODULES, CATEGORIES

DATA_ROOT = Path("data")
METRIC_KEYS = ["TTFB", "FCP", "TBT", "LCP", "CLS", "SI", "Total Transfer Size"]
CATEGORY_KEYS = list(CATEGORIES)


def list_page_files(module: str, app: str):
    """Retorna dict page -> {"Desktop": [files], "Mobile": [files]} para o app/módulo."""
    base = DATA_ROOT / module / app
    if not base.exists():
        return {}

    pages = {}
    for page_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        pages[page_dir.name] = {
            "Desktop": sorted(page_dir.glob("*.json")),
            "Mobile": sorted((page_dir / "mobile").glob("*.json")),
        }
    return pages


def get_metrics(filepath: Path):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print(f"Erro lendo {filepath}: {exc}")
        return None

    audits = data.get("audits", {})

    def get_val(key: str):
        return audits.get(key, {}).get("numericValue", 0)

    total_size = 0
    diagnostics = audits.get("diagnostics", {})
    if diagnostics and "details" in diagnostics and "items" in diagnostics["details"]:
        items = diagnostics["details"].get("items", [])
        if items:
            total_size = items[0].get("totalByteWeight", 0)

    if total_size == 0:
        net_reqs = audits.get("network-requests", {})
        if net_reqs and "details" in net_reqs and "items" in net_reqs["details"]:
            total_size = sum(item.get("transferSize", 0) for item in net_reqs["details"].get("items", []))

    return {
        "TTFB": get_val("server-response-time"),
        "FCP": get_val("first-contentful-paint"),
        "LCP": get_val("largest-contentful-paint"),
        "CLS": get_val("cumulative-layout-shift"),
        "TBT": get_val("total-blocking-time"),
        "SI": get_val("speed-index"),
        "Total Transfer Size": total_size,
    }


def get_category_scores(filepath: Path):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print(f"Erro lendo {filepath}: {exc}")
        return None

    categories = data.get("categories", {})
    return {
        "performance": categories.get("performance", {}).get("score", 0),
        "accessibility": categories.get("accessibility", {}).get("score", 0),
        "best-practices": categories.get("best-practices", {}).get("score", 0),
        "seo": categories.get("seo", {}).get("score", 0),
    }
