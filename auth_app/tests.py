from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient


class ApiLoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="pw12345",
        )

    def test_login_success_returns_token(self):
        r = self.client.post(
            "/api/login/",                      # <-- use the real path
            {"email": "alice@example.com", "password": "pw12345"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("token", r.json())

    def test_login_invalid_returns_401(self):
        r = self.client.post(
            "/api/login/",
            {"email": "alice@example.com", "password": "wrong"},
            format="json",
        )
        self.assertEqual(r.status_code, 401)