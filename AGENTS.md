# AGENTS.md

Quiz application built for a university course on software testing and quality ("Quiz application using Open Trivia DB").
Behavior is defined in `docs/DESIGN.md`. Treat it as the source of truth. If a task conflicts with it or is ambiguous, stop and ask instead of improvising.

## Stack
- Python 3.14, FastAPI (synchronous endpoints), SQLAlchemy 2.x (sync) with SQLite, Pydantic v2, httpx (sync)
- Frontend: plain HTML, CSS and JavaScript in `src/static`. No frameworks, no npm, no CDN.
- Tests (added in a later stage): `unittest`

## Layout
Only `main.py` and `config.py` live directly in `src/`. Everything else is in a package.
```
src/
  main.py              app factory: create_app()
  config.py            named constants
  errors/              domain exceptions, no HTTP knowledge
    base.py            QuizError
    not_found.py       QuizNotFoundError, AttemptNotFoundError
    validation.py      InvalidNickError, InvalidOptionError, NotEnoughQuestionsError
    conflict.py        AttemptFinishedError, WrongQuestionError
    upstream.py        UpstreamRateLimitedError, UpstreamUnavailableError
  db/
    engine.py          Base, engine, session factory, create_tables
    models/            one file per ORM model: quiz.py, question.py, attempt.py, answer.py
  logic/               pure functions, no I/O
  clients/             external API clients
  services/            business logic, dependencies injected via constructor
  api/
    schemas/           Pydantic request/response models of the REST API
    dependencies.py    FastAPI dependencies (session, services, clock, rng, trivia client)
    error_handlers.py  domain error -> HTTP response mapping
    quiz_routes.py
    attempt_routes.py
  static/              HTML, CSS, JS
scratch/               temporary demo scripts (see "Scratch scripts")
test/                  unit/, integration/, fixtures/ (added later)
docs/DESIGN.md
```
Import exceptions from their own module (for example `from src.errors.not_found import QuizNotFoundError`). `src/errors/__init__.py` stays empty.

## Commands (Windows, from the repository root)
- Create venv: `python -m venv .venv`, activate: `.venv\Scripts\activate`
- Install: `pip install -r requirements.txt -r requirements-dev.txt`
- Run: `uvicorn src.main:app --reload` (UI at http://127.0.0.1:8000/, Swagger at /docs)
- Lint and format: `ruff check .` and `ruff format .`
- Run a demo script: `python -m scratch.demo_<name>`
- Tests (later): `python -m unittest discover -s test -t .`

## Workflow rules
- Do exactly what the prompt asks. No extra features, files, endpoints, refactors or "improvements".
- NEVER run `git commit`, `git push`, `git tag` or change git config. The human commits. `git status` and `git diff` are allowed.
- Do not write tests unless the prompt explicitly asks for them.
- Before finishing: `ruff check .` passes, `ruff format .` is applied, and the verification steps from the prompt succeed.
- Final reply: briefly list changed files and the result of the verification steps.

## Scratch scripts
- A prompt may ask for a temporary demo script in `scratch/` (`scratch/__init__.py` exists so it runs with `python -m scratch.demo_<name>` from the repository root).
- A demo script prints what it does (inserted rows, fetched data, results) so the human can see the feature works. It is committed together with the feature.
- The next prompt deletes the previous demo script. Never delete or create scratch scripts on your own initiative.
- Demo scripts must pass `ruff check .` and `ruff format --check .`.

## Code rules
- PEP 8. `snake_case` for functions, variables and modules, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Everything is in English: identifiers, comments, docstrings, error messages, commit messages and the UI text. Exception: the README section headings required by the lecturer are Polish (the prompts give them exactly).
- Type hints on every function signature and attribute.
- No comments or docstrings for obvious code. Add a short comment only where something is non-obvious or intentional.
- No magic numbers or strings: use named constants from `src/config.py`. Add a constant to `config.py` in the commit that first needs it.
- Descriptive names. Do not use `data`, `tmp`, `obj`, `x`, `res`. Names of numbers must not sound like flags (`question_count`, not `questions`).
- Imports in three groups (standard library, third party, local `src.*`), a blank line between groups, alphabetical inside a group. No unused imports.
- Small functions (aim for at most 30 lines) and small single-responsibility classes. No giant modules.
- Dependencies (database session, trivia client, `random.Random`, clock) are injected through constructors and never created inside services or logic. No global mutable state.
- `logic/` contains only pure functions: no database, no network, no FastAPI imports.
- `services/` never import FastAPI. HTTP status codes exist only in `src/api/error_handlers.py`.
- Datetimes are naive UTC everywhere (`utc_now()` lives in `src/api/dependencies.py`).
- Never put the correct answer into any API response before the player has answered.
- In the frontend always insert external or user-provided text with `textContent`, never `innerHTML`.

## Test rules (from stage 2)
- `unittest` only. Unit tests in `test/unit/`, integration tests in `test/integration/`, fixtures in `test/fixtures/`, fakes in `test/fakes.py`.
- Arrange-Act-Assert. Every test has three sections marked with the comments `# Arrange`, `# Act`, `# Assert`, separated by blank lines.
- Exactly one assert per test. Several values only through `self.subTest`, still one assert per run.
- Test names: `test_<unit>_<condition>_<expected>`, for example `test_validate_nick_with_empty_string_raises_invalid_nick_error`.
- No real network in tests. Open Trivia DB is replaced by a fake client or `httpx.MockTransport`.
- Unit tests touch no database. Integration tests use in-memory SQLite (`sqlite://`).
- Tests are independent and deterministic: fixed clock, seeded `random.Random`.
