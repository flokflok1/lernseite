#!/usr/bin/env python3
"""
Fix Unified Repository Classes

Erstellt fehlende Unified-Repository-Klassen in Package-__init__.py Dateien
"""
from pathlib import Path
import re

PACKAGES = {
    'agent': ['AgentRepository', 'AgentStatsRepository', 'AgentWarmingRepository', 'AgentExtensionsRepository'],
    'token': ['TokenWalletRepository', 'TokenTransactionRepository', 'TokenAdminRepository', 'TokenAnalyticsRepository'],
    'subscription': ['PlanRepository', 'UserSubscriptionRepository', 'OrganisationSubscriptionRepository', 'SubscriptionLifecycleRepository', 'SubscriptionAnalyticsRepository'],
    'analytics': ['CoreEventsRepository', 'AggregationRepository', 'AdvancedAnalyticsRepository'],
    'learning_method': ['LearningMethodBaseRepository', 'LearningMethodAIRepository', 'LearningMethodFeedbackRepository', 'LearningMethodStatisticsRepository', 'LearningMethodInstanceRepository'],
    'ai_models': ['AIModelsRepository'],  # Schon als einzelne Klasse
    'authoring_action': ['AuthoringActionRepository'],  # Schon als einzelne Klasse
    'lm_model_routing': ['LMModelAssignmentRepository'],  # Schon als einzelne Klasse
    'lm_slot': ['CapabilitySlotRepository', 'LMSlotResolverRepository'],
}

UNIFIED_CLASS_NAMES = {
    'agent': 'AgentRepository',
    'token': 'TokenRepository',
    'subscription': 'SubscriptionRepository',
    'analytics': 'AnalyticsRepository',
    'learning_method': 'LearningMethodRepository',
    'lm_slot': 'LMSlotRepository',
}

def create_unified_class(package_name, sub_repos):
    """Create unified class code"""
    unified_name = UNIFIED_CLASS_NAMES.get(package_name, f"{package_name.title().replace('_', '')}Repository")

    if len(sub_repos) == 1:
        # Single repository - just re-export as unified name
        return f"\n\n# Unified class (re-export single repository)\n{unified_name} = {sub_repos[0]}\n"

    # Multiple repositories - create multi-inheritance class
    class_def = f"\n\nclass {unified_name}(\n"
    class_def += ",\n".join(f"    {repo}" for repo in sub_repos)
    class_def += "\n):\n"
    class_def += f'    """\n    Unified {unified_name} combining all functionality\n'
    class_def += "    This class uses multiple inheritance to aggregate methods from specialized modules.\n"
    class_def += '    """\n'
    class_def += "    pass\n"

    return class_def

def fix_package_init(package_path):
    """Fix a single package __init__.py"""
    init_file = package_path / '__init__.py'

    if not init_file.exists():
        print(f"  ✗ {package_path.name}/__init__.py nicht gefunden")
        return False

    package_name = package_path.name

    if package_name not in PACKAGES:
        return False

    content = init_file.read_text()

    # Check if unified class already exists
    unified_name = UNIFIED_CLASS_NAMES.get(package_name, "")
    if f"class {unified_name}(" in content or f"{unified_name} =" in content:
        print(f"  ✓ {package_name}/ - {unified_name} exists")
        return False

    # Add unified class
    sub_repos = PACKAGES[package_name]
    unified_code = create_unified_class(package_name, sub_repos)

    # Insert before __all__
    if '__all__' in content:
        parts = content.split('__all__')
        new_content = parts[0] + unified_code + "\n\n__all__"

        # Update __all__ to include unified class
        all_match = re.search(r'__all__\s*=\s*\[(.*?)\]', parts[1], re.DOTALL)
        if all_match:
            current_exports = all_match.group(1)
            new_exports = f"    '{unified_name}',\n{current_exports}"
            new_content += f" = [\n{new_exports}]\n"
        else:
            new_content += parts[1]
    else:
        new_content = content + unified_code
        new_content += f"\n\n__all__ = ['{unified_name}']\n"

    init_file.write_text(new_content)
    print(f"  ✓ {package_name}/ - {unified_name} added")
    return True

def main():
    repos_dir = Path(__file__).parent / 'app' / 'repositories'

    print("=" * 80)
    print("Fix Unified Repository Classes")
    print("=" * 80)

    fixed = 0

    for package_name in PACKAGES.keys():
        package_path = repos_dir / package_name
        if package_path.exists():
            if fix_package_init(package_path):
                fixed += 1

    print("=" * 80)
    print(f"✓ Fixed {fixed} packages")
    print("=" * 80)

if __name__ == '__main__':
    main()
