# Quiz Application: Design

(Repository copy: `docs/DESIGN.md`. Single source of truth for behavior.)

## 1. Overview
A web application (REST API + browser UI) where anyone creates a quiz from Open Trivia DB questions, shares its link, and players take it by entering only a nick. There are no accounts and no login. The whole application, including the UI, is in English.

Open Trivia DB returns random questions on every call, so a quiz stores a snapshot of the questions in the local database. All players of the same quiz get the same questions in the same order. The external API is called only when a quiz is created, never during play.

## 2. Scope
In scope: create quiz, play quiz (attempt), per-quiz leaderboard, browser UI.
Out of scope: authentication, categories, editing/deleting/expiring quizzes, real-time multiplayer, timers, question types other than `multiple` and `boolean`.

## 3. Flow
1. Creator submits `question_count` and optional `difficulty`. Backend calls Open Trivia DB once, stores quiz and questions, returns the quiz id. UI redirects to the quiz page (its URL is the shareable link).
2. Player opens the quiz page, enters a nick, an attempt is created, UI goes to the play page.
3. Play page loads the current question. Player picks an option, server evaluates it and returns feedback, the position advances. After the last question the attempt is finished.
4. Result page shows score and duration plus the quiz leaderboard.

## 4. Domain rules
- R1. `question_count` 1..20 (default 10). `difficulty` optional: `easy`, `medium`, `hard`. No category and no type filter.
- R2. Stored text is HTML-decoded. `multiple` questions: options shuffled once at creation and stored. `boolean` questions: options are always `["True", "False"]` (not shuffled), `correct_index` is 0 for "True" and 1 for "False". The question type is not stored; both kinds are just a list of options and a correct index.
- R3. If the API returns fewer questions than requested, store what came back. Zero questions: `not_enough_questions`.
- R4. Nick: trimmed, 1..30 characters, printable characters only. Not unique.
- R5. Questions are asked in order of `position` (0-based). No skipping, no going back. An answer is an option index.
- R6. An answer request carries `question_id`. It must equal the current question, otherwise `wrong_question` (409).
- R7. `selected_index` must be in `0..option_count-1`, otherwise `invalid_option` (422).
- R8. 1 point per correct answer. After the last question `finished_at` is set. An attempt is finished exactly when `finished_at` is not null (there is no status field).
- R9. After the attempt is finished, getting a question and submitting an answer give `attempt_finished` (409). The result is always available.
- R10. Leaderboard: finished attempts only. Order: score descending, duration ascending, `finished_at` ascending. Top 10. Rank is sequential 1..n.
- R11. Check order in `submit_answer`: attempt exists, attempt not finished, `question_id` matches, option index valid.
- R12. The correct answer (index or text) is never exposed before the answer is submitted.

## 5. Data model (SQLite, SQLAlchemy 2.x typed mappings)
- `Quiz`: `id` (str, uuid4, PK), `difficulty` (str or null), `created_at` (datetime). Relationship `questions` ordered by `position`, cascade delete. Property `question_count` = number of questions.
- `Question`: `id` (int, PK, autoincrement), `quiz_id` (FK), `position` (int), `text` (str), `category` (str), `difficulty` (str), `options` (JSON list of str), `correct_index` (int). Unique (`quiz_id`, `position`). Relationship `quiz` (back_populates `questions`).
- `Attempt`: `id` (str, uuid4, PK), `quiz_id` (FK), `nick` (str), `current_position` (int, default 0), `score` (int, default 0), `started_at` (datetime), `finished_at` (datetime or null). Property `is_finished` = `finished_at is not None`. Relationship `answers`.
- `Answer`: `id` (int, PK), `attempt_id` (FK), `question_id` (FK), `selected_index` (int), `is_correct` (bool). Unique (`attempt_id`, `question_id`).
- All datetimes are naive UTC.
- ORM models live one per file in `src/db/models/`, all imported in `src/db/models/__init__.py` so that `Base.metadata` knows every table.

## 6. Open Trivia DB integration
Request: `GET https://opentdb.com/api.php?amount={question_count}` plus `&difficulty={difficulty}` when set. No category, type, token or encode parameters. Text comes in the default HTML-entity encoding (for example `&quot;`).

Response:
```json
{"response_code": 0, "results": [
  {"type": "multiple", "difficulty": "medium", "category": "Animals",
   "question": "...", "correct_answer": "Krill",
   "incorrect_answers": ["Lobsters", "Shrimp", "Crabs"]}
]}
```
`type` is `multiple` (4 options) or `boolean` (`True`/`False`).

`response_code` mapping:
| Code | Meaning | Our error |
|---|---|---|
| 0 | success | none |
| 1 | not enough questions | `NotEnoughQuestionsError` |
| 5 | rate limit (1 request per 5 s per IP) | `UpstreamRateLimitedError` |
| 2, 3, 4 | invalid parameter / token problems | `UpstreamUnavailableError` |

Timeout 10 s. Network error, timeout, non-200 status, invalid JSON or missing keys: `UpstreamUnavailableError`. No retries.
Fields `question`, `correct_answer`, `incorrect_answers`, `category` are decoded with `html.unescape` and stripped by the quiz service before storing (the client returns raw values).

## 7. REST API (prefix `/api`)
| Method and path | Request body | Success | Errors |
|---|---|---|---|
| `POST /api/quizzes` | `{"question_count": 10, "difficulty": "easy"}` (both optional) | 201 `QuizResponse` | 422 validation, 422 `not_enough_questions`, 503 `upstream_rate_limited`, 502 `upstream_unavailable` |
| `GET /api/quizzes/{quiz_id}` | none | 200 `QuizResponse` | 404 `quiz_not_found` |
| `POST /api/quizzes/{quiz_id}/attempts` | `{"nick": "Ala"}` | 201 `AttemptResponse` | 404 `quiz_not_found`, 422 `invalid_nick` |
| `GET /api/attempts/{attempt_id}/question` | none | 200 `QuestionResponse` | 404 `attempt_not_found`, 409 `attempt_finished` |
| `POST /api/attempts/{attempt_id}/answer` | `{"question_id": 12, "selected_index": 3}` | 200 `AnswerResponse` | 404 `attempt_not_found`, 409 `attempt_finished`, 409 `wrong_question`, 422 `invalid_option` |
| `GET /api/attempts/{attempt_id}/result` | none | 200 `ResultResponse` | 404 `attempt_not_found` |
| `GET /api/quizzes/{quiz_id}/leaderboard` | none | 200 `list[LeaderboardEntryResponse]` | 404 `quiz_not_found` |

Schemas (`src/api/schemas/`):
- `QuizResponse`: `id`, `difficulty`, `question_count`
- `AttemptResponse`: `attempt_id`, `quiz_id`, `nick`
- `QuestionResponse`: `question_id`, `position`, `question_count`, `text`, `category`, `difficulty`, `options` (no correct answer fields). `question_count` is there because the play page knows only the attempt id.
- `AnswerResponse`: `is_correct`, `correct_index`, `finished` (the UI shows the correct option text from `options[correct_index]`)
- `ResultResponse`: `attempt_id`, `quiz_id`, `nick`, `score`, `question_count`, `duration_seconds` (float rounded to 1 decimal, null while the attempt is in progress)
- `LeaderboardEntryResponse`: `rank`, `nick`, `score`, `duration_seconds`
- `ErrorResponse`: `error`, `message` (documented in OpenAPI for error statuses)

## 8. Error contract
Domain errors return `{"error": "<code>", "message": "<text>"}`.
| Code | HTTP |
|---|---|
| `quiz_not_found`, `attempt_not_found` | 404 |
| `invalid_nick`, `invalid_option`, `not_enough_questions` | 422 |
| `attempt_finished`, `wrong_question` | 409 |
| `upstream_rate_limited` | 503 (+ header `Retry-After: 5`) |
| `upstream_unavailable` | 502 |
Request body validation errors keep the default FastAPI 422 body.

## 9. Architecture
- `create_app(database_url: str = DATABASE_URL) -> FastAPI`: builds engine and session factory, creates tables, stores the session factory in `app.state.session_factory`, registers error handlers, includes routers, mounts `src/static` at `/` (with `html=True`) last.
- `create_db_engine(database_url)`: SQLite gets `check_same_thread=False`; the in-memory URL `sqlite://` uses `StaticPool`.
- Services take dependencies through constructors: `QuizService(session, trivia_client, rng, clock)`, `AttemptService(session, clock)`, `LeaderboardService(session)`. `clock` is `Callable[[], datetime]`, `rng` is `random.Random`.
- `TriviaClient` is a `Protocol` with `fetch_questions(question_count: int, difficulty: str | None) -> list[TriviaQuestion]`. `HttpTriviaClient` implements it with httpx. Tests will use fakes.
- FastAPI dependencies live in `src/api/dependencies.py` (together with `utc_now()`) and can be overridden in tests.
- Endpoints are synchronous `def` functions.
- Service return types: `AttemptService.submit_answer` returns `AnswerOutcome(is_correct, correct_index, finished)`; `AttemptService.get_result` returns `AttemptResult(attempt_id, quiz_id, nick, score, question_count, duration_seconds)`; `LeaderboardService.get_leaderboard` returns `list[LeaderboardEntry(rank, nick, score, duration_seconds)]`. Field names match the response schemas.

## 10. UI (plain HTML, CSS, JS in `src/static`)
- UI text is English. Question texts are English (they come from the API).
- Pages: `index.html` (create quiz), `quiz.html?id=` (quiz info, share link, nick form, leaderboard), `play.html?attempt=` (one question at a time with feedback), `result.html?attempt=` (score, duration, leaderboard).
- JS files: `common.js` (API helper, error box, query params, duration formatting), plus one script per page.
- All pages show a footer: Open Trivia DB (https://opentdb.com), license CC BY-SA 4.0.
- External and user text is always inserted with `textContent`.
- Responsive, readable on a phone. Errors from the API are shown in a red box under the form.
- Refreshing the play page shows the current question; feedback for an already submitted answer is not restored.

## 11. Constants (`src/config.py`)
`APP_TITLE = "Quiz Application"`, `APP_VERSION = "0.1.0"`, `DATABASE_URL = "sqlite:///quiz.db"`, `TRIVIA_API_URL = "https://opentdb.com/api.php"`, `TRIVIA_TIMEOUT_SECONDS = 10`, `TRIVIA_CODE_SUCCESS = 0`, `TRIVIA_CODE_NOT_ENOUGH_QUESTIONS = 1`, `TRIVIA_CODE_RATE_LIMITED = 5`, `RATE_LIMIT_RETRY_SECONDS = 5`, `MIN_QUESTIONS = 1`, `MAX_QUESTIONS = 20`, `DEFAULT_QUESTIONS = 10`, `MIN_NICK_LENGTH = 1`, `MAX_NICK_LENGTH = 30`, `LEADERBOARD_SIZE = 10`, `QUESTION_TYPE_MULTIPLE = "multiple"`, `QUESTION_TYPE_BOOLEAN = "boolean"`, `BOOLEAN_OPTIONS = ("True", "False")`.
Each constant is added in the commit that first needs it.

## 12. Domain exceptions (`src/errors/`)
Base `QuizError(Exception)` in `base.py` with class attribute `error_code` and instance attribute `message`. Subclasses by file: `not_found.py` (`QuizNotFoundError`, `AttemptNotFoundError`), `validation.py` (`InvalidNickError`, `InvalidOptionError`, `NotEnoughQuestionsError`), `conflict.py` (`AttemptFinishedError`, `WrongQuestionError`), `upstream.py` (`UpstreamRateLimitedError`, `UpstreamUnavailableError`). HTTP statuses are mapped only in `src/api/error_handlers.py`.

## 13. API usage sequence
Creator:
1. `POST /api/quizzes` returns the quiz id. The UI redirects to `quiz.html?id=<id>`; that URL is the link to share (sending only the id also works).

Player (the creator or anyone with the link; this part is identical for everyone):
2. `GET /api/quizzes/{quiz_id}` for the quiz info.
3. `GET /api/quizzes/{quiz_id}/leaderboard` for the current ranking.
4. `POST /api/quizzes/{quiz_id}/attempts` with a nick returns `attempt_id`. The UI goes to `play.html?attempt=<attempt_id>`.
5. Repeat until `finished` is true: `GET /api/attempts/{attempt_id}/question`, then `POST /api/attempts/{attempt_id}/answer`.
6. `GET /api/attempts/{attempt_id}/result` for score and duration.
7. `GET /api/quizzes/{quiz_id}/leaderboard` to see the ranking including the finished attempt.

Someone who receives the link skips step 1 and starts at step 2.
