# Videoflix - Video Streaming Platform

A Django-based video streaming platform with adaptive HLS streaming, user authentication, and asynchronous video processing.

## Features

- **User Authentication**: Registration, email verification, login, password reset
- **Video Streaming**: Adaptive HLS streaming with multiple quality levels (480p, 720p, 1080p)
- **Asynchronous Processing**: Background video transcoding using Django RQ and Redis
- **Thumbnail Generation**: Automatic thumbnail extraction from uploaded videos
- **REST API**: Complete REST API for frontend integration
- **Admin Dashboard**: Django admin interface for content management

## Tech Stack

- **Backend**: Django 6.0.1, Django REST Framework
- **Database**: PostgreSQL
- **Cache & Queue**: Redis, Django RQ
- **Video Processing**: FFmpeg, HLS
- **Authentication**: JWT (SimplejWT) with HTTP-only cookies
- **Containerization**: Docker, Docker Compose

## Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- FFmpeg (included in Docker container)

## Quick Start with Docker

1. Clone the repository
2. Create a `.env` file in the project root with the following variables:

```env
SECRET_KEY=your-secret-key-here
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=your-password-here
DB_HOST=db
DB_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_LOCATION=redis://redis:6379/1
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@example.com
FRONTEND_URL=http://localhost:4200
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:4200
```

3. Start the application:

```bash
docker-compose up -d
```

4. Apply database migrations:

```bash
docker-compose exec web python manage.py migrate
```

5. Create a superuser:

```bash
docker-compose exec web python manage.py createsuperuser
```

6. Access the application:
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/

## Project Structure

```
videoflix_app/
├── auth_app/              # User authentication and authorization
│   ├── api/
│   │   ├── serializers.py # Request/response serializers
│   │   ├── services.py    # Business logic for auth operations
│   │   ├── tasks.py       # Background email tasks
│   │   ├── urls.py        # Auth API endpoints
│   │   └── views.py       # Auth API views
│   ├── models.py          # User profile model
│   └── authentication.py  # Custom JWT cookie authentication
├── video_app/             # Video management and streaming
│   ├── api/
│   │   ├── serializers.py # Video serializers
│   │   ├── services.py    # Video business logic
│   │   ├── signals.py     # Video lifecycle signals
│   │   ├── tasks.py       # Video processing tasks
│   │   ├── urls.py        # Video API endpoints
│   │   ├── utils.py       # HLS path utilities
│   │   └── views.py       # Video streaming views
│   └── models.py          # Video model
├── core/                  # Project settings and configuration
│   ├── settings.py        # Django settings
│   └── urls.py            # Root URL configuration
├── media/                 # Uploaded files and processed videos
├── static/                # Static files
├── docker-compose.yml     # Docker service definitions
├── backend.Dockerfile     # Backend container image
└── requirements.txt       # Python dependencies
```

## API Endpoints

### Authentication

- `POST /api/register/` - Register new user
- `GET /api/activate/<uidb64>/<token>/` - Activate user account
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout
- `POST /api/token/refresh/` - Refresh access token
- `POST /api/password_reset/` - Request password reset
- `POST /api/password_confirm/<uidb64>/<token>/` - Confirm password reset

### Videos

- `GET /api/video/` - List all videos (authenticated)
- `GET /api/video/<id>/<resolution>/index.m3u8` - Get HLS playlist (authenticated)
- `GET /api/video/<id>/<resolution>/<segment>/` - Get HLS video segment (authenticated)

## Video Processing

When a video is uploaded through the Django admin:

1. Video is saved to the `media/videos/` directory
2. A background task is queued to generate a thumbnail
3. A background task is queued to transcode the video to HLS format
4. The video is transcoded to three quality levels:
   - 480p (1400k bitrate)
   - 720p (2800k bitrate)
   - 1080p (5000k bitrate)
5. A master playlist is created for adaptive streaming
6. Processed files are saved to `media/hls/<video_id>/`

## Development

### Local Setup (without Docker)

1. Install Python 3.12+
2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install PostgreSQL and Redis locally or use Docker for these services only

5. Configure your `.env` file

6. Run migrations:

```bash
python manage.py migrate
```

7. Start Redis Queue worker:

```bash
python manage.py rqworker default high
```

8. Run the development server:

```bash
python manage.py runserver
```

## Email Configuration

The application sends emails for:
- **Registration**: Email verification link
- **Password Reset**: Password reset link

Email links point to the frontend application, which then forwards actions to the backend API.

## Security

- JWT tokens stored in HTTP-only cookies for XSS protection
- CORS configured for frontend origin
- CSRF protection enabled
- Secure cookie settings in production
- Generic error messages to prevent user enumeration

## Contributing

1. Follow PEP-8 style guidelines
2. Use snake_case for variables and functions
3. Add docstrings to all functions and classes
4. Remove all comments from code (use docstrings instead)
5. Test thoroughly before submitting

## License

This project is part of the Backend for Business Apps module.
