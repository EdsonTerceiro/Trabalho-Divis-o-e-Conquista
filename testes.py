# Bateria de testes do trabalho.
# 1) Roda todos os casos de casos_de_teste.json (entradas e saidas esperadas).
# 2) Compara forca bruta x divisao e conquista (x Kadane) em muitas entradas aleatorias.
# 3) Testa a leitura pela linha de comando (stdin), igual o professor vai fazer.
#
# Uso:  python testes.py

import json
import os
import random
import subprocess
import sys
import unittest

import etapa1_subarranjo as e1
import etapa2_par_proximo as e2
from ordenacao import merge_sort, quick_sort

PASTA = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(PASTA, "casos_de_teste.json"), encoding="utf-8") as f:
    CASOS = json.load(f)

LIMIARES_TESTADOS = [1, 2, 3, 4, 8, e2.LIMIAR_PADRAO]


class TesteOrdenacao(unittest.TestCase):
    def test_merge_e_quick(self):
        for _ in range(200):
            v = [random.randint(-50, 50) for _ in range(random.randint(0, 40))]
            self.assertEqual(merge_sort(v), sorted(v))
            w = list(v)
            quick_sort(w, 0, len(w) - 1)
            self.assertEqual(w, sorted(v))

    def test_quick_vetor_ja_ordenado_grande(self):
        # sem o pivo aleatorio isso estourava a recursao
        v = list(range(20000))
        quick_sort(v, 0, len(v) - 1)
        self.assertEqual(v, list(range(20000)))


class TesteEtapa1(unittest.TestCase):
    def test_casos_do_arquivo(self):
        for caso in CASOS["etapa1"]:
            vetor = e1.ler_entrada(caso["entrada"])
            esperado = tuple(caso["saida"])
            for nome, func in e1.ALGORITMOS.items():
                with self.subTest(caso=caso["id"], algoritmo=nome):
                    self.assertEqual(func(vetor), esperado)

    def test_aleatorio_compara_com_forca_bruta(self):
        random.seed(1)
        for _ in range(3000):
            n = random.randint(1, 40)
            faixa = random.choice([2, 5, 100])  # faixa pequena gera muitos empates
            vetor = [random.randint(-faixa, faixa) for _ in range(n)]
            esperado = e1.forca_bruta(vetor)
            self.assertEqual(e1.divisao_conquista(vetor), esperado, vetor)
            self.assertEqual(e1.kadane(vetor), esperado, vetor)

    def test_aleatorio_so_negativos(self):
        random.seed(2)
        for _ in range(500):
            vetor = [random.randint(-30, -1) for _ in range(random.randint(1, 30))]
            maior = max(vetor)
            esperado = (maior, vetor.index(maior), vetor.index(maior))
            for func in e1.ALGORITMOS.values():
                self.assertEqual(func(vetor), esperado)

    def test_resposta_e_coerente(self):
        # a soma devolvida tem que ser a soma do intervalo devolvido
        random.seed(3)
        for _ in range(500):
            vetor = [random.randint(-20, 20) for _ in range(random.randint(1, 60))]
            for func in e1.ALGORITMOS.values():
                soma, ini, fim = func(vetor)
                self.assertTrue(0 <= ini <= fim < len(vetor))
                self.assertEqual(sum(vetor[ini:fim + 1]), soma)

    def test_entrada_invalida(self):
        with self.assertRaises(ValueError):
            e1.ler_entrada("0")
        with self.assertRaises(ValueError):
            e1.ler_entrada("3\n1 2")


class TesteEtapa2(unittest.TestCase):
    def test_casos_do_arquivo(self):
        for caso in CASOS["etapa2"]:
            pontos = e2.ler_entrada(caso["entrada"])
            with self.subTest(caso=caso["id"], algoritmo="forca"):
                self.assertAlmostEqual(e2.forca_bruta(pontos)[0], caso["saida"], places=6)
            for limiar in LIMIARES_TESTADOS:
                with self.subTest(caso=caso["id"], algoritmo="dc", limiar=limiar):
                    self.assertAlmostEqual(e2.divisao_conquista(pontos, limiar)[0], caso["saida"], places=6)

    def test_aleatorio_compara_com_forca_bruta(self):
        random.seed(4)
        for _ in range(1500):
            n = random.randint(2, 80)
            lado = random.choice([3, 20, 1000])  # lado pequeno gera pontos repetidos e x iguais
            pontos = [(random.randint(-lado, lado), random.randint(-lado, lado)) for _ in range(n)]
            esperado = e2.forca_bruta(pontos)[0]
            for limiar in LIMIARES_TESTADOS:
                self.assertAlmostEqual(e2.divisao_conquista(pontos, limiar)[0], esperado, places=9)

    def test_aleatorio_float(self):
        random.seed(5)
        for _ in range(300):
            pontos = [(random.uniform(0, 1), random.uniform(0, 1)) for _ in range(random.randint(2, 200))]
            esperado = e2.forca_bruta(pontos)[0]
            self.assertAlmostEqual(e2.divisao_conquista(pontos, 2)[0], esperado, places=12)

    def test_par_devolvido_e_coerente(self):
        random.seed(6)
        for _ in range(300):
            pontos = [(random.randint(0, 50), random.randint(0, 50)) for _ in range(random.randint(2, 60))]
            d, (p, q) = e2.divisao_conquista(pontos, 2)
            self.assertAlmostEqual(e2.distancia(p, q), d)
            self.assertIn(p, pontos)
            self.assertIn(q, pontos)

    def test_nao_altera_entrada(self):
        pontos = [(5, 1), (1, 1), (3, 3)]
        copia = list(pontos)
        e2.divisao_conquista(pontos)
        self.assertEqual(pontos, copia)

    def test_entrada_invalida(self):
        with self.assertRaises(ValueError):
            e2.ler_entrada("1\n0 0")


class TesteLinhaDeComando(unittest.TestCase):
    def rodar(self, script, algoritmo, entrada):
        r = subprocess.run([sys.executable, os.path.join(PASTA, script), algoritmo],
                           input=entrada, capture_output=True, text=True, check=True)
        return r.stdout.split()

    def test_etapa1_cli(self):
        for caso in CASOS["etapa1"]:
            for alg in ("forca", "dc", "kadane"):
                saida = self.rodar("etapa1_subarranjo.py", alg, caso["entrada"])
                self.assertEqual([int(x) for x in saida], caso["saida"])

    def test_etapa2_cli(self):
        for caso in CASOS["etapa2"]:
            for alg in ("forca", "dc"):
                saida = self.rodar("etapa2_par_proximo.py", alg, caso["entrada"])
                self.assertAlmostEqual(float(saida[0]), caso["saida"], places=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
