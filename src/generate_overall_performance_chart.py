"""
Gráfico agregando a média de Performance de todos os apps (ufc-hub, sigaa, ufc-noticias)
e plataformas (Desktop/Mobile) somando Lighthouse e PageSpeed.
"""
from .charts_common import (
    APPS,
    APP_LABELS,
    COLORS,
    FIGS_ROOT,
    PLATFORMS,
    read_scores,
    group_mean_stdev,
    plot_grouped_series,
)


def main():
    records = read_scores(category_filter=["performance"])
    if not records:
        print("Nenhum dado encontrado. Nada a plotar.")
        return

    stats = group_mean_stdev(records, key_fields=["app", "platform"])
    audits_str = ", ".join(sorted({r["module"] for r in records}))

    x_labels = [APP_LABELS.get(app, app) for app in APPS]
    series = []
    for plat in PLATFORMS:
        values = [stats.get((app, plat), {}).get("mean", 0) for app in APPS]
        yerr = [stats.get((app, plat), {}).get("stdev", 0) for app in APPS]
        series.append({
            "label": plat,
            "values": values,
            "yerr": yerr,
            "color": COLORS.get(plat),
        })

    title = "Performance Média por Site"
    if audits_str:
        title += f" ({audits_str})"

    out_path = FIGS_ROOT / "resumo_performance_todos_apps.png"
    plot_grouped_series(
        x_labels=x_labels,
        series=series,
        title=title,
        ylabel="Pontuação Média",
        out_path=out_path,
        ylim=(60, 105),
    )


if __name__ == "__main__":
    main()
