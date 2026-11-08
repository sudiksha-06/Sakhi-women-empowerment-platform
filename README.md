# Sakhi – Women Empowerment & SHG Management Platform

A runnable full-stack MVP using React/Vite, Django REST Framework, JWT, and SQLite by default (switchable to MySQL). Includes demo seed data, skill assessment, courses, opportunities, product catalogue, pricing calculator, SHG ledger, financial summaries, and a Hindi/Hinglish voice assistant UI.

## Requirements
- Python 3.10+
- Node.js 18+
- MySQL 8+ (optional; SQLite works out of the box)

## 1. Backend
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows; on macOS/Linux use: cp .env.example .env
python manage.py makemigrations core
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```
Demo API: `http://127.0.0.1:8000/api/`

Demo credentials:
- username: `sakhi_demo`
- password: `Sakhi@12345`

## 2. Frontend
Open a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Open the Vite URL shown in the terminal (usually http://localhost:5173).

## MySQL setup
Create a database named `sakhi_db`, then edit `backend/.env`:
```
DB_ENGINE=mysql
DB_NAME=sakhi_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```
Install `mysqlclient` (included in requirements). If it fails to build on Windows, use SQLite for the demo or install the MySQL Connector/C build prerequisites.

## Gemini (optional)
Set `GEMINI_API_KEY` in `backend/.env`. The app has deterministic fallback responses when no key is configured. Do not commit real API keys.

## Important notes
- This is a functional educational MVP, not a certified banking/accounting product.
- Voice recognition uses browser Web Speech API and is best supported in Chrome/Edge. HTTPS or localhost is required for microphone access.
- Every ledger write requires explicit confirmation in the UI and is revalidated by the API. The API uses authenticated users and database transactions.
- Configure `DEBUG=False`, strong `SECRET_KEY`, HTTPS, backups, rate limiting, email verification, audit policies, and deployment secrets before production use.
