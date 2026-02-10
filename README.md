# Videoflix

> Django-based video streaming platform with adaptive HLS streaming and asynchronous video processing.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Development](#development)

## Features

- 🔐 **Authentication** - User registration, email verification, JWT-based login
- 🎥 **Adaptive Streaming** - HLS with multiple quality levels (480p, 720p, 1080p)
- ⚡ **Async Processing** - Background video transcoding with Django RQ
- 🖼️ **Auto Thumbnails** - Automatic thumbnail extraction from videos
- 🛡️ **Security** - HTTP-only cookies, CSRF protection, CORS
- 📦 **Dockerized** - Complete Docker setup for production-ready deployment

## Tech Stack

**Backend** • Django 6.0.1 • Django REST Framework  
**Database** • PostgreSQL  
**Cache & Queue** • Redis • Django RQ  
**Video** • FFmpeg • HLS  
**Auth** • JWT (SimplejWT)  
**Infrastructure** • Docker • Docker Compose

## Prerequisites

- Docker and Docker Compose
- Python 3.12+ _(for local development)_

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/AbbasEl11/videoflix_app
cd videoflix_app
```

**2. Create environment file**

Create `.env` in project root (see `.env.template`):

```env
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=adminpassword
DJANGO_SUPERUSER_EMAIL=admin@example.com

SECRET_KEY="your_secret_key_here"
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379
REDIS_DB=0

EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email_user
EMAIL_HOST_PASSWORD=your_email_user_password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=default_from_email
```

**3. Build and start services**

```bash
docker-compose up --build
```

The entrypoint automatically handles:
- Database migrations
- Superuser creation
- Static files collection
- RQ workers startup

**Access**

- API: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`

## Usage

### Uploading Videos

1. Log in to Django admin at `http://localhost:8000/admin/`
2. Navigate to Videos section
3. Upload video file
4. Video processing starts automatically in background
5. HLS files are generated in `media/hls/<video_id>/`

### Video Processing Pipeline

```
Upload → Thumbnail Generation → HLS Transcoding → 3 Quality Levels → Ready
```

Quality levels: **480p** (1400k) • **720p** (2800k) • **1080p** (5000k)

## API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/register/` | Register new user |
| `GET` | `/api/activate/<uidb64>/<token>/` | Activate account |
| `POST` | `/api/login/` | User login |
| `POST` | `/api/logout/` | User logout |
| `POST` | `/api/token/refresh/` | Refresh JWT token |
| `POST` | `/api/password_reset/` | Request password reset |
| `POST` | `/api/password_confirm/<uidb64>/<token>/` | Confirm password reset |

### Videos

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/video/` | List all videos | ✅ |
| `GET` | `/api/video/<id>/<resolution>/index.m3u8` | Get HLS playlist | ✅ |
| `GET` | `/api/video/<id>/<resolution>/<segment>/` | Get HLS segment | ✅ |

**Example Request**

```bash
# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure123"}'

# Get videos
curl http://localhost:8000/api/video/ \
  -H "Authorization: Bearer <your-token>"
```

## Project Structure

```
videoflix_app/
├── auth_app/                   # Authentication & User Management
│   ├── api/
│   │   ├── serializers.py      # Auth serializers
│   │   ├── services.py         # Auth business logic
│   │   ├── tasks.py            # Email background tasks
│   │   └── views.py            # Auth API views
│   └── authentication.py       # Custom JWT cookie auth
├── video_app/                  # Video Management & Streaming
│   ├── api/
│   │   ├── serializers.py      # Video serializers
│   │   ├── services.py         # Video business logic
│   │   ├── signals.py          # Video lifecycle hooks
│   │   ├── tasks.py            # Video processing tasks
│   │   └── views.py            # Streaming views
│   └── models.py               # Video model
├── core/                       # Django Configuration
│   ├── settings.py
│   └── urls.py
├── media/                      # User uploads & processed files
├── docker-compose.yml
└── requirements.txt
```

## Development

### Local Setup (without Docker)

**1. Setup Python environment**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Start services**

```bash
# Start only PostgreSQL and Redis
docker-compose up -d db redis
```

**3. Configure environment**

Update `.env` with local database settings.

**4. Run migrations**

```bash
python manage.py migrate
```

**5. Start RQ worker**

```bash
python manage.py rqworker default high
```

**6. Start dev server**

```bash
python manage.py runserver
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SUPERUSER_USERNAME` | Admin username | `admin` |
| `DJANGO_SUPERUSER_PASSWORD` | Admin password | `adminpassword` |
| `DJANGO_SUPERUSER_EMAIL` | Admin email | `admin@example.com` |
| `SECRET_KEY` | Django secret key | `your_secret_key_here` |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts (comma-separated) | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | CSRF origins (comma-separated) | `http://localhost:5500` |
| `DB_NAME` | PostgreSQL database name | `your_database_name` |
| `DB_USER` | PostgreSQL user | `your_database_user` |
| `DB_PASSWORD` | PostgreSQL password | `your_database_password` |
| `DB_HOST` | Database host | `db` |
| `DB_PORT` | Database port | `5432` |
| `REDIS_HOST` | Redis host | `redis` |
| `REDIS_LOCATION` | Redis connection URL | `redis://redis:6379/1` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DB` | Redis database number | `0` |
| `EMAIL_HOST` | SMTP server | `smtp.example.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_HOST_USER` | SMTP username | `your_email_user` |
| `EMAIL_HOST_PASSWORD` | SMTP password | `your_email_user_password` |
| `EMAIL_USE_TLS` | Use TLS | `True` |
| `EMAIL_USE_SSL` | Use SSL | `False` |
| `DEFAULT_FROM_EMAIL` | Default sender email | `default_from_email` |

### Email Functionality

Emails are sent for:
- **Registration** - Email verification link
- **Password Reset** - Password recovery link

Links redirect to frontend, which forwards actions to backend API.

### Security Features

- ✅ JWT stored in HTTP-only cookies (XSS protection)
- ✅ CORS configured for specific origins
- ✅ CSRF protection enabled
- ✅ Generic error messages (prevents user enumeration)

---

**License** • Part of Backend for Business Apps module
