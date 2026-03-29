# Zadanie Z0302: Firmware & Shell Exploration (Oprogramowanie Sterownika)

W tym folderze znajduje się rozwiązanie dla zadania analizy oprogramowania sterownika `cooler.bin` poprzez API z ograniczonym dostępem do maszyny wirtualnej (Linux Shell). 

Zadanie podzielone było na główną misję naprawienia i uruchomienia firmware'u, oraz ukryte zadanie poboczne ("side quest").

## Struktura Rozwiązania
- **`app.py`**: Skrypt pełniący rolę Agenta, korzystający ze zdefiniowanych narzędzi do interakcji z shellem oraz logiki Function Calling (Model Anthropic/Gemini). Implementuje wzorzec **Think-Act-Observe**.
- **`src/api.py`**: Niskopoziomowe połączenia z LLM (OpenRouter/Gemini) oraz z Shell API.
- **`src/tools.py`**: Definicje schematów narzędzi (`execute_command`, `submit_code`) oraz obsługa blokad (`bans`) i limitów czasowych (`rate limits`) nakładanych przez maszynę wirtualną.
- **`src/firmware-solver.prompt.md`**: System Prompt Agenta w którym opisane są zasady i struktura działania na wirtualnym terminalu.

---

## 1. Odkrycie i wykonanie Głównego Zadania (ECCS)

Zadaniem Agenta było uruchomienie programu chłodzenia `/opt/firmware/cooler/cooler.bin` i odesłanie otrzymanego kodu do `/verify`. Ze względu na pułapki w środowisku (np. ukryty plik konfiguracyjny `.gitignore`, ograniczenia do `/root`, `/etc`), Agent musiał eksplorować system niezwykle ostrożnie.

### Proces Rozwiązywania:
1. **Zabezpieczenie przed Rate Limitami i Banami**: Z logów (`logs/app.log`) wynikło, że API nakłada kary za niepoprawne pliki i zbyt dużą ilość wywołań na sekundę (`Za często wykonujesz zapytania`). Skrypt `tools.py` został rozwinięty o automatyczne zarządzanie przerwami (`time.sleep`).
2. **Eksploracja systemu (`ls`, `cat`)**: Agent sprawdził katalog główny aplikacji i odczytał zawartość pliku `.gitignore`. Według ustaleń – nie wolno było odczytywać plików wypisanych w tym ukrytym pliku.
3. **Odczytywanie Haseł i Ustawień**: Po dogłębnej eksploracji, w notatkach systemowych w katalogu użytkownika (`/home/operator/notes/pass.txt`), zostało odnalezione hasło `admin1`.
4. **Zarządzanie Plikiem Konfiguracyjnym**: Plik `/opt/firmware/cooler/settings.ini` musiał zostać zmodyfikowany (`editline`) z wyłączonego trybu bezpieczeństwa i ustawień na odpowiednie flagi pozwalające na wykonanie programu.
5. **Weryfikacja**: Agent uruchomił aplikację, poprawnie pozyskał flagę (`ECCS-...`) używając komendy `/opt/firmware/cooler/cooler.bin admin1` i automatycznie potwierdził ją poprzez system weryfikacji.

---

## 2. Rozwiązanie "Side Questu": `BRATWURST`

Zarówno w poleceniu od użytkownika, jak i podczas analizy logów pojawiały się wskazówki prowadzące do zadania pobocznego (Side Questu). Wskazówka brzmiała: 

> *"Uruchom mnie z niemieckim motylem"*

### Proces Dedukcji i Odkrycia:
1. Przetłumaczenie Słowa Klucz: "Niemiecki motyl" oznacza w tłumaczeniu na niemiecki słowo **`schmetterling`**.
2. Wskazówka "Uruchom mnie" implikowała, że musimy uruchomić plik wykonywalny w środowisku.
3. Dokonaliśmy weryfikacji dostępnych programów poprzez przeszukanie powłoki (katalogu `/bin` w VM):
    ```bash
    ls /bin
    # Wynik: ['bash', 'flaggengenerator', 'ls']
    ```
4. Plik **`flaggengenerator`** od razu przykuł uwagę – nazwa jest w języku niemieckim (Generator Flag).
5. Podjęta została próba uruchomienia tego programu wraz ze zdedukowanym słowem kluczowym:
    ```bash
    /bin/flaggengenerator schmetterling
    ```
6. API wirtualnej maszyny w odpowiedzi zwróciło ciąg znaków zakodowany w Base64: 
   `e0ZMRzpCUkFUV1VSU1R9`
7. Po zdekodowaniu Base64 w lokalnym środowisku, uzyskaliśmy prawidłowy ukryty sekret (flagę):
   **`{FLG:BRATWURST}`**
