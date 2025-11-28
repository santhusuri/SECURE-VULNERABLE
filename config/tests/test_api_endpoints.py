import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_mode_toggle_api(client):
    user = User.objects.create_user(username='testuser', password='testpass')
    client.login(username='testuser', password='testpass')

    # Assuming an API endpoint to toggle mode exists at core:toggle_mode
    url = reverse('core:toggle_mode')
    response = client.post(url, {'mode': 'vulnerable'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200
    assert b'vulnerable' in response.content

    response = client.post(url, {'mode': 'secure'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200
    assert b'secure' in response.content

@pytest.mark.django_db
def test_performance_log_api(client):
    user = User.objects.create_user(username='testuser2', password='testpass')
    client.login(username='testuser2', password='testpass')

    # Assuming an API endpoint to fetch performance logs exists at orders:performance_logs
    url = reverse('orders:performance_logs')
    response = client.get(url)
    assert response.status_code == 200
    assert b'performance' in response.content or b'logs' in response.content
