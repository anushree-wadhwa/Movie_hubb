from django.core.management.base import BaseCommand
from django.utils.text import slugify
from datetime import date, time
from movies.models import Genre, Language, CastMember, Movie, Theater, ShowSchedule

class Command(BaseCommand):
    help = "Create demo MovieHub data"

    def handle(self, *args, **kwargs):
        action = Genre.objects.get_or_create(name="Action")[0]
        drama = Genre.objects.get_or_create(name="Drama")[0]
        english = Language.objects.get_or_create(name="English")[0]
        hindi = Language.objects.get_or_create(name="Hindi")[0]
        cast, _ = CastMember.objects.get_or_create(name="Demo Actor")
        m1, _ = Movie.objects.get_or_create(
            slug="the-last-mission",
            defaults=dict(
                title="The Last Mission", description="A fictional action adventure demo movie.",
                genre=action, language=english, certification="UA",
                duration_minutes=128, release_date=date.today(),
                youtube_video_id=""
            )
        )
        m1.cast.add(cast)
        theater, _ = Theater.objects.get_or_create(name="MovieHub Cinemas", location="Mumbai")
        ShowSchedule.objects.get_or_create(
            movie=m1, theater=theater, show_date=date.today(),
            start_time=time(18, 30), end_time=time(20, 38),
            defaults={"total_seats": 100, "available_seats": 100}
        )
        self.stdout.write(self.style.SUCCESS("Demo data created."))
