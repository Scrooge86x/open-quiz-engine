# Testowanie i Jakość Oprogramowania

## Temat projektu
Open Quiz Engine – aplikacja quizowa wykorzystująca Open Trivia DB.

## Opis projektu
Open Quiz Engine to aplikacja webowa (REST API + interfejs przeglądarkowy) umożliwiająca tworzenie i rozgrywanie quizów opartych na pytaniach z serwisu [Open Trivia DB](https://opentdb.com). Nie wymaga rejestracji ani logowania – gracze podają jedynie pseudonim.

Główne funkcje:
- **Tworzenie quizu** – prowadzący wybiera liczbę pytań (1–20) i opcjonalnie poziom trudności; aplikacja pobiera pytania z Open Trivia DB i zapisuje je lokalnie, dzięki czemu wszyscy gracze otrzymują te same pytania w tej samej kolejności.
- **Udostępnianie** – adres URL strony quizu jest jednocześnie linkiem do udostępnienia; wystarczy go skopiować i wysłać innym graczom.
- **Rozgrywka** – gracz wpisuje pseudonim, a następnie odpowiada na pytania jedno po drugim; po każdej odpowiedzi widzi, czy była poprawna, i jaka była prawidłowa opcja.
- **Wyniki i ranking** – po ukończeniu próby gracz widzi swój wynik (liczba poprawnych odpowiedzi) i czas, a także tabelę rankingową top-10 ukończonych prób dla danego quizu (sortowanie: wynik malejąco, czas rosnąco, data ukończenia rosnąco).

Architektura:
- Backend: Python 3.14 z FastAPI (endpointy synchroniczne), SQLAlchemy 2.x z SQLite, httpx do komunikacji z Open Trivia DB.
- Frontend: czysty HTML, CSS i JavaScript (bez frameworków, bez npm), serwowany statycznie przez FastAPI.
- Kod podzielony na warstwy: `errors/` (wyjątki domenowe), `db/` (silnik bazy danych i modele ORM), `logic/` (czyste funkcje), `clients/` (klient HTTP), `services/` (logika biznesowa), `api/` (routery, schematy, zależności).

## Uruchomienie projektu
1. Utwórz środowisko wirtualne:
```powershell
python -m venv .venv
```

2. Aktywuj środowisko wirtualne:

Windows (PowerShell):
```powershell
.venv\Scripts\activate
```

macOS / Linux:
```bash
source .venv/bin/activate
```

3. Zainstaluj zależności:
```powershell
pip install -r requirements.txt -r requirements-dev.txt
```

4. Uruchom aplikację:
```powershell
uvicorn src.main:app --reload
```

5. Otwórz http://127.0.0.1:8000/ (interfejs użytkownika) lub http://127.0.0.1:8000/docs (Swagger UI).

Uwagi:
- Utworzenie quizu wymaga połączenia z internetem, bo pytania są pobierane z Open Trivia DB (limit serwisu: jedno zapytanie na 5 sekund z jednego adresu IP). Granie w już utworzony quiz internetu nie wymaga.
- Plik bazy danych `quiz.db` jest tworzony automatycznie przy pierwszym uruchomieniu.

## Testy
TODO

## Dokumentacja API
Pełna specyfikacja API w formacie OpenAPI 3.1 znajduje się w pliku [`docs/openapi.json`](docs/openapi.json).  
Interaktywna dokumentacja (Swagger UI) jest dostępna pod adresem http://127.0.0.1:8000/docs po uruchomieniu aplikacji.

Aby wygenerować plik specyfikacji ponownie po zmianie kodu (z aktywowanym środowiskiem wirtualnym):
```powershell
python -c "import json; from src.main import create_app; print(json.dumps(create_app('sqlite://').openapi(), ensure_ascii=False, indent=2))" > docs\openapi.json
```

### Przegląd endpointów

Wszystkie ścieżki mają prefiks `/api`. Błędy domenowe zwracają JSON `{"error": "<kod>", "message": "<treść>"}`.

| Metoda | Ścieżka | Opis | Sukces | Błędy |
|--------|---------|------|--------|-------|
| `POST` | `/api/quizzes` | Utwórz quiz (opcjonalnie: `question_count`, `difficulty`) | 201 `QuizResponse` | 422, 502, 503 |
| `GET` | `/api/quizzes/{quiz_id}` | Pobierz informacje o quizie | 200 `QuizResponse` | 404 |
| `POST` | `/api/quizzes/{quiz_id}/attempts` | Rozpocznij próbę (wymagane: `nick`) | 201 `AttemptResponse` | 404, 422 |
| `GET` | `/api/quizzes/{quiz_id}/leaderboard` | Ranking ukończonych prób (top 10) | 200 `list[LeaderboardEntryResponse]` | 404 |
| `GET` | `/api/attempts/{attempt_id}/question` | Pobierz bieżące pytanie | 200 `QuestionResponse` | 404, 409 |
| `POST` | `/api/attempts/{attempt_id}/answer` | Wyślij odpowiedź (`question_id`, `selected_index`) | 200 `AnswerResponse` | 404, 409, 422 |
| `GET` | `/api/attempts/{attempt_id}/result` | Pobierz wynik próby | 200 `ResultResponse` | 404 |

### Sekwencja użycia API

**Twórca quizu**

1. `POST /api/quizzes` zwraca id quizu. Interfejs przekierowuje na `quiz.html?id=<id>`; adres tej strony jest linkiem do udostępnienia (samo id też wystarczy).

**Gracz** (twórca lub każdy, kto dostał link; od tego miejsca przebieg jest taki sam dla wszystkich)

2. `GET /api/quizzes/{quiz_id}` – informacje o quizie.
3. `GET /api/quizzes/{quiz_id}/leaderboard` – aktualny ranking.
4. `POST /api/quizzes/{quiz_id}/attempts` z pseudonimem zwraca `attempt_id`. Interfejs przechodzi na `play.html?attempt=<attempt_id>`.
5. Powtarzaj aż `finished` będzie `true`: `GET /api/attempts/{attempt_id}/question`, a potem `POST /api/attempts/{attempt_id}/answer`.
6. `GET /api/attempts/{attempt_id}/result` – wynik i czas.
7. `GET /api/quizzes/{quiz_id}/leaderboard` – ranking razem z ukończoną próbą.

Osoba, która dostała link, pomija krok 1 i zaczyna od kroku 2.

### Schematy odpowiedzi

**QuizResponse** – `id`, `difficulty` (null = dowolny), `question_count`

**AttemptResponse** – `attempt_id`, `quiz_id`, `nick`

**QuestionResponse** – `question_id`, `position` (od 0), `question_count`, `text`, `category`, `difficulty`, `options` (lista tekstów; poprawna odpowiedź nie jest oznaczona)

**AnswerResponse** – `is_correct`, `correct_index`, `finished`

**ResultResponse** – `attempt_id`, `quiz_id`, `nick`, `score`, `question_count`, `duration_seconds` (null gdy próba niezakończona)

**LeaderboardEntryResponse** – `rank`, `nick`, `score`, `duration_seconds`

### Kody błędów

| Kod błędu | HTTP | Znaczenie |
|-----------|------|-----------|
| `quiz_not_found` | 404 | Quiz o podanym id nie istnieje |
| `attempt_not_found` | 404 | Próba o podanym id nie istnieje |
| `invalid_nick` | 422 | Pseudonim pusty, za długi lub zawiera niedrukowalne znaki |
| `invalid_option` | 422 | Indeks wybranej opcji poza zakresem |
| `not_enough_questions` | 422 | Open Trivia DB nie ma wystarczającej liczby pytań dla zadanych parametrów |
| `attempt_finished` | 409 | Próba jest już zakończona |
| `wrong_question` | 409 | Przesłana odpowiedź dotyczy innego pytania niż bieżące |
| `upstream_rate_limited` | 503 | Open Trivia DB nałożyło limit zapytań (nagłówek `Retry-After: 5`) |
| `upstream_unavailable` | 502 | Open Trivia DB jest niedostępne lub zwróciło nieprawidłową odpowiedź |

## Przypadki testowe dla testera manualnego
TODO

## Technologie użyte w projekcie
- Python 3.14
- FastAPI – framework REST API
- SQLAlchemy 2.x (synchroniczny) – ORM i dostęp do bazy danych
- SQLite – wbudowana relacyjna baza danych
- Pydantic v2 – walidacja schematów żądań i odpowiedzi
- httpx – synchroniczny klient HTTP do komunikacji z Open Trivia DB
- uvicorn – serwer ASGI
- HTML, CSS i JavaScript (bez frameworków) – interfejs przeglądarkowy
- Open Trivia DB (https://opentdb.com) – źródło pytań, licencja CC BY-SA 4.0
- ruff – linter i formatter
