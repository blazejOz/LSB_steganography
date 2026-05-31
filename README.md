# Steganografia LSB w obrazach cyfrowych (PNG)

Narzędzie CLI do ukrywania i wyciągania wiadomości tekstowych (ASCII) w najmniej znaczących bitach (LSB) pikseli obrazu PNG. Projekt zawiera również moduł do analizy jakości obrazu (PSNR) oraz testowania odporności na kompresję stratną JPEG.

## 1. Wymagania i Instalacja

Do uruchomienia programu wymagany jest **Python 3** oraz dwie biblioteki zewnętrzne do obsługi obrazów i operacji na macierzach:

* **Pillow** – do wczytywania, konwersji i zapisu plików graficznych.
* **NumPy** – do szybkich operacji na płaskich tablicach bajtów (odpowiednik tablic RAW/std::vector w C++).

Zależności możesz zainstalować jedną komendą w terminalu:

```bash
pip install Pillow numpy
```

## 2. Instrukcja uruchomienia (Sposób użycia CLI)

Program działa w pełni z poziomu wiersza poleceń (CLI). Obsługuje cztery główne tryby pracy, które przyjmuje jako pierwszy argument wywołania:

### A. Ukrywanie wiadomości (Embed)
Składnia: `python stego.py embed <obraz_wejsciowy> <obraz_wyjsciowy> "<wiadomosc>"`
```bash
python stego.py embed cover.png stego.png "C++_is_better_than_Python"
```

### B. Wyciąganie wiadomości (Extract)
Składnia: `python stego.py extract <obraz_stego> <dlugosc_wiadomosci>`
```bash
python stego.py extract stego.png 24
```
### C. Obliczanie metryki jakości (PSNR)
Składnia: `python stego.py psnr <obraz_oryginalny> <obraz_stego>`
```bash
python stego.py psnr cover.png stego.png
```
### D. Test kompresji JPEG (Eksperyment)
Składnia: `python stego.py jpeg_test <obraz_stego> "<oryginalna_wiadomosc>"`
```bash
python stego.py jpeg_test stego.png "C++_is_better_than_Python"
```


## 3. Teoretyczna pojemność steganograficzna

Maksymalna pojemność $C$ (wyrażona w znakach ASCII) dla obrazu bezstratnego o strukturze RGB definiowana jest poniższym wzorem matematycznym:

$$C = \frac{W \cdot H \cdot N}{8}$$

Gdzie:
* **W** – szerokość obrazu w pikselach (Width)
* **H** – wysokość obrazu w pikselach (Height)
* **N** – liczba kanałów kolorów na piksel (dla formatu RGB wynosi 3)
* **8** – liczba bitów potrzebna do zakodowania jednego znaku w standardzie ASCII

### Obliczenia dla obrazu testowego 256×256 RGB:

1. Każdy piksel składa się z 3 kanałów (Czerwony, Zielony, Niebieski). Każdy kanał to dokładnie 1 bajt (8 bitów) w pamięci.
2. Nasz algorytm modyfikuje wyłącznie najmłodszy bit (LSB) każdego bajtu, co oznacza, że w jednym bajcie obrazu ukrywamy dokładnie 1 bit wiadomości.
3. Łączna liczba dostępnych bajtów (nośników bitów) wynosi:
   $$256 \cdot 256 \cdot 3 = 196\,608 \text{ bajtów}$$
4. Dzieląc tę liczbę przez 8 bitów potrzebnych na jeden znak ASCII, otrzymujemy ostateczną maksymalną pojemność:
   $$C = \frac{196\,608}{8} = 24\,576 \text{ znaków ASCII}$$

**Wniosek:** Obraz o wymiarach zaledwie 256x256 pikseli jest w stanie pomieścić aż **24 576 znaków tekstowych**, co przekłada się na około 12-15 stron standardowego maszynopisu formatu A4, przy zachowaniu całkowitej niewidoczności dla ludzkiego oka.


## 4. Wyniki eksperymentów i analiza ilościowa

### A. Porównanie wizualne i jakość obrazu stego (PSNR)
Po ukryciu wiadomości tekstowej w pliku `cover.png` i zapisaniu go jako `stego.png`, przeprowadzono analizę porównawczą obu plików.

* **Ocena wizualna:** Obrazy są dla ludzkiego oka całkowicie identyczne. Subtelna modyfikacja najmłodszego bitu (zmiana wartości składowej koloru o maksymalnie 1 stopień w skali 0-255) nie wprowadza żadnych widocznych artefaktów, przebarwień ani zniekształceń.
* **Analiza matematyczna (PSNR):** Jakość techniczną obrazu stego wyznaczono za pomocą błędu średniokwadratowego (MSE) oraz szczytowego stosunku sygnału do szumu (PSNR).

Użyte wzory matematyczne:
$$MSE = \frac{1}{W \cdot H \cdot 3} \sum_{i,j,k} (I_{i,j,k} - K_{i,j,k})^2$$

$$PSNR = 20 \cdot \log_{10} \left( \frac{255}{\sqrt{MSE}} \right)$$

**Uzyskane wyniki:**
* **MSE:** 0.000007
* **PSNR:** **99.61 dB**

**Interpretacja wyniku:** W grafice komputerowej wartości PSNR powyżej 40 dB oznaczają obraz o jakości doskonałej (zmiany są niedostrzegalne). Wynik na poziomie **99.61 dB** udowadnia, że steganografia LSB wprowadza zakłócenia o skali niemal całkowicie pomijalnej, gwarantując najwyższy poziom utajnienia wizualnego.

---

### B. Wpływ kompresji stratnej JPEG (Odporność na ataki)
W ramach testu odporności, plik `stego.png` został poddany konwersji do formatu JPEG z różnymi stopniami jakości. Następnie spróbowano wyciągnąć z nich pierwotną informację.

| Jakość JPEG | Poprawność odczytanych bitów (%) | Czy tekst jest czytelny? |
| :---: | :---: | :---: |
| **95** | 47.50% | NIE (całkowity szum) |
| **90** | 44.50% | NIE (całkowity szum) |
| **75** | 46.50% | NIE (całkowity szum) |
| **50** | 46.50% | NIE (całkowity szum) |
| **25** | 46.50% | NIE (całkowity szum) |

**Wnioski z eksperymentu JPEG (Dlaczego dane zostały zniszczone?):**
1. **Działanie algorytmu JPEG:** Format JPEG jest kompresją stratną. Nie przechowuje on informacji o pojedynczych pikselach bezpośrednio. Zamiast tego dzieli obraz na bloki 8x8 i transformuje je za pomocą **Dyskretnej Transformacji Kosinusowej (DCT)** do domeny częstotliwości, a następnie poddaje kwantyzacji (zaokrąglaniu).
2. **Eliminacja LSB:** Podczas kwantyzacji JPEG odrzuca informacje o najwyższych częstotliwościach (subtelne detale niedostrzegalne dla oka). Najniższy bit (LSB), z punktu widzenia matematycznego, jest traktowany przez ten algorytm właśnie jako szum o wysokiej częstotliwości i zostaje bezpowrotnie nadpisany.
3. **Efekt losowości (Szum biały):** Wyniki poprawności bitowej na poziomie **44% - 47%** to podręcznikowy dowód na kompletną losowość danych. W świecie binarnym prawdopodobieństwo trafienia losowego bitu wynosi statystycznie 50% (jak rzut monetą). Każda próba odczytu LSB z pliku JPEG skutkuje więc otrzymaniem losowego ciągu zer i jedynek.

## 5. Podsumowanie i wnioski końcowe

Na podstawie przeprowadzonych eksperymentów sformułowano następujące wnioski końcowe dotyczące praktycznego zastosowania steganografii LSB:

* **Zależność od formatu pliku:** Metoda najmniej znaczącego bitu (LSB) działa bezbłędnie **wyłącznie w formatach z bezstratną kompresją (PNG)** lub zupełnie bez kompresji (BMP). Gwarantuje to, że każdy bajt obrazu zapisany przez algorytm osadzający zostanie odczytany w identycznej formie przez algorytm wyciągający.
* **Doskonała niewidzialność:** Wpływ metody LSB na jakość wizualną nośnika jest niezauważalny dla ludzkiego oka. Potwierdza to wyznaczona empirycznie metryka **PSNR na poziomie 99.61 dB**, co znacznie przekracza standardowy próg doskonałej jakości (40 dB).
* **Zerowa odporność na ataki:** Steganografia LSB w swojej podstawowej formie jest całkowicie bezbronna wobec jakichkolwiek modyfikacji pliku. Kompresja stratna JPEG niszczy strukturę LSB, zamieniając ukrytą wiadomość w losowy szum (poprawność bitowa na poziomie ~45%). Podobny efekt destrukcyjny wywołałaby zmiana rozmiaru obrazu, filtracja czy korekcja jasności.


