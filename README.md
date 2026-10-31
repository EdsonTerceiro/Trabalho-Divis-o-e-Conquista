# Trabalho Prático: Divisão e Conquista

Dupla: Amanda Uchoa e Francisco Edson.
Linguagem: Java 21 (funciona a partir do Java 17), sem bibliotecas externas.
Os gráficos são gerados por um script Python pequeno (`graficos.py`, com `matplotlib`), a partir do CSV que o Java grava.

## Arquivos

| Arquivo | O que tem |
|---|---|
| `src/Ordenacao.java` | merge sort e quick sort da aula, adaptados para ordenar por um `Comparator` (usados na Etapa 2) |
| `src/Etapa1.java` | Etapa 1: força bruta O(n²), divisão e conquista O(n log n) e Kadane O(n) |
| `src/Etapa2.java` | Etapa 2: força bruta O(n²) e divisão e conquista O(n log n) com limiar |
| `casos_de_teste.txt` | casos de teste com entrada, saída esperada e motivo de cada um |
| `src/Testes.java` | bateria de testes: casos do arquivo, testes aleatórios contra a força bruta e testes pela linha de comando |
| `src/Experimentos.java` | Etapa 3: mede os tempos e grava `resultados/medicoes.csv` e `resultados/maquina.txt` |
| `graficos.py` | lê o CSV e gera os gráficos `.png` e as tabelas (`resultados/tabelas.md`) |
| `resultados/` | medições brutas, configuração da máquina, gráficos e tabelas |
| `relatorio/` | relatório em PDF |

## Como executar

Compilar (na pasta do projeto):

```
javac -encoding UTF-8 -d bin src/*.java
```

Etapa 1. A entrada é `n` seguido de `n` inteiros. A saída é `soma inicio fim`, com índices a partir de 0:

```
echo "9  -2 1 -3 4 -1 2 1 -5 4" | java -cp bin Etapa1 dc       # divisão e conquista
echo "9  -2 1 -3 4 -1 2 1 -5 4" | java -cp bin Etapa1 forca    # força bruta
echo "9  -2 1 -3 4 -1 2 1 -5 4" | java -cp bin Etapa1 kadane   # O(n)
# saída: 6 3 6
```

Regra de desempate: maior soma; se empatar, menor início; se empatar de novo, menor fim.

Etapa 2. A entrada é `n` seguido de `n` pares `x y`. A saída é a distância (6 casas) e os dois pontos:

```
printf "4\n0 0\n5 5\n1 1\n9 9\n" | java -cp bin Etapa2 dc      # ou: forca
# saída:
# 1.414214
# 0 0
# 1 1
```

Testes:

```
java -cp bin Testes
```

Experimentos (cerca de 40 segundos) e gráficos:

```
java -cp bin Experimentos
pip install matplotlib
python3 graficos.py
```
