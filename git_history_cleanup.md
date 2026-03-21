# Usuwanie katalogu z historii Git

Te komendy pozwalają na całkowite usunięcie katalogu z historii Twojego repozytorium Git. Pamiętaj, że jest to **operacja destrukcyjna**, która przepisuje historię. Jeśli repozytorium jest współdzielone, inni współpracownicy będą musieli zreorganizować swoją pracę na nowej historii.

**Zawsze wykonaj kopię zapasową swojego repozytorium przed przystąpieniem do tych kroków!**

## Kroki:

1.  **Stwórz kopię zapasową swojego repozytorium (krytyczne!):**
    ```bash
    cp -Rv c:\Users\buyak\Documents\AI_devs c:\Users\buyak\Documents\AI_devs_backup
    ```

2.  **Przejdź do katalogu swojego repozytorium:**
    ```bash
    cd c:\Users\buyak\Documents\AI_devs
    ```

3.  **Uruchom `git filter-branch`, aby usunąć katalog z historii:**
    Zastąp `lekcje/` nazwą katalogu, który chcesz usunąć (np. `nazwa_katalogu_do_usuniecia/`).
    ```bash
    git filter-branch --force --index-filter "git rm -rf --cached --ignore-unmatch lekcje/" --prune-empty --tag-name-filter cat -- --all
    ```

4.  **Wyczyść stare referencje (opcjonalne, ale zalecane dla zwolnienia miejsca):**
    ```bash
    git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
    git reflog expire --expire=now --all
    git gc --prune=now
    ```

5.  **Wypchnij zmiany na zdalne repozytorium (wymaga force push!):**
    **OSTRZEŻENIE: Force push nadpisuje zdalną historię. Jeśli inni sklonowali repozytorium, napotkają problemy i będą musieli zrebase'ować swoją pracę.**

    Przed tym krokiem upewnij się, że masz skonfigurowane uwierzytelnianie (Personal Access Token lub klucze SSH), ponieważ GitHub nie obsługuje już uwierzytelniania hasłem dla operacji Git.

    ```bash
    git push origin --force --all
    git push origin --force --tags
    ```

## Ważne uwagi dotyczące uwierzytelniania GitHub (jeśli napotkasz błąd "Authentication failed"):

GitHub nie obsługuje już uwierzytelniania hasłem dla operacji Git. Musisz użyć Personal Access Token (PAT) lub kluczy SSH.

### Użycie Personal Access Token (PAT):

1.  **Wygeneruj PAT na GitHub:**
    *   Przejdź do ustawień swojego profilu GitHub: `https://github.com/settings/profile`
    *   W lewym pasku bocznym kliknij **Developer settings**.
    *   Kliknij **Personal access tokens**, a następnie **Tokens (classic)**.
    *   Kliknij **Generate new token**, a następnie **Generate new token (classic)**.
    *   Nadaj tokenowi opisową nazwę (np. "VS Code Git").
    *   Ustaw datę ważności tokena.
    *   Wybierz niezbędne zakresy (`scopes`). Dla ogólnego dostępu do repozytorium zazwyczaj potrzebujesz `repo` (pełna kontrola nad prywatnymi repozytoriami) i `workflow`.
    *   Kliknij **Generate token**.
    *   **Ważne:** Skopiuj wygenerowany token natychmiast. Nie będziesz mógł go ponownie zobaczyć!

2.  **Użyj PAT do uwierzytelniania:**
    Kiedy Git poprosi o nazwę użytkownika i hasło:
    *   Dla **nazwy użytkownika**, wprowadź swoją nazwę użytkownika GitHub.
    *   Dla **hasła**, wklej swój nowo wygenerowany Personal Access Token.

Alternatywnie, możesz skonfigurować Git, aby bezpiecznie przechowywał twoje dane uwierzytelniające za pomocą Git Credential Manager:
    ```bash
    git config --global credential.helper manager
    ```
    Przy następnej operacji Git wymagającej uwierzytelnienia, zostaniesz poproszony o zalogowanie się przez przeglądarkę lub podanie PAT raz, a następnie zostanie on bezpiecznie zapisany.
