from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AcademicYear, Profile, User


@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    """Guarantee every user (including ones made via createsuperuser) has a
    Profile row, so templates can always assume `user.profile` exists.

    Real registrations overwrite the placeholder `student_id` immediately
    within the same request (see accounts.views.RegisterView).
    """
    if created:
        Profile.objects.get_or_create(
            user=instance,
            defaults={
                "student_id": f"TEMP-{instance.pk}",
                "major": "",
                "academic_year": AcademicYear.FRESHMAN,
            },
        )
