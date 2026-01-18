"""
Learning Methods Plugin Discovery Service
Scans filesystem for lm_plugin_*.py files and registers them.
"""
import hashlib
import importlib.util
import json
from typing import List, Dict, Optional
from pathlib import Path
from app.infrastructure.persistence.repositories.plugins.lm_plugins import LMPluginRepository


PLUGIN_DIR = Path(__file__).parent.parent.parent.parent / 'plugins' / 'learning_methods'


class LMPluginDiscoveryService:
    """Service for discovering and registering LM plugins."""

    @staticmethod
    def scan_plugins() -> List[Dict]:
        """
        Scan plugin directory for lm_plugin_*.py files.

        Returns:
            List of discovered plugin metadata dicts
        """
        discovered = []

        if not PLUGIN_DIR.exists():
            print(f"Plugin directory does not exist: {PLUGIN_DIR}")
            return discovered

        for file_path in PLUGIN_DIR.glob('lm_plugin_*.py'):
            try:
                metadata = LMPluginDiscoveryService._extract_metadata(file_path)
                if metadata:
                    discovered.append(metadata)
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")

        return discovered

    @staticmethod
    def _extract_metadata(file_path: Path) -> Optional[Dict]:
        """
        Extract PLUGIN_METADATA from Python file without executing code.

        Args:
            file_path: Path to plugin file

        Returns:
            Metadata dict or None
        """
        # Load module
        spec = importlib.util.spec_from_file_location("temp_plugin", file_path)
        if not spec or not spec.loader:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Extract PLUGIN_METADATA
        if not hasattr(module, 'PLUGIN_METADATA'):
            return None

        metadata = module.PLUGIN_METADATA

        # Add file info
        metadata['file_path'] = str(file_path)
        metadata['file_hash'] = LMPluginDiscoveryService._hash_file(file_path)

        return metadata

    @staticmethod
    def _hash_file(file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def register_plugin(metadata: Dict, submitted_by: str) -> Optional[str]:
        """
        Register discovered plugin in database (pending_review state).

        Args:
            metadata: Plugin metadata dict
            submitted_by: User UUID who triggered scan

        Returns:
            Plugin UUID or None
        """
        # Check if plugin already exists
        existing = LMPluginRepository.find_by_code(metadata['plugin_code'])
        if existing:
            # Update file_hash if changed
            if existing['file_hash'] != metadata['file_hash']:
                LMPluginRepository.update_file_hash(metadata['plugin_code'], metadata['file_hash'])
            return existing['plugin_id']

        # Serialize JSON fields
        config_schema_json = json.dumps(metadata['config_schema'])
        default_config_json = json.dumps(metadata.get('default_config')) if metadata.get('default_config') else None
        agent_support_json = json.dumps(metadata.get('agent_support')) if metadata.get('agent_support') else None

        # Prepare plugin data
        plugin_data = {
            'plugin_code': metadata['plugin_code'],
            'name': metadata['name'],
            'description': metadata.get('description'),
            'group_code': metadata['group_code'],
            'tier': metadata['tier'],
            'ki_usage': metadata['ki_usage'],
            'icon': metadata['icon'],
            'config_schema': config_schema_json,
            'default_config': default_config_json,
            'agent_support': agent_support_json,
            'prompt_template': metadata.get('prompt_template'),
            'file_path': metadata['file_path'],
            'file_hash': metadata['file_hash'],
            'submitted_by': submitted_by
        }

        # Insert new plugin
        plugin_id = LMPluginRepository.insert_plugin(plugin_data)

        # Log submission
        if plugin_id:
            LMPluginRepository._log_approval_action(
                plugin_id, 'submitted', submitted_by, None
            )

        return plugin_id
