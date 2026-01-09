"""
Utilitários comuns para geração de gráficos do TCC:
- Leitura de CSVs em results/<app>/<module>/.
- Constantes compartilhadas (cores, rótulos, listas de apps/módulos/categorias).
- Funções de agregação (médias/DP) e plotagem de barras agrupadas.
"""
import csv
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable, List, Optional, Sequence
import matplotlib.pyplot as plt

# Estilo padrão
plt.style.use("ggplot")

APPS = ["ufc-hub", "sigaa", "ufc-noticias"]
MODULES = ["Lighthouse", "PageSpeed"]
CATEGORIES = ["performance", "accessibility", "best-practices", "seo"]
PLATFORMS = ["Desktop", "Mobile"]

RESULTS_ROOT = Path("results")
FIGS_ROOT = Path("figs")

COLORS = {
    "Desktop": "#2b7fff",
    "Mobile": "#EA4335",
    "ufc-hub": "#2b7fff",
    "sigaa": "#ffd503",
    "ufc-noticias": "#f83c5b",
}

APP_LABELS = {
    "ufc-hub": "UFC Hub",
    "sigaa": "SIGAA",
    "ufc-noticias": "UFC Notícias",
}

MODULE_LABELS = {
    "Lighthouse": "Lighthouse",
    "PageSpeed": "PageSpeed Insights",
}

CAT_LABELS = {
    "performance": "Performance",
    "accessibility": "Acessibilidade",
    "best-practices": "Boas Práticas",
    "seo": "SEO",
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _passes(value: str, allowed: Optional[Iterable[str]]) -> bool:
    return allowed is None or value in allowed


def read_scores(app_filter: Optional[Iterable[str]] = None,
                module_filter: Optional[Iterable[str]] = None,
                category_filter: Optional[Iterable[str]] = None) -> List[dict]:
    records: List[dict] = []
    if not RESULTS_ROOT.exists():
        return records

    for app_dir in RESULTS_ROOT.iterdir():
        if not app_dir.is_dir():
            continue
        app = app_dir.name
        if not _passes(app, app_filter):
            continue

        for module_dir in app_dir.iterdir():
            if not module_dir.is_dir():
                continue
            module = module_dir.name
            if not _passes(module, module_filter):
                continue

            for csv_path in module_dir.glob("scores_*.csv"):
                page = csv_path.stem.replace("scores_", "")
                with open(csv_path, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            category = row["Categoria"]
                            if not _passes(category, category_filter):
                                continue
                            records.append({
                                "app": app,
                                "module": module,
                                "page": page,
                                "platform": row["Plataforma"],
                                "category": category,
                                "mean": float(row["Média"]),
                                "median": float(row["Mediana"]),
                                "stdev": float(row["Desvio Padrão"]),
                                "min": float(row["Mínimo"]),
                                "max": float(row["Máximo"]),
                                "unit": row.get("Unidade", ""),
                            })
                        except (KeyError, ValueError):
                            continue
    return records


def read_performance(app_filter: Optional[Iterable[str]] = None,
                     module_filter: Optional[Iterable[str]] = None,
                     metric_filter: Optional[Iterable[str]] = None) -> List[dict]:
    records: List[dict] = []
    if not RESULTS_ROOT.exists():
        return records

    for app_dir in RESULTS_ROOT.iterdir():
        if not app_dir.is_dir():
            continue
        app = app_dir.name
        if not _passes(app, app_filter):
            continue

        for module_dir in app_dir.iterdir():
            if not module_dir.is_dir():
                continue
            module = module_dir.name
            if not _passes(module, module_filter):
                continue

            for csv_path in module_dir.glob("performance_*.csv"):
                page = csv_path.stem.replace("performance_", "")
                with open(csv_path, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            metric = row["Métrica"]
                            if not _passes(metric, metric_filter):
                                continue
                            records.append({
                                "app": app,
                                "module": module,
                                "page": page,
                                "platform": row["Plataforma"],
                                "metric": metric,
                                "mean": float(row["Média"]),
                                "median": float(row["Mediana"]),
                                "stdev": float(row["Desvio Padrão"]),
                                "min": float(row["Mínimo"]),
                                "max": float(row["Máximo"]),
                                "unit": row.get("Unidade", ""),
                            })
                        except (KeyError, ValueError):
                            continue
    return records


def group_mean_stdev(records: Iterable[dict], key_fields: Sequence[str], value_field: str = "mean"):
    acc = defaultdict(list)
    for rec in records:
        key = tuple(rec[k] for k in key_fields)
        acc[key].append(rec[value_field])

    result = {}
    for key, values in acc.items():
        if values:
            mean_val = statistics.mean(values)
            stdev_val = statistics.stdev(values) if len(values) > 1 else 0.0
        else:
            mean_val = 0.0
            stdev_val = 0.0
        result[key] = {"mean": mean_val, "stdev": stdev_val}
    return result


def plot_grouped_series(x_labels: Sequence[str],
                        series: Sequence[dict],
                        title: str,
                        ylabel: str,
                        out_path: Path,
                        ylim: Optional[tuple] = None,
                        rotation: int = 0,
                        bar_width: float = 0.35,
                        value_fmt: str = "%.1f") -> None:
    x = list(range(len(x_labels)))
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = []
    for idx, s in enumerate(series):
        offsets = [pos + (idx - (len(series) - 1) / 2) * bar_width for pos in x]
        rects = ax.bar(
            offsets,
            s["values"],
            width=bar_width,
            label=s.get("label"),
            color=s.get("color"),
            alpha=0.9,
            yerr=s.get("yerr"),
            capsize=5 if s.get("yerr") is not None else None,
        )
        bars.append(rects)

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=rotation, fontsize=11, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=11)
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=14, pad=16)
    if any(s.get("label") for s in series):
        ax.legend(fontsize=12)

    for rects in bars:
        ax.bar_label(rects, fmt=value_fmt, padding=3, fontsize=10, fontweight="bold")

    ensure_dir(out_path.parent)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Gráfico gerado: {out_path}")
