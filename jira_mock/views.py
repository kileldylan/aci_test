from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Pre-configured test data
TEST_ISSUES = {
    'PROJ-123': {
        'key': 'PROJ-123',
        'summary': 'User Authentication',
        'description': 'Users should be able to log in with their email and password',
        'status': 'In Progress',
        'acceptance_criteria': [
            'User can log in with valid email and password',
            'Invalid credentials show error message "Invalid email or password"',
            'Successful login redirects to dashboard',
            'Login attempts are logged',
            'Passwords are hashed and stored securely'
        ]
    },
    'PROJ-456': {
        'key': 'PROJ-456',
        'summary': 'Password Reset',
        'description': 'Users should be able to reset their password',
        'status': 'Open',
        'acceptance_criteria': [
            'User can request a password reset',
            'Reset email is sent',
            'Reset token expires after 1 hour',
            'User can choose a new password',
            'Automated tests cover the flow'
        ]
    }
}

@csrf_exempt
def jira_issue_detail(request, issue_key):
    """Mock Jira API endpoint for getting issue details"""
    if request.method == 'GET':
        issue = TEST_ISSUES.get(issue_key)
        if issue:
            return JsonResponse({
                'id': issue_key,
                'key': issue['key'],
                'fields': {
                    'summary': issue['summary'],
                    'description': issue['description'],
                    'status': {'name': issue['status']},
                    'customfield_10000': issue['acceptance_criteria']  # Custom field for AC
                }
            })
        return JsonResponse({'error': 'Issue not found'}, status=404)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def jira_search(request):
    """Mock Jira search endpoint"""
    if request.method == 'GET':
        jql = request.GET.get('jql', '')
        results = []
        for key, issue in TEST_ISSUES.items():
            if key in jql or issue['summary'].lower() in jql.lower():
                results.append({
                    'key': key,
                    'summary': issue['summary'],
                    'status': issue['status']
                })
        return JsonResponse({
            'issues': results,
            'total': len(results)
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)