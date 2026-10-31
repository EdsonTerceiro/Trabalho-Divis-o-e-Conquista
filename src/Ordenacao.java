import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Random;

// Merge sort e quick sort vistos em aula, passados para Java.
// Eles recebem um Comparator porque na Etapa 2 precisamos ordenar pontos por x e por y.
//
// Correcao em relacao a versao da aula: na combinacao faltava o "i++" dentro do if,
// o que fazia o while nunca terminar.
public class Ordenacao {

    private static final Random sorteio = new Random();

    public static <T> List<T> mergeSort(List<T> vetor, Comparator<T> comp) {
        if (vetor.size() <= 1) {
            return new ArrayList<>(vetor);
        }
        int meio = vetor.size() / 2;
        List<T> esquerda = mergeSort(vetor.subList(0, meio), comp);
        List<T> direita = mergeSort(vetor.subList(meio, vetor.size()), comp);
        return combinacao(esquerda, direita, comp);
    }

    public static <T> List<T> combinacao(List<T> esquerda, List<T> direita, Comparator<T> comp) {
        List<T> resultadoOrdenado = new ArrayList<>(esquerda.size() + direita.size());
        int i = 0;
        int j = 0;

        while (i < esquerda.size() && j < direita.size()) {
            if (comp.compare(esquerda.get(i), direita.get(j)) <= 0) {
                resultadoOrdenado.add(esquerda.get(i));
                i++; // <- estava faltando na versao da aula
            } else {
                resultadoOrdenado.add(direita.get(j));
                j++;
            }
        }
        resultadoOrdenado.addAll(esquerda.subList(i, esquerda.size()));
        resultadoOrdenado.addAll(direita.subList(j, direita.size()));
        return resultadoOrdenado;
    }

    // Mesma ideia da aula (particao com o pivo na posicao high).
    // Mudanca: sorteamos o pivo e trocamos com o high antes de particionar,
    // senao um vetor ja ordenado cai no pior caso O(n^2) e a recursao fica enorme.
    // Tambem fazemos a recursao so na parte menor (e um while na maior),
    // para a pilha ficar no maximo O(log n).
    public static <T> void quickSort(T[] vetor, int low, int high, Comparator<T> comp) {
        while (low < high) {
            int k = low + sorteio.nextInt(high - low + 1);
            troca(vetor, k, high);

            T pivot = vetor[high];
            int i = low;

            for (int j = low; j < high; j++) {
                if (comp.compare(vetor[j], pivot) < 0) {
                    troca(vetor, i, j);
                    i++;
                }
            }
            troca(vetor, i, high);

            if (i - low < high - i) {
                quickSort(vetor, low, i - 1, comp);
                low = i + 1;
            } else {
                quickSort(vetor, i + 1, high, comp);
                high = i - 1;
            }
        }
    }

    private static <T> void troca(T[] vetor, int a, int b) {
        T aux = vetor[a];
        vetor[a] = vetor[b];
        vetor[b] = aux;
    }

    public static void main(String[] args) {
        List<Integer> vetorOriginal = List.of(30, 2, 1, 22, 45, 3, 13, 70, 400);
        System.out.println("merge: " + vetorOriginal + " -> " + mergeSort(vetorOriginal, Comparator.naturalOrder()));

        Integer[] vetor = new Integer[20];
        for (int n = 0; n < 20; n++) {
            vetor[n] = sorteio.nextInt(121);
        }
        System.out.println("vetor desordenado " + java.util.Arrays.toString(vetor));
        quickSort(vetor, 0, vetor.length - 1, Comparator.naturalOrder());
        System.out.println("vetor ordenado " + java.util.Arrays.toString(vetor));
    }
}
