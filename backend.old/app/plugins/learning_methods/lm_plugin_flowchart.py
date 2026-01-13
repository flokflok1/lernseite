"""
Learning Method Plugin: Flowchart Builder
Description: Interactive flowchart creation for process visualization
Group: A (Erklärend - Explanation)
Tier: premium
"""

PLUGIN_METADATA = {
    # Required fields
    "plugin_code": "lm_flowchart",
    "name": "Flowchart Builder",
    "description": "Interactive flowchart creation for process visualization",
    "group_code": "A",  # A=Erklärend, B=Praxis, C=Prüfung
    "tier": "premium",  # basic, premium, or pro
    "ki_usage": "medium",  # intensive, medium, or optional
    "icon": "diagram-project",  # Icon identifier

    # JSON Schema v7 for config validation
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
                "default": 20,
                "description": "Maximum number of nodes in flowchart"
            },
            "allow_branches": {
                "type": "boolean",
                "default": True,
                "description": "Allow conditional branches"
            },
            "flowchart_type": {
                "type": "string",
                "enum": ["linear", "branching", "cyclic"],
                "default": "linear",
                "description": "Type of flowchart structure"
            }
        },
        "required": ["process_description"]
    },

    # Default configuration
    "default_config": {
        "max_nodes": 20,
        "allow_branches": True,
        "flowchart_type": "linear"
    },

    # Agent support (optional)
    "agent_support": {
        "can_generate": True,
        "requires_context": False,
        "estimated_tokens": 1500
    },

    # AI prompt template (optional)
    "prompt_template": "flowchart_generation"
}


def validate_plugin_data(data: dict) -> tuple[bool, str | None]:
    """
    Validate plugin instance data.

    Args:
        data: Plugin instance data dict

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate required fields
    if 'process_description' not in data:
        return False, "process_description is required"

    if not data['process_description'].strip():
        return False, "process_description cannot be empty"

    # Validate optional fields if present
    if 'max_nodes' in data:
        max_nodes = data['max_nodes']
        if not isinstance(max_nodes, int) or max_nodes < 5 or max_nodes > 50:
            return False, "max_nodes must be an integer between 5 and 50"

    if 'flowchart_type' in data:
        valid_types = ['linear', 'branching', 'cyclic']
        if data['flowchart_type'] not in valid_types:
            return False, f"flowchart_type must be one of {valid_types}"

    return True, None
