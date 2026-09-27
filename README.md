# DuraCast — Professional Construction Services Website

A complete Django 4.2 website for a construction company: a responsive, animated
public landing site plus a secure, configurable staff dashboard for managing
leads, projects, services, FAQs and site copy.


## About the Tailwind setup

This project loads Tailwind CSS from the **Play CDN**
(`https://cdn.tailwindcss.com`) — see `templates/base.html`. Design tokens
(colors, fonts, plugins) are configured inline in that same file.

Custom animation CSS (hero shimmer, button shine, scroll reveals, etc.)
lives in `static/css/style.css` and is loaded as a plain stylesheet.

### Files you can ignore

The following files are scaffolding for a future Tailwind CLI build. They
are **not loaded** and **not required** to run the project:

- `package.json`
- `tailwind.config.js`
- `static/src/input.css`

If you see these, don't run `npm install` or `npm run build` — nothing in
the current site depends on their output. They're kept for when we migrate
off the Play CDN in production.


## Stack

| Layer      | Technology                                              |
|------------|---------------------------------------------------------|
| Back-end   | Python 3.10+, Django 4.2+                               |
| Database   | PostgreSQL (production) / SQLite (development)          |
| Templating | Django Templates                                        |
| Styling    | Tailwind CSS (utility-first, no Bootstrap)              |
| Interactivity | Alpine.js 3 + vanilla JavaScript                     |
| Forms      | django-crispy-forms + crispy-tailwind                   |
| Animation  | AOS (Animate On Scroll) + Spline 3D viewer              |
| Icons      | Font Awesome 6                                          |
| Fonts      | Montserrat (headings) / Open Sans (body)                |

## Quick start

```bash
# 1. Clone and enter the project
git clone https://github.com/mchrnderitu-tech/duracast.git
cd duracast_project

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate     # Linux/macOS 
    #For  Windows cmd.exe: .venv\Scripts\activate
    #For  Windows Powershell: .\.venv\Scripts\Activate.ps1 

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure environment overrides
# The project ships with safe development defaults, so this step is optional.
# Create a .env file only if you want to override the defaults:
cp .env.example .env


# 5. Create the database schema
python manage.py makemigrations
python manage.py migrate

# 6. Seed realistic demo content (services, projects, FAQs, site copy)
python manage.py seed_data

# 7. Create your staff account
python manage.py createsuperuser

# 8. Run the development server
python manage.py runserver
