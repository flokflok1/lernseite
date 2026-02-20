"""
Database Seed for Feature Flags

Initializes all feature flags with their default state.
Run this after database tables are created.

Tables Required:
- feature_flags
- feature_flag_user_overrides
- feature_flag_org_overrides
- feature_flag_segments
- feature_flag_rollouts
"""

from app.core.feature_flags.flag_config import FEATURE_FLAGS, FEATURE_GROUPS
from app.infrastructure.persistence.repositories.feature_flags.seeds import FeatureFlagSeedRepository


def seed_feature_flags():
    """
    Seed database with all feature flags

    Inserts all flags from flag_config.py with their default state
    """
    print("🌱 Seeding feature flags...")

    count = FeatureFlagSeedRepository.seed_flags(FEATURE_FLAGS)

    for feature_name, default_state in FEATURE_FLAGS.items():
        print(f"  ✓ {feature_name}: {'ENABLED' if default_state else 'DISABLED'}")

    print(f"\n✅ Seeded {count} feature flags")


def seed_feature_groups():
    """
    Seed feature flag groups (optional - for admin UI)
    """
    print("\n🌱 Seeding feature flag groups...")

    count = FeatureFlagSeedRepository.seed_groups(FEATURE_GROUPS)

    for group_name, feature_list in FEATURE_GROUPS.items():
        print(f"  ✓ {group_name}: {len(feature_list)} features")

    print(f"\n✅ Seeded {count} feature groups")


def enable_feature_for_beta_users(feature_name: str):
    """
    Enable a feature for all beta users

    Args:
        feature_name: Feature flag name
    """
    FeatureFlagSeedRepository.seed_segment(feature_name, 'beta', True)
    print(f"✅ Enabled '{feature_name}' for beta users")


def set_percentage_rollout(feature_name: str, percentage: int):
    """
    Set percentage rollout for a feature

    Args:
        feature_name: Feature flag name
        percentage: 0-100
    """
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100")

    FeatureFlagSeedRepository.seed_rollout(feature_name, percentage)
    print(f"✅ Set '{feature_name}' to {percentage}% rollout")


if __name__ == '__main__':
    """
    Run this script directly to seed the database

    Usage:
        python -m app.core.feature_flags.db_seed
    """
    print("=" * 60)
    print("FEATURE FLAGS DATABASE SEED")
    print("=" * 60)

    try:
        seed_feature_flags()
        # seed_feature_groups()  # Uncomment if you have feature_flag_groups table

        print("\n" + "=" * 60)
        print("✅ SEEDING COMPLETE")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
