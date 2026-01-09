"""
Gráfico comparativo por aplicativo, agregando pontuações médias de todas as páginas
(Lighthouse e PageSpeed) para Performance, Acessibilidade, Boas Práticas e SEO em
Desktop e Mobile.
"""
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


def gerar_resumo_app(app: str) -> None:
    records = read_scores(app_filter=[app])
    if not records:
        print(f"Diretório não encontrado ou sem dados para {app}")
        return

    stats = group_mean_stdev(records, key_fields=["category", "platform"])
    modules_found = sorted({r["module"] for r in records})

    x_labels = [CAT_LABELS.get(c, c) for c in CATEGORIES]
    series = []
    for plat in PLATFORMS:
        values = [stats.get((cat, plat), {}).get("mean", 0) for cat in CATEGORIES]
        yerr = [stats.get((cat, plat), {}).get("stdev", 0) for cat in CATEGORIES]
        series.append({
            "label": plat,
            "values": values,
            "yerr": yerr,
            "color": COLORS.get(plat),
        })

    mods_str = ", ".join(modules_found)
    title = f"Resumo Geral de Qualidade - {APP_LABELS.get(app, app)}"
    if mods_str:
        title += f" ({mods_str})"

    out_path = FIGS_ROOT / app / "resumo_qualidade.png"
    plot_grouped_series(
        x_labels=x_labels,
        series=series,
        title=title,
        ylabel="Pontuação Média",
        out_path=out_path,
        ylim=(40, 115),
    )


def main():
    for app in APPS:
        gerar_resumo_app(app)


if __name__ == "__main__":
    main()
