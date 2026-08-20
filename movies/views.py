from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import RegisterForm, ReviewForm, ReportForm
from .models import Movie, ShowSchedule, Booking, Review, ReviewReport

def home(request):
    movies = Movie.objects.all()
    trending = Movie.objects.annotate(
        booking_count=Count("shows__bookings", filter=Q(shows__bookings__status="CONFIRMED"))
    ).order_by("-booking_count", "-release_date")[:6]
    recent = movies.order_by("-release_date")[:6]
    return render(request, "home.html", {"trending": trending, "recent": recent})

def movie_list(request):
    movies = Movie.objects.all()
    q = request.GET.get("q", "").strip()
    if q:
        movies = movies.filter(Q(title__icontains=q) | Q(description__icontains=q))
    genre = request.GET.get("genre")
    language = request.GET.get("language")
    if genre: movies = movies.filter(genre__name=genre)
    if language: movies = movies.filter(language__name=language)
    return render(request, "movies/list.html", {"movies": movies, "q": q})

def movie_detail(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    similar = Movie.objects.filter(
        genre=movie.genre, language=movie.language
    ).exclude(pk=movie.pk).order_by("-release_date", "-id")[:6]
    shows = movie.shows.filter(show_date__gte=timezone.localdate()).select_related("theater")
    reviews = movie.reviews.filter(is_reported=False).select_related("user")
    can_review = False
    if request.user.is_authenticated:
        can_review = Booking.objects.filter(
            user=request.user, show__movie=movie, status="CONFIRMED", watched=True
        ).exists()
    return render(request, "movies/detail.html", {
        "movie": movie, "similar": similar, "shows": shows,
        "reviews": reviews, "can_review": can_review
    })

@login_required
def book_show(request, show_id):
    show = get_object_or_404(ShowSchedule, pk=show_id)
    if request.method != "POST":
        return redirect("movie_detail", show.movie.slug)
    try:
        seats = int(request.POST.get("seats", 1))
    except ValueError:
        seats = 0
    if seats < 1 or seats > show.available_seats:
        messages.error(request, "Invalid number of seats.")
        return redirect("movie_detail", show.movie.slug)
    Booking.objects.create(user=request.user, show=show, seats=seats)
    show.available_seats -= seats
    show.save(update_fields=["available_seats"])
    messages.success(request, "Booking confirmed. After watching, mark it as watched to review.")
    return redirect("my_bookings")

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related("show__movie", "show__theater")
    return render(request, "bookings.html", {"bookings": bookings})

@login_required
def mark_watched(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if request.method == "POST":
        booking.watched = True
        booking.save(update_fields=["watched"])
        messages.success(request, "Movie marked as watched. You can now submit a verified review.")
    return redirect("my_bookings")

def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def review_create(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    eligible = Booking.objects.filter(
        user=request.user, show__movie=movie, status="CONFIRMED", watched=True
    ).exists()
    if not eligible:
        messages.error(request, "You can review this movie only after a confirmed booking has been marked watched.")
        return redirect("movie_detail", movie.slug)
    if Review.objects.filter(movie=movie, user=request.user).exists():
        return redirect("review_edit", Review.objects.get(movie=movie, user=request.user).id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie, review.user = movie, request.user
            review.save()
            messages.success(request, "Your review was submitted.")
            return redirect("movie_detail", movie.slug)
    else:
        form = ReviewForm()
    return render(request, "reviews/form.html", {"form": form, "movie": movie, "editing": False})

@login_required
def review_edit(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated.")
            return redirect("movie_detail", review.movie.slug)
    else:
        form = ReviewForm(instance=review)
    return render(request, "reviews/form.html", {"form": form, "movie": review.movie, "editing": True})

@login_required
def review_report(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if review.user_id == request.user.id:
        messages.error(request, "You cannot report your own review.")
        return redirect("movie_detail", review.movie.slug)
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report, created = ReviewReport.objects.get_or_create(
                review=review, reported_by=request.user,
                defaults={"reason": form.cleaned_data["reason"]}
            )
            if created:
                review.report_count += 1
                review.is_reported = True
                review.save(update_fields=["report_count", "is_reported"])
                messages.success(request, "Review reported to the administrators.")
            else:
                messages.info(request, "You already reported this review.")
            return redirect("movie_detail", review.movie.slug)
    else:
        form = ReportForm()
    return render(request, "reviews/report.html", {"form": form, "review": review})
