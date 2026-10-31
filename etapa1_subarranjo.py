# Etapa 1 - Subarranjo de Soma Maxima
#
# Entrada (stdin): um inteiro n seguido de n inteiros.
# Saida: soma maxima, indice de inicio e indice de fim (indices comecam em 0).
#
# Regra de desempate (as 3 versoes seguem a mesma regra):
#   1) maior soma;
#   2) se empatar, o intervalo que comeca mais cedo (menor inicio);
#   3) se ainda empatar, o intervalo mais curto (menor fim).
# Como pelo menos um elemento sempre e escolhido, um vetor so de negativos
# devolve o maior negativo (e nao 0).
#
# Uso:  python etapa1_subarranjo.py [forca|dc|kadane] < entrada.txt

import sys


def melhor(a, b):
    # devolve o melhor entre duas respostas (soma, inicio, fim) seguindo a regra de desempate
    if a[0] != b[0]:
        return a if a[0] > b[0] else b
    if a[1] != b[1]:
        return a if a[1] < b[1] else b
    return a if a[2] <= b[2] else b


# ---------------------------------------------------------------------------
# 1) Forca bruta - O(n^2)
# ---------------------------------------------------------------------------
def forca_bruta(vetor):
    n = len(vetor)
    melhor_soma = vetor[0]
    melhor_ini = 0
    melhor_fim = 0

    for i in range(n):
        soma = 0
        for j in range(i, n):
            soma += vetor[j]  # soma de vetor[i..j] aproveitando a anterior
            # so troca se for estritamente maior: assim ficamos com o menor i e o menor j
            if soma > melhor_soma:
                melhor_soma = soma
                melhor_ini = i
                melhor_fim = j

    return melhor_soma, melhor_ini, melhor_fim


# ---------------------------------------------------------------------------
# 2) Divisao e conquista - O(n log n)
#    T(n) = 2T(n/2) + O(n)
# ---------------------------------------------------------------------------
def cruzando_o_meio(vetor, low, meio, high):
    # melhor parte da esquerda que termina em meio
    soma = 0
    melhor_esq = vetor[meio]
    ini = meio
    for i in range(meio, low - 1, -1):
        soma += vetor[i]
        if soma >= melhor_esq:  # ">=" porque, empatando, queremos o inicio menor
            melhor_esq = soma
            ini = i

    # melhor parte da direita que comeca em meio+1
    soma = 0
    melhor_dir = vetor[meio + 1]
    fim = meio + 1
    for j in range(meio + 1, high + 1):
        soma += vetor[j]
        if soma > melhor_dir:  # ">" porque, empatando, queremos o fim menor
            melhor_dir = soma
            fim = j

    return melhor_esq + melhor_dir, ini, fim


def dc_recursivo(vetor, low, high):
    if low == high:  # caso base: um elemento so
        return vetor[low], low, low

    meio = (low + high) // 2
    esquerda = dc_recursivo(vetor, low, meio)
    direita = dc_recursivo(vetor, meio + 1, high)
    cruza = cruzando_o_meio(vetor, low, meio, high)

    # a resposta e o maior dos tres valores
    return melhor(melhor(esquerda, cruza), direita)


def divisao_conquista(vetor):
    return dc_recursivo(vetor, 0, len(vetor) - 1)


# ---------------------------------------------------------------------------
# 3) Questao desafio: versao O(n) (algoritmo de Kadane)
# ---------------------------------------------------------------------------
def kadane(vetor):
    atual = vetor[0]   # melhor soma de um intervalo que termina na posicao j
    ini_atual = 0
    resposta = (vetor[0], 0, 0)

    for j in range(1, len(vetor)):
        if atual >= 0:
            # vale a pena continuar o intervalo (se atual == 0, a soma e a mesma
            # mas o inicio fica menor, que e o que a regra de desempate pede)
            atual += vetor[j]
        else:
            # o que veio antes so atrapalha: comeca de novo em j
            atual = vetor[j]
            ini_atual = j
        resposta = melhor(resposta, (atual, ini_atual, j))

    return resposta


ALGORITMOS = {
    "forca": forca_bruta,
    "dc": divisao_conquista,
    "kadane": kadane,
}


def ler_entrada(texto):
    numeros = texto.split()
    n = int(numeros[0])
    vetor = [int(x) for x in numeros[1:n + 1]]
    if n < 1 or len(vetor) != n:
        raise ValueError("entrada invalida: precisa de n >= 1 e n numeros")
    return vetor


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    nome = sys.argv[1] if len(sys.argv) > 1 else "dc"
    vetor = ler_entrada(sys.stdin.read())
    soma, ini, fim = ALGORITMOS[nome](vetor)
    print(soma, ini, fim)
