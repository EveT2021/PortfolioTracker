import json

import pytest

from backend.app import create_app, db
from backend.app.config import TestConfig
from backend.app.models import AssetType, Portfolio, User


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        # create a test user used by asset/portfolio creation tests
        user = User(email='test@example.com', password_hash='x'*60)
        db.session.add(user)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_health(client):
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.get_json().get('status') == 'ok'


def test_create_asset(client):
    # the fixture created a user with id=1
    # first create an asset type
    r = client.post('/api/asset_types', json={'name': 'stock', 'description': 'Public equities'})
    assert r.status_code == 201
    at = r.get_json()

    payload = {'symbol': 'AAPL', 'type_id': at.get('id'), 'name': 'Apple'}
    r = client.post('/api/assets', json=payload)
    assert r.status_code == 201
    body = r.get_json()
    assert body.get('symbol') == 'AAPL'


def test_create_portfolio_and_holding(client):
    # create a portfolio
    r = client.post('/api/portfolios', json={'user_id': 1, 'name': 'Test Portfolio'})
    assert r.status_code == 201
    p = r.get_json()

    # create an asset type and asset
    r = client.post('/api/asset_types', json={'name': 'stock'})
    at = r.get_json()
    r = client.post('/api/assets', json={'symbol': 'TSLA', 'type_id': at.get('id'), 'name': 'Tesla'})
    asset = r.get_json()

    # add holding
    r = client.post('/api/holdings', json={'portfolio_id': p.get('id'), 'asset_id': asset.get('id'), 'quantity': '10', 'cost_basis': '7000'})
    assert r.status_code == 201
