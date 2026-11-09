"""Gera indicadores no terminal e um gráfico de faturamento mensal."""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.analysis import faturamento_mensal, load, resumo_vendas


BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=BASE_DIR / "data" / "vendas.csv")
    parser.add_argument("--output-dir", type=Path, default=BASE_DIR / "images")
    args = parser.parse_args()
    try:
        dados = load(args.csv)
    except (OSError, ValueError) as erro:
        parser.error(str(erro))

    resumo = resumo_vendas(dados)
    print(f"Faturamento total: {resumo['faturamento_total']:.2f}")
    print(f"Unidades vendidas: {resumo['unidades_vendidas']}")
    print(f"Registros de venda: {resumo['registros']}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    mensal = faturamento_mensal(dados)
    figura, eixo = plt.subplots(figsize=(8, 4))
    mensal.plot.bar(ax=eixo, color="#2563eb", rot=0)
    eixo.set(title="Faturamento mensal", xlabel="Mês", ylabel="Faturamento")
    figura.tight_layout()
    destino = args.output_dir / "faturamento.png"
    figura.savefig(destino, dpi=150)
    plt.close(figura)
    mensal.to_csv(args.output_dir / "faturamento_mensal.csv", index_label="Mes")
    print(f"Gráfico: {destino}")


if __name__ == "__main__":
    main()
