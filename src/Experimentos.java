import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Random;
import java.util.function.Consumer;

// Etapa 3 - Analise experimental
//
// Mede o tempo de cada algoritmo para tamanhos crescentes (media de 5 execucoes)
// e salva as medicoes brutas em resultados/medicoes.csv e a configuracao da
// maquina em resultados/maquina.txt. Os graficos e as tabelas sao feitos
// depois pelo graficos.py, que le esse CSV.
//
// Uso (na pasta do projeto):  java -cp bin Experimentos
public class Experimentos {

    static final int EXECUCOES = 5;
    static final int[] TAMANHOS = {100, 200, 400, 800, 1600, 3200, 6400};
    static final int[] TAMANHOS_PEQUENOS = {2, 4, 8, 16, 32, 64, 128, 256};
    static final int[] LIMIARES = {2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 128};
    static final int[] N_LIMIAR = {1600, 6400};
    static final int EXECUCOES_LIMIAR = 15; // mais execucoes porque as diferencas entre limiares sao pequenas

    static final List<String> linhasCsv = new ArrayList<>();
    static long lixo = 0; // usamos o resultado para o Java nao "jogar fora" a chamada

    static long[] vetorAleatorio(int n, Random r) {
        long[] v = new long[n];
        for (int i = 0; i < n; i++) v[i] = r.nextInt(201) - 100;
        return v;
    }

    static List<Etapa2.Ponto> pontosAleatorios(int n, Random r) {
        List<Etapa2.Ponto> p = new ArrayList<>(n);
        for (int i = 0; i < n; i++) p.add(new Etapa2.Ponto(r.nextDouble() * 10000, r.nextDouble() * 10000));
        return p;
    }

    // tempo medio de UMA chamada, em segundos (repete a chamada "rep" vezes)
    static <T> double cronometrar(Consumer<T> func, T entrada, int rep) {
        System.gc(); // pede para o coletor de lixo rodar antes, e nao no meio da medicao
        long inicio = System.nanoTime();
        for (int k = 0; k < rep; k++) func.accept(entrada);
        return (System.nanoTime() - inicio) / 1e9 / rep;
    }

    static void registrar(String experimento, String algoritmo, int n, String limiar, int execucao, double tempo) {
        linhasCsv.add(String.format(Locale.US, "%s,%s,%d,%s,%d,%.9f", experimento, algoritmo, n, limiar, execucao, tempo));
    }

    // "aquecimento": o Java compila o codigo durante a execucao (JIT), entao as primeiras
    // chamadas sao bem mais lentas. Rodamos tudo algumas vezes antes de medir.
    static void aquecer() {
        Random r = new Random(99);
        for (int k = 0; k < 600; k++) {
            long[] v = vetorAleatorio(500, r);
            lixo += Etapa1.forcaBruta(v)[0] + Etapa1.divisaoConquista(v)[0] + Etapa1.kadane(v)[0];
            List<Etapa2.Ponto> p = pontosAleatorios(500, r);
            lixo += (long) Etapa2.forcaBruta(p).distancia;
            for (int lim : new int[]{3, 8, 16, 64}) lixo += (long) Etapa2.divisaoConquista(p, lim).distancia;
        }
    }

    // nos tamanhos grandes tambem repetimos a chamada quando ela e muito rapida,
    // para cada medicao durar pelo menos alguns milissegundos (o relogio fica mais preciso)
    static int repeticoesGrandes(int n) { return Math.max(1, 20_000_000 / (n * n)); }

    static int repeticoesEtapa1(int n) { return Math.max(200, 2_000_000 / (n * n)); }
    static int repeticoesEtapa2(int n) { return Math.max(100, 400_000 / (n * n)); }

    public static void main(String[] args) throws IOException {
        Path pasta = Path.of("resultados");
        Files.createDirectories(pasta);
        System.out.println("Aquecendo o Java...");
        aquecer();

        System.out.println("Etapa 1 - tamanhos grandes");
        Random r = new Random(42);
        for (int n : TAMANHOS) {
            int rep = repeticoesGrandes(n);
            for (int e = 1; e <= EXECUCOES; e++) {
                long[] v = vetorAleatorio(n, r);
                registrar("etapa1", "Força bruta", n, "", e, cronometrar(x -> lixo += Etapa1.forcaBruta(x)[0], v, rep));
                registrar("etapa1", "Divisão e conquista", n, "", e, cronometrar(x -> lixo += Etapa1.divisaoConquista(x)[0], v, rep));
                registrar("etapa1", "Kadane O(n)", n, "", e, cronometrar(x -> lixo += Etapa1.kadane(x)[0], v, rep));
            }
            System.out.println("  n = " + n + " ok");
        }

        System.out.println("Etapa 1 - tamanhos pequenos (cada execucao repete a chamada varias vezes)");
        r = new Random(42);
        for (int n : TAMANHOS_PEQUENOS) {
            int rep = repeticoesEtapa1(n);
            for (int e = 1; e <= EXECUCOES; e++) {
                long[] v = vetorAleatorio(n, r);
                registrar("etapa1_pequeno", "Força bruta", n, "", e, cronometrar(x -> lixo += Etapa1.forcaBruta(x)[0], v, rep));
                registrar("etapa1_pequeno", "Divisão e conquista", n, "", e, cronometrar(x -> lixo += Etapa1.divisaoConquista(x)[0], v, rep));
                registrar("etapa1_pequeno", "Kadane O(n)", n, "", e, cronometrar(x -> lixo += Etapa1.kadane(x)[0], v, rep));
            }
        }

        System.out.println("Etapa 2 - tamanhos grandes (D&C com o limiar escolhido)");
        r = new Random(42);
        for (int n : TAMANHOS) {
            int rep = repeticoesGrandes(n);
            for (int e = 1; e <= EXECUCOES; e++) {
                List<Etapa2.Ponto> p = pontosAleatorios(n, r);
                registrar("etapa2", "Força bruta", n, "", e, cronometrar(x -> lixo += (long) Etapa2.forcaBruta(x).distancia, p, rep));
                registrar("etapa2", "Divisão e conquista", n, "", e, cronometrar(x -> lixo += (long) Etapa2.divisaoConquista(x).distancia, p, rep));
            }
            System.out.println("  n = " + n + " ok");
        }

        System.out.println("Etapa 2 - tamanhos pequenos (D&C 'pura', limiar 3)");
        r = new Random(42);
        for (int n : TAMANHOS_PEQUENOS) {
            int rep = repeticoesEtapa2(n);
            for (int e = 1; e <= EXECUCOES; e++) {
                List<Etapa2.Ponto> p = pontosAleatorios(n, r);
                registrar("etapa2_pequeno", "Força bruta", n, "", e, cronometrar(x -> lixo += (long) Etapa2.forcaBruta(x).distancia, p, rep));
                registrar("etapa2_pequeno", "Divisão e conquista", n, "", e, cronometrar(x -> lixo += (long) Etapa2.divisaoConquista(x, 3).distancia, p, rep));
            }
        }

        System.out.println("Etapa 2 - escolha do limiar");
        for (int n : N_LIMIAR) {
            Random rl = new Random(7);
            List<List<Etapa2.Ponto>> entradas = new ArrayList<>();
            for (int e = 0; e < EXECUCOES_LIMIAR; e++) entradas.add(pontosAleatorios(n, rl));
            // as mesmas entradas para todos os limiares (comparacao justa)
            for (int lim : LIMIARES) {
                for (int e = 0; e < EXECUCOES_LIMIAR; e++) {
                    final int l = lim;
                    registrar("etapa2_limiar_" + n, "n = " + n, n, String.valueOf(lim), e + 1,
                            cronometrar(x -> lixo += (long) Etapa2.divisaoConquista(x, l).distancia, entradas.get(e), 20));
                }
            }
            System.out.println("  n = " + n + " ok");
        }

        try (PrintWriter w = new PrintWriter(pasta.resolve("medicoes.csv").toFile(), StandardCharsets.UTF_8)) {
            w.println("experimento,algoritmo,n,limiar,execucao,tempo_s");
            for (String linha : linhasCsv) w.println(linha);
        }

        String cpu = "?";
        try {
            for (String l : Files.readAllLines(Path.of("/proc/cpuinfo"))) {
                if (l.startsWith("model name")) {
                    cpu = l.split(":", 2)[1].trim();
                    break;
                }
            }
        } catch (IOException e) {
            // fora do Linux nao tem /proc/cpuinfo
        }
        try (PrintWriter w = new PrintWriter(pasta.resolve("maquina.txt").toFile(), StandardCharsets.UTF_8)) {
            w.println("processador: " + cpu);
            w.println("nucleos: " + Runtime.getRuntime().availableProcessors());
            w.println("memoria maxima da JVM: " + Runtime.getRuntime().maxMemory() / (1024 * 1024) + " MB");
            w.println("sistema: " + System.getProperty("os.name") + " " + System.getProperty("os.version"));
            w.println("java: " + System.getProperty("java.version") + " (" + System.getProperty("java.vm.name") + ")");
        }
        System.out.println("Pronto! (ignore este numero: " + (lixo % 10) + ")");
    }
}
