"""
Gráficos de resumo por app e módulo (Lighthouse/PageSpeed), agregando categorias
de score (performance, accessibility, best-practices, seo) em Desktop e Mobile.
"""
from .charts_common import (
    APPS,
    CAT_LABELS,
    CATEGORIES,
    COLORS,
    FIGS_ROOT,
    MODULES,
    MODULE_LABELS,
    PLATFORMS,
    APP_LABELS,
    read_scores,
    group_mean_stdev,
    plot_grouped_series,
)


def gerar_resumo_app_modulo(app: str, module: str) -> None:
    records = read_scores(app_filter=[app], module_filter=[module])
    if not records:
        print(f"Aviso: nenhum dado para {app}/{module}")
        return

    stats = group_mean_stdev(records, key_fields=["platform", "category"])

    x_labels = [CAT_LABELS.get(c, c) for c in CATEGORIES]
    series = []
    for plat in PLATFORMS:
        values = [stats.get((plat, cat), {}).get("mean", 0) for cat in CATEGORIES]
        yerr = [stats.get((plat, cat), {}).get("stdev", 0) for cat in CATEGORIES]
        series.append({
            "label": plat,
            "values": values,
            "yerr": yerr,
            "color": COLORS.get(plat),
        })

    title = f"Resumo de Qualidade – {APP_LABELS.get(app, app)} ({MODULE_LABELS.get(module, module)})"
    out_path = FIGS_ROOT / app / module / "resumo_qualidade.png"
    plot_grouped_series(
        x_labels=x_labels,
        series=series,
        title=title,
        ylabel="Pontuação Média",
        out_path=out_path,
        ylim=(40, 120),
    )


def main():
    for app in APPS:
        for module in MODULES:
            gerar_resumo_app_modulo(app, module)


if __name__ == "__main__":
    main()