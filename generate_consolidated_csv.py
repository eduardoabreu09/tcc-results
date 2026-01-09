"""
Consolida os JSON brutos de Lighthouse/ e PageSpeed/ em quatro CSVs de médias
por app, agregando todas as páginas e separando Desktop e Mobile.

Saídas:
    - results/lighthouse_metrics_means.csv
    - results/lighthouse_scores_means.csv
    - results/pagespeed_metrics_means.csv
    - results/pagespeed_scores_means.csv

Cada linha traz a média do app inteiro, para cada métrica de desempenho
ou categoria de score.
"""
import csv
import statistics
from pathlib import Path

from src.charts_common import APPS, MODULES
from src.data_loader import (
    METRIC_KEYS,
    CATEGORY_KEYS,
    list_page_files,
    get_metrics,
    get_category_scores,
)

OUTPUT_DIR = Path("results")


def ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def mean_or_zero(values):
    return statistics.mean(values) if values else 0.0


def process_module(module: str, output_metrics: Path, output_scores: Path) -> None:
    header = ["Plataforma", "Métrica", "UFC Hub", "SIGAA", "UFC Notícias", "Unidade"]
    metric_rows = []
    score_rows = []

    # Estruturas acumuladoras por plataforma -> métrica -> app -> valores
    accum_metrics = {
        "Desktop": {k: {app: [] for app in APPS} for k in METRIC_KEYS},
        "Mobile": {k: {app: [] for app in APPS} for k in METRIC_KEYS},
    }
    accum_scores = {
        "Desktop": {k: {app: [] for app in APPS} for k in CATEGORY_KEYS},
        "Mobile": {k: {app: [] for app in APPS} for k in CATEGORY_KEYS},
    }

    for app in APPS:
        page_files = list_page_files(module, app)
        if not page_files:
            print(f"Pulando data/{module}/{app}: diretório não encontrado")
            continue

        for _, files in page_files.items():
            for platform, paths in [("Desktop", files.get("Desktop", [])), ("Mobile", files.get("Mobile", []))]:
                if not paths:
                    continue

                for file in paths:
                    metrics = get_metrics(file)
                    if metrics:
                        for k in METRIC_KEYS:
                            accum_metrics[platform][k][app].append(metrics[k])
                    scores = get_category_scores(file)
                    if scores:
                        for k in CATEGORY_KEYS:
                            accum_scores[platform][k][app].append(scores[k] * 100)  # converter para %
    # Finaliza pivotando para o formato solicitado
    for platform in ["Desktop", "Mobile"]:
        for key in METRIC_KEYS:
            hub_val = mean_or_zero(accum_metrics[platform][key]["ufc-hub"])
            sigaa_val = mean_or_zero(accum_metrics[platform][key]["sigaa"])
            noticias_val = mean_or_zero(accum_metrics[platform][key]["ufc-noticias"])

            unit = " ms"
            fmt = "{:.2f}"
            if key == "Total Transfer Size":
                unit = " KB"
                hub_val /= 1024
                sigaa_val /= 1024
                noticias_val /= 1024
            elif key == "CLS":
                unit = ""
                fmt = "{:.4f}"

            metric_rows.append([
                platform,
                key,
                fmt.format(hub_val),
                fmt.format(sigaa_val),
                fmt.format(noticias_val),
                unit,
            ])

        for key in CATEGORY_KEYS:
            hub_val = mean_or_zero(accum_scores[platform][key]["ufc-hub"])
            sigaa_val = mean_or_zero(accum_scores[platform][key]["sigaa"])
            noticias_val = mean_or_zero(accum_scores[platform][key]["ufc-noticias"])

            score_rows.append([
                platform,
                key,
                f"{hub_val:.2f}",
                f"{sigaa_val:.2f}",
                f"{noticias_val:.2f}",
                "%",
            ])

    ensure_dir(output_metrics)
    with open(output_metrics, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(metric_rows)

    ensure_dir(output_scores)
    with open(output_scores, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(score_rows)

    print(f"Arquivo gerado: {output_metrics} ({len(metric_rows)} linhas)")
    print(f"Arquivo gerado: {output_scores} ({len(score_rows)} linhas)")


def main():
    process_module(
        "Lighthouse",
        OUTPUT_DIR / "lighthouse_metrics_means.csv",
        OUTPUT_DIR / "lighthouse_scores_means.csv",
    )
    process_module(
        "PageSpeed",
        OUTPUT_DIR / "pagespeed_metrics_means.csv",
        OUTPUT_DIR / "pagespeed_scores_means.csv",
    )


if __name__ == "__main__":
    main()
