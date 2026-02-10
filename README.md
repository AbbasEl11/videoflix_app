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
git clone <repository-url>
cd videoflix_app
```

**2. Create environment file**

```bash
cp .env.example .env
```

**3. Start services**

```bash
docker-compose up -d
```

**4. Run migrations**

```bash
docker-compose exec web python manage.py migrate
```

**5. Create superuser**

```bash
docker-compose exec web python manage.py createsuperuser
```

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
# PostgreSQL and Redis required
docker-compose up db redis -d
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

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | - |
| `DB_NAME` | PostgreSQL database name | `videoflix_db` |
| `DB_USER` | PostgreSQL user | `videoflix_user` |
| `DB_PASSWORD` | PostgreSQL password | - |
| `DB_HOST` | Database host | `db` |
| `REDIS_HOST` | Redis host | `redis` |
| `EMAIL_HOST` | SMTP server | - |
| `EMAIL_HOST_USER` | SMTP username | - |
| `EMAIL_HOST_PASSWORD` | SMTP password | - |
| `FRONTEND_URL` | Frontend URL for email links | `http://localhost:4200` |
| `ALLOWED_HOSTS` | Allowed hosts (comma-separated) | `localhost` |
| `CSRF_TRUSTED_ORIGINS` | CSRF origins (comma-separated) | `http://localhost:4200` |

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
