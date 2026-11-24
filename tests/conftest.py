from pathlib import Path
import pytest
from characterlab import create_app

@pytest.fixture
def app(tmp_path):
    app=create_app({'TESTING':True,'DATABASE':str(tmp_path/'test.sqlite3'),'SECRET_KEY':'test-secret'})
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def csrf(client):
    with client.session_transaction() as s:
        return s['csrf']
