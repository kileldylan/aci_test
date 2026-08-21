from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.login_url = reverse('auth_app:login')
        self.dashboard_url = reverse('auth_app:dashboard')

    def test_login_with_valid_credentials(self):
        """Test that user can log in with valid email and password"""
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
        self.assertRedirects(response, self.dashboard_url)

    def test_login_with_invalid_credentials(self):
        """Test that invalid credentials show error message"""
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password')

    def test_login_redirects_to_dashboard(self):
        """Test that successful login redirects to dashboard"""
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertRedirects(response, self.dashboard_url)

    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))