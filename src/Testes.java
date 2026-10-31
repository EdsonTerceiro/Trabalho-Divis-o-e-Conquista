import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.Random;

// Bateria de testes do trabalho (sem bibliotecas externas).
// 1) Roda todos os casos de casos_de_teste.txt (entrada e saida esperada).
// 2) Compara forca bruta x divisao e conquista (x Kadane) em muitas entradas aleatorias.
// 3) Testa a leitura pela linha de comando (stdin), igual o professor vai fazer.
//
// Uso (na pasta do projeto):  java -cp bin Testes
public class Testes {

    static int passou = 0;
    static int falhou = 0;

    static final int[] LIMIARES_TESTADOS = {1, 2, 3, 4, 8, 12, Etapa2.LIMIAR_PADRAO, 32};

    static void confere(boolean ok, String descricao) {
        if (ok) {
            passou++;
        } else {
            falhou++;
            System.out.println("FALHOU: " + descricao);
        }
    }

    static boolean quase(double a, double b) {
        return Math.abs(a - b) < 1e-6;
    }

    // ---------------- leitura do arquivo de casos ----------------
    static class Caso {
        String id, etapa, motivo, entrada, saida;
    }

    static List<Caso> lerCasos(String arquivo) throws IOException {
        List<Caso> casos = new ArrayList<>();
        List<String> linhas = Files.readAllLines(Path.of(arquivo), StandardCharsets.UTF_8);
        Caso atual = null;
        String secao = "";
        StringBuilder texto = new StringBuilder();
        for (String linha : linhas) {
            if (linha.startsWith("#")) continue;
            if (linha.startsWith("CASO ")) {
                String[] partes = linha.split(" ");
                atual = new Caso();
                atual.id = partes[1];
                atual.etapa = partes[2];
            } else if (linha.startsWith("MOTIVO ")) {
                atual.motivo = linha.substring(7);
            } else if (linha.equals("ENTRADA") || linha.equals("SAIDA")) {
                secao = linha;
                texto.setLength(0);
            } else if (linha.equals("FIM")) {
                atual.saida = texto.toString().trim();
                casos.add(atual);
                secao = "";
            } else if (!secao.isEmpty()) {
                texto.append(linha).append("\n");
                if (secao.equals("ENTRADA")) atual.entrada = texto.toString();
            }
        }
        return casos;
    }

    // ---------------- testes ----------------
    static void testaOrdenacao(Random r) {
        for (int t = 0; t < 200; t++) {
            int n = r.nextInt(41);
            Integer[] v = new Integer[n];
            for (int i = 0; i < n; i++) v[i] = r.nextInt(101) - 50;
            Integer[] esperado = v.clone();
            Arrays.sort(esperado);
            confere(Ordenacao.mergeSort(Arrays.asList(v), Comparator.naturalOrder()).equals(Arrays.asList(esperado)), "merge sort");
            Integer[] w = v.clone();
            Ordenacao.quickSort(w, 0, w.length - 1, Comparator.naturalOrder());
            confere(Arrays.equals(w, esperado), "quick sort");
        }
        // vetor ja ordenado e grande: sem o pivo sorteado isso ficava O(n^2)
        Integer[] grande = new Integer[200000];
        for (int i = 0; i < grande.length; i++) grande[i] = i;
        Ordenacao.quickSort(grande, 0, grande.length - 1, Comparator.naturalOrder());
        boolean ok = true;
        for (int i = 0; i < grande.length; i++) ok &= grande[i] == i;
        confere(ok, "quick sort em vetor ja ordenado grande");
    }

    static void testaCasosEtapa1(List<Caso> casos) {
        for (Caso c : casos) {
            if (!c.etapa.equals("etapa1")) continue;
            long[] vetor = Etapa1.lerEntrada(c.entrada);
            long[] esperado = Arrays.stream(c.saida.split("\\s+")).mapToLong(Long::parseLong).toArray();
            for (String alg : new String[]{"forca", "dc", "kadane"}) {
                long[] obtido = Etapa1.rodar(alg, vetor);
                confere(Arrays.equals(obtido, esperado),
                        c.id + " (" + alg + "): esperado " + Arrays.toString(esperado) + ", veio " + Arrays.toString(obtido));
            }
        }
    }

    static void testaCasosEtapa2(List<Caso> casos) {
        for (Caso c : casos) {
            if (!c.etapa.equals("etapa2")) continue;
            List<Etapa2.Ponto> pontos = Etapa2.lerEntrada(c.entrada);
            double esperado = Double.parseDouble(c.saida);
            double fb = Etapa2.forcaBruta(pontos).distancia;
            confere(quase(fb, esperado), c.id + " (forca): esperado " + esperado + ", veio " + fb);
            for (int limiar : LIMIARES_TESTADOS) {
                double dc = Etapa2.divisaoConquista(pontos, limiar).distancia;
                confere(quase(dc, esperado), c.id + " (dc, limiar " + limiar + "): esperado " + esperado + ", veio " + dc);
            }
        }
    }

    static void testaAleatorioEtapa1(Random r) {
        int[] faixas = {2, 5, 100}; // faixa pequena gera muitos empates
        for (int t = 0; t < 5000; t++) {
            int n = 1 + r.nextInt(40);
            int faixa = faixas[r.nextInt(faixas.length)];
            long[] v = new long[n];
            for (int i = 0; i < n; i++) v[i] = r.nextInt(2 * faixa + 1) - faixa;
            long[] esperado = Etapa1.forcaBruta(v);
            confere(Arrays.equals(Etapa1.divisaoConquista(v), esperado), "aleatorio dc " + Arrays.toString(v));
            confere(Arrays.equals(Etapa1.kadane(v), esperado), "aleatorio kadane " + Arrays.toString(v));

            // a soma devolvida tem que ser a soma do intervalo devolvido
            long soma = 0;
            for (int i = (int) esperado[1]; i <= esperado[2]; i++) soma += v[i];
            confere(soma == esperado[0], "soma coerente " + Arrays.toString(v));
        }
        // so negativos: a resposta e o maior elemento
        for (int t = 0; t < 500; t++) {
            int n = 1 + r.nextInt(30);
            long[] v = new long[n];
            int posMaior = 0;
            for (int i = 0; i < n; i++) {
                v[i] = -1 - r.nextInt(30);
                if (v[i] > v[posMaior]) posMaior = i;
            }
            long[] esperado = {v[posMaior], posMaior, posMaior};
            for (String alg : new String[]{"forca", "dc", "kadane"}) {
                confere(Arrays.equals(Etapa1.rodar(alg, v), esperado), "so negativos " + alg + " " + Arrays.toString(v));
            }
        }
    }

    static void testaAleatorioEtapa2(Random r) {
        int[] lados = {3, 20, 1000}; // lado pequeno gera pontos repetidos e x iguais
        for (int t = 0; t < 2000; t++) {
            int n = 2 + r.nextInt(80);
            int lado = lados[r.nextInt(lados.length)];
            List<Etapa2.Ponto> pontos = new ArrayList<>();
            for (int i = 0; i < n; i++) {
                pontos.add(new Etapa2.Ponto(r.nextInt(2 * lado + 1) - lado, r.nextInt(2 * lado + 1) - lado));
            }
            double esperado = Etapa2.forcaBruta(pontos).distancia;
            for (int limiar : LIMIARES_TESTADOS) {
                Etapa2.Resultado res = Etapa2.divisaoConquista(pontos, limiar);
                confere(quase(res.distancia, esperado), "aleatorio etapa 2, limiar " + limiar);
                confere(quase(Etapa2.distancia(res.p, res.q), res.distancia), "par devolvido coerente");
            }
        }
        // coordenadas reais
        for (int t = 0; t < 300; t++) {
            int n = 2 + r.nextInt(200);
            List<Etapa2.Ponto> pontos = new ArrayList<>();
            for (int i = 0; i < n; i++) pontos.add(new Etapa2.Ponto(r.nextDouble(), r.nextDouble()));
            confere(quase(Etapa2.divisaoConquista(pontos, 2).distancia, Etapa2.forcaBruta(pontos).distancia), "aleatorio real");
        }
        // a D&C nao pode mexer na lista de quem chamou
        List<Etapa2.Ponto> pontos = new ArrayList<>(List.of(new Etapa2.Ponto(5, 1), new Etapa2.Ponto(1, 1), new Etapa2.Ponto(3, 3)));
        List<Etapa2.Ponto> copia = new ArrayList<>(pontos);
        Etapa2.divisaoConquista(pontos);
        confere(pontos.equals(copia), "nao altera a entrada");
    }

    static void testaEntradaInvalida() {
        String[] invalidas1 = {"0", "3\n1 2"};
        for (String s : invalidas1) {
            try {
                Etapa1.lerEntrada(s);
                confere(false, "etapa 1 deveria recusar: " + s);
            } catch (IllegalArgumentException e) {
                confere(true, "");
            }
        }
        try {
            Etapa2.lerEntrada("1\n0 0");
            confere(false, "etapa 2 deveria recusar n = 1");
        } catch (IllegalArgumentException e) {
            confere(true, "");
        }
    }

    static String rodarPrograma(String classe, String alg, String entrada) throws IOException, InterruptedException {
        String java = System.getProperty("java.home") + File.separator + "bin" + File.separator + "java";
        String cp = System.getProperty("java.class.path");
        Process p = new ProcessBuilder(java, "-cp", cp, classe, alg).redirectError(ProcessBuilder.Redirect.DISCARD).start();
        p.getOutputStream().write(entrada.getBytes(StandardCharsets.UTF_8));
        p.getOutputStream().close();
        String saida = new String(p.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
        p.waitFor();
        return saida.trim();
    }

    static void testaLinhaDeComando(List<Caso> casos) throws IOException, InterruptedException {
        for (Caso c : casos) {
            if (c.etapa.equals("etapa1")) {
                for (String alg : new String[]{"forca", "dc", "kadane"}) {
                    String saida = rodarPrograma("Etapa1", alg, c.entrada);
                    confere(saida.equals(c.saida), "linha de comando " + c.id + " " + alg + ": veio '" + saida + "'");
                }
            } else {
                for (String alg : new String[]{"forca", "dc"}) {
                    String saida = rodarPrograma("Etapa2", alg, c.entrada);
                    double d = Double.parseDouble(saida.split("\\s+")[0]);
                    confere(quase(d, Double.parseDouble(c.saida)), "linha de comando " + c.id + " " + alg + ": veio '" + saida + "'");
                }
            }
        }
    }

    public static void main(String[] args) throws Exception {
        String arquivo = args.length > 0 ? args[0] : "casos_de_teste.txt";
        List<Caso> casos = lerCasos(arquivo);
        Random r = new Random(1);

        System.out.println("Casos lidos do arquivo: " + casos.size());
        testaOrdenacao(r);
        testaCasosEtapa1(casos);
        testaCasosEtapa2(casos);
        testaAleatorioEtapa1(r);
        testaAleatorioEtapa2(r);
        testaEntradaInvalida();
        testaLinhaDeComando(casos);

        System.out.println("Verificacoes que passaram: " + passou);
        System.out.println("Verificacoes que falharam: " + falhou);
        System.exit(falhou == 0 ? 0 : 1);
    }
}
