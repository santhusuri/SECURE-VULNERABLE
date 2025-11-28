import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_performance_dashboard_access(client):
    # Login as user
    user = User.objects.create_user(username='testuser', password='testpass')
    client.login(username='testuser', password='testpass')

    url = reverse('orders:performance_dashboard')
    response = client.get(url)
    assert response.status_code == 200
    assert b'Attack Execution Count by Type' in response.content
    assert b'Average Execution Time per Attack Type' in response.content
    assert b'Average RAM Usage per Attack Type' in response.content
    assert b'Average CPU Usage per Attack Type' in response.content

@pytest.mark.django_db
def test_dashboard_graph_image_present(client):
    user = User.objects.create_user(username='testuser2', password='testpass')
    client.login(username='testuser2', password='testpass')

    url = reverse('orders:performance_dashboard')
    response = client.get(url)
    assert b'<img' in response.content or b'graph' in response.content
