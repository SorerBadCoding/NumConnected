from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from ai_assistant.models import FAQEntry
from announcements.models import Announcement, AnnouncementCategory
from assignments.models import Assignment, Priority, Status
from calendar_app.models import Exam, Holiday
from campus_map.models import CampusLocation, LocationCategory
from discussions.models import Post, PostCategory
from events.models import Event, EventCategory
from feedback.models import Feedback, FeedbackStatus, FeedbackType
from lecturers.models import Department, Lecturer
from resources_app.models import Resource, ResourceCategory, Tag

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
        self._seed_lecturers()
        self._seed_calendar_extras(now)
        self._seed_discussion_posts(admin, student)
        self._seed_campus_locations()
        self._seed_feedback(student)

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
            ("Intro to Algorithms - Week 1 Notes", "Lecture Notes", "Big-O notation, sorting algorithms, and complexity analysis.", "intro_algorithms_week1.txt", ["algorithms", "week-1"]),
            ("Calculus II - Final Exam 2025", "Past Exams", "Previous year's final exam with worked solutions.", "calc2_final_2025.txt", ["calculus", "final-exam"]),
            ("APA Citation Quick Guide", "Study Guides", "A quick reference for formatting citations in APA style.", "apa_citation_guide.txt", ["writing", "citations"]),
            ("Lab Report Template", "Templates", "Standard template for physics and chemistry lab reports.", "lab_report_template.txt", ["template", "lab"]),
            ("Microeconomics Midterm Study Guide", "Study Guides", "Key concepts and practice questions for the microeconomics midterm.", "microecon_study_guide.txt", ["midterm", "economics"]),
        ]
        for title, category_name, description, filename, tag_names in resources:
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
            resource.tags.set([Tag.objects.get_or_create(name=name)[0] for name in tag_names])

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

    def _seed_lecturers(self):
        lecturers = [
            ("Dr. Ada Lovelace", Department.COMPUTER_SCIENCE, "Algorithms, Data Structures, Machine Learning",
             "ada.lovelace@numconnect.edu", "Mon/Wed 2:00-4:00 PM", "Science Building, Room 214",
             "Dr. Lovelace specializes in algorithm design and has taught at NUM for over a decade."),
            ("Dr. Alan Turing", Department.MATHEMATICS, "Calculus II, Discrete Math, Number Theory",
             "alan.turing@numconnect.edu", "Tue/Thu 10:00-12:00 PM", "Math Building, Room 305",
             "Dr. Turing researches computability theory and enjoys teaching foundational math courses."),
            ("Dr. Marie Curie", Department.CHEMISTRY, "General Chemistry, Radiochemistry",
             "marie.curie@numconnect.edu", "Wed 1:00-3:00 PM", "Science Building, Room 118",
             "Dr. Curie's research focuses on radiochemistry and analytical methods."),
            ("Dr. John Maynard", Department.ECONOMICS, "Microeconomics, Macroeconomics",
             "john.maynard@numconnect.edu", "Mon/Fri 11:00-1:00 PM", "Business Building, Room 220",
             "Dr. Maynard teaches core economics courses with a focus on real-world policy analysis."),
        ]
        for name, department, subjects, email, office_hours, office_location, bio in lecturers:
            Lecturer.objects.get_or_create(
                name=name,
                defaults={
                    "department": department,
                    "subjects": subjects,
                    "email": email,
                    "office_hours": office_hours,
                    "office_location": office_location,
                    "biography": bio,
                },
            )

    def _seed_calendar_extras(self, now):
        Exam.objects.get_or_create(
            course="CS201", title="Midterm Exam",
            date=(now + timedelta(days=6)).date(),
            defaults={"start_time": "09:00", "end_time": "11:00", "location": "Hall A"},
        )
        Exam.objects.get_or_create(
            course="ENV101", title="Final Exam",
            date=(now + timedelta(days=14)).date(),
            defaults={"start_time": "13:00", "end_time": "15:00", "location": "Hall B"},
        )
        Holiday.objects.get_or_create(name="Founders Day", date=(now + timedelta(days=9)).date())

    def _seed_discussion_posts(self, admin, student):
        posts = [
            ("Best resources for Data Structures?", PostCategory.PROGRAMMING, student,
             "I'm struggling with linked lists and trees. Any book or video recommendations that really click?"),
            ("Reminder: Midterm review session Friday", PostCategory.ASSIGNMENTS, admin,
             "We'll be holding a review session in the main library, 4th floor, this Friday at 5pm. Bring questions!"),
            ("Tips for managing a heavy course load?", PostCategory.STUDY_TIPS, student,
             "This semester feels overwhelming. How do you all plan your week across multiple deadlines?"),
        ]
        for title, category, author, content in posts:
            Post.objects.get_or_create(title=title, defaults={"category": category, "author": author, "content": content})

    def _seed_campus_locations(self):
        locations = [
            ("Main Library", LocationCategory.LIBRARY, "Central library with 24/7 study zones during finals.", "Bldg L", 20, 25),
            ("Science Building", LocationCategory.BUILDING, "Home to Physics, Chemistry, and Biology departments.", "Bldg S", 45, 20),
            ("Computer Lab 1", LocationCategory.LAB, "24 workstations for CS coursework.", "Bldg S-114", 55, 35),
            ("Student Union Cafeteria", LocationCategory.CAFETERIA, "Main dining hall on campus.", "Bldg U", 30, 60),
            ("Student Affairs Office", LocationCategory.STUDENT_AFFAIRS, "Advising, records, and financial aid.", "Bldg A", 70, 55),
            ("Parking Lot A", LocationCategory.PARKING, "Main visitor and student parking.", "Lot A", 15, 80),
        ]
        for name, category, description, code, x, y in locations:
            CampusLocation.objects.get_or_create(
                name=name,
                defaults={"category": category, "description": description, "building_code": code, "x_position": x, "y_position": y},
            )

    def _seed_feedback(self, student):
        Feedback.objects.get_or_create(
            user=student, subject="Love the new dashboard",
            defaults={
                "feedback_type": FeedbackType.RATING, "rating": 5,
                "message": "The redesigned dashboard is so much easier to use. Great work!",
                "status": FeedbackStatus.OPEN,
            },
        )
        Feedback.objects.get_or_create(
            user=student, subject="Dark mode toggle sometimes flickers",
            defaults={
                "feedback_type": FeedbackType.BUG,
                "message": "When I switch themes quickly, the page flashes white for a moment before applying dark mode.",
                "status": FeedbackStatus.OPEN,
            },
        )
