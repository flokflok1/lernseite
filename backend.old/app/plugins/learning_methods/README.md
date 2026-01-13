# Learning Methods Plugins

This directory contains Learning Method plugins that extend the system with new learning method types.

## Plugin Structure

Each plugin must:
1. Be named `lm_plugin_<name>.py`
2. Define a `PLUGIN_METADATA` dictionary with required fields
3. Implement a `validate_plugin_data(data: dict)` function

## Plugin Metadata Fields

### Required Fields
- `plugin_code` (str): Unique identifier (e.g., "lm_flowchart")
- `name` (str): Display name (e.g., "Flowchart Builder")
- `group_code` (str): Group A, B, or C
- `tier` (str): "basic", "premium", or "pro"
- `ki_usage` (str): "intensive", "medium", or "optional"
- `icon` (str): Icon identifier
- `config_schema` (dict): JSON Schema v7 for configuration validation

### Optional Fields
- `description` (str): Plugin description
- `default_config` (dict): Default configuration values
- `agent_support` (dict): AI agent support metadata
- `prompt_template` (str): AI prompt template name

## Example Plugin

```python
"""
Learning Method Plugin: Flowchart Builder
Description: Interactive flowchart creation
Group: A (Erklärend)
Tier: premium
"""

PLUGIN_METADATA = {
    "plugin_code": "lm_flowchart",
    "name": "Flowchart Builder",
    "description": "Interactive flowchart creation for process visualization",
    "group_code": "A",
    "tier": "premium",
    "ki_usage": "medium",
    "icon": "diagram-project",

    "config_schema": {
        "type": "object",
        "properties": {
            "process_description": {
                "type": "string",
                "description": "Process to visualize"
            },
            "max_nodes": {
                "type": "integer",
                "minimum": 5,
                "maximum": 50,
                "default": 20
            }
        },
        "required": ["process_description"]
    },

    "default_config": {
        "max_nodes": 20
    }
}

def validate_plugin_data(data: dict) -> tuple[bool, str | None]:
    """Validate plugin instance data."""
    if 'process_description' not in data:
        return False, "process_description is required"
    return True, None
```

## Groups

- **Group A - Erklärend (Explanation):** Understanding and theory
- **Group B - Praxis (Practice):** Application and exercises
- **Group C - Prüfung (Assessment):** Testing and evaluation

## Workflow

1. Create plugin file in this directory
2. Admin scans for new plugins via Admin UI
3. Plugin appears in "Pending" tab (pending_review status)
4. Admin reviews metadata and approves/rejects
5. Admin activates approved plugin
6. Plugin becomes available for use in lessons

## Security

- SHA256 hash calculated for plugin integrity
- Admin approval required before activation
- Usage tracking prevents deletion of in-use plugins
- File hash validation on every scan

## See Also

- Migration: `/backend/migrations/02_Content/067_lm_plugins.sql`
- Repository: `/backend/app/repositories/plugins/lm_plugins.py`
- Discovery Service: `/backend/app/services/plugins/lm_discovery.py`
- Registry: `/backend/app/services/plugins/lm_registry.py`
