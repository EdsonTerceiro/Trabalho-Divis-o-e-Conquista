# Trabalho Prático: Divisão e Conquista

Dupla: Amanda Uchoa e _[nome do(a) colega]_.
Linguagem: Python 3 (testado no 3.13). Só a biblioteca padrão, mais `matplotlib` para os gráficos.

## Arquivos

| Arquivo | O que tem |
|---|---|
| `ordenacao.py` | merge sort e quick sort da aula, adaptados para ordenar por uma chave (usados na Etapa 2) |
| `etapa1_subarranjo.py` | Etapa 1: força bruta O(n²), divisão e conquista O(n log n) e Kadane O(n) |
| `etapa2_par_proximo.py` | Etapa 2: força bruta O(n²) e divisão e conquista O(n log n) com limiar |
| `casos_de_teste.json` | casos de teste com entrada, saída esperada e justificativa |
| `testes.py` | bateria de testes (casos do arquivo, testes aleatórios contra a força bruta e testes da linha de comando) |
| `experimentos.py` | Etapa 3: mede os tempos, gera o CSV, os gráficos e as tabelas |
| `resultados/` | `medicoes.csv` (medições brutas), `maquina.txt` (configuração da máquina), gráficos `.png` e tabelas |
| `relatorio/` | fonte LaTeX e PDF do relatório |

## Como executar

Etapa 1. A entrada é `n` seguido de `n` inteiros. A saída é `soma inicio fim`, com índices a partir de 0:

```
echo "9  -2 1 -3 4 -1 2 1 -5 4" | python3 etapa1_subarranjo.py dc       # divisão e conquista
echo "9  -2 1 -3 4 -1 2 1 -5 4" | python3 etapa1_subarranjo.py forca    # força bruta
echo "9  -2 1 -3 4 -1 2 1 -5 4" | python3 etapa1_subarranjo.py kadane   # O(n)
# saída: 6 3 6
```

Regra de desempate: maior soma; se empatar, menor início; se empatar de novo, menor fim.

Etapa 2. A entrada é `n` seguido de `n` pares `x y`. A saída é a distância (6 casas) e os dois pontos:

```
printf "4\n0 0\n5 5\n1 1\n9 9\n" | python3 etapa2_par_proximo.py dc      # ou: forca
# saída:
# 1.414214
# 0 0
# 1 1
```

Testes:

```
python3 testes.py
```

Experimentos (cerca de 1 minuto; `--rapido` vai só até n = 1600):

```
pip install matplotlib
python3 experimentos.py
```

Relatório (precisa de LaTeX):

```
cd relatorio && pdflatex relatorio.tex && pdflatex relatorio.tex
```
