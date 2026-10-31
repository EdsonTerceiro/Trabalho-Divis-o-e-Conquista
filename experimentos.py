# Etapa 3 - Analise experimental
#
# Mede o tempo de cada algoritmo para tamanhos crescentes (media de 5 execucoes),
# salva as medicoes brutas em CSV e gera os graficos e as tabelas do relatorio.
#
# Uso:  python experimentos.py           (demora alguns minutos por causa da forca bruta)
#       python experimentos.py --rapido  (so ate n = 1600, para conferir se roda)

import csv
import gc
import math
import os
import platform
import random
import statistics
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import etapa1_subarranjo as e1
import etapa2_par_proximo as e2

RAPIDO = "--rapido" in sys.argv
EXECUCOES = 5
TAMANHOS = [100, 200, 400, 800, 1600, 3200, 6400]
if RAPIDO:
    TAMANHOS = TAMANHOS[:5]
TAMANHOS_PEQUENOS = [2, 4, 8, 16, 32, 64, 128, 256]
LIMIARES = [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 128]
N_LIMIAR = [1600] if RAPIDO else [1600, 6400]
EXECUCOES_LIMIAR = 15  # mais execucoes aqui porque as diferencas entre limiares sao pequenas

PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_RES = os.path.join(PASTA, "resultados")
os.makedirs(PASTA_RES, exist_ok=True)

# cores (paleta categorica fixa) + marcadores diferentes, para nao depender so da cor
ESTILO = {
    "Forca bruta": dict(color="#2a78d6", marker="o"),
    "Divisao e conquista": dict(color="#eb6834", marker="s"),
    "Kadane O(n)": dict(color="#1baf7a", marker="^"),
}

linhas_csv = []  # experimento, algoritmo, n, limiar, execucao, tempo_s


def cronometrar(func, repeticoes=1):
    gc.collect()
    gc.disable()  # o coletor de lixo do Python atrapalha a medicao
    inicio = time.perf_counter()
    for _ in range(repeticoes):
        func()
    fim = time.perf_counter()
    gc.enable()
    return (fim - inicio) / repeticoes


def vetor_aleatorio(n, rng):
    return [rng.randint(-100, 100) for _ in range(n)]


def pontos_aleatorios(n, rng):
    return [(rng.uniform(0, 10000), rng.uniform(0, 10000)) for _ in range(n)]


def medir(experimento, algoritmos, tamanhos, gerador, repeticoes_por_n=None, limiar=""):
    rng = random.Random(42)
    for n in tamanhos:
        rep = repeticoes_por_n(n) if repeticoes_por_n else 1
        for execucao in range(1, EXECUCOES + 1):
            entrada = gerador(n, rng)  # uma entrada nova a cada execucao
            for nome, func in algoritmos.items():
                t = cronometrar(lambda: func(entrada), rep)
                linhas_csv.append([experimento, nome, n, limiar, execucao, t])
        print(f"  {experimento}: n = {n} ok", flush=True)


def medias(experimento, chave="n"):
    # agrupa as medicoes: {algoritmo: {n ou limiar: [tempos]}}
    grupos = {}
    for exp, alg, n, lim, _, t in linhas_csv:
        if exp != experimento:
            continue
        k = n if chave == "n" else lim
        grupos.setdefault(alg, {}).setdefault(k, []).append(t)
    return grupos


def grafico_tempos(experimento, titulo, arquivo, curvas_teoricas):
    grupos = medias(experimento)
    fig, eixos = plt.subplots(1, 2, figsize=(10, 3.8))

    for nome, dados in grupos.items():
        ns = sorted(dados)
        ts = [statistics.mean(dados[n]) for n in ns]
        eixos[0].plot(ns, ts, label=nome, linewidth=2, markersize=6, **ESTILO[nome])
        # grafico normalizado: tempo dividido pela complexidade prevista
        f = curvas_teoricas[nome]
        eixos[1].plot(ns, [t / f(n) for t, n in zip(ts, ns)], linewidth=2, markersize=6,
                      label=f"{nome}: t / {f.__doc__}", **ESTILO[nome])

    eixos[0].set_xscale("log", base=2)
    eixos[0].set_yscale("log")
    eixos[0].set_xlabel("n (escala log)")
    eixos[0].set_ylabel("tempo medio (s, escala log)")
    eixos[0].set_title(titulo)
    eixos[1].set_xscale("log", base=2)
    eixos[1].set_yscale("log")
    eixos[1].set_xlabel("n (escala log)")
    eixos[1].set_ylabel("tempo / complexidade prevista")
    eixos[1].set_title("Normalizado (reta horizontal = bate com a teoria)")
    for ax in eixos:
        ax.grid(True, which="major", color="#dddddd", linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA_RES, arquivo), dpi=150)
    plt.close(fig)


def grafico_simples(experimento, titulo, arquivo, chave="n", xlabel="n"):
    grupos = medias(experimento, chave)
    fig, ax = plt.subplots(figsize=(6, 3.6))
    for nome, dados in grupos.items():
        xs = sorted(dados)
        ts = [statistics.mean(dados[x]) * 1e6 for x in xs]
        ax.plot(xs, ts, label=nome, linewidth=2, markersize=6, **ESTILO[nome])
    ax.set_xscale("log", base=2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("tempo medio (microssegundos)")
    if chave == "n":
        ax.set_yscale("log")
    ax.set_title(titulo)
    ax.grid(True, color="#dddddd", linewidth=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    if len(grupos) > 1:
        ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA_RES, arquivo), dpi=150)
    plt.close(fig)


def grafico_limiar():
    fig, eixos = plt.subplots(1, len(N_LIMIAR), figsize=(5 * len(N_LIMIAR), 3.4), squeeze=False)
    for ax, n in zip(eixos[0], N_LIMIAR):
        dados = medias(f"etapa2_limiar_{n}", "limiar")[f"n = {n}"]
        xs = sorted(dados)
        ts = [statistics.mean(dados[x]) * 1e3 for x in xs]
        dp = [statistics.stdev(dados[x]) * 1e3 for x in xs]
        ax.errorbar(xs, ts, yerr=dp, color="#eb6834", marker="s", linewidth=2, markersize=6, capsize=3)
        melhor = xs[ts.index(min(ts))]
        ax.axvline(e2.LIMIAR_PADRAO, color="#888888", linestyle="--", linewidth=1)
        ax.text(e2.LIMIAR_PADRAO * 1.05, max(ts), f"escolhido = {e2.LIMIAR_PADRAO}", fontsize=8, color="#444444", va="top")
        ax.set_xscale("log", base=2)
        ax.set_xlabel("limiar (escala log)")
        ax.set_ylabel("tempo medio (ms)")
        ax.set_title(f"D&C x limiar, n = {n} (menor media: {melhor})", fontsize=10)
        ax.grid(True, color="#dddddd", linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA_RES, "etapa2_limiar.png"), dpi=150)
    plt.close(fig)


def tabela_latex(experimento, arquivo, chave="n", unidade=1e3, nome_unidade="ms"):
    grupos = medias(experimento, chave)
    algs = list(grupos)
    ks = sorted(next(iter(grupos.values())))
    rotulo = "$n$" if chave == "n" else "limiar"
    linhas = ["\\begin{tabular}{r" + "r" * len(algs) + "}", "\\hline",
              rotulo + " & " + " & ".join(f"{a} ({nome_unidade})" for a in algs) + " \\\\", "\\hline"]
    for k in ks:
        valores = []
        for a in algs:
            ts = grupos[a][k]
            valores.append(f"{statistics.mean(ts) * unidade:.3f} $\\pm$ {statistics.stdev(ts) * unidade:.3f}")
        linhas.append(f"{k} & " + " & ".join(valores) + " \\\\")
    linhas += ["\\hline", "\\end{tabular}"]
    with open(os.path.join(PASTA_RES, arquivo), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")


def config_maquina():
    cpu = platform.processor() or "?"
    try:
        with open("/proc/cpuinfo") as f:
            for linha in f:
                if linha.startswith("model name"):
                    cpu = linha.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    mem = "?"
    try:
        with open("/proc/meminfo") as f:
            kb = int(f.readline().split()[1])
            mem = f"{kb / 1024 / 1024:.1f} GB"
    except OSError:
        pass
    return {
        "processador": cpu,
        "nucleos": os.cpu_count(),
        "memoria": mem,
        "sistema": platform.platform(),
        "python": platform.python_version(),
    }


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    print("Etapa 1 - tamanhos grandes")
    medir("etapa1", {"Forca bruta": e1.forca_bruta,
                     "Divisao e conquista": e1.divisao_conquista,
                     "Kadane O(n)": e1.kadane}, TAMANHOS, vetor_aleatorio)

    print("Etapa 1 - tamanhos pequenos (cada execucao repete a chamada varias vezes)")
    medir("etapa1_pequeno", {"Forca bruta": e1.forca_bruta,
                             "Divisao e conquista": e1.divisao_conquista,
                             "Kadane O(n)": e1.kadane},
          TAMANHOS_PEQUENOS, vetor_aleatorio, repeticoes_por_n=lambda n: max(20, 20000 // n))

    print("Etapa 2 - tamanhos grandes (D&C com o limiar escolhido)")
    medir("etapa2", {"Forca bruta": e2.forca_bruta,
                     "Divisao e conquista": e2.divisao_conquista}, TAMANHOS, pontos_aleatorios)

    print("Etapa 2 - tamanhos pequenos (D&C 'pura', limiar = 3)")
    medir("etapa2_pequeno", {"Forca bruta": e2.forca_bruta,
                             "Divisao e conquista": lambda p: e2.divisao_conquista(p, 3)},
          TAMANHOS_PEQUENOS, pontos_aleatorios, repeticoes_por_n=lambda n: max(10, 4000 // n))

    print("Etapa 2 - escolha do limiar")
    for n in N_LIMIAR:
        rng = random.Random(7)
        entradas = [pontos_aleatorios(n, rng) for _ in range(EXECUCOES_LIMIAR)]
        # as mesmas entradas para todos os limiares (comparacao justa)
        for lim in LIMIARES:
            for execucao, entrada in enumerate(entradas, 1):
                t = cronometrar(lambda: e2.divisao_conquista(entrada, lim))
                linhas_csv.append([f"etapa2_limiar_{n}", f"n = {n}", n, lim, execucao, t])
        print(f"  n = {n} ok", flush=True)

    # CSV com as medicoes brutas
    with open(os.path.join(PASTA_RES, "medicoes.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["experimento", "algoritmo", "n", "limiar", "execucao", "tempo_s"])
        for linha in linhas_csv:
            w.writerow(linha[:5] + [f"{linha[5]:.9f}"])

    with open(os.path.join(PASTA_RES, "maquina.txt"), "w", encoding="utf-8") as f:
        for k, v in config_maquina().items():
            f.write(f"{k}: {v}\n")

    def n2(n):
        "n^2"
        return n * n

    def nlogn(n):
        "n log n"
        return n * math.log2(n)

    def lin(n):
        "n"
        return n

    grafico_tempos("etapa1", "Etapa 1 - subarranjo de soma maxima", "etapa1_tempos.png",
                   {"Forca bruta": n2, "Divisao e conquista": nlogn, "Kadane O(n)": lin})
    grafico_tempos("etapa2", "Etapa 2 - par de pontos mais proximos", "etapa2_tempos.png",
                   {"Forca bruta": n2, "Divisao e conquista": nlogn})
    grafico_simples("etapa1_pequeno", "Etapa 1 - entradas pequenas", "etapa1_pequeno.png")
    grafico_simples("etapa2_pequeno", "Etapa 2 - entradas pequenas (D&C com limiar 3)", "etapa2_pequeno.png")
    grafico_limiar()

    tabela_latex("etapa1", "tabela_etapa1.tex")
    tabela_latex("etapa2", "tabela_etapa2.tex")
    tabela_latex("etapa1_pequeno", "tabela_etapa1_pequeno.tex", unidade=1e6, nome_unidade="$\\mu$s")
    tabela_latex("etapa2_pequeno", "tabela_etapa2_pequeno.tex", unidade=1e6, nome_unidade="$\\mu$s")
    for n in N_LIMIAR:
        tabela_latex(f"etapa2_limiar_{n}", f"tabela_limiar_{n}.tex", chave="limiar")
    print("Pronto! Resultados em", PASTA_RES)
