"""
Pytest configuration and fixtures for LM Plugin tests
"""
import pytest
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture
def mock_plugin_metadata():
    """Fixture for plugin metadata"""
    return {
        'plugin_code': 'lm_test',
        'name': 'Test Plugin',
        'description': 'A test plugin for unit tests',
        'group_code': 'A',
        'tier': 'basic',
        'ki_usage': 'optional',
        'icon': '🧪',
        'config_schema': {
            'type': 'object',
            'properties': {
                'test_field': {
                    'type': 'string',
                    'description': 'Test field'
                }
            },
            'required': ['test_field']
        },
        'default_config': {
            'test_field': 'default value'
        },
        'agent_support': {
            'can_generate': True,
            'requires_context': False,
            'estimated_tokens': 500
        },
        'prompt_template': 'test_prompt',
        'file_path': '/path/to/test_plugin.py',
        'file_hash': 'abc123hash'
    }


@pytest.fixture
def mock_plugin_db_record():
    """Fixture for plugin database record"""
    return {
        'plugin_id': 'test-plugin-id-123',
        'plugin_code': 'lm_test',
        'name': 'Test Plugin',
        'description': 'A test plugin',
        'group_code': 'A',
        'tier': 'basic',
        'ki_usage': 'optional',
        'icon': '🧪',
        'config_schema': {'type': 'object'},
        'default_config': {},
        'approval_status': 'pending_review',
        'is_active': False,
        'file_path': '/path/to/test_plugin.py',
        'file_hash': 'abc123hash',
        'submitted_by': 'admin-id',
        'submitted_at': '2026-01-11T10:00:00',
        'reviewed_by': None,
        'reviewed_at': None,
        'activated_at': None,
        'created_at': '2026-01-11T10:00:00',
        'updated_at': '2026-01-11T10:00:00'
    }


@pytest.fixture
def sample_plugin_file_content():
    """Fixture for sample plugin file content"""
    return '''
PLUGIN_METADATA = {
    "plugin_code": "lm_test",
    "name": "Test Plugin",
    "description": "A test plugin",
    "group_code": "A",
    "tier": "basic",
    "ki_usage": "optional",
    "icon": "🧪",
    "config_schema": {
        "type": "object",
        "properties": {
            "test_field": {"type": "string"}
        },
        "required": ["test_field"]
    },
    "default_config": {
        "test_field": "default"
    }
}

def validate_plugin_data(data: dict) -> tuple[bool, str | None]:
    if 'test_field' not in data:
        return False, "test_field is required"
    return True, None
'''
