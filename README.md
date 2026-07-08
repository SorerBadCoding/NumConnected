# NUM Connect — Smart Student Portal

A production-quality Django 5 student portal covering the full academic
lifecycle — a public marketing site, a Notion/Linear-inspired dashboard,
assignments, a calendar, announcements, campus events, a discussion board,
a lecturer directory, study resources, an AI assistant, student analytics,
a campus map, a feedback center, and a notification system — behind a
premium, responsive, light/dark UI built with Bootstrap 5 and vanilla JS.

## Architecture

```
manage.py
numconnect/                    # project config
├── settings/
│   ├── base.py                # shared settings
│   ├── development.py         # DEBUG=True, used by manage.py
│   └── production.py          # env-driven secrets, security headers
├── urls.py
├── wsgi.py / asgi.py
apps/                          # local apps (importable as top-level packages)
├── core/                      # shared base model (+ ActivityLog, ContactMessage),
│                                 mixins, middleware, context processor, landing
│                                 page, global search, seed command
├── accounts/                  # custom User + Profile, auth, profile views
├── dashboard/                 # aggregated dashboard + student analytics
├── assignments/                # Assignment Manager (full CRUD + search)
├── calendar_app/                # Academic Calendar (month/week, exams, holidays)
├── announcements/              # staff CRUD, student read/search
├── events/                     # Campus Events (staff CRUD, RSVP, student view)
├── discussions/                 # Discussion Board (posts, likes, comments)
├── lecturers/                   # Lecturer Directory
├── resources_app/              # Study Resources (tags, favorites, downloads)
├── ai_assistant/                # Chat UI + pluggable AI provider
├── notifications/                # Notification Center
├── campus_map/                   # Interactive campus map
└── feedback/                     # Feedback Center / support tickets
templates/                     # base layouts + shared includes
static/                        # design-system.css, components.css, main.css, JS
media/                         # user uploads (profile pictures, resources, events)
```

Each feature app owns its `models.py`, `forms.py`, `views.py`, `urls.py`
(namespaced), and templates — a self-contained vertical slice, wired into
the sidebar/dashboard as it's built.

## Feature tour

- **Public landing page** (`/`) — animated hero, live stats, features,
  latest announcements/events, testimonials, FAQ accordion, contact form.
  Authenticated users are redirected straight to `/dashboard/`.
- **Dashboard** — welcome card, quick actions, stat tiles, Today's
  Schedule (assignments + events merged), Assignment Progress, Recent
  Activity feed, Recent Notifications, latest announcements/events/resources.
- **Assignment Manager** — full CRUD, search/filter, priority + status.
- **Academic Calendar** — month/week views color-coded by type
  (assignments/events/exams/holidays), with search.
- **Announcements & Campus Events** — staff CRUD, student read/search;
  events support RSVP (`attendees` M2M).
- **Discussion Board** — categorized posts with images, likes (AJAX),
  comments, search/filter, "Load More" pagination.
- **Lecturer Directory** — searchable/filterable faculty directory.
- **Study Resources** — categories, tags, favorites (AJAX), PDF preview
  modal, upload-progress bar, sort/filter, "Recently Viewed" panel.
- **AI Assistant** — quick-action prompt starters, suggested FAQ chips,
  recent-conversations sidebar; see below for the provider architecture.
- **Notification Center** — navbar dropdown + full page, unread badge,
  mark read/all-read; auto-created on new announcements/events/resources.
- **Student Analytics** (`/dashboard/analytics/`) — Chart.js bar/doughnut
  charts for weekly activity and on-time-vs-late completion, plus streak
  and download/RSVP counters.
- **Campus Map** — stylized interactive map with color-coded, clickable
  markers synced to a searchable/filterable location list.
- **Feedback Center** — students submit suggestions/bugs/feature
  requests/ratings; staff reply and change status (open → resolved/archived).

## Setup

```bash
python -m venv venv
venv\Scripts\activate           # Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo_data  # optional: realistic demo data for every app
python manage.py runserver
```

Visit http://127.0.0.1:8000/ — anonymous visitors see the landing page;
log in to reach the dashboard.

### Demo accounts (after `seed_demo_data`)

| Role    | Username | Password         |
|---------|----------|------------------|
| Admin   | admin    | AdminPass123!    |
| Student | jsmith   | StudentPass123!  |
| Student | akim     | StudentPass123!  |

Admin/staff accounts can create/edit/delete Announcements, Events, and
Study Resources (in-app, plus the full Django admin at `/admin/`), and
reply to/resolve feedback. Students get read/search access to those and
full CRUD over their own Assignments and Discussion posts.

## AI Assistant

`ai_assistant/providers.py` defines a `BaseAIProvider` interface. The
active provider is selected by the `AI_ASSISTANT_PROVIDER` setting:

- `local` (default) — matches student questions against the `FAQEntry`
  knowledge base (managed via Django admin). Fully offline.
- `openai` — set `AI_ASSISTANT_PROVIDER=openai` and `OPENAI_API_KEY`, then
  `pip install openai`. Views and templates need no changes to switch.

Quick-action buttons (Study Tips, Programming Helper, Summarize Notes,
Generate Quiz, Explain Code) insert a starter prompt into the composer
for the student to complete — they run through the same provider
abstraction, so they'll get real AI-quality answers the moment a real
provider is configured.

## Scheduled tasks

This project has no background task runner (Celery, etc.). One
management command is meant to be run periodically in production:

```bash
python manage.py send_due_reminders   # notifies students of assignments due within 24h
```

Schedule it hourly via cron / Windows Task Scheduler / your platform's
scheduled-jobs feature.

## Environments

- **Development** (`numconnect.settings.development`, the `manage.py`
  default): SQLite, `DEBUG=True`, console email backend.
- **Production** (`numconnect.settings.production`, used by `wsgi.py`):
  Postgres via `DATABASE_URL` (falls back to SQLite if unset), WhiteNoise
  for static files, HTTPS/HSTS security headers. Reads `DJANGO_SECRET_KEY`,
  `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` from the
  environment.

## Deploying to Railway

The repo already has what Railway needs: a `Procfile`, `requirements.txt`
with `gunicorn`/`whitenoise`/`dj-database-url`/`psycopg`, and
`numconnect/settings/production.py` wired for `DATABASE_URL`.

1. **Push to GitHub** (Railway deploys from a repo).
2. **New Project → Deploy from GitHub repo** in the Railway dashboard,
   pick this repo.
3. **Add a database**: in the project, `+ New` → `Database` → `PostgreSQL`.
   Railway creates it and exposes `DATABASE_URL` to other services in the
   project automatically.
4. **Set environment variables** on the web service (`Variables` tab):

   | Variable | Value |
   |---|---|
   | `DJANGO_SETTINGS_MODULE` | `numconnect.settings.production` |
   | `DJANGO_SECRET_KEY` | output of `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
   | `DJANGO_ALLOWED_HOSTS` | `your-app.up.railway.app` (see step 5) |
   | `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://your-app.up.railway.app` |

   `DATABASE_URL` is injected automatically once Postgres is linked —
   don't set it by hand. (The settings also auto-detect Railway's
   `RAILWAY_PUBLIC_DOMAIN` as a fallback, but setting the two above
   explicitly is more reliable.)
5. **Deploy**, then open `Settings → Networking` on the web service and
   click **Generate Domain** to get your `*.up.railway.app` URL. Copy it
   into `DJANGO_ALLOWED_HOSTS` / `DJANGO_CSRF_TRUSTED_ORIGINS` above if you
   hadn't already, then redeploy (or just restart — Railway restarts
   automatically when variables change).
6. **First-run data**: open a shell for the service (`railway run` via the
   CLI, or the dashboard's shell) and run:
   ```bash
   python manage.py createsuperuser
   # optional:
   python manage.py seed_demo_data
   ```
   Migrations and `collectstatic` already run automatically on every
   deploy via the `Procfile`.

**Media uploads (profile pictures, resources, event/discussion images)
will NOT persist across redeploys** unless you either:
- add a **Railway Volume** mounted at `/app/media` (simplest — Railway
  dashboard → service → `Volumes` → add one, mount path `media`), or
- switch `DEFAULT_FILE_STORAGE` to S3/Cloudinary via `django-storages` for
  real horizontal scaling.

For a demo/portfolio deploy, the Volume is the quick, correct fix — do
that before uploading real files.

## Running tests

Each app ships a `tests.py` covering permissions, CRUD, search, and the AI
provider (83 tests total). Because apps live under `apps/` and are
imported as top-level packages (via a `sys.path` insert in
`settings/base.py`), run tests with explicit app labels rather than a bare
`manage.py test` — otherwise `unittest`'s directory-based discovery
imports modules under an `apps.` prefix that doesn't match
`INSTALLED_APPS` and errors out:

```bash
python manage.py test accounts dashboard assignments announcements events resources_app ai_assistant core notifications calendar_app discussions lecturers campus_map feedback
```

## Notes

- Run `python manage.py runserver` normally (autoreload on) during
  development — Django's reloader watches template/static/Python files and
  restarts automatically on change.
- File uploads (profile pictures, resources, event images, discussion
  images, lecturer photos) are capped at 15 MB (`MAX_UPLOAD_SIZE_MB` in
  `settings/base.py`).
- Chart.js is loaded via CDN only on the analytics page — no new Python
  dependency was introduced for it.
