"""Leitura, validação e indicadores de vendas a partir de CSV."""

from pathlib import Path

import numpy as np
import pandas as pd


COLUNAS = ("Data", "Produto", "Categoria", "Quantidade", "Preco")


def load(path: str | Path) -> pd.DataFrame:
    """Carrega vendas válidas e calcula faturamento por linha.

    Quantidade representa unidades inteiras; preço e quantidade devem ser
    finitos e não negativos. Não altera o arquivo original.
    """
    dados = pd.read_csv(path)
    faltantes = set(COLUNAS) - set(dados.columns)
    if faltantes:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(sorted(faltantes))}")
    if dados.empty:
        raise ValueError("O CSV precisa conter ao menos uma venda.")

    dados = dados.copy()
    dados["Data"] = pd.to_datetime(dados["Data"], format="%Y-%m-%d", errors="coerce")
    if dados["Data"].isna().any():
        raise ValueError("Data inválida: use o formato AAAA-MM-DD.")

    for coluna in ("Produto", "Categoria"):
        dados[coluna] = dados[coluna].astype("string").str.strip()
        if dados[coluna].isna().any() or dados[coluna].eq("").any():
            raise ValueError(f"{coluna} não pode ficar vazio.")

    for coluna in ("Quantidade", "Preco"):
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")
        if (~np.isfinite(dados[coluna]) | dados[coluna].lt(0)).any():
            raise ValueError(f"{coluna} deve conter números finitos e não negativos.")
    if dados["Quantidade"].mod(1).ne(0).any():
        raise ValueError("Quantidade deve conter unidades inteiras.")

    dados["Faturamento"] = dados["Quantidade"] * dados["Preco"]
    if not np.isfinite(dados["Faturamento"]).all():
        raise ValueError("Faturamento fora do intervalo numérico suportado.")
    return dados


def resumo_vendas(dados: pd.DataFrame) -> dict[str, float | int]:
    """Resume a base carregada; cada linha representa um registro de venda."""
    return {
        "faturamento_total": float(dados["Faturamento"].sum()),
        "unidades_vendidas": int(dados["Quantidade"].sum()),
        "registros": len(dados),
    }


def faturamento_mensal(dados: pd.DataFrame) -> pd.Series:
    """Soma faturamento em ordem cronológica, separando mês e ano."""
    return dados.groupby(dados["Data"].dt.to_period("M"))["Faturamento"].sum().sort_index()
