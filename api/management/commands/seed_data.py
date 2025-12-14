from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Doctor, Patient, Appointment


class Command(BaseCommand):
    help = "Seed the database with demo doctors, patients, and appointments"

    def handle(self, *args, **options):
        demo_user, created = User.objects.get_or_create(
            username="demo",
            defaults={
                "email": "demo@example.com",
            },
        )
        if created:
            demo_user.set_password("password123")
            demo_user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user 'demo' / 'password123'"))
        else:
            self.stdout.write("Demo user already exists")

        doctors_data = [
            {"name": "Dr. Alice Smith", "specialization": "Cardiology", "email": "alice@example.com", "contact_number": "111-111-1111"},
            {"name": "Dr. Bob Jones", "specialization": "Neurology", "email": "bob@example.com", "contact_number": "222-222-2222"},
            {"name": "Dr. Carol Lee", "specialization": "Pediatrics", "email": "carol@example.com", "contact_number": "333-333-3333"},
        ]

        doctors = []
        for data in doctors_data:
            doctor, _ = Doctor.objects.get_or_create(email=data["email"], defaults=data)
            doctors.append(doctor)
        self.stdout.write(self.style.SUCCESS(f"Ensured {len(doctors)} doctors"))

        patients_data = [
            {"name": "John Doe", "age": 30, "contact_number": "555-0001", "address": "123 Main St"},
            {"name": "Jane Roe", "age": 45, "contact_number": "555-0002", "address": "456 Oak Ave"},
        ]

        patients = []
        for data in patients_data:
            patient, _ = Patient.objects.get_or_create(
                created_by=demo_user,
                name=data["name"],
                defaults=data,
            )
            patients.append(patient)
        self.stdout.write(self.style.SUCCESS(f"Ensured {len(patients)} patients for demo user"))

        if doctors and patients:
            Appointment.objects.get_or_create(patient=patients[0], doctor=doctors[0])
            Appointment.objects.get_or_create(patient=patients[0], doctor=doctors[1])
            Appointment.objects.get_or_create(patient=patients[1], doctor=doctors[2])

        self.stdout.write(self.style.SUCCESS("Demo appointments created (if not already present)"))
        self.stdout.write(self.style.SUCCESS("Seeding complete."))
