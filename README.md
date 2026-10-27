# StrikeZone — Bowling Management

StrikeZone is a Django web application for managing bowling centers, lanes, bowlers, scheduled games, and participant scores. The interface uses Bootstrap and Django templates. Authentication and user-facing account features are intentionally excluded.

## Features

1- Center and lane directory with availability and relationship-aware deletion checks.
2- Bowler profiles with automatically calculated averages based on recorded scores, plus search and average-based sorting.
3- Game scheduling, status filters, and detail pages.
4- Per-game bowler score entry, score editing, score deletion, and scoreboard ranking.
5- Responsive Bootstrap layout using locally bundled assets, a comprehensive CRUD-aware footer with links to all available record pages, reusable template partials, custom template filters/tags, and a custom 404 page.
6- SQLite by default; migrations create schema only and do not insert sample data.

## Languages used

- Python 3.12 or newer
- Django 6.1.2 (latest stable release at the time this project was assembled as was required for the prohect)
- SQLite
- Bootstrap 5.3.6 bundled locally under `static/vendor/bootstrap/` (no network required for framework CSS or JavaScript)


### Player scoring averages

A bowler's average is calculated automatically from all of that bowler's recorded game scores. It updates when a score is created, edited, or deleted. Players with no recorded scores display an em dash, and the average is not manually editable. Apply the included migration with `python manage.py migrate`.

## Installation and local run

From the extracted project directory:

### 1. Create and activate a virtual environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Apply migrations

```bash
python manage.py migrate
```

### 4. Run the development server

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. When `DJANGO_DEBUG=False`, the custom 404 page is used for missing routes. Bootstrap CSS and its JavaScript bundle are served from the project’s local `static/vendor/bootstrap/` directory, so layout, responsive navigation, forms, tables, buttons, and alerts work without external network access. `STATIC_URL` is configured as an absolute `/static/` path so assets load correctly on nested routes such as `/games/` and `/centers/1/`. A small local static-file route is included for the coursework evaluation workflow even when `DJANGO_DEBUG=False`; production deployments should serve static assets from a dedicated web server or static host.

## Suggested evaluator workflow

The database starts empty by design. All required objects can be created through the site's navigation; the Django admin is not required.

1. Open **Centers → Add center** and create a bowling center.
2. Open **Lanes → Add lane** and assign it to the center.
3. Open **Bowlers → Add bowler** and create at least two profiles.
4. Open **Games → Schedule game** and assign a lane, date/time, and status.
5. Open the game's detail page and use **Record participant score** for each bowler.
6. Open **Scoreboard** to sort, search, edit, or remove score records.

The UI provides navigation to every model: centers, lanes, bowlers, games, and game-score records. No admin or authentication interface is part of the required workflow. Lanes cannot be deleted while games reference them; centers cannot be deleted while lanes remain; bowlers with recorded scores cannot be deleted. These protections avoid broken relational data and return user-facing messages.

## URL map

| Section               | Route |
|-----------------------|-------|
| Dashboard             | `/` |
| Centers               | `/centers/` |
| Lanes                 | `/lanes/` |
| Bowlers               | `/players/` |
| Games                 | `/games/` |
| Scoreboard            | `/scores/` |
| Record a score        | `/scores/new/` |
| Custom not-found page | Handled by Django's `handler404` when `DEBUG=False` |

The shared footer links to all primary list/create routes and, once records exist, includes direct detail, edit, delete-confirmation, and game-specific score-entry links for each applicable record. This makes record-specific pages available from every page without requiring manual URL entry.

## Data model

- `BowlingCenter` has many `Lane` records (one-to-many).
- `BowlingGame` references a `Lane` (many-to-one).
- `BowlingGame` and `Bowler` have a many-to-many relationship through `GameScore`, which stores the numeric score and optional notes. Each bowler may have one score record per game; scores are validated between 0 and 300.

## Validation and engineering notes

Forms apply custom labels, help text, placeholders, Bootstrap widgets, and friendly validation messages. New games can only be assigned to lanes marked available; unavailable lanes are omitted from the scheduling choices and rejected by server-side form/model validation. Existing games may retain their current lane if it later becomes unavailable, but cannot be reassigned to an unavailable lane. Model validators and database constraints reinforce score bounds and uniqueness. A disabled, read-only guidance field is included on the lane and game forms, and the game-specific score form fixes the selected game. Successful writes redirect to the relevant detail page. Deletion requires a confirmation page.

The codebase uses three Django apps with separated responsibilities: `centers`, `players`, and `games`. Class-based views, shared form styling, template inheritance, partial templates, explicit URL namespaces, database-aware querysets, and custom template filters/tags are used to keep responsibilities cohesive.

## Tests

Run the test suite with:

```bash
python manage.py test
```

The tests cover public page access, core form validation, lane-number uniqueness, unavailable-lane scheduling restrictions, score bounds, duplicate score prevention, and game detail navigation.
# Strikezone-bowling-management-django-project
