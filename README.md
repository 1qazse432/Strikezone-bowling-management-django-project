# StrikeZone — Bowling Management Platform

StrikeZone is a Django application for managing bowling centers, lanes, bowlers, games, and game scores. It provides operational CRUD workflows, a searchable scoreboard, performance analytics, and CSV exports. The interface uses Django templates and locally bundled Bootstrap assets.

## Main capabilities

- **Centers and lanes:** maintain venue details, lane surfaces, and lane availability. Lane numbers are unique within each center.
- **Bowler profiles:** maintain player profiles and calculate each bowler's average directly from recorded scores.
- **Game scheduling:** schedule games, assign available lanes, update statuses, and record participant results.
- **Scoreboard:** search, filter, sort, edit, and delete game scores. Duplicate bowler entries within a game are prevented.
- **Performance insights:** review score distribution, monthly activity, player rankings, center comparisons, and perfect games.
- **CSV export:** download the current scoreboard search as a spreadsheet-compatible CSV. Text cells are protected against spreadsheet formula injection.
- **Responsive interface:** Bootstrap 5.3.6, shared navigation, a comprehensive footer, reusable template partials, custom template tags and filters, and a custom 404 page.

The project uses three Django apps with separate responsibilities:

| App       | Responsibility |
|-----------|---|
| `centers` | Bowling centers and lanes |
| `players` | Bowler profiles and derived statistics |
| `games`   | Games, score records, scoreboard, analytics, and exports |

## Technology

- Python 3.12 or newer
- Django 6.1.2 (latest stable release at the time this project was assembled as was required for the project)
- SQLite
- Bootstrap 5.3.6 (bundled locally; no CDN dependency)

## Installation and startup

The project starts with its default configuration. No source-code edits, environment variables, database credentials, or external service credentials are required for local evaluation.

### 1. Extract the archive

Extract the project and open the `strikezone_project_fixed` directory, which contains `manage.py`.

### 2. Create a virtual environment

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

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

The database is created automatically as `db.sqlite3`. Migrations create the database schema only; they do not insert example or prepopulated records.

### 5. Start the application

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

To run the automated test suite:

```bash
python manage.py test
```

The project test suite contains 33 automated tests covering model validation, form behavior, empty-database workflows, navigation, CRUD routes, analytics, exports, and the custom 404 page.

## Configuration and environment variables

The default local configuration uses SQLite, `DEBUG=False`, and the allowed hosts `localhost`, `127.0.0.1`, and `testserver`. No credentials are required.

The following variables are optional. They are read directly from the process environment. The application does not load `.env` files automatically.

| Variable               | Default                          | Purpose |
|------------------------|----------------------------------|---|
| `DJANGO_SECRET_KEY`    | Development-only fallback        | Use a private random value outside local evaluation. |
| `DJANGO_DEBUG`         | `False`                          | Set to `True` for local debug output. Keep `False` to test the custom 404 page. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,testserver` | Comma-separated allowed hostnames. |

`.env.example` documents the optional settings but is not required. Example shell configuration:

**macOS / Linux**

```bash
export DJANGO_SECRET_KEY="replace-with-a-long-random-value"
export DJANGO_DEBUG="True"
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
```

**Windows PowerShell**

```powershell
$env:DJANGO_SECRET_KEY = "replace-with-a-long-random-value"
$env:DJANGO_DEBUG = "True"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
```

## Evaluator workflow

The database is intentionally empty after migration. Create all records through the website; the Django admin and direct database editing are not part of the workflow.

1. Open **Centers → Add center** and create a bowling center.
2. Open **Lanes → Add lane** and assign one or more lanes to that center.
3. Open **Bowlers → Add bowler** and create player profiles.
4. Open **Games → Schedule game** and select an available lane.
5. Open a game's detail page and select **Record participant score** for each bowler.
6. Open **Scoreboard** to search, sort, edit, delete, or export results.
7. Open **Insights** to review live performance statistics.

The main navigation and shared footer connect the principal pages. Once records exist, the footer also provides links to their detail, edit, and delete-confirmation pages.

## Data model

| Model           | Main relationships |
|-----------------|---|
| `BowlingCenter` | One center has many lanes. |
| `Lane`          | Each lane belongs to one center and can host many games. |
| `Bowler`        | One bowler can have many score records. |
| `BowlingGame`   | Each game uses one lane and has many score records. |
| `GameScore`     | Each score connects one game and one bowler. |

`BowlingGame` and `Bowler` have a many-to-many relationship through `GameScore`. The through model stores the score and optional result notes. A database uniqueness constraint permits only one score per bowler per game. Scores are limited to the ten-pin range of 0–300.

## Validation and implementation notes

- `config/forms.py` is included as a shared project module. All three apps import `BootstrapFormMixin` from `config.forms`; keep this file in the `config` package when copying or deploying the project.
- Forms define labels, help text, placeholders, and user-friendly validation messages. The shared mixin adds Bootstrap classes and accessible help/error attributes.
- Read-only or disabled fields are rendered on the lane and game forms to provide operational and scoring guidance. Derived bowler averages are not manually editable.
- New games can only use available lanes. A lane cannot be deleted while referenced by a game; a center cannot be deleted while it has lanes; and a bowler cannot be deleted while score records reference them.
- Successful create and update operations redirect to the relevant detail page. Deletion uses a confirmation page and relationship-aware checks.
- The application uses class-based views, reusable form and view mixins, a service layer for analytics and score queries, ORM aggregation, database constraints, and exception handling for concurrent duplicate-score submissions.
- All pages use the Django Template Engine, template inheritance, shared partials, built-in filters, and custom bowling template tags/filters.
- Bootstrap assets are served locally from `static/vendor/bootstrap/`. The local static route supports the coursework evaluation setup with the default `DEBUG=False` configuration. A production deployment should serve static files through a dedicated web server or static host.

## URL reference

| Page                  | URL |
|-----------------------|---|
| Dashboard             | `/` |
| Centers               | `/centers/` |
| Lanes                 | `/lanes/` |
| Bowlers               | `/players/` |
| Games                 | `/games/` |
| Scoreboard            | `/scores/` |
| CSV export            | `/scores/export/` |
| Performance insights  | `/insights/` |
| Custom not-found page | Django 404 handler when `DEBUG=False` |

## Project structure

```text
strikezone_project/
├── config/                 # Settings, root URLs, shared forms, context processors
├── centers/                # Bowling centers and lanes
├── players/                # Bowler profiles
├── games/                  # Games, scores, analytics, and exports
├── templates/              # Base layout, app pages, and reusable partials
├── static/                 # Site CSS and locally bundled Bootstrap
├── manage.py
├── requirements.txt
└── README.md
```
