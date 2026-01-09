"""
Gera gráficos por página, aplicativo e módulo a partir dos CSVs em results/<app>/<module>,
com barras agrupadas e lógica compartilhada via charts_common.
"""
from typing import Dict, List
from .charts_common import (
    APPS,
    APP_LABELS,
    COLORS,
    FIGS_ROOT,
    MODULE_LABELS,
    PLATFORMS,
    read_performance,
    read_scores,
    group_mean_stdev,
    plot_grouped_series,
)

FIG_DIR = FIGS_ROOT


def plot_metric_means(records: List[Dict], app: str, module: str, metric: str) -> None:
    data = [r for r in records if r["app"] == app and r["module"] == module and r["metric"] == metric]
    if not data:
        return

    stats = group_mean_stdev(data, key_fields=["page", "platform"])
    pages = sorted({r["page"] for r in data})
    unit = data[0].get("unit", "") if data else ""

    series = []
    for idx, platform in enumerate(PLATFORMS):
        values = [stats.get((page, platform), {}).get("mean", 0) for page in pages]
        yerr = [stats.get((page, platform), {}).get("stdev", 0) for page in pages]
        series.append({
            "label": platform,
            "values": values,
            "yerr": yerr,
            "color": COLORS.get(platform),
        })

    ylabel = metric if not unit else f"{metric} ({unit})"
    out_path = FIG_DIR / app / module / f"{metric}_por_pagina.png"
    plot_grouped_series(
        x_labels=pages,
        series=series,
        title=f"{metric} por pagina e plataforma – {module} / {app}",
        ylabel=ylabel,
        out_path=out_path,
        rotation=20,
        bar_width=0.35,
    )


def plot_category_means(records: List[Dict], app: str, module: str, category: str) -> None:
    data = [r for r in records if r["app"] == app and r["module"] == module and r["category"] == category]
    if not data:
        return

    stats = group_mean_stdev(data, key_fields=["page", "platform"])
    pages = sorted({r["page"] for r in data})
    unit = data[0].get("unit", "") if data else ""

    series = []
    for platform in PLATFORMS:
        values = [stats.get((page, platform), {}).get("mean", 0) for page in pages]
        yerr = [stats.get((page, platform), {}).get("stdev", 0) for page in pages]
        series.append({
            "label": platform,
            "values": values,
            "yerr": yerr,
            "color": COLORS.get(platform),
        })

    ylabel = category if not unit else f"{category} ({unit})"
    out_path = FIG_DIR / app / module / f"{category}_scores_por_pagina.png"
    plot_grouped_series(
        x_labels=pages,
        series=series,
        title=f"Pontuacoes de {category} por pagina – {module} / {app}",
        ylabel=ylabel,
        out_path=out_path,
        rotation=20,
        bar_width=0.35,
        ylim=(0, 105),
    )


def plot_metric_across_apps(records: List[Dict], module: str, metric: str) -> None:
    data = [r for r in records if r["module"] == module and r["metric"] == metric]
    if not data:
        return

    stats = group_mean_stdev(data, key_fields=["app", "platform"])
    unit = data[0].get("unit", "") if data else ""
    apps = [a for a in APPS if any(r["app"] == a for r in data)]

    series = []
    for platform in PLATFORMS:
        values = [stats.get((app, platform), {}).get("mean", 0) for app in apps]
        yerr = [stats.get((app, platform), {}).get("stdev", 0) for app in apps]
        series.append({
            "label": platform,
            "values": values,
            "yerr": yerr,
            "color": COLORS.get(platform),
        })

    ylabel = metric if not unit else f"{metric} ({unit})"
    module_display = MODULE_LABELS.get(module, module)
    x_labels = [APP_LABELS.get(a, a) for a in apps]
    out_path = FIG_DIR / "comparativos" / module / f"{metric}_apps.png"
    plot_grouped_series(
        x_labels=x_labels,
        series=series,
        title=f"{metric} médio por aplicativo – {module_display}",
        ylabel=ylabel,
        out_path=out_path,
        rotation=10,
    )


def plot_category_across_apps(records: List[Dict], module: str, category: str) -> None:
    data = [r for r in records if r["module"] == module and r["category"] == category]
    if not data:
        return

    stats = group_mean_stdev(data, key_fields=["app", "platform"])
    unit = data[0].get("unit", "") if data else ""
    apps = [a for a in APPS if any(r["app"] == a for r in data)]

    series = []
    for platform in PLATFORMS:
        values = [stats.get((app, platform), {}).get("mean", 0) for app in apps]
        yerr = [stats.get((app, platform), {}).get("stdev", 0) for app in apps]
        series.append({
            "label": platform,
            "values": values,
            "yerr": yerr,
            "color": COLORS.get(platform),
        })

    ylabel = category if not unit else f"{category} ({unit})"
    module_display = MODULE_LABELS.get(module, module)
    x_labels = [APP_LABELS.get(a, a) for a in apps]
    out_path = FIG_DIR / "comparativos" / module / f"{category}_scores_apps.png"
    plot_grouped_series(
        x_labels=x_labels,
        series=series,
        title=f"Pontuações médias de {category} por aplicativo – {module_display}",
        ylabel=ylabel,
        out_path=out_path,
        rotation=10,
        ylim=(0, 105),
    )


def main():
    perf_records = read_performance()
    score_records = read_scores()

    if not perf_records and not score_records:
        print("Nenhum dado encontrado em results/. Nada a plotar.")
        return

    apps = sorted({r["app"] for r in perf_records} | {r["app"] for r in score_records})
    modules = sorted({r["module"] for r in perf_records} | {r["module"] for r in score_records})

    metrics_to_plot = ["LCP", "FCP", "TTFB", "TBT", "CLS", "Total Transfer Size"]
    categories_to_plot = ["performance", "accessibility", "best-practices", "seo"]

    for app in apps:
        for module in modules:
            for metric in metrics_to_plot:
                plot_metric_means(perf_records, app, module, metric)
            for category in categories_to_plot:
                plot_category_means(score_records, app, module, category)

    for module in modules:
        for metric in metrics_to_plot:
            plot_metric_across_apps(perf_records, module, metric)
        for category in categories_to_plot:
            plot_category_across_apps(score_records, module, category)

    print("Concluido.")


if __name__ == "__main__":
    main()
