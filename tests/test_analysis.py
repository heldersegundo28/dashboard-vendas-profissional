"""Regressões de cálculos e rejeição de bases inválidas."""

import tempfile
import unittest
from pathlib import Path

from src.analysis import faturamento_mensal, load, resumo_vendas


class AnaliseVendasTest(unittest.TestCase):
    def carregar(self, conteudo):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "vendas.csv"
            arquivo.write_text(conteudo, encoding="utf-8")
            return load(arquivo)

    def test_indicadores_da_base_de_exemplo(self):
        dados = load(Path(__file__).resolve().parents[1] / "data" / "vendas.csv")
        self.assertEqual(resumo_vendas(dados), {
            "faturamento_total": 1550.0, "unidades_vendidas": 15, "registros": 2,
        })

    def test_agrega_mes_e_ano_em_ordem_cronologica(self):
        dados = self.carregar(
            "Data,Produto,Categoria,Quantidade,Preco\n"
            "2026-02-01,Mouse,Perifericos,2,10.50\n"
            "2026-01-15,Mouse,Perifericos,3,10\n"
            "2026-02-05,Teclado,Perifericos,1,20\n"
            "2027-01-01,Mouse,Perifericos,1,15\n"
        )
        mensal = faturamento_mensal(dados)
        self.assertEqual([str(mes) for mes in mensal.index], ["2026-01", "2026-02", "2027-01"])
        self.assertEqual(mensal.tolist(), [30, 41, 15])

    def test_rejeita_colunas_ausentes(self):
        with self.assertRaisesRegex(ValueError, "Colunas obrigatórias"):
            self.carregar("Data,Produto\n2026-01-01,Mouse\n")

    def test_rejeita_base_vazia(self):
        with self.assertRaisesRegex(ValueError, "ao menos uma venda"):
            self.carregar("Data,Produto,Categoria,Quantidade,Preco\n")

    def test_rejeita_datas_invalidas(self):
        with self.assertRaisesRegex(ValueError, "Data inválida"):
            self.carregar("Data,Produto,Categoria,Quantidade,Preco\n2026-02-30,Mouse,Perifericos,1,10\n")

    def test_rejeita_numeros_invalidos(self):
        for quantidade, preco in [("-1", "10"), ("1", "-2"), ("abc", "10"),
                                  ("1", ""), ("inf", "1"), ("1", "inf"), ("1.5", "10")]:
            with self.subTest(quantidade=quantidade, preco=preco), self.assertRaises(ValueError):
                self.carregar("Data,Produto,Categoria,Quantidade,Preco\n"
                              f"2026-01-01,Mouse,Perifericos,{quantidade},{preco}\n")

    def test_rejeita_produto_ou_categoria_vazios(self):
        for produto, categoria in [("", "Perifericos"), ("Mouse", " ")]:
            with self.subTest(produto=produto), self.assertRaises(ValueError):
                self.carregar("Data,Produto,Categoria,Quantidade,Preco\n"
                              f"2026-01-01,{produto},{categoria},1,10\n")

    def test_aceita_zero_e_remove_espacos(self):
        dados = self.carregar("Data,Produto,Categoria,Quantidade,Preco\n"
                             "2026-01-01, Mouse , Perifericos ,0,10\n")
        self.assertEqual(dados.iloc[0]["Produto"], "Mouse")
        self.assertEqual(resumo_vendas(dados)["faturamento_total"], 0)


if __name__ == "__main__":
    unittest.main()
