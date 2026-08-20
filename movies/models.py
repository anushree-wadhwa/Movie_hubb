from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg

class Genre(models.Model):
    name = models.CharField(max_length=80, unique=True)
    def __str__(self): return self.name

class Language(models.Model):
    name = models.CharField(max_length=80, unique=True)
    def __str__(self): return self.name

class CastMember(models.Model):
    name = models.CharField(max_length=150)
    profile_image = models.ImageField(upload_to="cast/", blank=True, null=True)
    biography = models.TextField(blank=True)
    def __str__(self): return self.name

class Movie(models.Model):
    CERTIFICATIONS = [
        ("U", "U"),
        ("UA", "UA"),
        ("A", "A"),
        ("S", "S"),
    ]
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, related_name="movies")
    language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name="movies")
    cast = models.ManyToManyField(CastMember, blank=True, related_name="movies")
    youtube_video_id = models.CharField(max_length=30, blank=True, help_text="Only the YouTube video ID, e.g. dQw4w9WgXcQ")
    certification = models.CharField(max_length=3, choices=CERTIFICATIONS, default="UA")
    duration_minutes = models.PositiveIntegerField(default=120)
    release_date = models.DateField()
    poster = models.ImageField(upload_to="posters/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-release_date", "title"]

    def __str__(self): return self.title

    @property
    def average_rating(self):
        value = self.reviews.filter(is_reported=False).aggregate(avg=Avg("rating"))["avg"]
        return round(value or 0, 1)

    @property
    def review_count(self):
        return self.reviews.filter(is_reported=False).count()

    @property
    def is_recent(self):
        from django.utils import timezone
        return (timezone.now().date() - self.release_date).days <= 60

class MovieImage(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="movie_gallery/")
    caption = models.CharField(max_length=150, blank=True)
    def __str__(self): return f"{self.movie.title} - image"

class Theater(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    address = models.TextField(blank=True)
    def __str__(self): return f"{self.name} - {self.location}"

class ShowSchedule(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="shows")
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name="shows")
    show_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_seats = models.PositiveIntegerField(default=100)
    available_seats = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ["show_date", "start_time"]

    def __str__(self):
        return f"{self.movie.title} | {self.theater.name} | {self.show_date} {self.start_time}"

class Booking(models.Model):
    STATUS = [("CONFIRMED", "Confirmed"), ("CANCELLED", "Cancelled")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    show = models.ForeignKey(ShowSchedule, on_delete=models.PROTECT, related_name="bookings")
    seats = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=12, choices=STATUS, default="CONFIRMED")
    watched = models.BooleanField(default=False)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.user} - {self.show.movie.title}"

class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField()
    is_reported = models.BooleanField(default=False)
    report_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["movie", "user"], name="one_review_per_user_movie")
        ]
        ordering = ["-created_at"]

    @property
    def verified_viewer(self):
        return Booking.objects.filter(
            user=self.user, show__movie=self.movie, status="CONFIRMED", watched=True
        ).exists()

    def __str__(self): return f"{self.movie.title} - {self.user.username}"

class ReviewReport(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="reports")
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["review", "reported_by"], name="one_report_per_user_review")
        ]

    def __str__(self): return f"Report #{self.pk}"
