import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Scanner;

// Etapa 2 - Par de Pontos Mais Proximos
//
// Entrada (stdin): um inteiro n (n >= 2) seguido de n pares "x y".
// Saida: a menor distancia (6 casas decimais) e os dois pontos do par.
// Se houver varios pares com a menor distancia, qualquer um e aceito
// (os testes conferem a distancia).
//
// Uso:  java -cp bin Etapa2 [forca|dc] < entrada.txt
public class Etapa2 {

    // limiar: se o subproblema tiver ate LIMIAR pontos, resolve por forca bruta.
    // O valor foi escolhido pelos experimentos (ver Experimentos.java e o relatorio).
    public static final int LIMIAR_PADRAO = 6;

    public static class Ponto {
        final double x, y;

        Ponto(double x, double y) {
            this.x = x;
            this.y = y;
        }

        @Override
        public String toString() {
            return formatar(x) + " " + formatar(y);
        }

        private static String formatar(double v) {
            return v == Math.rint(v) ? String.valueOf((long) v) : String.valueOf(v);
        }
    }

    public static class Resultado {
        final double distancia;
        final Ponto p, q;

        Resultado(double distancia, Ponto p, Ponto q) {
            this.distancia = distancia;
            this.p = p;
            this.q = q;
        }
    }

    static final Comparator<Ponto> PELA_X = (a, b) -> a.x != b.x ? Double.compare(a.x, b.x) : Double.compare(a.y, b.y);
    static final Comparator<Ponto> PELA_Y = (a, b) -> Double.compare(a.y, b.y);

    static double distancia(Ponto a, Ponto b) {
        return Math.hypot(a.x - b.x, a.y - b.y);
    }

    // ------------------------------------------------------------------
    // 1) Forca bruta - O(n^2): compara todos os pares
    // ------------------------------------------------------------------
    public static Resultado forcaBruta(List<Ponto> pontos) {
        Resultado melhor = new Resultado(Double.POSITIVE_INFINITY, null, null);
        int n = pontos.size();
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                double d = distancia(pontos.get(i), pontos.get(j));
                if (d < melhor.distancia) {
                    melhor = new Resultado(d, pontos.get(i), pontos.get(j));
                }
            }
        }
        return melhor;
    }

    // ------------------------------------------------------------------
    // 2) Divisao e conquista - O(n log n)
    //    T(n) = 2T(n/2) + O(n)
    // ------------------------------------------------------------------

    // o que a recursao devolve: a resposta e os pontos daquele pedaco ordenados por y
    static class Parcial {
        final Resultado resultado;
        final List<Ponto> porY;

        Parcial(Resultado resultado, List<Ponto> porY) {
            this.resultado = resultado;
            this.porY = porY;
        }
    }

    // px: pontos ordenados por x
    static Parcial dcRecursivo(List<Ponto> px, int limiar) {
        int n = px.size();

        if (n <= limiar) {
            return new Parcial(forcaBruta(px), Ordenacao.mergeSort(px, PELA_Y));
        }

        // dividir pela linha vertical na mediana dos x
        int meio = n / 2;
        double xMeio = px.get(meio).x;

        Parcial esq = dcRecursivo(px.subList(0, meio), limiar);
        Parcial dir = dcRecursivo(px.subList(meio, n), limiar);

        Resultado melhor = esq.resultado.distancia <= dir.resultado.distancia ? esq.resultado : dir.resultado;
        double delta = melhor.distancia;

        // a "combinacao" do merge sort junta os dois lados ja ordenados por y em O(n).
        // Assim nao precisamos reordenar por y em todo nivel da recursao.
        List<Ponto> py = Ordenacao.combinacao(esq.porY, dir.porY, PELA_Y);

        // faixa de largura 2*delta em volta da linha
        List<Ponto> faixa = new ArrayList<>();
        for (Ponto p : py) {
            if (Math.abs(p.x - xMeio) < delta) {
                faixa.add(p);
            }
        }

        // cada ponto da faixa so precisa ser comparado com os 7 seguintes (ordem por y)
        for (int i = 0; i < faixa.size(); i++) {
            for (int j = i + 1; j < Math.min(i + 8, faixa.size()); j++) {
                if (faixa.get(j).y - faixa.get(i).y >= delta) {
                    break; // daqui pra frente so fica mais longe em y
                }
                double d = distancia(faixa.get(i), faixa.get(j));
                if (d < delta) {
                    delta = d;
                    melhor = new Resultado(d, faixa.get(i), faixa.get(j));
                }
            }
        }
        return new Parcial(melhor, py);
    }

    public static Resultado divisaoConquista(List<Ponto> pontos, int limiar) {
        if (pontos.size() < 2) {
            throw new IllegalArgumentException("precisa de pelo menos 2 pontos");
        }
        Ponto[] px = pontos.toArray(new Ponto[0]); // copia para nao mexer na lista de quem chamou
        Ordenacao.quickSort(px, 0, px.length - 1, PELA_X); // ordenacao inicial por x
        return dcRecursivo(List.of(px), Math.max(limiar, 1)).resultado;
    }

    public static Resultado divisaoConquista(List<Ponto> pontos) {
        return divisaoConquista(pontos, LIMIAR_PADRAO);
    }

    public static Resultado rodar(String nome, List<Ponto> pontos) {
        switch (nome) {
            case "forca": return forcaBruta(pontos);
            case "dc": return divisaoConquista(pontos);
            default: throw new IllegalArgumentException("algoritmo desconhecido: " + nome);
        }
    }

    public static List<Ponto> lerEntrada(String texto) {
        Scanner sc = new Scanner(texto).useLocale(Locale.US);
        if (!sc.hasNextInt()) throw new IllegalArgumentException("entrada invalida");
        int n = sc.nextInt();
        if (n < 2) throw new IllegalArgumentException("entrada invalida: precisa de n >= 2");
        List<Ponto> pontos = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            if (!sc.hasNextDouble()) throw new IllegalArgumentException("entrada invalida: faltam coordenadas");
            double x = sc.nextDouble();
            if (!sc.hasNextDouble()) throw new IllegalArgumentException("entrada invalida: faltam coordenadas");
            double y = sc.nextDouble();
            pontos.add(new Ponto(x, y));
        }
        return pontos;
    }

    public static void main(String[] args) throws IOException {
        String nome = args.length > 0 ? args[0] : "dc";
        String texto = new String(System.in.readAllBytes());
        Resultado r = rodar(nome, lerEntrada(texto));
        System.out.println(String.format(Locale.US, "%.6f", r.distancia));
        System.out.println(r.p);
        System.out.println(r.q);
    }
}
