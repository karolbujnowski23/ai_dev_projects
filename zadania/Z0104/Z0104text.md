## Transkrypcja filmu z Fabułą

"To imponujące... Przyznam, że nieźle go załatwiłeś. Operator zupełnie się nie zorientował, że rozmawiał z automatem innym niż dotychczas.

Mamy już przekierowaną paczkę, tylko musimy jeszcze dopracować pewne kwestie formalne.

Nasz transport zostanie przewieziony koleją. Użyjemy do tego jednej z linii kolejowych, która jest doprowadzona niemal wprost do elektrowni, którą chcemy reaktywować.

Wiem, że decydując się na współpracę z Centralą spodziewałeś się misji polegających bezpośrednio na ratowaniu świata i pracy z nowymi technologiami, ale... prawda jest taka, że każdy superbohater wcześniej czy później styka się ze zwykłym wypełnianiem urzędowych dokumentów. Takie jest życie.

Musimy przygotować fałszywe dokumenty przewozowe, które są niezbędne do poprawnego obsłużenia naszej paczki. Wszystkie informacje na temat tego, jak przygotować taką kartę przewozu towaru, znajdziesz w notatkach dołączonych do tego filmu.

Powodzenia!

Aaa! i obiecuję, że w tym tygodniu nie dam Ci już papierów do wypełniania."

## Zadanie

Musisz przesłać do Centrali poprawnie wypełnioną deklarację transportu w Systemie Przesyłek Konduktorskich. W takim dokumencie niestety nie można wpisać, czego się tylko chce, ponieważ jest on weryfikowany zarówno przez ludzi, jak i przez automaty.

Jako że dysponujemy zerowym budżetem, musisz tak spreparować dane, aby była to przesyłka darmowa lub opłacana przez sam "System". Transport będziemy realizować z Gdańska do Żarnowca.

Udało nam się zdobyć fałszywy numer nadawcy (450202122), który powinien przejść kontrolę. Sama paczka waży mniej więcej 2,8 tony. Nie dodawaj proszę żadnych uwag specjalnych, bo zawsze się o to czepiają i potem weryfikują takie przesyłki ręcznie.

Co do opisu zawartości, możesz wprost napisać, co to jest (to nasze kasety do reaktora). Nie będziemy tutaj ściemniać, bo przekierowujemy prawdziwą paczkę. A! Nie przejmuj się, że trasa, którą chcemy jechać jest zamknięta. Zajmiemy się tym później.

Dokumentacja przesyłek znajduje się tutaj:

[https://hub.ag3nts.org/dane/doc/index.md](https://hub.ag3nts.org/dane/doc/index.md)

Dane niezbędne do nadania przesyłki:

| Pole | Wartość |
| --- | --- |
| Nadawca (identyfikator) | `450202122` |
| Punkt nadawczy | Gdańsk |
| Punkt docelowy | Żarnowiec |
| Waga | 2,8 tony (2800 kg) |
| Budżet | 0 PP (przesyłka ma być darmowa lub finansowana przez System) |
| Zawartość | kasety z paliwem do reaktora |
| Uwagi specjalne | brak - nie dodawaj żadnych uwag |

Gotową deklarację (cały tekst, sformatowany dokładnie jak wzór) przesyłasz jako string w polu `answer.declaration` do `/verify`. Nazwa zadania to **sendit**.

### Format odpowiedzi do Hub-u

Wyślij metodą **POST** na `https://hub.ag3nts.org/verify`:

```json
{
  "apikey": "tutaj-twój-klucz",
  "task": "sendit",
  "answer": {
    "declaration": "tutaj-wstaw-caly-tekst-deklaracji"
  }
}
```

Pole `declaration` to pełny tekst wypełnionej deklaracji - z zachowaniem formatowania, separatorów i kolejności pól dokładnie tak jak we wzorze z dokumentacji.

### Jak do tego podejść - krok po kroku

1. **Pobierz dokumentację** - zacznij od `index.md`. To główny plik dokumentacji, ale nie jedyny - zawiera odniesienia do wielu innych plików (załączniki, osobne pliki z danymi). Powinieneś pobrać i przeczytać wszystkie pliki które mogą być potrzebne do wypełnienia deklaracji.
2. **Uwaga: nie wszystkie pliki są tekstowe** - część dokumentacji może być dostarczona jako pliki graficzne. Takie pliki wymagają przetworzenia z użyciem modelu z możliwościami przetwarzania obrazów (vision).
3. **Znajdź wzór deklaracji** - w dokumentacji znajdziesz ze wzorem formularza. Wypełnij każde pole zgodnie z danymi przesyłki i regulaminem.
4. **Ustal prawidłowy kod trasy** - trasa Gdańsk - Żarnowiec wymaga sprawdzenia sieci połączeń i listy tras.
5. **Oblicz lub ustal opłatę** - regulamin SPK zawiera tabelę opłat. Opłata zależy od kategorii przesyłki, jej wagi i przebiegu trasy. Budżet wynosi 0 PP - zwróć uwagę, które kategorie przesyłek są finansowane przez System.
6. **Wyślij deklarację** - gotowy tekst wyślij do `/verify`. Jeśli Hub odrzuci odpowiedź z komunikatem błędu, przeczytaj go uważnie - będzie zawierał wskazówki co poprawić.
7. **Koniec** - jeśli wszystko przebiegło pomyślnie, Hub zwróci flagę `{FLG:...}`.

### Wskazówki

- **Czytaj całą dokumentację, nie tylko index.md** - regulamin SPK składa się z wielu plików. Odpowiedzi na pytania dotyczące kategorii, opłat, tras czy wzoru deklaracji mogą znajdować się w różnych załącznikach.
- **Nie pomijaj plików graficznych** - dokumentacja zawiera co najmniej jeden plik w formacie graficznym. Dane w nim zawarte mogą być niezbędne do poprawnego wypełnienia deklaracji.
- **Wzór deklaracji jest ścisły** - formatowanie musi być zachowane dokładnie tak jak we wzorze. Hub weryfikuje zarówno wartości, jak i format dokumentu.
- **Skróty** - jeśli trafisz na skrót, którego nie rozumiesz, użyj dokumentacji żeby dowiedzieć się co on oznacza.

### Index of /dane/doc
==================

| ![Image 1: [ICO]](https://hub.ag3nts.org/icons/blank.gif) | [Name](https://hub.ag3nts.org/dane/doc/?C=N;O=D) | [Last modified](https://hub.ag3nts.org/dane/doc/?C=M;O=A) | [Size](https://hub.ag3nts.org/dane/doc/?C=S;O=A) | [Description](https://hub.ag3nts.org/dane/doc/?C=D;O=A) |
| --- | --- | --- | --- | --- |
| * * * |
| ![Image 2: [PARENTDIR]](https://hub.ag3nts.org/icons/back.gif) | [Parent Directory](https://hub.ag3nts.org/dane/) |  | - |  |
| ![Image 3: [TXT]](https://hub.ag3nts.org/icons/text.gif) | [dodatkowe-wagony.md](https://hub.ag3nts.org/dane/doc/dodatkowe-wagony.md) | 2026-02-16 13:42 | 444 |  |
| ![Image 4: [TXT]](https://hub.ag3nts.org/icons/text.gif) | [index.md](https://hub.ag3nts.org/dane/doc/index.md) | 2026-02-16 14:25 | 43K |  |
| ![Image 5: [TXT]](https://hub.ag3nts.org/icons/text.gif) | [poziomy.md](https://hub.ag3nts.org/dane/doc/poziomy.md) | 2026-02-16 11:05 | 33K |  |
| ![Image 6: [IMG]](https://hub.ag3nts.org/icons/image2.gif) | [trasy-wylaczone.png](https://hub.ag3nts.org/dane/doc/trasy-wylaczone.png) | 2026-02-16 14:19 | 102K |  |
| ![Image 7: [TXT]](https://hub.ag3nts.org/icons/text.gif) | [zalacznik-A.md](https://hub.ag3nts.org/dane/doc/zalacznik-A.md) | 2026-02-16 10:58 | 80 |  |
| ![Image 8: [TXT]](https://hub.ag3nts.org/icons/text.gif) | [zalacznik-B.md](https://hub.ag3nts.org/dane/doc/zalacznik-B.md) | 2026-02-16 10:58 | 102 |  |
| ![Image 9: [TXT]](https://hub.ag3nts.org/icons/text.gif) | [zalacznik-C.md](https://hub.ag3nts.org/dane/doc/zalacznik-C.md) | 2026-02-16 10:58 | 711 |  |
| ![Image 10: [TXT]](https://hub.ag3nts.org/icons/text.gif) | [zalacznik-D.md](https://hub.ag3nts.org/dane/doc/zalacznik-D.md) | 2026-02-16 10:58 | 1.4K |  |
| ![Image 11: [TXT]](https://hub.ag3nts.org/icons/text.gif) | [zalacznik-E.md](https://hub.ag3nts.org/dane/doc/zalacznik-E.md) | 2026-02-16 14:13 | 1.1K |  |
| ![Image 12: [TXT]](https://hub.ag3nts.org/icons/text.gif) | [zalacznik-F.md](https://hub.ag3nts.org/dane/doc/zalacznik-F.md) | 2026-02-16 10:58 | 1.7K |  |
| ![Image 13: [TXT]](https://hub.ag3nts.org/icons/text.gif) | [zalacznik-G.md](https://hub.ag3nts.org/dane/doc/zalacznik-G.md) | 2026-02-16 14:13 | 1.0K |  |
| ![Image 14: [TXT]](https://hub.ag3nts.org/icons/text.gif) | [zalacznik-H.md](https://hub.ag3nts.org/dane/doc/zalacznik-H.md) | 2026-02-16 13:27 | 865 |  |
| * * * |
