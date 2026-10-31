# Le resultados/medicoes.csv (gerado pelo Experimentos.java) e faz os graficos
# e as tabelas do relatorio. Usamos Python so aqui, porque o matplotlib
# e bem mais simples para gerar graficos do que fazer isso em Java.
#
# Uso:  pip install matplotlib
#       python3 graficos.py

import csv
import math
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
LIMIAR_ESCOLHIDO = 6  # mesmo valor de Etapa2.LIMIAR_PADRAO

ESTILO = {
    "Força bruta": dict(color="#2a78d6", marker="o"),
    "Divisão e conquista": dict(color="#eb6834", marker="s"),
    "Kadane O(n)": dict(color="#1baf7a", marker="^"),
}

linhas = []
with open(os.path.join(PASTA, "medicoes.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        linhas.append(r)


def medias(experimento, chave="n"):
    grupos = {}
    for r in linhas:
        if r["experimento"] != experimento:
            continue
        k = int(r[chave])
        grupos.setdefault(r["algoritmo"], {}).setdefault(k, []).append(float(r["tempo_s"]))
    return grupos


def n2(n):
    "n^2"
    return n * n


def nlogn(n):
    "n log n"
    return n * math.log2(n)


def lin(n):
    "n"
    return n


def grafico_tempos(experimento, titulo, arquivo, curvas):
    grupos = medias(experimento)
    fig, eixos = plt.subplots(1, 2, figsize=(10, 3.8))
    for nome, dados in grupos.items():
        ns = sorted(dados)
        ts = [statistics.mean(dados[n]) for n in ns]
        eixos[0].plot(ns, ts, label=nome, linewidth=2, markersize=6, **ESTILO[nome])
        f = curvas[nome]
        eixos[1].plot(ns, [t / f(n) for t, n in zip(ts, ns)], linewidth=2, markersize=6,
                      label=f"{nome}: t / {f.__doc__}", **ESTILO[nome])
    eixos[0].set_ylabel("tempo medio (s, escala log)")
    eixos[0].set_title(titulo)
    eixos[1].set_ylabel("tempo / complexidade prevista")
    eixos[1].set_title("Normalizado (reta horizontal = bate com a teoria)")
    for ax in eixos:
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xlabel("n (escala log)")
        ax.grid(True, which="major", color="#dddddd", linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA, arquivo), dpi=150)
    plt.close(fig)


def grafico_pequeno(experimento, titulo, arquivo):
    grupos = medias(experimento)
    fig, ax = plt.subplots(figsize=(6, 3.6))
    for nome, dados in grupos.items():
        xs = sorted(dados)
        ax.plot(xs, [statistics.mean(dados[x]) * 1e6 for x in xs], label=nome, linewidth=2, markersize=6, **ESTILO[nome])
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("tempo medio (microssegundos)")
    ax.set_title(titulo)
    ax.grid(True, color="#dddddd", linewidth=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA, arquivo), dpi=150)
    plt.close(fig)


def grafico_limiar(ns):
    fig, eixos = plt.subplots(1, len(ns), figsize=(5 * len(ns), 3.4), squeeze=False)
    for ax, n in zip(eixos[0], ns):
        dados = medias(f"etapa2_limiar_{n}", "limiar")[f"n = {n}"]
        xs = sorted(dados)
        ts = [statistics.mean(dados[x]) * 1e3 for x in xs]
        dp = [statistics.stdev(dados[x]) * 1e3 for x in xs]
        ax.errorbar(xs, ts, yerr=dp, color="#eb6834", marker="s", linewidth=2, markersize=6, capsize=3)
        melhor = xs[ts.index(min(ts))]
        ax.axvline(LIMIAR_ESCOLHIDO, color="#888888", linestyle="--", linewidth=1)
        ax.text(LIMIAR_ESCOLHIDO * 1.05, max(ts), f"escolhido = {LIMIAR_ESCOLHIDO}", fontsize=8, color="#444444", va="top")
        ax.set_xscale("log", base=2)
        ax.set_xlabel("limiar (escala log)")
        ax.set_ylabel("tempo medio (ms)")
        ax.set_title(f"D&C x limiar, n = {n} (menor media: {melhor})", fontsize=10)
        ax.grid(True, color="#dddddd", linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA, "etapa2_limiar.png"), dpi=150)
    plt.close(fig)


def tabela(experimento, chave="n", unidade=1e3, nome_unidade="ms"):
    grupos = medias(experimento, chave)
    algs = list(grupos)
    ks = sorted(next(iter(grupos.values())))
    rotulo = "n" if chave == "n" else "limiar"
    saida = [f"| {rotulo} | " + " | ".join(f"{a} ({nome_unidade})" for a in algs) + " |",
             "| " + " | ".join(["---"] * (len(algs) + 1)) + " |"]
    for k in ks:
        vals = []
        for a in algs:
            ts = grupos[a][k]
            vals.append(f"{statistics.mean(ts) * unidade:.3f} ± {statistics.stdev(ts) * unidade:.3f}".replace(".", ","))
        saida.append(f"| {k} | " + " | ".join(vals) + " |")
    return "\n".join(saida)


if __name__ == "__main__":
    grafico_tempos("etapa1", "Etapa 1 - subarranjo de soma maxima", "etapa1_tempos.png",
                   {"Força bruta": n2, "Divisão e conquista": nlogn, "Kadane O(n)": lin})
    grafico_tempos("etapa2", "Etapa 2 - par de pontos mais proximos", "etapa2_tempos.png",
                   {"Força bruta": n2, "Divisão e conquista": nlogn})
    grafico_pequeno("etapa1_pequeno", "Etapa 1 - entradas pequenas", "etapa1_pequeno.png")
    grafico_pequeno("etapa2_pequeno", "Etapa 2 - entradas pequenas (D&C com limiar 3)", "etapa2_pequeno.png")
    ns_limiar = sorted({int(r["n"]) for r in linhas if r["experimento"].startswith("etapa2_limiar_")})
    grafico_limiar(ns_limiar)

    with open(os.path.join(PASTA, "tabelas.md"), "w", encoding="utf-8") as f:
        f.write("## Etapa 1 (ms)\n\n" + tabela("etapa1") + "\n\n")
        f.write("## Etapa 2 (ms)\n\n" + tabela("etapa2") + "\n\n")
        f.write("## Etapa 1, entradas pequenas (us)\n\n" + tabela("etapa1_pequeno", unidade=1e6, nome_unidade="µs") + "\n\n")
        f.write("## Etapa 2, entradas pequenas (us)\n\n" + tabela("etapa2_pequeno", unidade=1e6, nome_unidade="µs") + "\n\n")
        for n in ns_limiar:
            f.write(f"## Limiar, n = {n} (ms)\n\n" + tabela(f"etapa2_limiar_{n}", chave="limiar") + "\n\n")
    print("Graficos e tabelas em", PASTA)
