# Podsumowanie Misji Drona DRN-BMB7

## Cel Misji
Zniszczenie tamy w pobliżu elektrowni **PWR6132PL** w celu przywrócenia chłodzenia reaktora (zgodnie z transkrypcją fabularną).

## Parametry Techniczne
- **Obiekt docelowy:** `PWR6132PL`
- **Sektor (x,y):** `2,4` (Kolumna 2, Wiersz 4)
- **Wysokość:** `100m`
- **Moc silników:** `10%` (po osiągnięciu celu)
- **Zadania dodatkowe:** Pełna kalibracja, wykonanie zdjęcia, raport powrotu.

## Sekwencja Instrukcji API
Instrukcje muszą być wysłane w tablicy `instructions` do endpointu `/verify`.

```json
[
  "calibrateGPS",
  "calibrateCompass",
  "selfCheck",
  "setDestinationObject(PWR6132PL)",
  "set(2,4)",
  "set(100m)",
  "set(engineON)",
  "set(10%)",
  "set(image)",
  "set(destroy)",
  "set(return)",
  "flyToLocation"
]
```

## Notatki Implementacyjne
1. **Kalibracja:** Wykonywana jako pierwszy krok przed startem silników.
2. **Kolejność:** Parametry lotu (`set`) muszą być ustawione przed wywołaniem `flyToLocation`.
3. **Moc:** Zmniejszona do 10% zgodnie z wymaganiem operatora.
4. **Endpoint:** `POST https://hub.ag3nts.org/verify`
