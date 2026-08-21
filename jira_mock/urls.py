from django.urls import path
from . import views

app_name = 'jira_mock'

urlpatterns = [
    path('jira/issues/<str:issue_key>/', views.jira_issue_detail, name='jira_issue'),
    path('jira/search/', views.jira_search, name='jira_search'),
]