# Z0202: Rozwi¹zanie Zadania "Electricity"

Ten projekt rozwi¹zuje zagadkê logiczn¹ "Electricity" (Zadanie Z0202) z kursu, wykorzystuj¹c koncepcjê autonomicznego Agenta komunikuj¹cego siê z modelami wizyjnymi oraz zewnêtrznym API œrodowiska testowego.

## Logika Dzia³ania

Zadanie polega na obracaniu p³ytek na planszy o wymiarach 3x3 w celu stworzenia po³¹czeñ pomiêdzy elektrowniami doprowadzaj¹cych pr¹d. Do dyspozycji mamy:
- API udostêpniaj¹ce aktualny uk³ad planszy jako obrazek .png,
- API przyjmuj¹ce komendy obrotu konkretnej p³ytki (o 90 stopni w prawo),
- Model docelowy (wzorzec), do którego d¹¿ymy.

Proces decyzyjny Agenta zosta³ oparty na pêtli:
1. **Resetowanie planszy:** Upewnienie siê, ¿e stan p³ytek jest wyzerowany do oryginalnego uk³adu.
2. **Pobieranie stanu (Obserwacja):** Skrypt pobiera aktualny obraz siatki z API.
3. **Analiza AI (Vision):** Obraz jest przesy³any do modelu AI Vision (gemini-3.1-pro-preview) z wytycznymi nakazuj¹cymi zwrócenie uk³adu poszczególnych "kabli" dla wszystkich 9 p³ytek z u¿yciem formatu JSON i uwzglêdnieniem kierunków krawêdzi (top, bottom, left, right).
4. **Porównanie (Obliczanie Ró¿nic):** Pobrany w JSON stan z obrazka z AI jest porównywany matematycznie ze "stanem docelowym" zapisanym na sztywno w kodzie (GROUND_TRUTH). Agent wylicza iloœæ wymaganych rotacji w prawo (od 0 do 3), aby aktualny u³amek planszy odpowiada³ wzorcowi.
5. **Egzekucja (Dzia³anie na API):** Agent puszcza sekwencjê zapytañ POST /verify dla ka¿dego elementu o iloœæ rotacji zdefiniowan¹ z etapu 4.
6. **Poszukiwanie Flagi:** Jeœli w odpowiedzi na POST po wykonanej rotacji od API padnie {FLG:xxx}, Agent wie, ¿e zadanie zakoñczono sukcesem i przerywa dzia³anie. W przypadku pomy³ki, wraca do punktu 2, maj¹c na to ³¹cznie okreœlon¹ liczbê prób.

## Struktura Plików
- pp.py: G³ówny plik startowy projektu, uruchamiaj¹cy asynchronicznie Agenta.
- src/agent.py: Zawiera g³ówn¹ klasê pêtli zachowañ, zarz¹dzaj¹c¹ krokami analizy, podejmowaniem decyzji o obrotach i odpytywaniem API.
- src/api.py: Agreguje funkcje do wysy³ania komend POST do serwerów zadania i zapytañ do Google Gemini.
- src/config.py: Przechowuje zmienne œrodowiskowe, definicjê wzorcowego docelowego rozwi¹zania (GROUND_TRUTH) w postaci s³ownika kierunków.
- src/helpers/logger.py: System logowania do wygodnego odczytu i zapisywania wyników w pliku gent.log.

## Zastosowane Biblioteki

W projekcie u¿yto podstawowych narzêdzi, bez wymyœlania ko³a na nowo:

- **equests**: Podstawa projektu do odpytywania zapytañ po sieci dla API hub.ag3nts.org oraz do REST API Gemini.
- **python-dotenv**: Odpowiedzialna za zaczytywanie kluczy GEMINI_LLM_APIKEY i APIKEY bez twardego kodowania ich w plikach konfiguracyjnych.
- **syncio**: S³u¿y do uruchamiania asynchronicznych akcji przez wejœcie z pp.py.
- **ase64**: S³u¿y do enkapsulowania obrazków jako ci¹gi znaków ase64 dla payloadu wysy³anego do modeli Google Generative AI (zamiast wysy³ania linku i ryzykowania niepobrania w œrodowisku proxy).

## Uruchomienie

Aby zainicjalizowaæ agenta upewnij siê, ¿e masz ustawione odpowiednie zmienne, zainstaluj listê narzêdzi i wywo³aj komendê:

`ash
python -m pip install -r requirements.txt
python app.py
`
Otwórz z poziomu œrodowiska tworzony na bie¿¹co plik gent.log by œledziæ postêpy modelu w rotacji.
