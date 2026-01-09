"""
Orquestra a geração de todos os gráficos do projeto em uma única execução,
reutilizando os módulos em lib/.
"""
from src import generate_compartive_charts
from src import generate_app_summary_chart
from src import generate_module_summary_chart
from src import generate_overall_category_chart
from src import generate_overall_performance_chart


def main() -> None:
	print("[1/5] Gráficos comparativos por página/app/módulo...")
	generate_compartive_charts.main()

	print("[2/5] Resumos gerais por app...")
	generate_app_summary_chart.main()

	print("[3/5] Resumos por app e módulo...")
	generate_module_summary_chart.main()

	print("[4/5] Comparativo por categoria (Desktop/Mobile)...")
	generate_overall_category_chart.main()

	print("[5/5] Resumo geral de performance...")
	generate_overall_performance_chart.main()

	print("Concluído.")


if __name__ == "__main__":
	main()
