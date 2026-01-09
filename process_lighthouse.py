"""
Processa JSONs de Lighthouse e PageSpeed para gerar CSVs por página, app e plataforma
(Desktop/Mobile), contendo estatísticas de métricas e pontuações de categorias.
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


def calculate_stats(values):
    if not values:
        return {
            'mean': 0, 'median': 0, 'stdev': 0, 'min': 0, 'max': 0
        }
    return {
        'mean': statistics.mean(values),
        'median': statistics.median(values),
        'stdev': statistics.stdev(values) if len(values) > 1 else 0,
        'min': min(values),
        'max': max(values)
    }


def format_stats_row(key, stats):
    if key == 'Total Transfer Size':
        s = {k: v / 1024 for k, v in stats.items()}
        unit = " KB"
        fmt = "{:.2f}"
    elif key == 'CLS':
        s = stats
        unit = ""
        fmt = "{:.4f}"
    else:
        s = stats
        unit = " ms"
        fmt = "{:.2f}"

    # Use standard format method to avoid f-string nested brace issues
    vals = [
        fmt.format(s['mean']),
        fmt.format(s['median']),
        fmt.format(s['stdev']),
        fmt.format(s['min']),
        fmt.format(s['max'])
    ]

    return "| {} | {}{} | {}{} | {}{} | {}{} | {}{} |".format(
        key,
        vals[0], unit,
        vals[1], unit,
        vals[2], unit,
        vals[3], unit,
        vals[4], unit
    )


def format_stats_for_csv(key, stats):
    """Return formatted stats and unit for CSV export."""
    if key == 'Total Transfer Size':
        factor = 1 / 1024
        unit = "KB"
        decimals = 2
    elif key == 'CLS':
        factor = 1
        unit = ""
        decimals = 4
    else:
        factor = 1
        unit = "ms"
        decimals = 2
    fmt = "{:." + str(decimals) + "f}"
    values = [fmt.format(stats[name] * factor)
              for name in ['mean', 'median', 'stdev', 'min', 'max']]
    return values, unit


def format_score_stats_for_csv(stats):
    """Return formatted score stats (percentage) for CSV export."""
    fmt = "{:.2f}"
    values = [fmt.format(stats[name])
              for name in ['mean', 'median', 'stdev', 'min', 'max']]
    return values, "%"


def process_app_module(app, module):
    page_files = list_page_files(module, app)
    if not page_files:
        print(f"Skipping {module}/{app}: base path not found or empty")
        return

    results_dir = Path('results') / app / module
    results_dir.mkdir(parents=True, exist_ok=True)

    for page, files in page_files.items():
        desktop_files = files.get('Desktop', [])
        mobile_files = files.get('Mobile', [])

        if not desktop_files and not mobile_files:
            print(f"Skipping {module}/{app}/{page}: no JSON files found")
            continue

        metrics_map = {
            'Desktop': {'files': desktop_files, 'data': {}},
            'Mobile': {'files': mobile_files, 'data': {}}
        }

        category_map = {
            'Desktop': {'files': desktop_files, 'data': {}},
            'Mobile': {'files': mobile_files, 'data': {}}
        }

        for platform in ['Desktop', 'Mobile']:
            metrics_map[platform]['data'] = {k: [] for k in METRIC_KEYS}
            category_map[platform]['data'] = {k: [] for k in CATEGORY_KEYS}

            for file in metrics_map[platform]['files']:
                m = get_metrics(file)
                if m:
                    for key in METRIC_KEYS:
                        metrics_map[platform]['data'][key].append(m[key])

                c = get_category_scores(file)
                if c:
                    for key in CATEGORY_KEYS:
                        category_map[platform]['data'][key].append(c[key])

        csv_rows = []
        csv_header = ['Plataforma', 'Métrica', 'Média', 'Mediana',
                      'Desvio Padrão', 'Mínimo', 'Máximo', 'Unidade']
        score_csv_rows = []
        score_csv_header = ['Plataforma', 'Categoria', 'Média',
                            'Mediana', 'Desvio Padrão', 'Mínimo', 'Máximo', 'Unidade']

        for platform in ['Desktop', 'Mobile']:
            for key in METRIC_KEYS:
                values = metrics_map[platform]['data'][key]
                stats = calculate_stats(values)
                csv_values, unit = format_stats_for_csv(key, stats)
                csv_rows.append([platform, key, *csv_values, unit])

            for key in CATEGORY_KEYS:
                values = category_map[platform]['data'][key]
                # scores converted to percentage
                stats = calculate_stats([v * 100 for v in values])
                percent_values, percent_unit = format_score_stats_for_csv(
                    stats)
                score_csv_rows.append(
                    [platform, key, *percent_values, percent_unit])

        csv_output_path = results_dir / f'performance_{page}.csv'
        with open(csv_output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(csv_header)
            writer.writerows(csv_rows)

        score_output_path = results_dir / f'scores_{page}.csv'
        with open(score_output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(score_csv_header)
            writer.writerows(score_csv_rows)

        print(f"Done: {module}/{app}/{page}")


for app in APPS:
    for module in MODULES:
        process_app_module(app, module)
