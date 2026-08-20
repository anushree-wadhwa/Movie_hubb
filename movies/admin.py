from django.contrib import admin
from .models import (
    Genre, Language, CastMember, Movie, MovieImage,
    Theater, ShowSchedule, Booking, Review, ReviewReport
)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "language", "certification", "release_date", "average_rating")
    list_filter = ("genre", "language", "certification", "release_date")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("cast",)

class MovieImageInline(admin.TabularInline):
    model = MovieImage
    extra = 2

MovieAdmin.inlines = [MovieImageInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("movie", "user", "rating", "verified", "is_reported", "created_at")
    list_filter = ("rating", "is_reported")
    search_fields = ("movie__title", "user__username", "text")
    actions = ["mark_safe"]

    @admin.display(boolean=True, description="Verified")
    def verified(self, obj): return obj.verified_viewer

    @admin.action(description="Clear selected review reports")
    def mark_safe(self, request, queryset):
        queryset.update(is_reported=False, report_count=0)

@admin.register(ShowSchedule)
class ShowScheduleAdmin(admin.ModelAdmin):
    list_display = ("movie", "theater", "show_date", "start_time", "available_seats")
    list_filter = ("show_date", "theater")
    search_fields = ("movie__title", "theater__name")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "show", "seats", "status", "watched", "booked_at")
    list_filter = ("status", "watched")

@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ("review", "reported_by", "resolved", "created_at")
    list_filter = ("resolved",)

admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(CastMember)
admin.site.register(Theater)
admin.site.site_header = "MovieHub Administration"
admin.site.site_title = "MovieHub Admin"
admin.site.index_title = "Manage Movies, Shows & Reviews"
