# NUM Connect — Smart Student Portal

A production-quality Django 5 student portal: assignments, announcements,
campus events, study resources, an AI assistant, and global search — behind
a premium, responsive, light/dark UI built with Bootstrap 5 and vanilla JS.

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
├── core/                      # shared base model, mixins, middleware,
│                                 context processor, global search, seed command
├── accounts/                  # custom User + Profile, auth, profile views
├── dashboard/                 # aggregated dashboard view
├── assignments/                # Assignment Manager (full CRUD + search)
├── announcements/              # staff CRUD, student read/search
├── events/                     # Campus Events (staff CRUD, student view)
├── resources_app/              # Study Resources (upload, categories, download)
└── ai_assistant/                # Chat UI + pluggable AI provider
templates/                     # base layouts + shared includes
static/                        # design-system.css, components.css, main.css, JS
media/                         # user uploads (profile pictures, resources, events)
```

Each feature app owns its `models.py`, `forms.py`, `views.py`, `urls.py`
(namespaced), and templates — a self-contained vertical slice, wired into
the sidebar/dashboard as it's built.

## Setup

```bash
python -m venv venv
venv\Scripts\activate           # Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo_data  # optional: realistic demo data
python manage.py runserver
```

Visit http://127.0.0.1:8000/ — you'll be redirected to log in.

### Demo accounts (after `seed_demo_data`)

| Role    | Username | Password         |
|---------|----------|------------------|
| Admin   | admin    | AdminPass123!    |
| Student | jsmith   | StudentPass123!  |
| Student | akim     | StudentPass123!  |

Admin/staff accounts can create/edit/delete Announcements, Events, and
Study Resources (in-app, plus the full Django admin at `/admin/`). Students
get read/search access to those and full CRUD over their own Assignments.

## AI Assistant

`ai_assistant/providers.py` defines a `BaseAIProvider` interface. The
active provider is selected by the `AI_ASSISTANT_PROVIDER` setting:

- `local` (default) — matches student questions against the `FAQEntry`
  knowledge base (managed via Django admin). Fully offline.
- `openai` — set `AI_ASSISTANT_PROVIDER=openai` and `OPENAI_API_KEY`, then
  `pip install openai`. Views and templates need no changes to switch.

## Environments

- **Development** (`numconnect.settings.development`, the `manage.py`
  default): SQLite, `DEBUG=True`, console email backend.
- **Production** (`numconnect.settings.production`, used by `wsgi.py`):
  reads `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`,
  `DJANGO_CSRF_TRUSTED_ORIGINS` from the environment, enables HTTPS/HSTS
  security headers. Swap the SQLite `DATABASES` entry for a managed
  database before deploying.

## Running tests

Each app ships a `tests.py` covering permissions, CRUD, search, and the AI
provider. Because apps live under `apps/` and are imported as top-level
packages (via a `sys.path` insert in `settings/base.py`), run tests with
explicit app labels rather than a bare `manage.py test` — otherwise
`unittest`'s directory-based discovery imports modules under an `apps.`
prefix that doesn't match `INSTALLED_APPS` and errors out:

```bash
python manage.py test accounts dashboard assignments announcements events resources_app ai_assistant core
```

## Notes

- Run `python manage.py runserver` normally (autoreload on) during
  development — Django's reloader watches template/static/Python files and
  restarts automatically on change.
- File uploads (profile pictures, resources, event images) are capped at
  15 MB (`MAX_UPLOAD_SIZE_MB` in `settings/base.py`).
