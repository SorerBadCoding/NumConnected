from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from ai_assistant.models import FAQEntry
from announcements.models import Announcement, AnnouncementCategory
from assignments.models import Assignment, Priority, Status
from events.models import Event, EventCategory
from resources_app.models import Resource, ResourceCategory

User = get_user_model()


class Command(BaseCommand):
    help = "Populate the database with realistic demo data for NUM Connect."

    def handle(self, *args, **options):
        now = timezone.now()

        admin = self._get_or_create_staff_user()
        student = self._get_or_create_student(
            username="jsmith",
            email="jsmith@numconnect.edu",
            first_name="Jamie",
            last_name="Smith",
            student_id="2024-00456",
            major="Computer Science",
            academic_year="junior",
            bio="Junior CS major interested in machine learning and web development.",
        )
        self._get_or_create_student(
            username="akim",
            email="akim@numconnect.edu",
            first_name="Alex",
            last_name="Kim",
            student_id="2023-00219",
            major="Business Administration",
            academic_year="senior",
            bio="Senior in Business Admin, minoring in Economics.",
        )

        categories = self._seed_resource_categories()
        self._seed_resources(categories, admin)
        self._seed_announcements(admin, now)
        self._seed_events(admin, now)
        self._seed_assignments(student, now)
        self._seed_faq()

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write("Admin login:   username=admin      password=AdminPass123!")
        self.stdout.write("Student login: username=jsmith     password=StudentPass123!")

    def _get_or_create_staff_user(self):
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@numconnect.edu",
                "first_name": "NUM",
                "last_name": "Administrator",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("AdminPass123!")
            admin.save()
        profile = admin.profile
        if profile.student_id.startswith("TEMP-"):
            profile.student_id = "STAFF-0001"
            profile.major = "University Administration"
            profile.save()
        return admin

    def _get_or_create_student(self, *, username, email, first_name, last_name, student_id, major, academic_year, bio):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "first_name": first_name, "last_name": last_name},
        )
        if created:
            user.set_password("StudentPass123!")
            user.save()
        profile = user.profile
        profile.student_id = student_id
        profile.major = major
        profile.academic_year = academic_year
        profile.bio = bio
        profile.save()
        return user

    def _seed_resource_categories(self):
        names = ["Lecture Notes", "Past Exams", "Study Guides", "Templates"]
        categories = {}
        for name in names:
            category, _ = ResourceCategory.objects.get_or_create(name=name)
            categories[name] = category
        return categories

    def _seed_resources(self, categories, admin):
        resources = [
            ("Intro to Algorithms - Week 1 Notes", "Lecture Notes", "Big-O notation, sorting algorithms, and complexity analysis.", "intro_algorithms_week1.txt"),
            ("Calculus II - Final Exam 2025", "Past Exams", "Previous year's final exam with worked solutions.", "calc2_final_2025.txt"),
            ("APA Citation Quick Guide", "Study Guides", "A quick reference for formatting citations in APA style.", "apa_citation_guide.txt"),
            ("Lab Report Template", "Templates", "Standard template for physics and chemistry lab reports.", "lab_report_template.txt"),
            ("Microeconomics Midterm Study Guide", "Study Guides", "Key concepts and practice questions for the microeconomics midterm.", "microecon_study_guide.txt"),
        ]
        for title, category_name, description, filename in resources:
            if Resource.objects.filter(title=title).exists():
                continue
            resource = Resource(
                title=title,
                description=description,
                category=categories.get(category_name),
                uploaded_by=admin,
            )
            resource.file.save(filename, ContentFile(f"{title}\n\n{description}\n".encode()), save=False)
            resource.save()

    def _seed_announcements(self, admin, now):
        announcements = [
            ("Midterm Exam Schedule Released", AnnouncementCategory.ACADEMIC, True,
             "The midterm exam schedule for all departments is now available on the student portal. Please check your exam dates and locations carefully."),
            ("Library Extended Hours During Finals", AnnouncementCategory.GENERAL, False,
             "The main library will be open 24/7 during the two weeks of finals to support your studying. Bring your student ID for after-hours access."),
            ("Career Fair Registration Now Open", AnnouncementCategory.CAREER, False,
             "Registration for the Spring Career Fair is now open. Over 50 companies will be attending — don't miss this opportunity to network."),
            ("Campus Wi-Fi Maintenance This Weekend", AnnouncementCategory.URGENT, True,
             "Campus Wi-Fi will undergo scheduled maintenance this Saturday from 1 AM to 5 AM. Expect intermittent connectivity during this window."),
            ("Guest Lecture: AI in Modern Healthcare", AnnouncementCategory.EVENT, False,
             "Join us for a special guest lecture on the applications of AI in modern healthcare, hosted by the Computer Science department."),
        ]
        for title, category, pinned, content in announcements:
            Announcement.objects.get_or_create(
                title=title,
                defaults={
                    "content": content,
                    "category": category,
                    "author": admin,
                    "is_pinned": pinned,
                    "publish_at": now - timedelta(days=1),
                },
            )

    def _seed_events(self, admin, now):
        events = [
            ("Freshman Welcome Mixer", EventCategory.SOCIAL, "Student Union Hall", 3, 18, 21,
             "An evening of games, food, and networking to welcome new students to campus."),
            ("Spring Career Fair", EventCategory.CAREER, "Main Gymnasium", 7, 10, 16,
             "Meet recruiters from over 50 companies across tech, finance, and healthcare."),
            ("AI in Healthcare Guest Lecture", EventCategory.ACADEMIC, "Auditorium B, Science Building", 5, 14, 15,
             "A guest lecture exploring how AI is transforming diagnostics and patient care."),
            ("Intramural Basketball Finals", EventCategory.SPORTS, "Campus Sports Complex", 10, 17, 19,
             "Cheer on your favorite dorm team in the intramural basketball championship."),
            ("Resume Writing Workshop", EventCategory.WORKSHOP, "Career Center, Room 204", 2, 13, 14,
             "Hands-on workshop covering resume structure, formatting, and common mistakes to avoid."),
        ]
        for title, category, location, days_ahead, start_hour, end_hour, description in events:
            start = (now + timedelta(days=days_ahead)).replace(hour=start_hour, minute=0, second=0, microsecond=0)
            end = start.replace(hour=end_hour)
            Event.objects.get_or_create(
                title=title,
                defaults={
                    "description": description,
                    "category": category,
                    "location": location,
                    "start_datetime": start,
                    "end_datetime": end,
                    "organizer": admin,
                },
            )

    def _seed_assignments(self, student, now):
        assignments = [
            ("Essay on Renewable Energy", "ENV101", 2, Priority.HIGH, Status.IN_PROGRESS,
             "Write a 1500-word essay analyzing the impact of renewable energy adoption."),
            ("Problem Set 4", "CS201", 5, Priority.MEDIUM, Status.NOT_STARTED,
             "Complete problems 1-10 covering binary trees and graph traversal."),
            ("Lab Report: Titration Experiment", "CHEM110", 1, Priority.HIGH, Status.NOT_STARTED,
             "Summarize the titration lab results and calculate molar concentration."),
            ("Group Presentation Slides", "BUS220", 9, Priority.LOW, Status.NOT_STARTED,
             "Prepare slides for the group presentation on market entry strategy."),
            ("Reading Reflection: Chapter 5", "ENG150", -3, Priority.MEDIUM, Status.COMPLETED,
             "Write a one-page reflection on the assigned chapter."),
        ]
        for title, course, days_offset, priority, status, description in assignments:
            due_date = now + timedelta(days=days_offset)
            Assignment.objects.get_or_create(
                owner=student,
                title=title,
                defaults={
                    "course": course,
                    "description": description,
                    "due_date": due_date,
                    "priority": priority,
                    "status": status,
                },
            )

    def _seed_faq(self):
        faqs = [
            ("How do I reset my password?",
             "password, reset, forgot password, change password",
             "Go to My Profile > Change Password. If you're logged out, use the 'Forgot password' link on the login page."),
            ("How do I submit an assignment?",
             "submit assignment, turn in, upload assignment, homework",
             "Open Assignment Manager, click on the assignment, and mark it as Completed once you've submitted your work through your course platform."),
            ("Where can I see campus events?",
             "events, campus events, activities, what's happening",
             "Check the Campus Events page from the sidebar — it lists all upcoming events with dates, times, and locations."),
            ("How do I download study resources?",
             "download, study resources, notes, past exams",
             "Visit Study Resources, find the file you need, and click the Download button. You can filter by category or search by keyword."),
            ("Can I extend an assignment deadline?",
             "extension, deadline, late submission, extend due date",
             "NUM Connect doesn't manage deadline extensions directly — please contact your course instructor or academic advisor for extension requests."),
            ("How do I update my major or academic year?",
             "update profile, change major, academic year, student id",
             "Go to My Profile > Edit Profile to update your major, academic year, bio, or profile picture."),
            ("What are the library hours?",
             "library hours, library open, library schedule",
             "The library is open 8 AM - 10 PM on weekdays, and extends to 24/7 access during finals week — check Announcements for the exact dates."),
        ]
        for question, keywords, answer in faqs:
            FAQEntry.objects.get_or_create(question=question, defaults={"keywords": keywords, "answer": answer})
