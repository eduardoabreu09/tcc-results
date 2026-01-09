# Dados e resultados do TCC (UFC Hub)

Este repositório reúne os dados coletados e os gráficos gerados para o TCC que analisou a qualidade do site UFC Hub (e apps relacionados: SIGAA e UFC Notícias) usando Lighthouse e PageSpeed Insights.

## Estrutura
- `data/`: JSONs brutos das auditorias (Desktop e Mobile) por app e página.
- `results/`: CSVs gerados a partir dos JSONs (por página) e consolidados (médias globais).
- `figs/`: Gráficos prontos (por app, módulo e comparativos) gerados a partir dos CSVs.
- `src/`: utilitários e geradores de gráficos (código compartilhado e scripts modulados).
- Scripts Python na raiz: orquestram processamento e geração de gráficos.

## Scripts principais
- `process_lighthouse.py`: lê JSONs em `data/` e produz CSVs por página em `results/<app>/<modulo>/`.
- `generate_consolidated_csv.py`: consolida os JSONs em quatro arquivos de médias globais em `results/` (Desktop/Mobile, Lighthouse/PageSpeed).
- `generate_charts.py`: orquestra a geração de **todos** os gráficos usando os módulos em `lib/`.

### Módulos em `src/`
- `src/generate_compartive_charts.py`: gráficos por página, app e comparativos entre apps.
- `src/generate_app_summary_chart.py`: resumo geral por app (Desktop vs Mobile) agregando todas as páginas.
- `src/generate_module_summary_chart.py`: resumo por app e módulo (Lighthouse/PageSpeed).
- `src/generate_overall_category_chart.py`: comparativo de categorias por plataforma.
- `src/generate_overall_performance_chart.py`: comparativo geral de performance entre apps.
- `src/charts_common.py` e `src/data_loader.py`: helpers compartilhados (constantes, cores, leitura de dados, agregação e plotagem).

## Como reproduzir
1) Certifique-se de ter Python 3 instalado e `matplotlib`: `pip install matplotlib`.
2) (Opcional) Reprocessar JSONs em `data/`: `python process_lighthouse.py` (gera CSVs por página em `results/<app>/<modulo>/`).
3) Gerar CSVs consolidados (médias globais): `python generate_consolidated_csv.py`.
4) Gerar todos os gráficos de uma vez: `python generate_charts.py`.