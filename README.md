# TripAdmin Project

A Django project for managing trips with PDF generation capabilities.

## Project Structure

- **tripadmin**: Main Django project configuration
- **trips**: Django app for trip management

## Installation & Setup

### 1. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
```

**Activate the virtual environment:**

- **Windows**: `venv\Scripts\activate`
- **macOS/Linux**: `source venv/bin/activate`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

**Edit `.env` with your configuration:**
- `SECRET_KEY`: Your Django secret key (generate a new one for production)
- `DEBUG`: Set to `False` in production

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Features

- **Django 4.2+**: Latest stable Django framework
- **Crispy Forms**: Enhanced form rendering with `django-crispy-forms`
- **PDF Generation**: PDF export capabilities with `weasyprint`
- **Environment Configuration**: Secure settings management with `python-decouple`

## Development

### Create Django Migrations

```bash
python manage.py makemigrations
```

### Apply Migrations

```bash
python manage.py migrate
```

### Access Admin Panel

Navigate to `http://localhost:8000/admin/` and log in with your superuser credentials.

## Production Deployment

Before deploying to production:

1. Set `DEBUG=False` in your `.env` file
2. Generate a new `SECRET_KEY`
3. Update `ALLOWED_HOSTS` in `settings.py`
4. Configure a production database (e.g., PostgreSQL)
5. Set up proper static file handling
6. Use a production WSGI server (e.g., Gunicorn)

## Required Packages

- Django
- django-crispy-forms
- weasyprint
- python-decouple

## License

Your License Here
