from django.db import models
from django.utils import timezone

class JiraIssue(models.Model):
    """Mock Jira issue for testing ACI"""
    key = models.CharField(max_length=20, unique=True)
    summary = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, default='Open')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    # Acceptance criteria stored as JSON
    acceptance_criteria = models.JSONField(default=list)
    
    def __str__(self):
        return f"{self.key}: {self.summary}"

class TestModel(models.Model):
    test_field = models.CharField(max_length=50)

class Profile(models.Model):
    name = models.CharField(max_length=50)
    phone = models.IntegerField()