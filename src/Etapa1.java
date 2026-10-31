import java.io.IOException;
import java.util.Scanner;

// Etapa 1 - Subarranjo de Soma Maxima
//
// Entrada (stdin): um inteiro n seguido de n inteiros.
// Saida: soma maxima, indice de inicio e indice de fim (indices comecam em 0).
//
// Regra de desempate (as 3 versoes seguem a mesma regra):
//   1) maior soma;
//   2) se empatar, o intervalo que comeca mais cedo (menor inicio);
//   3) se ainda empatar, o intervalo mais curto (menor fim).
// O intervalo tem pelo menos um elemento, entao um vetor so de negativos
// devolve o maior negativo (e nao 0).
//
// As somas sao long: com int, somar valores grandes estoura 2^31 (caso E1-16).
//
// Uso:  java -cp bin Etapa1 [forca|dc|kadane] < entrada.txt
public class Etapa1 {

    // resposta = {soma, inicio, fim}
    static long[] melhor(long[] a, long[] b) {
        if (a[0] != b[0]) return a[0] > b[0] ? a : b;
        if (a[1] != b[1]) return a[1] < b[1] ? a : b;
        return a[2] <= b[2] ? a : b;
    }

    // ------------------------------------------------------------------
    // 1) Forca bruta - O(n^2)
    // ------------------------------------------------------------------
    public static long[] forcaBruta(long[] vetor) {
        int n = vetor.length;
        long melhorSoma = vetor[0];
        int melhorIni = 0;
        int melhorFim = 0;

        for (int i = 0; i < n; i++) {
            long soma = 0;
            for (int j = i; j < n; j++) {
                soma += vetor[j]; // soma de vetor[i..j] aproveitando a anterior
                // so troca se for estritamente maior: assim ficamos com o menor i e o menor j
                if (soma > melhorSoma) {
                    melhorSoma = soma;
                    melhorIni = i;
                    melhorFim = j;
                }
            }
        }
        return new long[]{melhorSoma, melhorIni, melhorFim};
    }

    // ------------------------------------------------------------------
    // 2) Divisao e conquista - O(n log n)
    //    T(n) = 2T(n/2) + O(n)
    // ------------------------------------------------------------------
    static long[] cruzandoOMeio(long[] vetor, int low, int meio, int high) {
        // melhor parte da esquerda que termina em meio
        long soma = 0;
        long melhorEsq = vetor[meio];
        int ini = meio;
        for (int i = meio; i >= low; i--) {
            soma += vetor[i];
            if (soma >= melhorEsq) { // ">=" porque, empatando, queremos o inicio menor
                melhorEsq = soma;
                ini = i;
            }
        }

        // melhor parte da direita que comeca em meio+1
        soma = 0;
        long melhorDir = vetor[meio + 1];
        int fim = meio + 1;
        for (int j = meio + 1; j <= high; j++) {
            soma += vetor[j];
            if (soma > melhorDir) { // ">" porque, empatando, queremos o fim menor
                melhorDir = soma;
                fim = j;
            }
        }
        return new long[]{melhorEsq + melhorDir, ini, fim};
    }

    static long[] dcRecursivo(long[] vetor, int low, int high) {
        if (low == high) { // caso base: um elemento so
            return new long[]{vetor[low], low, low};
        }
        int meio = (low + high) / 2;
        long[] esquerda = dcRecursivo(vetor, low, meio);
        long[] direita = dcRecursivo(vetor, meio + 1, high);
        long[] cruza = cruzandoOMeio(vetor, low, meio, high);

        // a resposta e o maior dos tres valores
        return melhor(melhor(esquerda, cruza), direita);
    }

    public static long[] divisaoConquista(long[] vetor) {
        return dcRecursivo(vetor, 0, vetor.length - 1);
    }

    // ------------------------------------------------------------------
    // 3) Questao desafio: versao O(n) (algoritmo de Kadane)
    // ------------------------------------------------------------------
    public static long[] kadane(long[] vetor) {
        long atual = vetor[0]; // melhor soma de um intervalo que termina na posicao j
        int iniAtual = 0;
        long[] resposta = {vetor[0], 0, 0};

        for (int j = 1; j < vetor.length; j++) {
            if (atual >= 0) {
                // vale a pena continuar o intervalo (se atual == 0 a soma e a mesma,
                // mas o inicio fica menor, que e o que a regra de desempate pede)
                atual += vetor[j];
            } else {
                // o que veio antes so atrapalha: comeca de novo em j
                atual = vetor[j];
                iniAtual = j;
            }
            resposta = melhor(resposta, new long[]{atual, iniAtual, j});
        }
        return resposta;
    }

    public static long[] rodar(String nome, long[] vetor) {
        switch (nome) {
            case "forca": return forcaBruta(vetor);
            case "dc": return divisaoConquista(vetor);
            case "kadane": return kadane(vetor);
            default: throw new IllegalArgumentException("algoritmo desconhecido: " + nome);
        }
    }

    public static long[] lerEntrada(String texto) {
        Scanner sc = new Scanner(texto);
        if (!sc.hasNextInt()) throw new IllegalArgumentException("entrada invalida");
        int n = sc.nextInt();
        if (n < 1) throw new IllegalArgumentException("entrada invalida: precisa de n >= 1");
        long[] vetor = new long[n];
        for (int i = 0; i < n; i++) {
            if (!sc.hasNextLong()) throw new IllegalArgumentException("entrada invalida: faltam numeros");
            vetor[i] = sc.nextLong();
        }
        return vetor;
    }

    public static void main(String[] args) throws IOException {
        String nome = args.length > 0 ? args[0] : "dc";
        String texto = new String(System.in.readAllBytes());
        long[] r = rodar(nome, lerEntrada(texto));
        System.out.println(r[0] + " " + r[1] + " " + r[2]);
    }
}
