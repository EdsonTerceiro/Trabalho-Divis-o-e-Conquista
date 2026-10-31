# Etapa 2 - Par de Pontos Mais Proximos
#
# Entrada (stdin): um inteiro n (n >= 2) seguido de n pares "x y".
# Saida: a menor distancia (6 casas decimais) e os dois pontos do par.
# Se houver mais de um par com a menor distancia, qualquer um deles e aceito
# (os testes conferem a distancia).
#
# Uso:  python etapa2_par_proximo.py [forca|dc] < entrada.txt

import math
import sys

from ordenacao import combinacao, merge_sort, quick_sort

INFINITO = float("inf")

# limiar: se o subproblema tiver ate LIMIAR pontos, resolve por forca bruta.
# O valor foi escolhido pelos experimentos (ver experimentos.py e o relatorio).
LIMIAR_PADRAO = 8


def distancia(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def pela_x(p):
    return (p[0], p[1])


def pela_y(p):
    return p[1]


# ---------------------------------------------------------------------------
# 1) Forca bruta - O(n^2): compara todos os pares
# ---------------------------------------------------------------------------
def forca_bruta(pontos):
    n = len(pontos)
    melhor_d = INFINITO
    melhor_par = None
    for i in range(n):
        for j in range(i + 1, n):
            d = distancia(pontos[i], pontos[j])
            if d < melhor_d:
                melhor_d = d
                melhor_par = (pontos[i], pontos[j])
    return melhor_d, melhor_par


# ---------------------------------------------------------------------------
# 2) Divisao e conquista - O(n log n)
#    T(n) = 2T(n/2) + O(n)
# ---------------------------------------------------------------------------
def dc_recursivo(px, limiar):
    # px: pontos ordenados por x.
    # devolve (distancia, par, pontos ordenados por y)
    n = len(px)

    if n <= limiar:
        d, par = forca_bruta(px)
        return d, par, merge_sort(px, pela_y)

    # dividir pela linha vertical na mediana dos x
    meio = n // 2
    x_meio = px[meio][0]

    d_esq, par_esq, py_esq = dc_recursivo(px[:meio], limiar)
    d_dir, par_dir, py_dir = dc_recursivo(px[meio:], limiar)

    if d_esq <= d_dir:
        delta, par = d_esq, par_esq
    else:
        delta, par = d_dir, par_dir

    # a "combinacao" do merge sort junta os dois lados ja ordenados por y em O(n).
    # Assim nao precisamos reordenar por y em todo nivel da recursao.
    py = combinacao(py_esq, py_dir, pela_y)

    # faixa de largura 2*delta em volta da linha
    faixa = [p for p in py if abs(p[0] - x_meio) < delta]

    # cada ponto da faixa so precisa ser comparado com os 7 seguintes (ordem por y)
    for i in range(len(faixa)):
        for j in range(i + 1, min(i + 8, len(faixa))):
            if faixa[j][1] - faixa[i][1] >= delta:
                break  # daqui pra frente so fica mais longe em y
            d = distancia(faixa[i], faixa[j])
            if d < delta:
                delta = d
                par = (faixa[i], faixa[j])

    return delta, par, py


def divisao_conquista(pontos, limiar=LIMIAR_PADRAO):
    if len(pontos) < 2:
        raise ValueError("precisa de pelo menos 2 pontos")
    px = list(pontos)  # copia para nao alterar a lista de quem chamou
    quick_sort(px, 0, len(px) - 1, pela_x)  # ordenacao inicial por x
    d, par, _ = dc_recursivo(px, max(limiar, 1))
    return d, par


ALGORITMOS = {
    "forca": forca_bruta,
    "dc": divisao_conquista,
}


def converter(texto):
    return float(texto) if ("." in texto or "e" in texto.lower()) else int(texto)


def ler_entrada(texto):
    numeros = texto.split()
    n = int(numeros[0])
    valores = [converter(v) for v in numeros[1:2 * n + 1]]
    if n < 2 or len(valores) != 2 * n:
        raise ValueError("entrada invalida: precisa de n >= 2 e n pares x y")
    return [(valores[2 * k], valores[2 * k + 1]) for k in range(n)]


if __name__ == "__main__":
    nome = sys.argv[1] if len(sys.argv) > 1 else "dc"
    pontos = ler_entrada(sys.stdin.read())
    d, (p, q) = ALGORITMOS[nome](pontos)
    print(f"{d:.6f}")
    print(p[0], p[1])
    print(q[0], q[1])
