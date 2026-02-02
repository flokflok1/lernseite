"""
Learning Methods Runtime Registry (Singleton)
Loads and caches active plugins with hot-reload capability.
Built-in LMs (0-11) are database-driven; plugins (100+) extend the registry.
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from app.infrastructure.persistence.repositories.learning_method.catalog import LearningMethodCatalogRepository
from app.infrastructure.persistence.repositories.plugins.lm_plugins import LMPluginRepository
import logging

logger = logging.getLogger(__name__)


class LMPluginRegistry:
    """
    Singleton registry for Learning Method plugins.
    Hot-reloads every 5 minutes to pick up new/updated plugins.

    Method Type Ranges:
    - 0-11: Built-in LMs (from database - learning_method_types table)
    - 100+: Plugin LMs (from database - extensions)
    """

    _instance: Optional['LMPluginRegistry'] = None
    _plugins: Dict[int, Dict] = {}  # plugin method_type -> plugin data
    _plugin_id_map: Dict[int, str] = {}  # method_type -> plugin_id mapping
    _last_reload: Optional[datetime] = None
    _reload_interval = timedelta(minutes=5)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._plugins = {}
            cls._instance._plugin_id_map = {}
            cls._instance._last_reload = None
        return cls._instance

    def get_learning_method(self, method_type: int) -> Optional[Dict]:
        """
        Get learning method by type (built-in or plugin).
        Auto-reloads if interval expired.

        Args:
            method_type: Method type ID (0-11 built-in, 100+ plugin)

        Returns:
            Learning method dict or None (database-driven)
        """
        self._maybe_reload()

        # Built-in LMs (0-11) from database
        if 0 <= method_type <= 11:
            return LearningMethodCatalogRepository.get_by_type(method_type=method_type)

        # Plugin LMs (100+)
        return self._plugins.get(method_type)

    def get_all_methods(self) -> Dict[int, Dict]:
        """
        Get all learning methods (built-in + plugins).

        Returns:
            Dictionary mapping method_type to method dict (database-driven)
        """
        self._maybe_reload()

        all_methods = {}
        # Add built-in LMs (0-11) from database
        for method_type in range(12):
            method_data = LearningMethodCatalogRepository.get_by_type(method_type=method_type)
            if method_data:
                all_methods[method_type] = method_data

        # Add plugin LMs (100+)
        all_methods.update(self._plugins)

        return all_methods

    def get_plugin_id_by_method_type(self, method_type: int) -> Optional[str]:
        """
        Get plugin_id for a given method_type.

        Args:
            method_type: Method type ID (100+)

        Returns:
            Plugin UUID or None
        """
        self._maybe_reload()
        return self._plugin_id_map.get(method_type)

    def force_reload(self):
        """Force immediate reload of plugins."""
        logger.info("Force reloading LM plugin registry...")
        self._load_plugins()

    def _maybe_reload(self):
        """Reload plugins if interval expired."""
        now = datetime.utcnow()
        if self._last_reload is None or (now - self._last_reload) > self._reload_interval:
            logger.info("Hot-reloading LM plugin registry (interval expired)...")
            self._load_plugins()

    def _load_plugins(self):
        """Load active plugins from database."""
        try:
            active_plugins = LMPluginRepository.get_active_plugins()

            self._plugins.clear()
            self._plugin_id_map.clear()

            for plugin in active_plugins:
                # Allocate method_type (100+)
                method_type = self._allocate_method_type(plugin)

                # Convert to LearningMethodDefinition
                lm_def = self._plugin_to_definition(plugin, method_type)

                self._plugins[method_type] = lm_def
                self._plugin_id_map[method_type] = plugin['plugin_id']

            self._last_reload = datetime.utcnow()
            logger.info(f"Loaded {len(active_plugins)} active plugin(s) into registry")

        except Exception as e:
            logger.error(f"Error loading plugins into registry: {e}")
            # Keep old plugins in case of error

    def _allocate_method_type(self, plugin: Dict) -> int:
        """
        Allocate method_type for plugin (100+).

        Strategy: Use plugin_id hash to generate stable method_type.
        This ensures the same plugin always gets the same method_type.

        Args:
            plugin: Plugin data dictionary

        Returns:
            Method type (>= 100)
        """
        # Use plugin_id hash to generate stable method_type
        plugin_id_hash = hash(plugin['plugin_id'])
        # Ensure method_type is in range 100-999 (900 possible slots)
        method_type = 100 + (abs(plugin_id_hash) % 900)

        # Check for collision (very unlikely with 900 slots)
        while method_type in self._plugins:
            method_type += 1
            if method_type >= 1000:
                method_type = 100  # Wrap around

        return method_type

    def _plugin_to_definition(self, plugin: Dict, method_type: int) -> Dict:
        """
        Convert plugin database record to standard method dict (database-driven).

        Args:
            plugin: Plugin data from database
            method_type: Allocated method_type

        Returns:
            Method dict matching database schema
        """
        return {
            'method_type': method_type,
            'name': plugin['name'],
            'description': plugin.get('description', ''),
            'group_code': plugin['group_code'],
            'tier': plugin['tier'],
            'icon': plugin.get('icon', 'puzzle-piece'),
            'prompt_template': plugin.get('prompt_template'),
            'default_config': plugin.get('default_config'),
            'agent_support': plugin.get('agent_support'),
            'ki_usage': plugin.get('ki_usage', 'intensive')
        }


# Global registry instance
_registry = LMPluginRegistry()


def get_learning_method(method_type: int) -> Optional[Dict]:
    """
    Get learning method by type (built-in or plugin).

    This is the main entry point for getting any learning method.
    Returns database-driven method definition.

    Args:
        method_type: Method type ID (0-11 built-in, 100+ plugin)

    Returns:
        Method dict or None

    Example:
        >>> lm = get_learning_method(0)  # Built-in LM00
        >>> print(lm['name'])
        'Tiefgehende Erklärung'

        >>> plugin_lm = get_learning_method(100)  # Plugin LM
        >>> print(plugin_lm['name'] if plugin_lm else 'Not loaded')
    """
    return _registry.get_learning_method(method_type)


def get_all_learning_methods() -> Dict[int, Dict]:
    """
    Get all learning methods (built-in + plugins).

    Returns database-driven method definitions.

    Returns:
        Dictionary mapping method_type to method dict
    """
    return _registry.get_all_methods()


def force_reload_registry():
    """
    Force immediate reload of plugin registry.

    Use this after activating/deactivating plugins via admin panel.
    """
    _registry.force_reload()


def get_plugin_id_by_method_type(method_type: int) -> Optional[str]:
    """
    Get plugin_id for a given method_type.

    Args:
        method_type: Method type ID (100+)

    Returns:
        Plugin UUID or None
    """
    return _registry.get_plugin_id_by_method_type(method_type)
