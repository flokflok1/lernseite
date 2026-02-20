"""
Integration tests for Content Translation API endpoints.

Tests the REST API for managing content translations (courses, chapters, lessons).
Distinct from i18n endpoints which handle UI string translations.
"""

import pytest
import json
from datetime import datetime
from app import create_app
from app.infrastructure.persistence.database.connection import get_connection
from app.application.services.content.translation.service import ContentTranslationService

pytestmark = pytest.mark.skip(
    reason="Integration tests require running PostgreSQL database. "
           "setup_test_data() calls get_connection() which causes PoolTimeout without DB."
)


@pytest.fixture(scope='function')
def app():
    """Create Flask app for testing."""
    app = create_app('testing')

    with app.app_context():
        # Setup test data
        setup_test_data()
        yield app
        # Cleanup
        cleanup_test_data()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Get authentication headers for testing.

    In a real test, this would login a test user and get a JWT token.
    For now, we'll create a mock auth header.
    """
    # Note: This assumes the app has test user setup
    # In production, you'd login first and get a real token
    return {
        'Authorization': 'Bearer test-token-12345',
        'Content-Type': 'application/json'
    }


def setup_test_data():
    """Setup test data in database."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Create test translation
            cursor.execute("""
                INSERT INTO translations
                (translation_id, namespace, key_path, language_code, text, source, status, created_at, updated_at)
                VALUES
                (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT DO NOTHING
            """, (
                'test-trans-001',
                'courses',
                'course_123.chapter_5.title',
                'de',
                'Kapitel 5: Grundlagen',
                'ki',
                'active'
            ))
            conn.commit()


def cleanup_test_data():
    """Cleanup test data from database."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM translations WHERE translation_id LIKE 'test-%'")
            cursor.execute("DELETE FROM translation_jobs WHERE job_id LIKE 'test-%'")
            conn.commit()


class TestGetTranslation:
    """Test GET /api/v1/translation/{namespace}/{key_path}/{language_code}"""

    def test_get_translation_success(self, client):
        """Test retrieving an existing translation."""
        response = client.get(
            '/api/v1/translation/courses/course_123.chapter_5.title/de'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['namespace'] == 'courses'
        assert data['data']['text'] == 'Kapitel 5: Grundlagen'

    def test_get_translation_not_found(self, client):
        """Test retrieving non-existent translation."""
        response = client.get(
            '/api/v1/translation/courses/nonexistent/de'
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'NOT_FOUND'


class TestInitiateKiTranslation:
    """Test POST /api/v1/translation/ki/translate"""

    def test_initiate_ki_translation_success(self, client, auth_headers):
        """Test initiating a KI translation job."""
        request_body = {
            'namespace': 'courses',
            'key_path': 'course_456.chapter_2.description',
            'target_language': 'pl',
            'content_type': 'html',
            'context': {
                'domain': 'education',
                'tone': 'academic'
            }
        }

        response = client.post(
            '/api/v1/translation/ki/translate',
            data=json.dumps(request_body),
            headers=auth_headers
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'job_id' in data['data']
        assert data['data']['status'] == 'pending'
        assert data['data']['target_language'] == 'pl'

    def test_initiate_ki_translation_missing_required_field(self, client, auth_headers):
        """Test KI translation with missing required field."""
        request_body = {
            'namespace': 'courses',
            # Missing key_path
            'target_language': 'pl'
        }

        response = client.post(
            '/api/v1/translation/ki/translate',
            data=json.dumps(request_body),
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_initiate_ki_translation_unauthorized(self, client):
        """Test KI translation without authentication."""
        request_body = {
            'namespace': 'courses',
            'key_path': 'course_456.chapter_2.description',
            'target_language': 'pl'
        }

        response = client.post(
            '/api/v1/translation/ki/translate',
            data=json.dumps(request_body)
        )

        assert response.status_code == 401


class TestUpdateTranslation:
    """Test PATCH /api/v1/translation/{translation_id}"""

    def test_update_translation_success(self, client, auth_headers):
        """Test updating an existing translation."""
        request_body = {
            'text': 'Kapitel 5: Grundlagen und Konzepte',
            'status': 'active'
        }

        response = client.patch(
            '/api/v1/translation/test-trans-001',
            data=json.dumps(request_body),
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        # Should return updated translation data
        if 'data' in data:
            assert data['data']['text'] == 'Kapitel 5: Grundlagen und Konzepte'

    def test_update_translation_missing_text(self, client, auth_headers):
        """Test updating translation without text field."""
        request_body = {
            'status': 'active'
            # Missing required 'text' field
        }

        response = client.patch(
            '/api/v1/translation/test-trans-001',
            data=json.dumps(request_body),
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_update_translation_empty_text(self, client, auth_headers):
        """Test updating translation with empty text."""
        request_body = {
            'text': '   ',  # Only whitespace
            'status': 'active'
        }

        response = client.patch(
            '/api/v1/translation/test-trans-001',
            data=json.dumps(request_body),
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_update_translation_not_found(self, client, auth_headers):
        """Test updating non-existent translation."""
        request_body = {
            'text': 'Updated text',
            'status': 'active'
        }

        response = client.patch(
            '/api/v1/translation/nonexistent-id',
            data=json.dumps(request_body),
            headers=auth_headers
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error']['code'] == 'NOT_FOUND'


class TestDeleteTranslation:
    """Test DELETE /api/v1/translation/{translation_id}"""

    def test_delete_translation_success(self, client, auth_headers):
        """Test deleting an existing translation (admin only)."""
        # Note: This requires admin role in auth_headers
        response = client.delete(
            '/api/v1/translation/test-trans-001',
            headers=auth_headers
        )

        # Should be 204 No Content or 403 Forbidden (depending on role)
        # For this test without proper admin setup, we expect 403
        assert response.status_code in [204, 403]

    def test_delete_translation_not_found(self, client, auth_headers):
        """Test deleting non-existent translation."""
        response = client.delete(
            '/api/v1/translation/nonexistent-id',
            headers=auth_headers
        )

        # Should be 404 or 403 depending on auth/role
        assert response.status_code in [404, 403]


class TestGetJobStatus:
    """Test GET /api/v1/translation/job/{job_id}"""

    def test_get_job_status_success(self, client, auth_headers):
        """Test retrieving translation job status."""
        # First, create a job
        request_body = {
            'namespace': 'courses',
            'key_path': 'course_789.chapter_3.intro',
            'target_language': 'en'
        }

        create_response = client.post(
            '/api/v1/translation/ki/translate',
            data=json.dumps(request_body),
            headers=auth_headers
        )

        job_data = json.loads(create_response.data)
        job_id = job_data['data']['job_id']

        # Now retrieve the job status
        response = client.get(
            f'/api/v1/translation/job/{job_id}',
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['job_id'] == job_id
        assert data['data']['status'] == 'pending'

    def test_get_job_status_not_found(self, client, auth_headers):
        """Test retrieving non-existent job status."""
        response = client.get(
            '/api/v1/translation/job/nonexistent-job-id',
            headers=auth_headers
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error']['code'] == 'NOT_FOUND'


class TestEndpointSecurity:
    """Test security aspects of translation endpoints."""

    def test_protected_endpoints_require_auth(self, client):
        """Test that protected endpoints require authentication."""
        # POST /ki/translate requires auth
        response = client.post(
            '/api/v1/translation/ki/translate',
            data=json.dumps({'namespace': 'courses', 'key_path': 'test', 'target_language': 'de'})
        )
        assert response.status_code == 401

        # PATCH requires auth
        response = client.patch(
            '/api/v1/translation/test-id',
            data=json.dumps({'text': 'test'})
        )
        assert response.status_code == 401

        # DELETE requires auth
        response = client.delete('/api/v1/translation/test-id')
        assert response.status_code == 401

        # GET job status requires auth
        response = client.get('/api/v1/translation/job/test-id')
        assert response.status_code == 401

    def test_public_get_translation_no_auth_required(self, client):
        """Test that GET translation endpoint is public."""
        response = client.get(
            '/api/v1/translation/courses/course_123.chapter_5.title/de'
        )

        # Should NOT be 401 (no auth required for public endpoint)
        assert response.status_code != 401


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
