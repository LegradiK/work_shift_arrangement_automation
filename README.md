# RotaFlow — Work Shift Arrangement

> ⚠️ **This project is still ongoing and not finished.** Features may be incomplete, subject to change, or missing.

A Django-based web application for organising and visualising staff work shifts across a 6-month rolling calendar.

---

## Features

### Calendar View
- Monthly calendar powered by [FullCalendar v6](https://fullcalendar.io/)
- Three shift types displayed per day: **Morning** (06:00–14:00), **Afternoon** (14:00–22:00), **Night** (22:00–06:00)
- Each shift bar shows the number of staff assigned
- Filter the calendar to a single shift type using the Morning / Afternoon / Night buttons in the toolbar

### Staff Sidebar
- Staff are organised into labelled category bars matching the shift colour scheme:
  - **Full time – Day**
  - **Full time – Night**
  - **Part time – Day**
  - **Part time – Night**
- Click **All** to return to the full overview
- Click any staff member's name to switch to their personal calendar view

### Personal Staff Calendar
- Shows only the shifts a selected staff member is assigned to
- Displays a **weekly hours total** in each Saturday cell
- Displays a **monthly hours total** in the info bar below the toolbar
- Hours are **flagged in red** if they fall more than 20% outside the expected range:
  - Full-time: ~37.5 h/week, ~160 h/month
  - Part-time: ~20 h/week, ~87 h/month

### Understaffing & Overstaffing Warnings
- A **warning icon** appears on a shift bar when the number of assigned staff falls below the minimum threshold:
  - Morning / Afternoon: fewer than 4 staff
  - Night: fewer than 3 staff
- An **overstaffed icon** appears when the number exceeds the maximum:
  - Morning / Afternoon: more than 6 staff
  - Night: more than 5 staff
- A legend explaining both icons is shown in the info bar when viewing the full overview (All)

### Admin Features
- Admins can log in via the **Login** button in the top-right of the header
- When logged in, clicking a shift bar opens a popup to:
  - View all staff currently assigned to that shift
  - **Add** a staff member from a dropdown
  - **Remove** a staff member with the ✕ button
  - **Confirm** changes and close the popup (calendar refreshes automatically)

### Shift Generation
- A management command (`python manage.py generate_shifts`) generates 6 months of shifts from today based on each staff member's employment type and shift preference stored in the database:
  - **Full-time** staff: 5 shifts per week (2 days off), morning/afternoon or night depending on preference
  - **Part-time** staff: 2–3 shifts per week on a 3-3-2 cycle averaging ~20 h/week

---

## Setup & Running

Create a `data.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

> `data.env` is listed in `.gitignore` and should never be committed.

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Generate 6 months of shifts
python manage.py generate_shifts

# Run the development server
python manage.py runserver
```

> To access admin features, create a superuser: `python manage.py createsuperuser`

---

## Tech Stack

- **Backend:** Django 6
- **Database:** SQLite
- **Frontend:** FullCalendar v6, HTMX v2, Nunito (Google Fonts)
- **Auth:** Django built-in authentication

---

## Icon Credits

- <a href="https://www.flaticon.com/free-icons/warning" title="warning icons">Warning icons by Good Ware — Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/danger" title="danger icons">Danger icons by Andrean Prabowo — Flaticon</a>
