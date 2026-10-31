# Algoritmos de ordenacao vistos em aula (merge sort e quick sort).
# Aqui eles foram adaptados para receber uma "chave" (funcao que diz por qual
# valor comparar), porque na Etapa 2 precisamos ordenar pontos por x e por y.
#
# Correcao em relacao a versao da aula: na funcao combinacao faltava o "i += 1"
# dentro do if, o que fazia o while nunca terminar.

import random


def merge_sort(vetor, chave=lambda v: v):
    if len(vetor) <= 1:
        return vetor

    meio = len(vetor) // 2
    esquerda = merge_sort(vetor[:meio], chave)
    direita = merge_sort(vetor[meio:], chave)

    return combinacao(esquerda, direita, chave)


def combinacao(esquerda, direita, chave=lambda v: v):
    resultado_ordenado = []
    i = 0
    j = 0

    while i < len(esquerda) and j < len(direita):
        if chave(esquerda[i]) <= chave(direita[j]):
            resultado_ordenado.append(esquerda[i])
            i += 1  # <- estava faltando na versao da aula
        else:
            resultado_ordenado.append(direita[j])
            j += 1
    resultado_ordenado.extend(esquerda[i:])
    resultado_ordenado.extend(direita[j:])
    return resultado_ordenado


def quick_sort(vetor, low, high, chave=lambda v: v):
    # Mesma ideia da aula (particao de Lomuto, pivo na posicao high).
    # Mudanca: sorteamos um pivo e trocamos ele com o high antes de particionar.
    # Sem isso, um vetor ja ordenado cai no pior caso O(n^2) e estoura o
    # limite de recursao do Python com alguns milhares de elementos.
    # Tambem fazemos a recursao so na parte menor e um "while" na maior,
    # para a pilha ficar no maximo O(log n).
    while low < high:
        k = random.randint(low, high)
        vetor[k], vetor[high] = vetor[high], vetor[k]

        pivot = chave(vetor[high])
        i = low

        for j in range(low, high):
            if chave(vetor[j]) < pivot:
                vetor[i], vetor[j] = vetor[j], vetor[i]
                i += 1

        vetor[i], vetor[high] = vetor[high], vetor[i]

        if i - low < high - i:
            quick_sort(vetor, low, i - 1, chave)
            low = i + 1
        else:
            quick_sort(vetor, i + 1, high, chave)
            high = i - 1


if __name__ == "__main__":
    vetor_original = [30, 2, 1, 22, 45, 3, 13, 70, 400]
    print(f"merge: {vetor_original} -> {merge_sort(vetor_original)}")

    vetor = [random.randint(0, 120) for n in range(20)]
    print(f"vetor desordenado {vetor}")
    quick_sort(vetor, 0, len(vetor) - 1)
    print(f"vetor ordenado {vetor}")
