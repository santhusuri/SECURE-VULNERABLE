import pytest
from django.urls import reverse
from django.test import Client

@pytest.mark.django_db
def test_accounts_register_secure(client):
    session = client.session
    session['sim_mode'] = 'secure'
    session.save()
    url = reverse('accounts:register')
    response = client.get(url)
    assert response.status_code == 200
    assert b"Secure" in response.content or b"Register" in response.content

@pytest.mark.django_db
def test_accounts_register_vulnerable(client):
    session = client.session
    session['sim_mode'] = 'vulnerable'
    session.save()
    url = reverse('accounts:vuln_register')
    response = client.get(url)
    assert response.status_code == 200
    assert b"Vulnerable" in response.content or b"Register" in response.content

@pytest.mark.django_db
def test_orders_checkout_secure(client):
    session = client.session
    session['sim_mode'] = 'secure'
    session['cart'] = {'1': {'price': 10, 'qty': 1}}
    session.save()
    url = reverse('orders:checkout')
    response = client.get(url)
    assert response.status_code == 200
    assert b"Secure" in response.content or b"Checkout" in response.content

@pytest.mark.django_db
def test_orders_checkout_vulnerable(client):
    session = client.session
    session['sim_mode'] = 'vulnerable'
    session['cart'] = {'1': {'price': 10, 'qty': 1}}
    session.save()
    url = reverse('orders:checkout')
    response = client.get(url)
    assert response.status_code == 200
    assert b"Vulnerable" in response.content or b"Checkout" in response.content

@pytest.mark.django_db
def test_products_list_secure(client):
    session = client.session
    session['sim_mode'] = 'secure'
    session.save()
    url = reverse('products:product_list')
    response = client.get(url)
    assert response.status_code == 200
    assert b"Secure" in response.content or b"Products" in response.content

@pytest.mark.django_db
def test_products_list_vulnerable(client):
    session = client.session
    session['sim_mode'] = 'vulnerable'
    session.save()
    url = reverse('products:product_list')
    response = client.get(url)
    assert response.status_code == 200
    assert b"Vulnerable" in response.content or b"Products" in response.content

@pytest.mark.django_db
def test_shipping_detail_secure(client):
    session = client.session
    session['sim_mode'] = 'secure'
    session.save()
    # Assuming shipment with id=1 exists for testing
    url = reverse('shipping:shipping_details', args=[1])
    response = client.get(url)
    assert response.status_code in [200, 404]  # 404 if no shipment with id=1
    if response.status_code == 200:
        assert b"Secure" in response.content or b"Shipment" in response.content

@pytest.mark.django_db
def test_shipping_detail_vulnerable(client):
    session = client.session
    session['sim_mode'] = 'vulnerable'
    session.save()
    url = reverse('shipping:shipping_details', args=[1])
    response = client.get(url)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert b"Vulnerable" in response.content or b"Shipment" in response.content
