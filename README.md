# MovieHub - Django Movie Management System

A complete movie management module for managing movies, genres, languages, cast, theaters, shows, bookings, ratings and reviews.

## Features
- Django Admin management
- Movies with age certification, duration, descriptions and YouTube trailers
- Multiple poster/gallery images
- Genres, languages and cast
- Theater and show schedule management
- User registration/login
- Booking system
- Watched verification
- Ratings and reviews
- Verified Viewer badge
- Review editing and reporting
- Automatic average rating
- Trending and recently released movies
- Similar movies by genre and language
- Responsive UI
- Vercel configuration

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:
- Site: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Admin workflow
1. Create Genre and Language.
2. Add Cast Members.
3. Add Movies.
4. Upload a poster and add gallery images.
5. Enter only the YouTube video ID in the trailer field.
6. Add Theaters.
7. Add Show Schedules.
8. Create test users/bookings.
9. Mark a booking as watched.
10. Submit a review as that user.

## Vercel
Set environment variables:
- SECRET_KEY
- DEBUG=False
- ALLOWED_HOSTS=.vercel.app
- DATABASE_URL=<your PostgreSQL connection string>
- CSRF_TRUSTED_ORIGINS=https://your-project.vercel.app

Then deploy the repository from Vercel.

Note: persistent media uploads should use external object storage in production. For a school/demo deployment, seed movie posters through the admin after deployment or use an external media storage service.
