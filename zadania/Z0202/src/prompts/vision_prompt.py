VISION_PROMPT_SINGLE_TILE = """
Na obrazku znajduje się jeden wycięty fragment (płytka) z planszy z widocznym na niej fragmentem przewodu (kabla).
Określ, do których krawędzi tego kafelka dochodzi przewód.
Krawędzie mogą to być tylko: "top" (góra), "bottom" (dół), "left" (lewo), "right" (prawo).

Zwróć TYLKO obiekt JSON z listą wyłapanych krawędzi. Nie dodawaj żadnego dodatkowego tekstu ani znaków markdown (np. ```json).
Przykład poprawnej odpowiedzi:
{
  "edges": ["top", "left"]
}
Jeśli kafelka nie posiada żadnego narysowanego przewodu (co nie powinno mieć miejsca), zwróć:
{
  "edges": []
}
"""

VISION_PROMPT_FULL_BOARD = """
Na obrazku znajduje się szachownica 3x3 z przewodami.
Zignoruj resztę obrazka (elektrownie po bokach, itp.). Skup się TYLKO na siatce 3x3 na środku.

Dla każdego z 9 kafelków (od 1x1 do 3x3) określ, do jakich krawędzi danego kafelka dochodzi przewód.
Krawędzie to wyłącznie: "top", "bottom", "left", "right".

Zwróć TYLKO wynik w postaci poprawnego JSON, reprezentującego słownik, gdzie kluczem jest identyfikator pola (np. "1x1"), a wartością lista krawędzi do których dotyka przewód.
Nie dodawaj żadnego dodatkowego tekstu ani znaczników markdown.

Przykład poprawnego wyniku:
{
  "1x1": ["bottom", "right"],
  "1x2": ["left", "right", "bottom"],
  "1x3": ["left", "right"],
  "2x1": ["top", "bottom"],
  "2x2": ["top", "bottom", "right"],
  "2x3": ["left", "right", "bottom"],
  "3x1": ["top", "left", "right"],
  "3x2": ["top", "left"],
  "3x3": ["top", "right"]
}
"""
