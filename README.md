___
### *System sterowania robotem przemysłowym za pomocą ludzkich gestów*


# 1. Cel i idea

Głównym założeniem projektu było zintegrowanie systemu sterowania  za pomocą gestów dłoni dla roboto przemysłowego firmy ABB IRB 120.

Praca została podzielona na etapy:
- Przygotowanie danych treningowych oraz przeprowadzenie procesu uczenia modelu sieci neuronowej MLP klasyfikatora gestów. 
- Opracowanie techniki wykorzystania zbioru gestów do sterowania robotem.
- Zaprojektowanie GUI, umożliwiającego analizę procesów sterowania i kontroli działań aplikacji
- Przeprowadzenie testów końcowych aplikacji 
- Opracowania wyników końcowych.

# 2.  Aplikacja

Opis funkcjonalności i możliwości aplikacji główna idea działania.

![[readmeAssets/speed_upx2.mov]]

![[readmeAssets/RobotStudio 2-16_17.mp4]]

![[readmeAssets/RobotStudio 2-16_12.mp4]]
Aplikacja końcowa pozwalała użytkownikowi  na działanie w:

***Interfejsie***
-  akcje ruchu - poruszanie się w 6 kierunkach wewnątrz aplikacji UP, DOWN, LEFT, RIGHT oraz operacje zagłębienia i wynurzenia miedzy sekcjami.
-  akcje interakcji - możliwość wciskania przycisków ( klik, przytrzymanie ), operacja Slider'a
***Komunikacji z robotem***
-  ustawienie połączenia - konfiguracja transmisji rozkazów pomiędzy klientem-serwerm-robotem
-  sterowanie krokowe - nisko-prędkościowe ruchy sterujące efektorem w układzie kartezjańskim robota względem układu World
-  uruchamianie programów robota - startowanie, zatrzymywanie, wznawianie programów utworzonych na jednostce robota

Implementacja systemu sterowania wykorzystała aktywacje funkcji poprzez przygotowane drzewo hierarchiczne wykorzystujące kombinacje z 2 rąk odczytujących 13 etykiet klas gestów. Każda ręką posiada przydzieloną funkcję dłoń lewa, główna (niebieska) i dłoń prawa wykonawcza (żółta). Dłoń główna pozwalała na wybór grupy poleceń, natomiast dłoń wykonawcza odpowiadała za wykonanie jednej z 28 funkcji końcowych. 

[grafika wprowadzania gestów]

Wywołanie funkcji jest wynikiem zakończenia składania kolejki zapytania ( sekcja różowa GUI). Gesty w systemie przekładne są na zestaw komend widoczny w kolejce zapytania oraz komendy ukryte ( wykonujące się w tle działania kolejki). Każdorazowa zmiana gestu otwiera proces dekodowania etykiety gestu i uruchomienia w wyniku końcowym kompilatora wykonawczego.  Przy czym możliwa jest zmiana poprzedniego stanu kolejki bądź powrót do wszego stopnia polecenia.

[grafika sposobu działania kompilatora wykonawczego]

Detekcja gestów odbywa się na podstawie wytrenowanego na potrzeby badania modelu perceptronu wielowarstwowego ( 3 warstwy ukryte, po 128, 128, 64 neurony) u umożliwiającego klasyfikację 13 unikalnych etykiet klas gestów.
![[readmeAssets/Pasted image 20260514235838.png]]
*rys. Próbka 13 klas gestów*.

# 3. Architektura

Wykorzystane pakiety bibliotek, narzędzia, sprzętu struktury aplikacji.

Aplikacja końcowa składa się z 3 warstw: 
- Klienta - Kamera stereoskopowa ZED 2 (k), Jetson AGX Xaveir (g)
- Serwer - Komputer z aplikacją serwera
- Robot - Kontroler oraz jednostka robota

Wykorzystane narzędzia programistyczne
- python 3.10
- C# framework 4.8
- Rapid (form ABB)
- Mediapipe
- Tensorflow
- numpy, seaborn, matplotlib, 


![[readmeAssets/Pasted image 20260515000206.png]]
*rys. stanowisko projektowe*

Główną komputer odpowiadał za przetwarzanie obrazu z kamery, jego transmisję oraz operowanie GUI. Serwer miał za zadanie wywoływać żądania sterujące poprzez pakiet ABB PC SDK. Kontroler robota posiadał zestaw przygotowanych programów i umożliwiał dodatkowy podgląd pracy robota dzięki Flexpendat'owi. 

Programowo każdej warstwie odpowiadał oddzielny wątek wykonawczy. 

![[readmeAssets/Pasted image 20260515001322.png]]
*rys. architektura softwerowa aplikacji* 

Zdjęcia odczytywane z kamery ZED zostają prze konwertowane na chmurę 21 punktów charakterystycznych poprzez model Mediapipe, kolejno punkty zostają przetransformowane na etykietę klasy próbkowanej co okres 50ms. Wy wyniku próbkowania dyskretny model przebiegu czasowego gestów w czasie pozwala na określenie kombinacji gestów sterujących.  W przypadku aktywacji funkcji na serwer zostaje przesłany komunikat Command-Tag: nieokreślający komendę i zestaw argumentów. W końcowym etapie zdekodowana wiadomość na serwerze uruchamia funkcję z pakietu ABB SKD opowiadające za sterowanie oraz informacje statusowe. 

# 4. Problemy 

W badaniu napotkałem szereg pomniejszych problemów które wymagały rozwiązania. 
### (a) Przygotowanie zbioru danych testowych do modelu

W projekcie wykorzystana została otwarto źródłowa baza zdjęć z opisanymi etykietami HaGRIDv2 (https://github.com/hukenovs/hagrid/blob/master/README.md). Z pośród bazy zostały wytypowane etykiety 13 gestów z próbą 2000 zdjęć na klasę. Problematyko pojawiła się w próbkach, zdjęcia posiadają różne skale,  pozycje dłoni na zdjęciu, dodatkowe niewłaściwie dłonie (ręka trzymająca telefon do zdjęcia ). 
![[readmeAssets/Pasted image 20260515010834.png|455]]
Ponieważ klasyfikator gestów ma cechować się z założenia jak najwyższa niezawodnością korelacja miedzy danymi z populacji klasy musi mieć zachowana jak najwyższa korelację. Dlatego rozwiązanie wymagało zbudowania 2 warstw: normalizującej i filtrującej pozwalającej eliminować gesty o niższej korelacji. 
![[readmeAssets/Pasted image 20260515003235.png]]
*rys. Końcowa korelacja danych przedstawiona na wykresie T-SNE*

### (b) Aktywacja przeskoków miedzy gestami

Do reprezentacji gestów w czasie zastosowałem odwzorowanie kolorystyczne,
każdemu gestowi przypadał jeden unikalny kolor.  Sterowanie odbywa się poprzez miany gestów, zwane przeskokami.  

![[readmeAssets/Pasted image 20260515003524.png|455]]

Przy zmianach gestów bądź podczas utrzymywania składnika pojawiają się rożne klasyfikacje gestów, co może spowodować uruchomieniem niewłaściwej funkcji aktywacyjnej, co jest niedopuszczalne ze względów bezpieczeństwa pracy z robotem. Dlatego w założeniu przebieg dyskretny musiał zostać przekształcony do postaci bezpiecznej poprzez operację miksowania, która ujednolica etykiety w czasie. Problem został rozwiązany poprzez zastosowanie deterministycznego automatu stanów. Jego model iteracyjny pozwalał na wykonanie miksowania w średnio 3 iteracje. Model zakłada analizę 7 najmłodszych próbek i aktywowany jest w chwili wykrycia zmiany gestu. 

![[readmeAssets/Pasted image 20260515004951.png|443]]
*rys. przykładowy porces iteracyjny funkcji miksowania*

Zastosowanie modelu pozwala:
- utrzymywać stan gestu
- redukować zakłócenia 
- ujednolicać przebieg
-  przerywać pracę w przypadku zbyt wysokiego poziomu zakłóceń 

Zastosowanie aromatu  sprowadza się do przeprowadzenia rachunku macierzowego bez potrzeby rozbudowywania  bloku if-statment w programie. 

### (c) Przesuwanie efektora 

Projekt zakładał umożliwienie poruszania się efektorem robota o minimalny krok. Stosowane sterowanie robotem odbywa się w trybie AUTO co oznacza, że operator ma ograniczone sterowanie robotem, oraz robot pracuje na pełnej prędkości. W przypadku chęci zastosowania systemu z operatorem w przestrzeni roboczej robota wymagane jest zachowanie względów bezpieczeństwa jak i  zachowanie braku kolizyjności z elementami stanowiska. Ponieważ robot nie jest sterowany bezpośrednio z panelu Flexpendant, a sieć TCP/IP pojawiają się problemy z opóźnieniami przerwania ruchu robota.  W rozwiązaniu zostały użyte 2 podejścia: ograniczenie prędkości robota do minimum, oraz zastosowanie stosu do obsługi dekrementacji ruchów. Ostatecznie flansza robota poruszała się pozornym ruchem liniowym. 

### (d) Wielowątkowość

Obsługa GUI, komunikacja z serwerem, przetwarzania obrazu oraz działanie równocześnie 2 modeli klasyfikacji powodowała znaczne obciążenie sprzętowe dla jednego wątku, gdzie głównym wyznacznikiem była szybkość transmisji obrazu i pozyskiwania etykiet klas. Problem został rozwiązany dzięki rozbiciu struktury programu na wielowątkową. Dzięki takiemu rozbiciu uzyskana została płynna transmisja danych, widoczna w GUI oraz nisko opóźniony proces emisji danych na serwer.