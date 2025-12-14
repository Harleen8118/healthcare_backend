from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Doctor, Patient, Appointment


class AuthTests(APITestCase):
	def test_register_creates_user(self):
		url = "/api/auth/register/"
		data = {
			"username": "newuser",
			"email": "newuser@example.com",
			"password": "password123",
		}
		response = self.client.post(url, data, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(User.objects.filter(username="newuser").exists())

	def test_login_returns_jwt_tokens(self):
		user = User.objects.create_user(
			username="loginuser",
			email="login@example.com",
			password="password123",
		)
		url = "/api/auth/login/"
		data = {"username": user.username, "password": "password123"}
		response = self.client.post(url, data, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn("access", response.data)
		self.assertIn("refresh", response.data)


class BaseAuthenticatedAPITestCase(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="testuser",
			email="test@example.com",
			password="password123",
		)
		login_response = self.client.post(
			"/api/auth/login/",
			{"username": "testuser", "password": "password123"},
			format="json",
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)
		self.token = login_response.data["access"]
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")


class PatientTests(BaseAuthenticatedAPITestCase):
	def test_create_patient(self):
		url = "/api/patients/"
		data = {
			"name": "John Doe",
			"age": 30,
			"contact_number": "555-0000",
			"address": "123 Main St",
		}
		response = self.client.post(url, data, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		patient = Patient.objects.get(id=response.data["id"])
		self.assertEqual(patient.created_by, self.user)

	def test_list_patients_only_for_authenticated_user(self):
		other_user = User.objects.create_user(
			username="other",
			email="other@example.com",
			password="password123",
		)
		Patient.objects.create(
			created_by=self.user,
			name="Mine",
			age=25,
			contact_number="111",
			address="Addr 1",
		)
		Patient.objects.create(
			created_by=other_user,
			name="NotMine",
			age=40,
			contact_number="222",
			address="Addr 2",
		)

		response = self.client.get("/api/patients/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["name"], "Mine")

	def test_get_update_delete_patient(self):
		patient = Patient.objects.create(
			created_by=self.user,
			name="John Doe",
			age=30,
			contact_number="555-0000",
			address="123 Main St",
		)
		detail_url = f"/api/patients/{patient.id}/"

		response_get = self.client.get(detail_url)
		self.assertEqual(response_get.status_code, status.HTTP_200_OK)

		response_put = self.client.put(
			detail_url,
			{
				"name": "John Updated",
				"age": 31,
				"contact_number": "555-0001",
				"address": "New Address",
			},
			format="json",
		)
		self.assertEqual(response_put.status_code, status.HTTP_200_OK)
		self.assertEqual(response_put.data["name"], "John Updated")

		response_delete = self.client.delete(detail_url)
		self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Patient.objects.filter(id=patient.id).exists())


class DoctorTests(BaseAuthenticatedAPITestCase):
	def test_create_and_list_doctors(self):
		create_url = "/api/doctors/"
		data = {
			"name": "Dr. Smith",
			"specialization": "Cardiology",
			"email": "smith@example.com",
			"contact_number": "123-456-7890",
		}
		response_create = self.client.post(create_url, data, format="json")
		self.assertEqual(response_create.status_code, status.HTTP_201_CREATED)

		response_list = self.client.get(create_url)
		self.assertEqual(response_list.status_code, status.HTTP_200_OK)
		self.assertGreaterEqual(len(response_list.data), 1)

	def test_get_update_delete_doctor(self):
		doctor = Doctor.objects.create(
			name="Dr. Original",
			specialization="Dermatology",
			email="orig@example.com",
			contact_number="000-000-0000",
		)
		detail_url = f"/api/doctors/{doctor.id}/"

		response_get = self.client.get(detail_url)
		self.assertEqual(response_get.status_code, status.HTTP_200_OK)

		response_put = self.client.put(
			detail_url,
			{
				"name": "Dr. Updated",
				"specialization": "Dermatology",
				"email": "updated@example.com",
				"contact_number": "111-111-1111",
			},
			format="json",
		)
		self.assertEqual(response_put.status_code, status.HTTP_200_OK)
		self.assertEqual(response_put.data["name"], "Dr. Updated")

		response_delete = self.client.delete(detail_url)
		self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Doctor.objects.filter(id=doctor.id).exists())


class MappingTests(BaseAuthenticatedAPITestCase):
	def setUp(self):
		super().setUp()
		self.doctor1 = Doctor.objects.create(
			name="Dr. A",
			specialization="Cardiology",
			email="a@example.com",
			contact_number="111",
		)
		self.doctor2 = Doctor.objects.create(
			name="Dr. B",
			specialization="Neurology",
			email="b@example.com",
			contact_number="222",
		)
		self.patient = Patient.objects.create(
			created_by=self.user,
			name="Patient X",
			age=50,
			contact_number="333",
			address="Addr",
		)

	def test_create_and_list_mappings(self):
		url = "/api/mappings/"
		data = {"patient": self.patient.id, "doctor": self.doctor1.id}
		response_create = self.client.post(url, data, format="json")
		self.assertEqual(response_create.status_code, status.HTTP_201_CREATED)

		response_list = self.client.get(url)
		self.assertEqual(response_list.status_code, status.HTTP_200_OK)
		self.assertGreaterEqual(len(response_list.data), 1)

	def test_filter_mappings_by_patient(self):
		Appointment.objects.create(patient=self.patient, doctor=self.doctor1)
		Appointment.objects.create(patient=self.patient, doctor=self.doctor2)

		response = self.client.get(f"/api/mappings/?patient={self.patient.id}")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 2)

	def test_delete_mapping(self):
		mapping = Appointment.objects.create(patient=self.patient, doctor=self.doctor1)
		detail_url = f"/api/mappings/{mapping.id}/"

		response_delete = self.client.delete(detail_url)
		self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Appointment.objects.filter(id=mapping.id).exists())


class SeedDataCommandTests(APITestCase):
	def test_seed_data_command_creates_expected_objects(self):
		call_command("seed_data")

		self.assertTrue(User.objects.filter(username="demo").exists())
		self.assertGreaterEqual(Doctor.objects.count(), 3)
		self.assertGreaterEqual(Patient.objects.count(), 2)
		self.assertGreaterEqual(Appointment.objects.count(), 1)

