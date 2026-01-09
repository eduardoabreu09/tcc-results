"""
Comparação das categorias (performance, accessibility, best-practices, seo) entre apps,
separando Desktop e Mobile. Gera um gráfico de barras por plataforma.
"""
from collections import defaultdict
from .charts_common import (
    APPS,
    APP_LABELS,
    CAT_LABELS,
    CATEGORIES,
    COLORS,
    FIGS_ROOT,
    PLATFORMS,
    read_scores,
    group_mean_stdev,
    plot_grouped_series,
)


def main():
    records = read_scores()
    if not records:
        print("Nenhum dado encontrado. Nada a plotar.")
        return

    stats = group_mean_stdev(records, key_fields=["platform", "category", "app"])
    auditorias = sorted({r["module"] for r in records})
    audits_str = ", ".join(auditorias)

    x_labels = [CAT_LABELS.get(c, c) for c in CATEGORIES]

    for plat in PLATFORMS:
        series = []
        for app in APPS:
            values = [stats.get((plat, cat, app), {}).get("mean", 0) for cat in CATEGORIES]
            yerr = [stats.get((plat, cat, app), {}).get("stdev", 0) for cat in CATEGORIES]
            series.append({
                "label": APP_LABELS.get(app, app),
                "values": values,
                "yerr": yerr,
                "color": COLORS.get(app),
            })

        title = f"Pontuação média por categoria – {plat}"
        if audits_str:
            title += f" ({audits_str})"

        out_path = FIGS_ROOT / f"resumo_categorias_{plat.lower()}.png"
        plot_grouped_series(
            x_labels=x_labels,
            series=series,
            title=title,
            ylabel="Pontuação Média",
            out_path=out_path,
            bar_width=0.25,
            ylim=(40, 120),
        )


if __name__ == "__main__":
    main()
